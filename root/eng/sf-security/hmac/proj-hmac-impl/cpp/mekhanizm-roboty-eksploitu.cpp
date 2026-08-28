#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace crypto {

struct ForgedPayload {
    std::array<uint8_t, 32> forged_hash;
    std::vector<uint8_t> extension_stream; // Pad + шкідливий хвіст
};

ForgedPayload perform_length_extension_attack(
    std::span<const uint8_t, 32> original_hash,
    size_t known_total_len, // Довжина Key + Message
    std::span<const uint8_t> extension_data)
{
    // 1. Формування оригінального вирівнювання (padding)
    std::vector<uint8_t> pad;
    pad.push_back(0x80);
    size_t rem = known_total_len % 64;
    size_t pad_len = (rem < 56) ? (56 - rem) : (120 - rem);
    pad.resize(pad_len, 0x00);

    uint64_t bitlen = known_total_len * 8;
    for (int i = 7; i >= 0; --i) {
        pad.push_back(static_cast<uint8_t>(bitlen >> (i * 8)));
    }

    // 2. Ініціалізація стану з перехопленого гешу
    Sha256 forged_ctx;
    // Відновлення внутрішніх 32-бітних слів стану
    std::array<uint32_t, 8> restored_state{};
    for (size_t i = 0; i < 8; ++i) {
        restored_state[i] = (static_cast<uint32_t>(original_hash[i * 4]) << 24) |
                            (static_cast<uint32_t>(original_hash[i * 4 + 1]) << 16) |
                            (static_cast<uint32_t>(original_hash[i * 4 + 2]) << 8) |
                            (static_cast<uint32_t>(original_hash[i * 4 + 3]));
    }

    // Додаємо хвіст до розширеного тіла
    std::vector<uint8_t> payload = pad;
    payload.insert(payload.end(), extension_data.begin(), extension_data.end());

    // 3. Обчислення сфальсифікованого тегу
    return { Sha256::hash(payload), payload };
}

} // namespace crypto
