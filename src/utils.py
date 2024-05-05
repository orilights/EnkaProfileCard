import base64
import json
import os
import hashlib
import time

from loguru import logger

CACHE_ROOT = './cache/'


def get_ts():
    return int(time.time())


def write_cache(path: str, data: str, ttl=-1):
    full_path = os.path.join(CACHE_ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    json.dump({
        'expire': -1 if ttl == -1 else get_ts() + ttl,
        'data': data
    }, open(f'{full_path}.json', 'w', encoding='utf-8'))


def read_cache(path: str, allow_expire=False):
    full_path = os.path.join(CACHE_ROOT, path)
    if not os.path.exists(f'{full_path}.json'):
        return None
    try:
        cache = json.load(open(f'{full_path}.json', 'r', encoding='utf-8'))
        if cache['expire'] == -1:
            return cache['data']
        if cache['expire'] < get_ts() and not allow_expire:
            return None
        return cache['data']
    except Exception as e:
        return None


def to_base64(src: bytes | str) -> str:
    if isinstance(src, str):
        return to_base64(open(src, 'rb').read())
    return base64.b64encode(src).decode('utf-8')


def md5(text: str):
    return hashlib.md5(text.encode()).hexdigest()


def timeit(name):

    def decorator(func):

        def wrapper(*args, **kwargs):
            ts = time.time()
            result = func(*args, **kwargs)
            logger.info(f'[{name}] cost:{time.time() - ts}s')
            return result

        return wrapper

    return decorator
