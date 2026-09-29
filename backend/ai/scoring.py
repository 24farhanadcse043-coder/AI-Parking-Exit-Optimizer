from ai.congestion import congestion_score


def calculate_exit_score(
    queue_length,
    waiting_time,
    distance,
    congestion_level
):
    """
    Calculate the overall cost of an exit.

    Lower score = more efficient exit.
    """

    queue_score = queue_length * 0.40

    waiting_score = waiting_time * 0.30

    distance_score = (distance / 100) * 0.10

    traffic_score = congestion_score(
        congestion_level
    ) * 0.20

    total_score = (
        queue_score
        + waiting_score
        + distance_score
        + traffic_score
    )

    return round(total_score, 2)