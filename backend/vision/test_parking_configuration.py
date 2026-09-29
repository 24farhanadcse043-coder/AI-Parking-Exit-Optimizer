from vision.parking_spaces import PARKING_SPACES


print(
    "Total parking spaces:",
    len(PARKING_SPACES)
)

print()

for space in PARKING_SPACES[:10]:

    print(
        space["space_number"],
        "=>",
        "(",
        space["x1"],
        ",",
        space["y1"],
        ") to (",
        space["x2"],
        ",",
        space["y2"],
        ")"
    )