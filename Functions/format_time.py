def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    time_units = []
    if hours > 0:
        time_units.append(f"{hours}H")
    if minutes > 0 or hours > 0:
        time_units.append(f"{minutes}M")
    time_units.append(f"{seconds}S")

    return " : ".join(time_units)
