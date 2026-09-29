import asyncio
import websockets


async def test_dashboard_websocket():

    uri = "ws://127.0.0.1:8000/ws/dashboard"

    print(
        "Connecting to dashboard WebSocket..."
    )

    async with websockets.connect(
        uri
    ) as websocket:

        print(
            "Dashboard WebSocket connected!"
        )

        print(
            "Waiting for dashboard update..."
        )

        print(
            "--------------------------------"
        )

        try:

            message = await asyncio.wait_for(

                websocket.recv(),

                timeout=30
            )

            print(
                "Received dashboard update:"
            )

            print(message)

        except asyncio.TimeoutError:

            print(
                "No dashboard update "
                "received within 30 seconds."
            )


asyncio.run(
    test_dashboard_websocket()
)