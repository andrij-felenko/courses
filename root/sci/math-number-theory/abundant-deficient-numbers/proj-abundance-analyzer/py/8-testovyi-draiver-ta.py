def main():
    limit = 1000
    sieve = LinearSieve(limit)

    print("=== Abundance Analysis for N = 1..1000 ===")
    abundant_cnt = 0
    perfect_cnt = 0

    for i in range(1, limit + 1):
        if sieve.sigma[i] == 2 * i:
            perfect_cnt += 1
            print(f"Perfect number found: {i}")
        elif sieve.is_abundant(i):
            abundant_cnt += 1

    print(f"Total Abundant: {abundant_cnt} ({abundant_cnt * 100.0 / limit:.2f}%)")
    print(f"Total Perfect: {perfect_cnt}")

    print("\n=== Searching for Weird Numbers ===")
    for i in range(1, limit + 1):
        if is_weird_number(i):
            print(f"Weird number found: {i}")

    print("\n=== Tracing Aliquot Sequence for 220 ===")
    trace_aliquot_sequence(220, 10)

if __name__ == "__main__":
    main()
