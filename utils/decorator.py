import time
from utils.log import logger


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
            raise RuntimeError(f"Reached maximum attempts ({max_attempts})")

        return wrapper

    return decorator
