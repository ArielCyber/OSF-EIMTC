def is_iterable(subject):
    try:
        iterator = iter(subject)
    except TypeError:
        return False
    else:
        return True