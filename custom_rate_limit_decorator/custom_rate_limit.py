import redis

from .custom_rate_limit_config import *
from .custom_rate_limit_errors import *

cache = redis.Redis(decode_responses=True)


def check_attempts(key, value, amount, expiry):
    rate_limit_value = cache.get(get_keystring(key, value))
    if rate_limit_value == None:
        create_key(key, value, expiry)
        return True
    else:
        rate_limit_value = int(rate_limit_value)
        if rate_limit_value >= amount:
            return False
        add_attempt(key, value)
        return True


def add_attempt(key, value):
    cache.incr(get_keystring(key, value))


def create_key(key, value, expiry):
    cache.setex(get_keystring(key, value), expiry, 1)


def get_keystring(key, value):
    return key + "::" + value


def CustomRateLimit(function):
    """
        Decorator for applying access rate limits to methods based on an unique identifier.
        This unique identifier should be something that can be used to uniquely identify the method caller - 
        Eg. - Phone number, User ID, IP Address, etc along with the method name.

        :param unique_identifier:       Unique identifier key name (E.g - LoginUserID, OTPPhoneNumber, RequestIPAdress, etc)
                                        Type: string     
        :param unique_identifier_value: Unique identifier value (E.g - "TestUser1", "+911234566890", "127.0.0.1", etc)
                                        Type: string
        :param rate_limit_amount:       Amount after which access is to be denied
                                        Type: int
        :param rate_limit_expiry:       Time in seconds after which access will be allowed again
                                        Type: int
    """

    def wrapper(*args, **kwargs):
        rate_limit_config = kwargs.get(RATE_LIMIT_CONFIG, {})
        unique_identifier_key = rate_limit_config.get(UNIQUE_IDENTIFIER_KEY)
        unique_identifier_value = rate_limit_config.get(
            UNIQUE_IDENTIFIER_VALUE)
        rate_limit_amount = int(rate_limit_config.get(RATE_LIMIT_AMOUNT, 0))
        rate_limit_expiry = int(rate_limit_config.get(RATE_LIMIT_EXPIRY, 0))
        if unique_identifier_key is None or unique_identifier_value is None or rate_limit_amount <= 0 or rate_limit_expiry <= 0:
            return function(*args, **kwargs)
        elif rate_limit_amount <= 0 or rate_limit_expiry <= 0:
            return function(*args, **kwargs)
        elif check_attempts(unique_identifier_key, unique_identifier_value, rate_limit_amount, rate_limit_expiry):
            return function(*args, **kwargs)
        else:
            raise RateLimitApplied
    return wrapper
