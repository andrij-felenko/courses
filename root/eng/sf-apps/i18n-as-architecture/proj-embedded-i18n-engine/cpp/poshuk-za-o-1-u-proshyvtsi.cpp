// Пошук індексу повідомлення за алгоритмом CHD за O(1) на C++20
[[nodiscard]] constexpr uint32_t mphf_lookup(std::span<const uint8_t> g_table, uint32_t r, uint32_t n, std::string_view key) noexcept {
    uint32_t h0 = runtime_hash(key) % r;
    uint32_t d  = g_table[h0];
    
    uint32_t h1 = runtime_hash(key) % n;
    if (d == 0) return h1;
    
    uint32_t h2 = (runtime_hash(key) ^ 0x5bd1e995) % n;
    return (h1 + d * h2) % n;
}
