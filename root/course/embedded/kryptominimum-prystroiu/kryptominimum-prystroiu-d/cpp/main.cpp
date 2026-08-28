#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>

namespace crypto {

// RAII-обгортка для гарантованого занулення пам'яті при виході зі скоупу
template <size_t N>
class SecureBuffer {
public:
    std::array<uint8_t, N> data{};

    ~SecureBuffer() {
        volatile uint8_t *p = data.data();
        for (size_t i = 0; i < N; ++i) {
            p[i] = 0;
        }
    }

    constexpr size_t size() const { return N; }
    uint8_t* raw() { return data.data(); }
    const uint8_t* raw() const { return data.data(); }
    std::span<const uint8_t, N> span() const { return std::span<const uint8_t, N>(data); }
};

// Порівняння за постійний час для std::span
bool constant_time_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) {
    if (a.size() != b.size()) {
        return false;
    }

    uint8_t result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= (a[i] ^ b[i]);
    }

    return (result == 0);
}

// Дерандомізатор фон Неймана на C++
constexpr std::optional<uint8_t> von_neumann_decorrelate(uint8_t bit_pair) {
    const uint8_t b0 = (bit_pair >> 1) & 0x01;
    const uint8_t b1 = bit_pair & 0x01;

    if (b0 == 0 && b1 == 1) return 0;
    if (b0 == 1 && b1 == 0) return 1;
    return std::nullopt; // 00 та 11 відкидаються
}

} // namespace crypto
