
def truncate_string(s, max_len=24):
    if len(s) > max_len:
        return s[:max_len - 4] + " ..."

    return s

