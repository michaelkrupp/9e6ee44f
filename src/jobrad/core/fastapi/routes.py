import json
from typing import Final

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ...domain.chat_message import ChatMessage, ChatMessageID
from ...domain.chat_room import ChatRoom, ChatRoomID
from ...infrastructure.logging import get_logger
from ..service.chat_service import ChatService
from .templates import AGENT_TEMPLATE, CUSTOMER_TEMPLATE, templates

router: Final[APIRouter] = APIRouter()
logger: Final = get_logger(__name__)

router.mount("/static", StaticFiles(directory="static"), name="static")

CHAT_ROOM_ID_COOKIE: Final[str] = "chat_room_id"


@router.get("/", response_class=HTMLResponse)
async def get_customer_view(request: Request):
    chat_service: ChatService = request.app.state.chat_service

    try:
        chat_room_id = request.cookies[CHAT_ROOM_ID_COOKIE]
        chat_room = await chat_service.get_chat_room(chat_room_id)
    except KeyError:
        chat_room = await chat_service.create_chat_room()

    response = templates.TemplateResponse(
        request=request,
        name=CUSTOMER_TEMPLATE,
        context=dict(state=request.app.state, chat_room=chat_room),
    )
    response.set_cookie(CHAT_ROOM_ID_COOKIE, chat_room.id)
    return response


@router.get("/agent", response_class=HTMLResponse)
async def get_agent_view(request: Request):
    chat_service: ChatService = request.app.state.chat_service
    chat_rooms = await chat_service.get_chat_rooms()

    response = templates.TemplateResponse(
        request=request,
        name=AGENT_TEMPLATE,
        context=dict(state=request.app.state, chat_rooms=chat_rooms),
    )
    return response


@router.websocket("/chat/{chat_room_id}")
async def customer_websocket(websocket: WebSocket, chat_room_id: ChatRoomID):
    await websocket.accept()

    chat_service: ChatService = websocket.app.state.chat_service

    try:
        chat_room = await chat_service.get_chat_room(chat_room_id)
    except KeyError:
        logger.error("Chat room not found", chat_room_id=chat_room_id)
        await websocket.close()
        return

    await chat_service.subscribe_messages(chat_room.id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                chat_message = ChatMessage.from_json(
                    data,
                    sender="customer",
                )
            except json.JSONDecodeError:
                logger.error(
                    "Invalid JSON",
                    chat_room_id=chat_room_id,
                    websocket_id=id(websocket),
                    data=data,
                )
                continue
            await chat_service.send_message(chat_room.id, chat_message)
    except WebSocketDisconnect:
        pass
    finally:
        await chat_service.unsubscribe_messages(chat_room.id, websocket)


@router.websocket("/agent/chat/{chat_room_id}")
async def agent_websocket(websocket: WebSocket, chat_room_id: ChatRoomID):
    await websocket.accept()

    chat_service: ChatService = websocket.app.state.chat_service

    try:
        chat_room = await chat_service.get_chat_room(chat_room_id)
    except KeyError:
        logger.error("Chat room not found", chat_room_id=chat_room_id)
        await websocket.close()
        return

    await chat_service.subscribe_messages(chat_room.id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                chat_message = ChatMessage.from_json(
                    data,
                    sender="agent",
                )
            except json.JSONDecodeError:
                logger.error(
                    "Invalid JSON",
                    chat_room_id=chat_room_id,
                    websocket_id=id(websocket),
                    data=data,
                )
                continue
            await chat_service.send_message(chat_room.id, chat_message)
    except WebSocketDisconnect:
        pass
    finally:
        await chat_service.unsubscribe_messages(chat_room.id, websocket)


@router.websocket("/agent/notifications")
async def agent_notifications(websocket: WebSocket):
    await websocket.accept()

    chat_service: ChatService = websocket.app.state.chat_service

    await chat_service.subscribe_notifications(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await chat_service.unsubscribe_notifications(websocket)
