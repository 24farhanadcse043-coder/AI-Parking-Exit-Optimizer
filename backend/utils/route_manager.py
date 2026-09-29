from fastapi import WebSocket


class RouteConnectionManager:

    def __init__(self):
        self.active_connections = {}

    async def connect(
        self,
        vehicle_number: str,
        websocket: WebSocket
    ):
        await websocket.accept()

        if vehicle_number not in self.active_connections:
            self.active_connections[vehicle_number] = []

        self.active_connections[vehicle_number].append(
            websocket
        )

    def disconnect(
        self,
        vehicle_number: str,
        websocket: WebSocket
    ):
        if vehicle_number in self.active_connections:

            if websocket in self.active_connections[
                vehicle_number
            ]:
                self.active_connections[
                    vehicle_number
                ].remove(websocket)

            if not self.active_connections[
                vehicle_number
            ]:
                del self.active_connections[
                    vehicle_number
                ]

    async def send_to_vehicle(
        self,
        vehicle_number: str,
        message: dict
    ):
        if vehicle_number not in self.active_connections:
            return

        disconnected = []

        for websocket in self.active_connections[
            vehicle_number
        ]:

            try:
                await websocket.send_json(message)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(
                vehicle_number,
                websocket
            )


route_manager = RouteConnectionManager()