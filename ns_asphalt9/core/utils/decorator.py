import traceback
from ..cache import cache
from ..utils.log import logger


def retry(max_attempts):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.info(f"Attempt {attempts} failed: {str(e)}")
                    logger.debug(
                        f"Attempt {attempts} failed: {str(e)}, traceback: {traceback.format_exc()}"
                    )
            raise RuntimeError(f"Reached maximum attempts ({max_attempts})")

        return wrapper

    return decorator


def cache_decorator(cls_type):
    def decorator(cls):
        if cls_type not in ["page", "task"]:
            raise Exception("Not support cache type!")
        key = f"{cls_type}_{cls.name}"
        cache.check(key)
        cache.set(key, cls)
        return cls

    return decorator
