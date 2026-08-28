#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <random>

uint32_t fnv1a_fixed(uint32_t key, uint32_t m) noexcept {
    uint32_t hash = 2166136261U;
    hash = (hash ^ (key & 0xFF)) * 16777619U;
    hash = (hash ^ ((key >> 8) & 0xFF)) * 16777619U;
    return hash % m;
}

int main() {
    constexpr uint32_t m = 1024;
    constexpr uint32_t n = 10000;

    std::vector<uint32_t> bad_keys;
    bad_keys.reserve(n);

    uint32_t candidate = 0;
    while (bad_keys.size() < n) {
        if (fnv1a_fixed(candidate, m) == 42) {
            bad_keys.push_back(candidate);
        }
        candidate++;
    }

    std::cout << "Сформовано " << n << " колізійних ключів для бакета [42]\n";

    std::mt19937_64 rng(std::random_device{}());
    universal_hashing::MultiplyShiftHasher univ_hasher(10, rng());

    std::vector<uint32_t> buckets(m, 0);
    for (uint32_t key : bad_keys) {
        buckets[univ_hasher(key)]++;
    }

    auto max_chain = *std::max_element(buckets.begin(), buckets.end());
    std::cout << "Максимальна довжина ланцюжка універсального хешування: " << max_chain << "\n";

    return 0;
}
