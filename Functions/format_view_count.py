def format_view_count(view_count):
    if view_count >= 1_000_000_000:
        return f"{view_count // 1_000_000_000}B"
    elif view_count >= 1_000_000:
        return f"{view_count // 1_000_000}M"
    elif view_count >= 1_000:
        return f"{view_count // 1_000}K"
    else:
        return str(view_count)
