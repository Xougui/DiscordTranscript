from functools import wraps
from typing import Any, Dict, Tuple

_internal_cache: dict = {}


def _wrap_and_store_coroutine(cache, key, coro):
    """Wrap a coroutine and store its result in the cache.

    Args:
        cache (dict): The cache to store the result in.
        key (str): The key to store the result under.
        coro (coroutine): The coroutine to wrap.

    Returns:
        coroutine: The wrapped coroutine.
    """

    async def func():
        value = await coro
        cache[key] = value
        return value

    return func()


def _wrap_new_coroutine(value):
    """Wrap a value in a new coroutine.

    Args:
        value: The value to wrap.

    Returns:
        coroutine: The new coroutine.
    """

    async def new_coroutine():
        return value

    return new_coroutine()


def clear_cache():
    """Clear the internal cache."""
    _internal_cache.clear()


def cache():
    """A decorator to cache the results of a function."""

    def decorator(func):
        def _make_key(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
            """Make a cache key from the function's arguments."""

            def _true_repr(o):
                if o.__class__.__repr__ is object.__repr__:
                    # this is how MessageConstruct can retain
                    # caching across multiple instances
                    return f"<{o.__class__.__module__}.{o.__class__.__name__}>"
                return repr(o)

            key = [f"{func.__module__}.{func.__name__}"]
            key.extend(_true_repr(o) for o in args)
            for k, v in kwargs.items():
                key.append(_true_repr(k))
                key.append(_true_repr(v))

            return ":".join(key)

        @wraps(func)
        def wrapper(*args, **kwargs):
            """The wrapper function for the decorator."""
            key = _make_key(args, kwargs)
            try:
                value = _internal_cache[key]
            except KeyError:
                value = func(*args, **kwargs)
                return _wrap_and_store_coroutine(_internal_cache, key, value)
            else:
                return _wrap_new_coroutine(value)

        wrapper.cache = _internal_cache
        wrapper.clear_cache = _internal_cache.clear()
        return wrapper

    return decorator
