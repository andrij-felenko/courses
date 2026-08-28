#include <iostream>
#include <variant>
#include <cstdint>
#include <string>
#include <compare>

namespace math {

struct Finite { uint64_t value; };
struct Aleph  { uint64_t index; };
struct Beth   { uint64_t index; };

class Cardinal {
public:
    using Storage = std::variant<Finite, Aleph, Beth>;

    constexpr Cardinal(uint64_t val) : data_(Finite{val}) {}
    constexpr Cardinal(Storage s) : data_(s) {}

    static constexpr Cardinal aleph(uint64_t idx) { return Cardinal(Aleph{idx}); }
    static constexpr Cardinal beth(uint64_t idx)  { return Cardinal(Beth{idx}); }
    static constexpr Cardinal continuum()         { return Cardinal(Beth{1}); }

    [[nodiscard]] const Storage& raw() const noexcept { return data_; }

    [[nodiscard]] std::string str() const {
        return std::visit([](const auto& v) -> std::string {
            using T = std::decay_t<decltype(v)>;
            if constexpr (std::is_same_v<T, Finite>) {
                return std::to_string(v.value);
            } else if constexpr (std::is_same_v<T, Aleph>) {
                return "Aleph_" + std::to_string(v.index);
            } else if constexpr (std::is_same_v<T, Beth>) {
                return (v.index == 1) ? "c" : ("Beth_" + std::to_string(v.index));
            }
        }, data_);
    }

    friend auto operator<=>(const Cardinal& a, const Cardinal& b) noexcept {
        return std::visit([](const auto& x, const auto& y) -> std::strong_ordering {
            using Tx = std::decay_t<decltype(x)>;
            using Ty = std::decay_t<decltype(y)>;

            if constexpr (std::is_same_v<Tx, Finite> && std::is_same_v<Ty, Finite>) {
                return x.value <=> y.value;
            } else if constexpr (std::is_same_v<Tx, Finite>) {
                return std::strong_ordering::less;
            } else if constexpr (std::is_same_v<Ty, Finite>) {
                return std::strong_ordering::greater;
            } else if constexpr (std::is_same_v<Tx, Ty>) {
                return x.index <=> y.index;
            } else if constexpr (std::is_same_v<Tx, Aleph> && std::is_same_v<Ty, Beth>) {
                if (x.index == 0 && y.index == 0) return std::strong_ordering::equal;
                return std::strong_ordering::less;
            } else {
                if (x.index == 0 && y.index == 0) return std::strong_ordering::equal;
                return std::strong_ordering::greater;
            }
        }, a.data_, b.data_);
    }

    friend bool operator==(const Cardinal& a, const Cardinal& b) noexcept {
        return (a <=> b) == 0;
    }

private:
    Storage data_;
};

inline Cardinal operator+(const Cardinal& a, const Cardinal& b) {
    if (std::holds_alternative<Finite>(a.raw()) && std::holds_alternative<Finite>(b.raw())) {
        return Cardinal(std::get<Finite>(a.raw()).value + std::get<Finite>(b.raw()).value);
    }
    return (a >= b) ? a : b;
}

inline Cardinal operator*(const Cardinal& a, const Cardinal& b) {
    if ((std::holds_alternative<Finite>(a.raw()) && std::get<Finite>(a.raw()).value == 0) ||
        (std::holds_alternative<Finite>(b.raw()) && std::get<Finite>(b.raw()).value == 0)) {
        return Cardinal(0);
    }
    if (std::holds_alternative<Finite>(a.raw()) && std::holds_alternative<Finite>(b.raw())) {
        return Cardinal(std::get<Finite>(a.raw()).value * std::get<Finite>(b.raw()).value);
    }
    return (a >= b) ? a : b;
}

inline Cardinal pow(const Cardinal& base, const Cardinal& exp) {
    if (std::holds_alternative<Finite>(exp.raw()) && std::get<Finite>(exp.raw()).value == 0) return Cardinal(1);
    if (std::holds_alternative<Finite>(base.raw()) && std::get<Finite>(base.raw()).value == 0) return Cardinal(0);
    if (std::holds_alternative<Finite>(base.raw()) && std::get<Finite>(base.raw()).value == 1) return Cardinal(1);

    if (std::holds_alternative<Finite>(base.raw()) && std::holds_alternative<Finite>(exp.raw())) {
        uint64_t b = std::get<Finite>(base.raw()).value;
        uint64_t e = std::get<Finite>(exp.raw()).value;
        uint64_t res = 1;
        for (uint64_t i = 0; i < e; ++i) res *= b;
        return Cardinal(res);
    }

    if (std::holds_alternative<Finite>(base.raw()) && std::get<Finite>(base.raw()).value >= 2) {
        if (std::holds_alternative<Aleph>(exp.raw())) return Cardinal::beth(std::get<Aleph>(exp.raw()).index + 1);
        if (std::holds_alternative<Beth>(exp.raw()))  return Cardinal::beth(std::get<Beth>(exp.raw()).index + 1);
    }

    if (base <= exp) {
        if (std::holds_alternative<Aleph>(exp.raw())) return Cardinal::beth(std::get<Aleph>(exp.raw()).index + 1);
        if (std::holds_alternative<Beth>(exp.raw()))  return Cardinal::beth(std::get<Beth>(exp.raw()).index + 1);
    }

    return base;
}

} // namespace math
