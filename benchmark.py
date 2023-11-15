from custom_rate_limit_decorator.custom_rate_limit import CustomRateLimit
from custom_rate_limit_decorator.custom_rate_limit_config import UNIQUE_IDENTIFIER_KEY, UNIQUE_IDENTIFIER_VALUE, RATE_LIMIT_AMOUNT, RATE_LIMIT_EXPIRY
from custom_rate_limit_decorator.custom_rate_limit_errors import RateLimitApplied
import logging
import time
from tqdm import trange


def rate_limit_config(method_identifier, unique_identifier, value, rate_limit_amount, rate_limit_expiry):

    ratelimitcheck_conf = {}
    ratelimitcheck_conf[UNIQUE_IDENTIFIER_KEY] = method_identifier + \
        "_" + unique_identifier
    ratelimitcheck_conf[UNIQUE_IDENTIFIER_VALUE] = value
    ratelimitcheck_conf[RATE_LIMIT_AMOUNT] = rate_limit_amount
    ratelimitcheck_conf[RATE_LIMIT_EXPIRY] = rate_limit_expiry
    return ratelimitcheck_conf


def login_with_rate_limit(user_id, password, expiry):

    # User can request for login at most 2 times in expiry amount of seconds
    try:
        login(user_id, password, RATE_LIMIT_CONFIG=rate_limit_config(
            "login", "user_id", user_id, 2, expiry))
        return True
    except RateLimitApplied:
        return False


@CustomRateLimit
def login(user_id, password, RATE_LIMIT_CONFIG=None):

    logging.info("Logging in user " + user_id)
    return True


def method_calls(expiry):
    start_time1 = time.time()
    login_result = login("TestUser", "TestPwd")
    end_time1 = time.time()

    start_time2 = time.time()
    login_result = login_with_rate_limit("TestUser", "TestPwd", expiry)
    end_time2 = time.time()

    without_rate_limit = (end_time1 - start_time1) * 1000
    with_rate_limit = (end_time2 - start_time2) * 1000

    return with_rate_limit, without_rate_limit


def benchmark_method_calls(time_sleep, time_expiry, no_of_calls):
    average_time_with_rate_limit = 0
    average_time_without_rate_limit = 0
    for _ in trange(no_of_calls):
        with_rate_limit, without_rate_limit = method_calls(time_expiry)
        average_time_with_rate_limit += with_rate_limit
        average_time_without_rate_limit += without_rate_limit
        time.sleep(time_sleep)
    print(
        f"Average time without rate limit - {average_time_without_rate_limit/no_of_calls} ms per method call, measured for {no_of_calls} calls")
    print(
        f"Average time with rate limt - {average_time_with_rate_limit/no_of_calls} ms per method call, measured for {no_of_calls} calls")
    print(
        f"On an average, with rate limit took {average_time_with_rate_limit/average_time_without_rate_limit} more time compared to without rate limit, measured for {no_of_calls} calls")


if __name__ == "__main__":
    print("Running for Case 1 - Method calls done at 2s intervals, rate limit expiry is 8s with 2 attempts; Rate limit hits twice in a 8s period")
    benchmark_method_calls(2, 8, 300)
    print("Running for Case 2 - Method calls done at 2s intervals, rate limit expiry is 2s with 2 attempts; Rate limit is never hit")
    benchmark_method_calls(2, 2, 300)
