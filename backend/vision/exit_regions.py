import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

REGION_FILE = os.path.join(
    BASE_DIR,
    "exit_regions.json"
)


DEFAULT_REGIONS = {
    "Exit A": {
        "x1": 0,
        "y1": 0,
        "x2": 640,
        "y2": 300
    },
    "Exit B": {
        "x1": 640,
        "y1": 0,
        "x2": 1280,
        "y2": 300
    },
    "Exit C": {
        "x1": 0,
        "y1": 300,
        "x2": 1280,
        "y2": 720
    }
}


def load_exit_regions():

    if not os.path.exists(REGION_FILE):

        print(
            "⚠️ exit_regions.json not found."
        )

        print(
            "📐 Using default exit regions."
        )

        return DEFAULT_REGIONS

    try:

        with open(
            REGION_FILE,
            "r"
        ) as file:

            regions = json.load(file)

        required_exits = [
            "Exit A",
            "Exit B",
            "Exit C"
        ]

        for exit_name in required_exits:

            if exit_name not in regions:

                print(
                    f"⚠️ Missing {exit_name}."
                )

                print(
                    "📐 Using default exit regions."
                )

                return DEFAULT_REGIONS

        print(
            "✅ Loaded calibrated exit regions."
        )

        return regions

    except Exception as error:

        print(
            f"❌ Exit region loading error: {error}"
        )

        print(
            "📐 Using default exit regions."
        )

        return DEFAULT_REGIONS


EXIT_REGIONS = load_exit_regions()