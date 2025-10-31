"""Tests for the filter options API endpoint."""

import time
from typing import Any

import pytest
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tracer_provider(client: TestClient) -> TracerProvider:
    """Set up OpenTelemetry tracing that sends to the test client."""
    from opentelemetry.proto.collector.trace.v1 import trace_service_pb2
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

    provider = TracerProvider()

    class TestClientExporter(SpanExporter):
        def export(self, spans: Any) -> SpanExportResult:
            if spans:
                request = trace_service_pb2.ExportTraceServiceRequest()
                resource_spans = request.resource_spans.add()
                scope_spans = resource_spans.scope_spans.add()

                # Add workforce resource attribute
                resource_attr = resource_spans.resource.attributes.add()
                resource_attr.key = "agentic_layer.workforce"
                resource_attr.value.string_value = "test-workforce"

                for span in spans:
                    if span.attributes and span.attributes.get("conversation_id"):
                        otlp_span = scope_spans.spans.add()
                        otlp_span.name = span.name
                        otlp_span.span_id = span.context.span_id.to_bytes(8, "big")
                        otlp_span.trace_id = span.context.trace_id.to_bytes(16, "big")
                        otlp_span.start_time_unix_nano = span.start_time or 0
                        otlp_span.end_time_unix_nano = span.end_time or span.start_time or 0

                        if span.attributes:
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
            return SpanExportResult.SUCCESS

        def shutdown(self) -> None:
            pass

    processor = SimpleSpanProcessor(TestClientExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return provider


def test_filter_api_empty_state(client: TestClient) -> None:
    """Test that the filter API returns empty lists when no events have been processed."""
    # Clear any existing state by accessing the registry
    from app.core.state import filter_registry

    filter_registry.conversation_ids.clear()
    filter_registry.workforce_names.clear()

    response = client.get("/api/filters")
    assert response.status_code == 200

    data = response.json()
    assert "conversation_ids" in data
    assert "workforce_names" in data
    assert isinstance(data["conversation_ids"], list)
    assert isinstance(data["workforce_names"], list)


def test_filter_api_with_events(client: TestClient, tracer_provider: TracerProvider) -> None:
    """Test that the filter API returns tracked values after processing events."""
    # Clear state
    from app.core.state import filter_registry

    filter_registry.conversation_ids.clear()
    filter_registry.workforce_names.clear()

    # Create test spans with different conversation IDs
    tracer = trace.get_tracer(__name__)

    test_conversations = [
        "conv-id-1",
        "conv-id-2",
        "conv-id-3",
    ]

    for conv_id in test_conversations:
        start_time = time.time_ns()
        with tracer.start_as_current_span("before_agent", start_time=start_time) as span:
            span.set_attribute("conversation_id", conv_id)
            span.set_attribute("agent_name", "test-agent")

    # Give events time to process
    time.sleep(0.1)

    # Check the API
    response = client.get("/api/filters")
    assert response.status_code == 200

    data = response.json()

    # Should have all three conversation IDs
    assert len(data["conversation_ids"]) == 3
    assert set(data["conversation_ids"]) == set(test_conversations)

    # Should have the workforce name from resource attributes
    assert len(data["workforce_names"]) == 1
    assert "test-workforce" in data["workforce_names"]


def test_filter_stats_endpoint(client: TestClient, tracer_provider: TracerProvider) -> None:
    """Test the filter stats endpoint."""
    # Clear state
    from app.core.state import filter_registry

    filter_registry.conversation_ids.clear()
    filter_registry.workforce_names.clear()

    # Create a test span
    tracer = trace.get_tracer(__name__)
    start_time = time.time_ns()
    with tracer.start_as_current_span("before_agent", start_time=start_time) as span:
        span.set_attribute("conversation_id", "test-conv-123")
        span.set_attribute("agent_name", "test-agent")

    # Give events time to process
    time.sleep(0.1)

    # Check the stats API
    response = client.get("/api/filters/stats")
    assert response.status_code == 200

    data = response.json()
    assert "conversation_ids_count" in data
    assert "workforce_names_count" in data
    assert data["conversation_ids_count"] == 1
    assert data["workforce_names_count"] == 1
