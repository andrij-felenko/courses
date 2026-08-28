int main() {
    constexpr std::uint32_t limit = 1000;
    LinearSieve sieve(limit);

    std::cout << "=== Abundance Analysis for N = 1..1000 ===\n";
    std::uint32_t abundant_cnt = 0;
    std::uint32_t perfect_cnt = 0;

    for (std::uint32_t i = 1; i <= limit; ++i) {
        if (sieve.get_sigma(i) == 2 * static_cast<std::uint64_t>(i)) {
            perfect_cnt++;
            std::cout << "Perfect number found: " << i << "\n";
        } else if (sieve.is_abundant(i)) {
            abundant_cnt++;
        }
    }

    std::cout << "Total Abundant: " << abundant_cnt << " (" 
              << (static_cast<double>(abundant_cnt) * 100.0 / limit) << "%)\n";
    std::cout << "Total Perfect: " << perfect_cnt << "\n";

    std::cout << "\n=== Searching for Weird Numbers ===\n";
    for (std::uint64_t i = 1; i <= limit; ++i) {
        if (WeirdNumberDetector::is_weird(i)) {
            std::cout << "Weird number found: " << i << "\n";
        }
    }

    std::cout << "\n=== Tracing Aliquot Sequence for 220 ===\n";
    AliquotTracer::trace(220, 10);

    return 0;
}
