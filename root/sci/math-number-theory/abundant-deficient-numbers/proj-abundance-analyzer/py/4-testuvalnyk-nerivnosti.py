import math

EXP_GAMMA = 1.7810724179901979852

def check_robin_inequality(n: int, sigma_n: int) -> bool:
    if n <= 5040:
        return True
    index = sigma_n / n
    bound = EXP_GAMMA * math.log(math.log(n))
    return index < bound
