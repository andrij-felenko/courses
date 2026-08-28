#include <vector>
#include <cstdint>
#include <span>
#include <algorithm>
#include <bit>

void sha256(std::span<const uint8_t> data, std::span<uint8_t, 32> out);

// Генератор маски MGF1 на базі SHA-256 (C++20 span)
void mgf1_sha256(std::span<const uint8_t> seed, std::span<uint8_t> mask) {
    uint32_t counter = 0;
    std::vector<uint8_t> hash_buf(seed.size() + 4);
    std::copy(seed.begin(), seed.end(), hash_buf.begin());

    size_t generated = 0;
    std::array<uint8_t, 32> digest{};

    while (generated < mask.size()) {
        // Конвертація лічильника в Big-Endian
        hash_buf[seed.size() + 0] = static_cast<uint8_t>(counter >> 24);
        hash_buf[seed.size() + 1] = static_cast<uint8_t>(counter >> 16);
        hash_buf[seed.size() + 2] = static_cast<uint8_t>(counter >> 8);
        hash_buf[seed.size() + 3] = static_cast<uint8_t>(counter);

        sha256(hash_buf, digest);

        const size_t to_copy = std::min(mask.size() - generated, digest.size());
        std::copy_n(digest.begin(), to_copy, mask.begin() + generated);

        generated += to_copy;
        ++counter;
    }
}
