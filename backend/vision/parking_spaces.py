import json
import os


LAYOUT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "parking_layout.json"
)


def generate_default_spaces():

    parking_spaces = []

    space_number = 1

    for row in range(10):

        for column in range(10):

            x1 = 50 + column * 170
            y1 = 100 + row * 150

            x2 = x1 + 150
            y2 = y1 + 120

            parking_spaces.append({
                "space_number": f"P{space_number:03d}",
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })

            space_number += 1

    return parking_spaces


def load_parking_spaces():

    if not os.path.exists(LAYOUT_FILE):

        print(
            "⚠️ parking_layout.json not found."
        )

        print(
            "📐 Using default 100-space layout."
        )

        return generate_default_spaces()

    try:

        with open(
            LAYOUT_FILE,
            "r"
        ) as file:

            parking_spaces = json.load(file)

        # Empty layout means that no parking
        # positions have been configured yet.
        #
        # It does NOT mean that there are
        # zero vehicles.

        if not isinstance(
            parking_spaces,
            list
        ):

            print(
                "⚠️ Invalid parking layout format."
            )

            print(
                "📐 Using default layout."
            )

            return generate_default_spaces()

        if len(parking_spaces) == 0:

            print(
                "⚠️ Parking layout is empty."
            )

            print(
                "📐 Using default 100-space layout."
            )

            return generate_default_spaces()

        print(
            f"✅ Loaded "
            f"{len(parking_spaces)} parking spaces."
        )

        return parking_spaces

    except Exception as error:

        print(
            f"❌ Parking layout error: {error}"
        )

        print(
            "📐 Using default 100-space layout."
        )

        return generate_default_spaces()


PARKING_SPACES = load_parking_spaces()