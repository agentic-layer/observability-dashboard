import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.routes.traces import router as trace_router
from .api.routes.websockets import router as websocket_router
from .utils.log_filters import EndpointFilter

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="Observability Dashboard",
    description="App for receiving and processing tracing data and sending them out via websocket",
)

excluded_endpoints = ["/health"]
logging.getLogger("uvicorn.access").addFilter(EndpointFilter(excluded_endpoints))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include the API routers first (before static file mounting)
app.include_router(trace_router)
app.include_router(websocket_router)

# Mount static files with SPA support
app.mount("/", StaticFiles(directory="./frontend/dist/", html=True, check_dir=False), name="spa")
