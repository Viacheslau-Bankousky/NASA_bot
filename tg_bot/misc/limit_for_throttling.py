from typing import Callable, Any


def rate_limit(limit: int, key=None) -> Callable[[Any], Any]:
    """Decorates function, sets the time limit or special key as the dictionary
    values of the name space of the object of the called function

    :param: limit: time limit for calling the throttled function
    :type: limit: integer
    :param: key: key for more specific throttling of the calling function
    :type: key: None
    :return: called function
    :rtype: Callable[[Any], Any]

    """
    def decorator(function):
        setattr(function, 'throttling_rate_limit', limit)
        if key:
            setattr(function, 'throttling_key', key)
        return function
    return decorator