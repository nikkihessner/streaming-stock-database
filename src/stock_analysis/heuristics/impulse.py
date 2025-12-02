def wave1_correct_direction(snapshot, wave_index):
    expected = snapshot.context["direction"].get(1)

    start = snapshot.context["wave_start"]
    end   = snapshot.context["wave_end"]

    diff = end - start

    # diff == 0 means no movement → invalid wave
    if diff == 0:
        return False, "zero_length_wave"

    # Determine actual direction
    actual = "up" if diff > 0 else "down"

    if actual == expected:
        return True, f"expected={expected}, actual={actual}, diff={diff}"
    else:
        return False, f"expected={expected}, actual={actual}, diff={diff}"

