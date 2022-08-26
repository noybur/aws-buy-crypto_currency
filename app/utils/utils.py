def bool_from_str(text: str) -> bool:
    if text.lower() == 'true':
        return True
    return False


def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)
