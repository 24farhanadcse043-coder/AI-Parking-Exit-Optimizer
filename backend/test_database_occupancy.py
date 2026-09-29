from database import SessionLocal
from models import ParkingSpace


print("=" * 60)
print("   PARKAI — DATABASE OCCUPANCY VERIFICATION")
print("=" * 60)


db = SessionLocal()

try:

    spaces = (
        db.query(ParkingSpace)
        .order_by(ParkingSpace.id)
        .all()
    )

    print(
        f"\nParking spaces found: {len(spaces)}"
    )

    occupied_count = 0

    for space in spaces:

        status = (
            "OCCUPIED"
            if space.occupied
            else "FREE"
        )

        if space.occupied:
            occupied_count += 1

        print(
            f"{space.space_number}: "
            f"{status} | "
            f"vehicle={space.vehicle_number}"
        )

    available_count = (
        len(spaces)
        - occupied_count
    )

    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)

    print(
        f"Total spaces: {len(spaces)}"
    )

    print(
        f"Occupied spaces: {occupied_count}"
    )

    print(
        f"Available spaces: {available_count}"
    )

    if (
        occupied_count == 1
        and spaces
    ):

        print(
            "\n✅ SQLITE OCCUPANCY DATA "
            "IS WORKING."
        )

    else:

        print(
            "\n❌ SQLITE OCCUPANCY DATA "
            "IS NOT AS EXPECTED."
        )

finally:

    db.close()