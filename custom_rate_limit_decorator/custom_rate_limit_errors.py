class RateLimitApplied(Exception):
    """
    Error that is thrown when rate limit has been applied
    """

    def __init__(self, message="Rate Limit has been applied and access to this method has been restricted"):
        self.message = message
        super().__init__(self.message)
