uint32_t fast_bounded_rand(uint32_t range, uint32_t (*random_src)()) {
    uint64_t multiresult = static_cast<uint64_t>(random_src()) * static_cast<uint64_t>(range);
    uint32_t leftover = static_cast<uint32_t>(multiresult); // Молодші 32 біти

    if (leftover < range) {
        uint32_t threshold = -range % range; // Поріг обчислюється лише у 0.1% випадків
        while (leftover < threshold) {
            multiresult = static_cast<uint64_t>(random_src()) * static_cast<uint64_t>(range);
            leftover = static_cast<uint32_t>(multiresult);
        }
    }
    return static_cast<uint32_t>(multiresult >> 32); // Старші 32 біти є цільовим числом
}
