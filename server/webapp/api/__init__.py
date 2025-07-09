from common.config import SERVICE_API_KEYS
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .bots import router as bots_router
from .conversations import router as conversations_router
from .scenario import router as scenario_router

router = APIRouter()

router.include_router(conversations_router, tags=["Conversations"])
router.include_router(bots_router, tags=["Bots"])
router.include_router(scenario_router, tags=["Scenario"])


@router.get("/", response_class=JSONResponse)
async def config():
    # Note: do not send gemini-api-key in production (key will be exposed to the client.) Please see README.
    return {
        "websocket-enabled": bool(SERVICE_API_KEYS["gemini"]),
        "webrtc-enabled": bool(SERVICE_API_KEYS["daily"]),
        "gemini-api-key": SERVICE_API_KEYS["gemini"],
    }
