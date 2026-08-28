static unsigned long resident(void *addr, std::size_t len) {
    std::size_t n = len / PGSZ;
    std::vector<unsigned char> vec(n);
    unsigned long r = 0;
    if (mincore(addr, len, vec.data()) == 0) {
        for (std::size_t i = 0; i < n; ++i) {
            r += vec[i] & 1u;
        }
    }
    return r;
}
