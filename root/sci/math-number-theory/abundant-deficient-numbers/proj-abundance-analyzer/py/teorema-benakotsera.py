def is_semiperfect_bitwise(n: int, divisors: list[int]) -> bool:
    # У Python цілі числа виконують побітові зсуви над нескінченною розрядністю!
    dp = 1  # 0-й біт встановлено у 1

    for d in divisors:
        dp |= (dp << d)
        if (dp >> n) & 1:
            return True

    return bool((dp >> n) & 1)

def is_weird_number(n: int) -> bool:
    if n <= 1:
        return False

    divisors = []
    sum_proper = 0
    d = 1
    while d * d <= n:
        if n % d == 0:
            divisors.append(d)
            sum_proper += d
            paired = n // d
            if paired != d and paired != n:
                divisors.append(paired)
                sum_proper += paired
        d += 1

    if sum_proper <= n:
        return False

    divisors.sort()
    return not is_semiperfect_bitwise(n, divisors)
