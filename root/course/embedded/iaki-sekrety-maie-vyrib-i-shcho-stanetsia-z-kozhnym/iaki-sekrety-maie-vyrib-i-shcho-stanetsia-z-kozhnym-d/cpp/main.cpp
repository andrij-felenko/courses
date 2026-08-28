#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

namespace embedded::security {

/**
 * Гарантоване затирання пам'яті для C++20.
 */
inline void secure_wipe(std::span<uint8_t> memory) noexcept {
    if (memory.empty()) {
        return;
    }

    auto* ptr = static_cast<volatile uint8_t*>(memory.data());
    for (size_t i = 0; i < memory.size(); ++i) {
        ptr[i] = 0x00;
    }

    #if defined(__GNUC__) || defined(__clang__)
    __asm__ __volatile__("" : : "r"(memory.data()) : "memory");
    #endif
}

/**
 * Порівняння за константний час у C++.
 */
[[nodiscard]] inline bool constant_time_equals(
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
 * Автоматичний захищений буфер для ключів (RAII обгортка).
 * Затирає свій вміст нулями автоматично при виході з області видимості.
 */
template <size_t KeySize>
class ScopedKeyBuffer {
public:
    constexpr ScopedKeyBuffer() noexcept {
        storage_.fill(0x00);
    }

    explicit ScopedKeyBuffer(std::span<const uint8_t, KeySize> src) noexcept {
        std::copy(src.begin(), src.end(), storage_.begin());
    }

    ~ScopedKeyBuffer() noexcept {
        secure_wipe(std::span<uint8_t>(storage_));
    }

    ScopedKeyBuffer(const ScopedKeyBuffer&) = delete;
    ScopedKeyBuffer& operator=(const ScopedKeyBuffer&) = delete;

    ScopedKeyBuffer(ScopedKeyBuffer&& other) noexcept {
        std::copy(other.storage_.begin(), other.storage_.end(), storage_.begin());
        secure_wipe(std::span<uint8_t>(other.storage_));
    }

    ScopedKeyBuffer& operator=(ScopedKeyBuffer&& other) noexcept {
        if (this != &other) {
            secure_wipe(std::span<uint8_t>(storage_));
            std::copy(other.storage_.begin(), other.storage_.end(), storage_.begin());
            secure_wipe(std::span<uint8_t>(other.storage_));
        }
        return *this;
    }

    [[nodiscard]] std::span<const uint8_t, KeySize> view() const noexcept {
        return std::span<const uint8_t, KeySize>(storage_);
    }

    [[nodiscard]] std::span<uint8_t, KeySize> mutable_view() noexcept {
        return std::span<uint8_t, KeySize>(storage_);
    }

private:
    std::array<uint8_t, KeySize> storage_;
};

} // namespace embedded::security
