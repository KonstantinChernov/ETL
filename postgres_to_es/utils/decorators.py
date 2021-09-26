import logging
from functools import wraps
from time import sleep


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            attempt = 0
            sleep_time = start_sleep_time
            while True:
                try:
                    attempt += 1
                    response = func(*args, **kwargs)
                except Exception as e:
                    logging.exception(e)
                    sleep_time = start_sleep_time * factor**attempt if sleep_time < border_sleep_time else sleep_time
                    sleep(sleep_time)
                else:
                    return response
        return inner
    return func_wrapper


def coroutine(f):
    """
    Декоратор для инициализации корутины
    """
    def wrapper(*args, **kwargs):
        g = f(*args, **kwargs)
        g.send(None)
        return g
    return wrapper
