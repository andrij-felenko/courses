int main(void) {
    const char *doc1 = "пошук за схожістю індекс жаккара алгоритми";
    const char *doc2 = "пошук за схожістю індекс жаккара структури";

    uint64_t *shingles1 = NULL, *shingles2 = NULL;
    size_t len1 = create_shingles_c(doc1, 4, &shingles1);
    size_t len2 = create_shingles_c(doc2, 4, &shingles2);

    double exact_j = jaccard_exact_sorted(shingles1, len1, shingles2, len2);
    printf("Точний коефіцієнт Жаккара: %.4f\n", exact_j);

    // Розрахунок MinHash
    size_t K = 128;
    minhash_generator_t *gen = minhash_init(K);

    uint64_t *sig1 = (uint64_t*)malloc(K * sizeof(uint64_t));
    uint64_t *sig2 = (uint64_t*)malloc(K * sizeof(uint64_t));

    minhash_compute(gen, shingles1, len1, sig1);
    minhash_compute(gen, shingles2, len2, sig2);

    double approx_j = minhash_similarity_c(sig1, sig2, K);
    printf("Оцінка MinHash (K=%1u): %.4f\n", (unsigned)K, approx_j);

    free(shingles1);
    free(shingles2);
    free(sig1);
    free(sig2);
    minhash_free(gen);
    return 0;
}
