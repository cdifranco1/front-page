
from time import time, sleep
import threading


class RateLimiter:
    def __init__(self, rate_limit_period: int, rate_limit_amount: int,  initial_amount: int = 0) -> None:
        self.last_reset = time()

        self.rate_limit_period = rate_limit_period
        self.rate_limit_amount = rate_limit_amount

        self.current_amount = initial_amount

        self.lock = threading.RLock()

    def __reset(self) -> None:
        self.current_amount = 0
        self.last_reset = time()

    def _try_reset(self) -> None:
        if time() - self.last_reset > self.rate_limit_period:
            self.__reset()
            return True
        return False

    def would_exceed_limit(self, next_amount: int) -> bool:
        if self.current_amount + next_amount > self.rate_limit_amount:
            return True
        return False

    def _seconds_remaining(self) -> float:
        return self.rate_limit_period - (time() - self.last_reset)

    def _sleep_and_reset(self) -> None:
        sleep(self._seconds_remaining())
        self.__reset()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            increment_amount = kwargs["increment_amount"] if "increment_amount" in kwargs else 1

            with self.lock:
                if self._try_reset():
                    self.current_amount += increment_amount
                    return func(*args, **kwargs)

                elif self.would_exceed_limit(increment_amount):
                    self._sleep_and_reset()
                    self.current_amount += increment_amount

                    print(f"Current amount: {self.current_amount}; Time remaining: {
                          self._seconds_remaining()}")
                    return func(*args, **kwargs)
                else:
                    print(f"Current amount: {self.current_amount}; Time remaining: {
                          self._seconds_remaining()}")
                    self.current_amount += increment_amount
                    return func(*args, **kwargs)

        return wrapper


if __name__ == "__main__":
    test_rate_limiter = RateLimiter(
        rate_limit_period=10, rate_limit_amount=5500)

    @test_rate_limiter.limit
    async def some_api_call(**kwargs):
        print("API call made")

    from asyncio import TaskGroup, run

    async def create_tasks():
        tasks = []
        async with TaskGroup() as g:
            for i in range(10):
                tasks.append(g.create_task(
                    some_api_call(call_i=i, increment_amount=1000)))

        return [t.result() for t in tasks]

    run(create_tasks())
