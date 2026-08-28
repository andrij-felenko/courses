def sum_proper_divisors(n: int) -> int:
    if n <= 1:
        return 0
    current_sigma = 1
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            term_sum = 1
            p_power = 1
            while temp % d == 0:
                p_power *= d
                term_sum += p_power
                temp //= d
            current_sigma *= term_sum
        d += 1
    if temp > 1:
        current_sigma *= (1 + temp)
    return current_sigma - n

def trace_aliquot_sequence(start: int, max_steps: int = 100) -> None:
    curr = start
    visited = set()
    print(f"Sequence for {start}: {curr}", end="")

    for _ in range(max_steps):
        visited.add(curr)
        curr = sum_proper_divisors(curr)
        print(f" -> {curr}", end="")

        if curr == 0:
            print(" [Terminated]")
            return
        if curr in visited:
            print(" [Cycle Detected]")
            return
    print(" [Reached Max Steps]")
