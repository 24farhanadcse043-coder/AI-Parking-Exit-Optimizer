import asyncio
import websockets


async def test_recommendation_websocket():

    uri = "ws://127.0.0.1:8000/ws/recommendations"

    print("Connecting to AI recommendation WebSocket...")

    async with websockets.connect(uri) as websocket:

        print("AI recommendation WebSocket connected!")
        print("Waiting for recommendation update...")
        print("--------------------------------")

        try:

            message = await asyncio.wait_for(
                websocket.recv(),
                timeout=30
            )

            print("Received AI recommendation:")
            print(message)

        except asyncio.TimeoutError:

            print(
                "No recommendation update received "
                "within 30 seconds."
            )


asyncio.run(test_recommendation_websocket())