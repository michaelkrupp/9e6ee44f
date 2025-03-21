import os
import signal
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ...infrastructure.logging import LoggingContextMiddleware, get_logger
from ..service.chat_service import ChatService
from .routes import router

logger: Final = get_logger(__name__)


def handle_sigint(signal, frame):
    logger.info("SIGINT received, terminating application")
    os._exit(0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    signal.signal(signal.SIGINT, handle_sigint)
    logger.info("Application ready")
    app.state.chat_service = ChatService()
    yield
    logger.info("Application exit")


app: Final[FastAPI] = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",
)

app.add_middleware(LoggingContextMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
