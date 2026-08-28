#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>

template <typename T>
class RingBufferSpan {
private:
    std::span<T> storage_;

public:
    explicit constexpr RingBufferSpan(std::span<T> storage) noexcept 
        : storage_(storage) {}

    [[nodiscard]] constexpr T& at_wrapped(std::int32_t index) const {
        const auto n = static_cast<std::int32_t>(storage_.size());
        std::int32_t rem = index % n;
        if (rem < 0) {
            rem += n;
        }
        return storage_[static_cast<std::size_t>(rem)];
    }
};
