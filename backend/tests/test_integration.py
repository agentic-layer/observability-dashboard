"""Integration tests for trace receiving and event sending."""

import json
import signal
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2
from opentelemetry.sdk.trace import TracerProvider
from starlette.websockets import WebSocketDisconnect

from agent_monitor.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tracer_provider(client):
    """Set up OpenTelemetry tracing that sends to the test client."""
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    provider = TracerProvider()

    class TestClientExporter:
        def export(self, spans):
            if spans:
                request = trace_service_pb2.ExportTraceServiceRequest()
                resource_spans = request.resource_spans.add()
                scope_spans = resource_spans.scope_spans.add()

                for span in spans:
                    if span.attributes.get("conversation_id"):
                        otlp_span = scope_spans.spans.add()
                        otlp_span.name = span.name
                        otlp_span.span_id = span.context.span_id.to_bytes(8, "big")
                        otlp_span.trace_id = span.context.trace_id.to_bytes(16, "big")
                        otlp_span.start_time_unix_nano = span.start_time
                        otlp_span.end_time_unix_nano = span.end_time or span.start_time

                        for key, value in span.attributes.items():
                            kv_pair = otlp_span.attributes.add()
                            kv_pair.key = key
                            if isinstance(value, str):
                                kv_pair.value.string_value = value
                            elif isinstance(value, bool):
                                kv_pair.value.bool_value = value
                            elif isinstance(value, int):
                                kv_pair.value.int_value = value
                            else:
                                kv_pair.value.string_value = str(value)

                client.post(
                    "/v1/traces",
                    content=request.SerializeToString(),
                    headers={"content-type": "application/x-protobuf"},
                )
            return None

        def shutdown(self):
            pass

    processor = SimpleSpanProcessor(TestClientExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return provider


@pytest.fixture
def mock_spans_data():
    """Load mock spans data from JSON file."""
    mock_file = Path(__file__).parent / "mock_spans.json"
    with open(mock_file) as f:
        return json.load(f)


def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutError("WebSocket receive timeout")


def receive_with_timeout(websocket):
    """Receive JSON from WebSocket with proper timeout using signal."""
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1)

    try:
        return websocket.receive_json()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def create_test_spans_from_mock_data(mock_data: List[Dict[str, Any]], client: TestClient):
    """Create OpenTelemetry spans from mock data and send them to the endpoint."""
    tracer = trace.get_tracer(__name__)

    for span_data in mock_data:
        start_time = time.time_ns()
        with tracer.start_as_current_span(span_data.get("name", "test_span"), start_time=start_time) as span:
            attributes = span_data.get("attributes", {})
            for key, value in attributes.items():
                span.set_attribute(key, value)
            time.sleep(5e-9)
        time.sleep(20e-6)


def test_full_system_integration(client, mock_spans_data, tracer_provider):
    """Test complete system: receive spans -> process -> send to WebSockets."""
    conversation_1 = None
    for span_data in mock_spans_data:
        if "conversation_id" in span_data.get("attributes", {}):
            conversation_1 = span_data["attributes"]["conversation_id"]
            break

    assert conversation_1 is not None, "Could not find conversation_id in mock data"

    global_events = []
    conversation_events = []

    with client.websocket_connect("/ws") as global_ws:
        welcome = global_ws.receive_json()
        assert welcome["type"] == "global_connection_established"

        with client.websocket_connect(f"/ws/{conversation_1}") as conv_ws:
            conv_welcome = conv_ws.receive_json()
            assert conv_welcome["type"] == "connection_established"
            assert conv_welcome["conversation_id"] == conversation_1

            create_test_spans_from_mock_data(mock_spans_data, client)
            time.sleep(0.1)

            for _ in range(35):
                try:
                    event = receive_with_timeout(conv_ws)
                    conversation_events.append(event)
                except (WebSocketDisconnect, TimeoutError):
                    pass

            for _ in range(40):
                try:
                    event = receive_with_timeout(global_ws)
                    global_events.append(event)
                except (WebSocketDisconnect, TimeoutError):
                    pass

    assert len(global_events) == 34, f"Expected 34 global events, got {len(global_events)}"
    assert len(conversation_events) == 30, f"Expected 30 conversation events, got {len(conversation_events)}"

    for event in conversation_events:
        assert event["conversation_id"] == conversation_1


def test_conversation_filtering(client, mock_spans_data, tracer_provider):
    """Test that conversation-specific WebSocket only receives events for that conversation."""
    conversation_1 = None
    for span_data in mock_spans_data:
        if "conversation_id" in span_data.get("attributes", {}):
            conversation_1 = span_data["attributes"]["conversation_id"]
            break

    assert conversation_1 is not None, "Could not find conversation_id in mock data"
    events_received = []

    with client.websocket_connect(f"/ws/{conversation_1}") as websocket:
        websocket.receive_json()
        create_test_spans_from_mock_data(mock_spans_data, client)
        time.sleep(0.1)

        try:
            for _ in range(35):
                event = receive_with_timeout(websocket)
                events_received.append(event)
        except (WebSocketDisconnect, TimeoutError):
            pass

    assert len(events_received) > 0, "Expected some events to be received"
    for event in events_received:
        assert event.get("conversation_id") == conversation_1


def test_invalid_trace_data(client):
    """Test handling of invalid trace data."""
    response = client.post(
        "/v1/traces", content=b"invalid protobuf data", headers={"content-type": "application/x-protobuf"}
    )
    assert response.status_code == 400


def test_empty_trace_data(client):
    """Test handling of empty trace data."""
    # Send empty content - the endpoint should handle gracefully
    response = client.post("/v1/traces", content=b"", headers={"content-type": "application/x-protobuf"})
    # Empty data might return 400, which is acceptable behavior
    assert response.status_code in [200, 400]
