#pragma omp parallel for schedule(dynamic, 1) reduction(+:totalPrimes)
for (std::size_t s = 0; s < numSegments; ++s) {
    std::uint64_t low = limit + 1 + s * L1_CACHE_BYTES;
    std::uint64_t high = std::min(low + L1_CACHE_BYTES - 1, N);
    
    // Кожен потік має свій локальний сегмент у L1-кеші свого ядра
    std::vector<std::uint8_t> localSegment(high - low + 1, 1);
    
    for (std::uint32_t p : basePrimes) {
        std::uint64_t start = ((low + p - 1) / p) * static_cast<std::uint64_t>(p);
        start = std::max(start, static_cast<std::uint64_t>(p) * p);

        for (std::uint64_t j = start; j <= high; j += p) {
            localSegment[j - low] = 0;
        }
    }

    std::uint64_t localCount = 0;
    for (std::uint8_t val : localSegment) {
        if (val) localCount++;
    }
    totalPrimes += localCount;
}
