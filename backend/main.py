import asyncio


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from database import Base, engine
import models

# =========================================================
# API ROUTES
# =========================================================

from routes.vehicles import router as vehicle_router
from routes.parking import router as parking_router
from routes.exits import router as exit_router
from routes.recommendations import router as recommendation_router
from routes.route_guidance import router as route_guidance_router
from routes.dashboard import router as dashboard_router
from routes.simulation import router as simulation_router
from routes.vision import router as vision_router
from routes.web import router as web_router

# =========================================================
# WEBSOCKET MANAGERS
# =========================================================

from utils.websocket_manager import manager
from utils.route_manager import route_manager
from utils.dashboard_manager import dashboard_manager
from utils.recommendation_manager import recommendation_manager


# =========================================================
# SERVICES
# =========================================================

from services.parking_simulator import start_simulation

from services.shared_camera import shared_camera

from services.vision_state import (
    vision_sync,
    vision_manager
)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Parking Exit Flow Optimizer",
    description=(
        "AI-based smart parking management "
        "and exit optimization system"
    ),
    version="1.0.0"
)
app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static"
)


# =========================================================
# VISION SERVICES
# =========================================================

# Both vision services use the SAME camera.




# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
async def startup_event():

    print(
        "🚀 AI Parking Exit Flow Optimizer starting..."
    )

    # -----------------------------------------------------
    # Start ONE shared camera
    # -----------------------------------------------------

    try:

        shared_camera.start()

        print(
            "🎥 Shared camera ready."
        )

    except Exception as error:

        print(
            f"❌ Camera startup error: {error}"
        )

        # Continue starting the API.
        # Vision services will not work until
        # the camera becomes available.

    # -----------------------------------------------------
    # Start simulated parking traffic
    # -----------------------------------------------------

    asyncio.create_task(
        start_simulation()
    )

    print(
        "✅ Real-time parking simulation started."
    )

    # -----------------------------------------------------
    # Start parking occupancy vision
    # -----------------------------------------------------

    if shared_camera.running:

        asyncio.create_task(
            vision_sync.run()
        )

        print(
            "🚗 Real-time parking vision "
            "monitoring started."
        )

        # -------------------------------------------------
        # Start live exit AI vision
        # -------------------------------------------------

        asyncio.create_task(
            vision_manager.run()
        )

        print(
            "🤖 Live vision AI analysis started."
        )

    else:

        print(
            "⚠️ Vision services were not started "
            "because the shared camera is unavailable."
        )


# =========================================================
# INCLUDE API ROUTERS
# =========================================================

app.include_router(
    vehicle_router
)

app.include_router(
    parking_router
)

app.include_router(
    exit_router
)

app.include_router(
    recommendation_router
)

app.include_router(
    route_guidance_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    simulation_router
)

app.include_router(
    vision_router
)

app.include_router(web_router)

# =========================================================
# PARKING WEBSOCKET
# =========================================================

@app.websocket(
    "/ws/parking"
)
async def parking_websocket(
    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )


# =========================================================
# VEHICLE ROUTE WEBSOCKET
# =========================================================

@app.websocket(
    "/ws/route/{vehicle_number}"
)
async def route_websocket(
    websocket: WebSocket,
    vehicle_number: str
):

    await route_manager.connect(
        vehicle_number,
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        route_manager.disconnect(
            vehicle_number,
            websocket
        )


# =========================================================
# DASHBOARD WEBSOCKET
# =========================================================

@app.websocket(
    "/ws/dashboard"
)
async def dashboard_websocket(
    websocket: WebSocket
):

    await dashboard_manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        dashboard_manager.disconnect(
            websocket
        )


# =========================================================
# AI RECOMMENDATION WEBSOCKET
# =========================================================

@app.websocket(
    "/ws/recommendations"
)
async def recommendation_websocket(
    websocket: WebSocket
):

    await recommendation_manager.connect(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        recommendation_manager.disconnect(
            websocket
        )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": (
            "AI Parking Exit Flow Optimizer"
        ),
        "status": "running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "database": "connected",
        "vision": (
            "enabled"
            if shared_camera.running
            else "unavailable"
        ),
        "simulation": "enabled",
        "live_ai": (
            "enabled"
            if shared_camera.running
            else "unavailable"
        )
    }


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event("shutdown")
async def shutdown_event():

    print(
        "🛑 AI Parking Exit Flow Optimizer shutting down..."
    )

    # Stop parking vision service
    vision_sync.stop()

    # Stop live AI vision service
    vision_manager.stop()

    # Stop the ONE shared camera
    shared_camera.stop()

    print(
        "✅ All vision services stopped."
    )

