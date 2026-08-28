#include <array>
#include <cstdint>

namespace esp_nvs {

struct SecurityConfig {
    std::array<uint8_t, 32> encryption_key{}; /**< Ключ шифрування корисних даних */
    std::array<uint8_t, 32> tweak_key{};      /**< Ключ налаштування зміщення */
};

} // namespace esp_nvs
