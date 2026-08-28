#include <cstdint>
#include <array>
#include <span>
#include <string_view>

/* У C++ таблиця CRC32 обчислюється на етапі компіляції 
   та не вимагає перевірок ініціалізації у runtime. */

class CRC32Calculator {
public:
    static constexpr uint32_t Polynomial = 0xEDB88320U;

    static consteval auto generate_table() {
        std::array<uint32_t, 256> table{};
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t crc = i;
            for (uint32_t j = 0; j < 8; ++j) {
                crc = (crc & 1) ? ((crc >> 1) ^ Polynomial) : (crc >> 1);
            }
            table[i] = crc;
        }
        return table;
    }

    static inline constexpr auto Table = generate_table();

    [[nodiscard]] static constexpr uint32_t compute(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t byte : data) {
            const auto index = static_cast<uint8_t>((crc ^ byte) & 0xFF);
            crc = Table[index] ^ (crc >> 8);
        }
        return crc ^ 0xFFFFFFFFU;
    }

    [[nodiscard]] static constexpr uint32_t compute(std::string_view str) noexcept {
        return compute(std::span{reinterpret_cast<const uint8_t*>(str.data()), str.size()});
    }
};
