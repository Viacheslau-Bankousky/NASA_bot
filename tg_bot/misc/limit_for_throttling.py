def rate_limit(limit: int, key=None):
    # TODO написать докстринг
    def decorator(function):
        setattr(function, 'throttling_rate_limit', limit)
        if key:
            setattr(function, 'throttling_key', key)
        return function

    return decorator