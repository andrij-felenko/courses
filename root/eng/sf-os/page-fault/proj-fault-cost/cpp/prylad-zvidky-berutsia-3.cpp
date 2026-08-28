static void touch_seq(char *p, std::size_t len, bool write) {
    unsigned long acc = 0;
    for (std::size_t i = 0; i < len; i += PGSZ) {
        if (write) p[i] = 1;
        else acc += static_cast<unsigned char>(p[i]);
    }
    sink += acc; // без цього рядка циклу не буде
}

static std::vector<std::size_t> permutation(std::size_t n) {
    std::vector<std::size_t> idx(n);
    for (std::size_t i = 0; i < n; ++i) idx[i] = i;
    std::mt19937 g(1337);
    std::shuffle(idx.begin(), idx.end(), g);
    return idx;
}

static void touch_perm(char *p, const std::vector<std::size_t> &idx) {
    unsigned long acc = 0;
    for (std::size_t k : idx) {
        acc += static_cast<unsigned char>(p[k * PGSZ]);
    }
    sink += acc;
}
