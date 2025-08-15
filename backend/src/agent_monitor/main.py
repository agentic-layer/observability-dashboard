import logging

from fastapi import FastAPI

from .api.routes.traces import router as trace_router
from .api.routes.websockets import router as websocket_router
from .utils.log_filters import EndpointFilter

app = FastAPI(
    title="Agent Communication Dashboard Backend",
    description="Backend service for receiving and processing tracing data and sending them out via websocket",
)

excluded_endpoints = ["/health"]
logging.getLogger("uvicorn.access").addFilter(EndpointFilter(excluded_endpoints))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


logger = logging.getLogger(__name__)

# Include the routers
app.include_router(trace_router)
app.include_router(websocket_router)
