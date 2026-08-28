// C++20: Типобезпечне форматування без динамічної пам'яті та RTTI
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <charconv>

// Компактний буфер фіксованого розміру (розміщується на стеку)
template <std::size_t N>
class FixedStringBuffer {
public:
    constexpr FixedStringBuffer() = default;

    bool append(std::string_view sv) noexcept {
        if (len_ + sv.size() >= N) return false;
        for (char c : sv) data_[len_++] = c;
        data_[len_] = '\0';
        return true;
    }

    bool append_int(std::integral auto val) noexcept {
        auto [ptr, ec] = std::to_chars(data_ + len_, data_ + N - 1, val);
        if (ec != std::errc()) return false;
        len_ = static_cast<std::size_t>(ptr - data_);
        data_[len_] = '\0';
        return true;
    }

    [[nodiscard]] std::string_view view() const noexcept {
        return std::string_view(data_, len_);
    }

private:
    char data_[N]{};
    std::size_t len_{0};
};
