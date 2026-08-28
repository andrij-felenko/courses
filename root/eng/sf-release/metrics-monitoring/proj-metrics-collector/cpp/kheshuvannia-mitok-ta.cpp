inline uint64_t hash_metric_signature(std::string_view name, std::string_view labels) noexcept {
    constexpr uint64_t kFnvPrime = 1099511628211ULL;
    uint64_t hash = 14695981039346656037ULL; // FNV Offset Basis

    for (char c : name) {
        hash ^= static_cast<uint64_t>(c);
        hash *= kFnvPrime;
    }
    hash ^= 0xFF; // Розділювач просторів імен
    hash *= kFnvPrime;
    for (char c : labels) {
        hash ^= static_cast<uint64_t>(c);
        hash *= kFnvPrime;
    }
    return hash;
}
