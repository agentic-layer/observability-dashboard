import logging

from fastapi import FastAPI

from .api.routes.traces import router as trace_router
from .api.routes.websockets import router as websocket_router

app = FastAPI(
    title="Agent Communication Dashboard Backend",
    description="Backend service for receiving and processing tracing data and sending them out via websocket",
)

logger = logging.getLogger(__name__)

# Include the routers
app.include_router(trace_router)
app.include_router(websocket_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
