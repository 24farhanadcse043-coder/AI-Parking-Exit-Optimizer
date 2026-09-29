import asyncio
import websockets


async def test_websocket():

    uri = "ws://127.0.0.1:8000/ws/parking"

    async with websockets.connect(uri) as websocket:

        print("WebSocket connected successfully!")
        print("Waiting for parking update...")

        try:
            message = await asyncio.wait_for(
                websocket.recv(),
                timeout=10
            )

            print("Received real-time update:")
            print(message)

        except asyncio.TimeoutError:
            print("No update received within 10 seconds.")


asyncio.run(test_websocket())