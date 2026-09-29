def calculate_congestion_level(queue_length, waiting_time):
    """
    Calculate congestion based on queue length
    and estimated waiting time.
    """

    score = (
        queue_length * 0.6
        + waiting_time * 0.4
    )

    if score <= 5:
        return "LOW"

    elif score <= 10:
        return "MEDIUM"

    else:
        return "HIGH"


def congestion_score(congestion_level):
    """
    Convert congestion level into a numerical penalty.
    """

    levels = {
        "LOW": 1,
        "MEDIUM": 5,
        "HIGH": 10
    }

    return levels.get(
        congestion_level.upper(),
        10
    )