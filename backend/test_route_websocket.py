import asyncio
import websockets


async def test_route_websocket():

    vehicle_number = "TN03EF9012"

    uri = (
        f"ws://127.0.0.1:8000"
        f"/ws/route/{vehicle_number}"
    )

    print("Connecting to vehicle route WebSocket...")

    async with websockets.connect(uri) as websocket:

        print("Vehicle route WebSocket connected!")
        print("Waiting for route update...")
        print("--------------------------------")

        try:

            message = await asyncio.wait_for(
                websocket.recv(),
                timeout=30
            )

            print("Received route update:")
            print(message)

        except asyncio.TimeoutError:

            print(
                "No route update received "
                "within 30 seconds."
            )


asyncio.run(test_route_websocket())