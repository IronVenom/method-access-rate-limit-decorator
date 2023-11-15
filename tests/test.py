from custom_rate_limit_decorator.custom_rate_limit import CustomRateLimit
from custom_rate_limit_decorator.custom_rate_limit_config import UNIQUE_IDENTIFIER_KEY, UNIQUE_IDENTIFIER_VALUE, RATE_LIMIT_AMOUNT, RATE_LIMIT_EXPIRY
from custom_rate_limit_decorator.custom_rate_limit_errors import RateLimitApplied
import random
import string
import logging

logging.basicConfig(level=logging.INFO)


def generate_user_id():

    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


def test_same_method_different_users():

    user_id_1 = generate_user_id()
    assert login_with_rate_limit(user_id_1, "TestPwd1") == True
    assert login_with_rate_limit(user_id_1, "TestPwd1") == True
    assert login_with_rate_limit(user_id_1, "TestPwd1") == False

    user_id_2 = generate_user_id()
    assert login_with_rate_limit(user_id_2, "TestPwd2") == True
    assert login_with_rate_limit(user_id_2, "TestPwd2") == True
    assert login_with_rate_limit(user_id_2, "TestPwd2") == False


def test_different_methods_same_user():

    user_id = generate_user_id()
    assert login_with_rate_limit(user_id, "TestPwd") == True
    assert login_with_rate_limit(user_id, "TestPwd") == True
    assert login_with_rate_limit(user_id, "TestPwd") == False

    assert request_otp_with_rate_limit(user_id) == True
    assert request_otp_with_rate_limit(user_id) == True
    assert request_otp_with_rate_limit(user_id) == True
    assert request_otp_with_rate_limit(user_id) == False


def test_no_config():

    user_id = generate_user_id()
    assert request_otp(user_id) == True
    assert request_otp(user_id) == True
    assert request_otp(user_id) == True
    assert request_otp(user_id) == True

    assert login(user_id, "TestPwd") == True
    assert login(user_id, "TestPwd") == True
    assert login(user_id, "TestPwd") == True


def rate_limit_config(method_identifier, unique_identifier, value, rate_limit_amount, rate_limit_expiry):

    ratelimitcheck_conf = {}
    ratelimitcheck_conf[UNIQUE_IDENTIFIER_KEY] = method_identifier + \
        "_" + unique_identifier
    ratelimitcheck_conf[UNIQUE_IDENTIFIER_VALUE] = value
    ratelimitcheck_conf[RATE_LIMIT_AMOUNT] = rate_limit_amount
    ratelimitcheck_conf[RATE_LIMIT_EXPIRY] = rate_limit_expiry
    return ratelimitcheck_conf


def login_with_rate_limit(user_id, password):

    # User can request for login at most two times in two minutes
    try:
        login(user_id, password, RATE_LIMIT_CONFIG=rate_limit_config(
            "login", "user_id", user_id, 2, 120))
        return True
    except RateLimitApplied:
        logging.error("Rate limit applied for user " + user_id + " for login")
        return False


def request_otp_with_rate_limit(user_id):

    # User can request for OTP at most three times in two minutes
    try:
        request_otp(user_id, RATE_LIMIT_CONFIG=rate_limit_config(
            "request_otp", "user_id", user_id, 3, 120))
        return True
    except RateLimitApplied:
        logging.error("Rate limit applied for user " +
                      user_id + " for otp request")
        return False


@CustomRateLimit
def login(user_id, password, RATE_LIMIT_CONFIG=None):

    logging.info("Logging in user " + user_id)
    return True


@CustomRateLimit
def request_otp(user_id, RATE_LIMIT_CONFIG=None):

    logging.info("Request otp for user " + user_id)
    return True
