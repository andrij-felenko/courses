cache = {}

def fib(n):
    if n < 2:
        return n
    if n in cache:            # уже рахували? — бери готове
        return cache[n]
    result = fib(n - 1) + fib(n - 2)
    cache[n] = result         # запам'ятай, щоб не рахувати вдруге
    return result
