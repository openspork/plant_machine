def time_in_range(start, stop, curr):
    if start <= stop:
        return start <= curr <= stop
    else:
        return start <= curr or curr <= stop