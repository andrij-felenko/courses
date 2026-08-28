#include <vector>
#include <cstdint>
#include <iostream>

uint64_t count_coprime_pairs_fast(int32_t n) {
    MobiusSieve sieve(n);
    std::vector<int64_t> pref_m(n + 1, 0);

    for (size_t i = 1; i <= static_cast<size_t>(n); ++i) {
        pref_m[i] = pref_m[i - 1] + sieve.mu[i];
    }

    uint64_t total_pairs = 0;
    int32_t l = 1;

    while (l <= n) {
        int32_t k = n / l;
        int32_t r = n / k;
        int64_t block_sum_mu = pref_m[r] - pref_m[l - 1];
        total_pairs += static_cast<uint64_t>(block_sum_mu) * static_cast<uint64_t>(k) * static_cast<uint64_t>(k);
        l = r + 1;
    }

    return total_pairs;
}
