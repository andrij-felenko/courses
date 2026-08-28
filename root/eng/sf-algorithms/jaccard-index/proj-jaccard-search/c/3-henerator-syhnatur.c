typedef struct {
    uint64_t a;
    uint64_t b;
} minhash_func_t;

typedef struct {
    size_t k_funcs;
    minhash_func_t *funcs;
    uint64_t prime;
} minhash_generator_t;

minhash_generator_t* minhash_init(size_t k_funcs) {
    minhash_generator_t *gen = (minhash_generator_t*)malloc(sizeof(minhash_generator_t));
    if (!gen) return NULL;

    gen->k_funcs = k_funcs;
    gen->prime = 4294967311ULL; // Велике просте число > 2^32
    gen->funcs = (minhash_func_t*)malloc(k_funcs * sizeof(minhash_func_t));

    for (size_t i = 0; i < k_funcs; ++i) {
        gen->funcs[i].a = (uint64_t)rand() % (gen->prime - 1) + 1;
        gen->funcs[i].b = (uint64_t)rand() % gen->prime;
    }
    return gen;
}

void minhash_compute(const minhash_generator_t *gen, 
                     const uint64_t *shingles, size_t shingle_cnt,
                     uint64_t *out_sig) {
    for (size_t i = 0; i < gen->k_funcs; ++i) {
        uint64_t min_h = UINT64_MAX;
        uint64_t a = gen->funcs[i].a;
        uint64_t b = gen->funcs[i].b;
        uint64_t p = gen->prime;

        for (size_t j = 0; j < shingle_cnt; ++j) {
            uint64_t h = (a * shingles[j] + b) % p;
            if (h < min_h) {
                min_h = h;
            }
        }
        out_sig[i] = min_h;
    }
}

double minhash_similarity_c(const uint64_t *sig_a, const uint64_t *sig_b, size_t k_funcs) {
    size_t matches = 0;
    for (size_t i = 0; i < k_funcs; ++i) {
        if (sig_a[i] == sig_b[i]) {
            matches++;
        }
    }
    return (double)matches / (double)k_funcs;
}

void minhash_free(minhash_generator_t *gen) {
    if (gen) {
        free(gen->funcs);
        free(gen);
    }
}
