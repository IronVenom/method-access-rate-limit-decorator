This is a basic implementation of a decorator for applying time based access rate limits to methods based on an unique identifier such as User ID, Phone number, IP Address, etc. 

Some use cases where it can be used - 

1. API Usage
2. Authentication and Login
3. User actions (comments, posts, etc.)

Here's  a simple example -

```python
def rate_limit_config(method_identifier, unique_identifier, value, rate_limit_amount, rate_limit_expiry):

    ratelimitcheck_conf = {}
    ratelimitcheck_conf[UNIQUE_IDENTIFIER_KEY] = method_identifier + unique_identifier
    ratelimitcheck_conf[UNIQUE_IDENTIFIER_VALUE] = value
    ratelimitcheck_conf[RATE_LIMIT_AMOUNT] = rate_limit_amount
    ratelimitcheck_conf[RATE_LIMIT_EXPIRY] = rate_limit_expiry
    return ratelimitcheck_conf

def login_with_rate_limit(user_id, password):

    # User can request for login at most two times in two minutes
    try:
        login(user_id, password, RATE_LIMIT_CONFIG=rate_limit_config(
            "login", "user_id", user_id, 2, 120))
    except RateLimitApplied:
        ## Handle rate limit by returning appropriate value
    
@CustomRateLimit
def login(user_id, password, RATE_LIMIT_CONFIG=None):
    ## Do something
```

The method `rate_limit_config()` can be made as a generic utility method that different methods can reuse.

If `login()` is called directly, then the `RATE_LIMIT_CONFIG` is sent as `None` by default and rate limit won't be applied and access to method will be granted everytime.

Since python modules are naturally singletons, a common redis connection instance will be used for all usages of the decorator.

## Prerequisites

### Redis

Redis needs to be installed in order to use the decorator. Rate limit data is cached on redis. Default configuration is used (localhost:6379, db = 0) so no change in port or db is needed after installing.

Redis server needs to be live when using the decorator or while running the test or benchmark scripts.

### Installing dependencies 

Create a virtual environment if you want and install the dependencies.

#### Creating virtual env and activating it -

```
> python3 -m venv .venv
> source .venv/bin/activate
```
#### Install dependencies -
```
> python3 -m pip install -r requirements.txt
```

## Running tests script

Following commands are to be run in project root directory. 

Run tests with logs - 

```
pytest --no-header --log-cli-level=INFO -vs test.py
```

Run tests without logs - 

```
pytest --no-header -v test.py
```

## Overhead cost due to use of Redis

There is an overhead cost if the rate limit decorator is used - it will increase the response time of the method on which it is applied. The cost will be highest for the first call that is made to any method that uses the decorator, since it will be responsible for connecting to Redis. This will only happen once. After that all calls will use the same shared Redis cache instance.



### Running benchmark script

Following command is to be run in project root directory - 

```
python3 benchmark.py
```