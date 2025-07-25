import json
from uuid import UUID

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.services.chat_service import manager
from app.utils.logger import get_logger, Module

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)
logger = get_logger(Module.WEBSOCKET)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    await websocket.accept()
    await manager.connect(websocket, user_id)
    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)

            logger.info(data)

            recipient_id_str = data['recipient_id']
            message = data['message']

            try:
                recipient_uuid = UUID(recipient_id_str)
            except ValueError:
                logger.warning(f"Invalid recipient_id format: {recipient_id_str}")
                continue

            # await manager.send_message(message, recipient_id)
            full_message_payload = {
                "sender_id": str(user_id),
                "message": message
            }

            await manager.send_message(json.dumps(full_message_payload), recipient_uuid)

    except WebSocketDisconnect:
        logger.warning(f"{user_id} hiện không online.")
        await manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"Lỗi xảy ra với client {user_id}: {e}")
        await manager.disconnect(user_id)
