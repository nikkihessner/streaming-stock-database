def check_direction(snapshot, wave_index):
    """
    General direction sanity check.
    
    We measure the raw price change (diff = end - start),
    convert that into a wave direction ("up" or "down"),
    then convert that wave direction into the implied trend direction,
    and compare that trend direction to the expected trend direction.
    """

    expected_trend = snapshot.context["trend_direction"]   # "up" or "down"

    start = snapshot.context["wave_start"]
    end   = snapshot.context["wave_end"]

    diff = end - start

    if diff == 0:
        return False, "zero_length_wave"

    # Raw wave direction: did this wave move up or down?
    wave_dir = "up" if diff > 0 else "down"

    # Waves 1,3,5 move WITH the trend
    # Waves 2,4 move AGAINST the trend
    if wave_index in (1, 3, 5):
        implied_trend = wave_dir
    else:  # 2,4
        implied_trend = "down" if wave_dir == "up" else "up"

    if implied_trend == expected_trend:
        return True, f"expected={expected_trend}, implied={implied_trend}, diff={diff}"
    else:
        return False, f"expected={expected_trend}, implied={implied_trend}, diff={diff}"