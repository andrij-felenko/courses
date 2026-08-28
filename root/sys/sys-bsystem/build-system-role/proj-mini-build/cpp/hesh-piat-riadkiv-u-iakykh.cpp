struct Fnv {                        // FNV-1a, 64 біти: xor байтом, потім множення
    uint64_t h = 14695981039346656037ull;
    void feed(const void* p, size_t n) {
        auto b = static_cast<const unsigned char*>(p);
        for (size_t i = 0; i < n; ++i) { h ^= b[i]; h *= 1099511628211ull; }
    }
    void feed(std::string_view s) { feed(s.data(), s.size()); }
    void sep() { feed("\x1e", 1); }      // межа поля: щоб «ab»+«c» ≠ «a»+«bc»
};

static bool hashFile(const fs::path& p, Fnv& h) {
    std::ifstream f(p, std::ios::binary);
    if (!f) return false;
    char buf[1 << 16];
    while (f.read(buf, sizeof buf) || f.gcount())
        h.feed(buf, static_cast<size_t>(f.gcount()));
    return true;
}
