// cpp
#include <cstdint>

class Literal {
    uint32_t code_{0};
public:
    constexpr Literal() noexcept = default;
    constexpr Literal(uint32_t var, bool is_neg) noexcept 
        : code_((var << 1) | (is_neg ? 1u : 0u)) {}
    
    [[nodiscard]] constexpr uint32_t var() const noexcept { return code_ >> 1; }
    [[nodiscard]] constexpr bool is_neg() const noexcept { return (code_ & 1u) != 0; }
    [[nodiscard]] constexpr Literal neg() const noexcept { return Literal(code_ ^ 1u); }
    [[nodiscard]] constexpr uint32_t code() const noexcept { return code_; }
    
    constexpr bool operator==(const Literal& o) const noexcept { return code_ == o.code_; }
    constexpr bool operator!=(const Literal& o) const noexcept { return code_ != o.code_; }
private:
    constexpr explicit Literal(uint32_t raw_code) noexcept : code_(raw_code) {}
};
