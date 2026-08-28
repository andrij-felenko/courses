import time

def wait_until(predicate, timeout, poll=0.01):
    deadline = time.monotonic() + timeout
    while True:
        value = predicate()
        if value:
            return value
        if time.monotonic() >= deadline:
            raise TimeoutError(f"умова не настала за {timeout} с")
        time.sleep(poll)
