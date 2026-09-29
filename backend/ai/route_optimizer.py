from ai.scoring import calculate_exit_score


def find_best_exit(exits):
    """
    Find the most efficient available exit.

    Lower score means a better route.
    """

    available_exits = [
        exit_data
        for exit_data in exits
        if exit_data["is_available"]
    ]

    if not available_exits:
        return None

    scored_exits = []

    for exit_data in available_exits:

        score = calculate_exit_score(
            queue_length=exit_data["queue_length"],
            waiting_time=exit_data["waiting_time"],
            distance=exit_data["distance"],
            congestion_level=exit_data["congestion_level"]
        )

        scored_exits.append({
            "name": exit_data["name"],
            "queue_length": exit_data["queue_length"],
            "waiting_time": exit_data["waiting_time"],
            "distance": exit_data["distance"],
            "congestion_level": exit_data["congestion_level"],
            "score": score
        })

    scored_exits.sort(
        key=lambda x: x["score"]
    )

    best_exit = scored_exits[0]

    alternatives = scored_exits[1:]

    return {
        "recommended_exit": best_exit,
        "alternative_exits": alternatives
    }