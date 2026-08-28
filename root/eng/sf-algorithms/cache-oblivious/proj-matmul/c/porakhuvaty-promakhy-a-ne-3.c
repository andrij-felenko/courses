static void fill(void)
{
    for (size_t i = 0; i < (size_t)N*N; i++) {
        arena[A_OFF + i] = (double)(i % 7) - 3.0;    // цілі −3…3
        arena[B_OFF + i] = (double)(i % 5) - 2.0;    // цілі −2…2
        arena[C_OFF + i] = 0.0;
    }
}

int main(void)
{
    fill(); cache_reset(); naive_mult();
    uint64_t m1 = misses;
    double *C = arena + C_OFF;
    static double ref[N*N];
    memcpy(ref, C, sizeof ref);

    fill(); cache_reset(); rec_mult(N, A_OFF, B_OFF, C_OFF);
    uint64_t m2 = misses;

    printf("результати збігаються: %s\n",
           memcmp(ref, C, sizeof ref) == 0 ? "так" : "НІ");
    printf("наївний:     %10llu промахів\n", (unsigned long long)m1);
    printf("рекурсивний: %10llu промахів\n", (unsigned long long)m2);
    printf("виграш: %.1f×\n", (double)m1 / (double)m2);
    return 0;
}
