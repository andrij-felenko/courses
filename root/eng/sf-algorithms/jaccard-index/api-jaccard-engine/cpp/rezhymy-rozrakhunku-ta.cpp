enum class Mode : uint32_t {
    ExactSorted = 0,
    ExactHash   = 1,
    MinHash     = 2
};

struct Config {
    Mode mode = Mode::ExactSorted;
    size_t shingle_size = 4;
    size_t minhash_k = 128;
    double sim_threshold = 0.5;
    uint64_t random_seed = 42;
};
