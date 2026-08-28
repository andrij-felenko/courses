#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <algorithm>

namespace embedded::crypto {

/**
 * Гарантоване затирання ділянки пам'яті в стилі C++.
 */
inline void secure_zero_memory(std::span<uint8_t> buffer) noexcept {
    if (buffer.empty()) {
        return;
    }

    auto* ptr = static_cast<volatile uint8_t*>(buffer.data());
    for (size_t i = 0; i < buffer.size(); ++i) {
        ptr[i] = 0x00;
    }

    #if defined(__GNUC__) || defined(__clang__)
    __asm__ __volatile__("" : : "r"(buffer.data()) : "memory");
    #endif
}

/**
 * Порівняння двох блоків пам'яті за строго константний час.
 */
[[nodiscard]] inline bool constant_time_compare(
    std::span<const uint8_t> a, 
    std::span<const uint8_t> b) noexcept 
{
    if (a.size() != b.size()) {
        return false;
    }

    volatile uint8_t diff = 0;
    const auto* pa = static_cast<const volatile uint8_t*>(a.data());
    const auto* pb = static_cast<const volatile uint8_t*>(b.data());

    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (pa[i] ^ pb[i]);
    }

    return (diff == 0);
}

/**
 * Безпечний буфер фіксованого розміру для криптографічних ключів (RAII).
 * Гарантовано затирає свій вміст нулями при виході з області видимості.
 */
template <size_t N>
class SecureKeyBuffer {
public:
    constexpr SecureKeyBuffer() noexcept {
        data_.fill(0x00);
    }

    explicit SecureKeyBuffer(std::span<const uint8_t, N> source) noexcept {
        std::copy(source.begin(), source.end(), data_.begin());
    }

    ~SecureKeyBuffer() noexcept {
        secure_zero_memory(std::span<uint8_t>(data_));
    }

    // Заборона небезпечного копіювання секретів у пам'яті
    SecureKeyBuffer(const SecureKeyBuffer&) = delete;
    SecureKeyBuffer& operator=(const SecureKeyBuffer&) = delete;

    // Дозвіл безпечного переміщення
    SecureKeyBuffer(SecureKeyBuffer&& other) noexcept {
        std::copy(other.data_.begin(), other.data_.end(), data_.begin());
        secure_zero_memory(std::span<uint8_t>(other.data_));
    }

    SecureKeyBuffer& operator=(SecureKeyBuffer&& other) noexcept {
        if (this != &other) {
            secure_zero_memory(std::span<uint8_t>(data_));
            std::copy(other.data_.begin(), other.data_.end(), data_.begin());
            secure_zero_memory(std::span<uint8_t>(other.data_));
        }
        return *this;
    }

    [[nodiscard]] std::span<const uint8_t, N> view() const noexcept {
        return std::span<const uint8_t, N>(data_);
    }

    [[nodiscard]] std::span<uint8_t, N> mutable_view() noexcept {
        return std::span<uint8_t, N>(data_);
    }

    [[nodiscard]] constexpr size_t size() const noexcept {
        return N;
    }

private:
    std::array<uint8_t, N> data_;
};

} // namespace embedded::crypto
