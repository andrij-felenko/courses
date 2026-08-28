int main(void) {
    uint32_t limit = 1000;
    LinearSieve* sieve = create_sieve(limit);
    if (!sieve) {
        fprintf(stderr, "Allocation error\n");
        return 1;
    }

    printf("=== Abundance Analysis for N = 1..1000 ===\n");
    uint32_t abundant_cnt = 0;
    uint32_t perfect_cnt = 0;

    for (uint32_t i = 1; i <= limit; ++i) {
        if (sieve->sigma[i] == 2 * (uint64_t)i) {
            perfect_cnt++;
            printf("Perfect number found: %u\n", i);
        } else if (sieve->sigma[i] > 2 * (uint64_t)i) {
            abundant_cnt++;
        }
    }

    printf("Total Abundant: %u (%.2f%%)\n", abundant_cnt, (double)abundant_cnt * 100.0 / limit);
    printf("Total Perfect: %u\n", perfect_cnt);

    printf("\n=== Searching for Weird Numbers ===\n");
    for (uint64_t i = 1; i <= limit; ++i) {
        if (is_weird_number(i)) {
            printf("Weird number found: %llu\n", (unsigned long long)i);
        }
    }

    printf("\n=== Tracing Aliquot Sequence for 220 ===\n");
    trace_aliquot_sequence(220, 10);

    free_sieve(sieve);
    return 0;
}
