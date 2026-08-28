#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <algorithm>

namespace crypto {

/**
 * RAII-обгортка для автоматичного безпечного затирання секретних даних у стеку.
 */
template <size_t N>
class SecureBuffer {
public:
    SecureBuffer() noexcept { data_.fill(0); }
    ~SecureBuffer() noexcept { clean(); }

    // Заборона копіювання для запобігання дублювання ключів
    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;

    // Дозвіл переміщення
    SecureBuffer(SecureBuffer&& other) noexcept {
        data_ = other.data_;
        other.clean();
    }

    uint8_t* data() noexcept { return data_.data(); }
    const uint8_t* data() const noexcept { return data_.data(); }
    size_t size() const noexcept { return N; }

    std::span<uint8_t, N> span() noexcept { return std::span<uint8_t, N>(data_); }
    std::span<const uint8_t, N> span() const noexcept { return std::span<const uint8_t, N>(data_); }

    void clean() noexcept {
        volatile uint8_t* p = data_.data();
        for (size_t i = 0; i < N; ++i) {
            p[i] = 0;
        }
    }

private:
    std::array<uint8_t, N> data_;
};

} // namespace crypto
