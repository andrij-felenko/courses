#include <iostream>
#include <variant>
#include <cstdint>
#include <string>
#include <compare>
#include <algorithm>

namespace cardinal {

struct Finite { uint64_t value; };
struct Aleph  { uint64_t index; };
struct Beth   { uint64_t index; };

class Cardinal {
public:
    using Repr = std::variant<Finite, Aleph, Beth>;

    constexpr Cardinal(uint64_t val) : repr_(Finite{val}) {}
    constexpr Cardinal(Repr repr) : repr_(repr) {}

    static constexpr Cardinal make_aleph(uint64_t idx) { return Cardinal(Aleph{idx}); }
    static constexpr Cardinal make_beth(uint64_t idx)  { return Cardinal(Beth{idx}); }
    static constexpr Cardinal continuum()             { return Cardinal(Beth{1}); }

    [[nodiscard]] const Repr& data() const noexcept { return repr_; }

    [[nodiscard]] std::string to_string() const {
        return std::visit([](const auto& v) -> std::string {
            using T = std::decay_t<decltype(v)>;
            if constexpr (std::is_same_v<T, Finite>) {
                return std::to_string(v.value);
            } else if constexpr (std::is_same_v<T, Aleph>) {
                return "Aleph_" + std::to_string(v.index);
            } else if constexpr (std::is_same_v<T, Beth>) {
                if (v.index == 1) return "c (Beth_1)";
                return "Beth_" + std::to_string(v.index);
            }
        }, repr_);
    }

    friend auto operator<=>(const Cardinal& lhs, const Cardinal& rhs) noexcept {
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
        }, lhs.repr_, rhs.repr_);
    }

    friend bool operator==(const Cardinal& lhs, const Cardinal& rhs) noexcept {
        return (lhs <=> rhs) == 0;
    }

private:
    Repr repr_;
};

/* Арифметичні операції */
inline Cardinal operator+(const Cardinal& a, const Cardinal& b) {
    if (std::holds_alternative<Finite>(a.data()) && std::holds_alternative<Finite>(b.data())) {
        return Cardinal(std::get<Finite>(a.data()).value + std::get<Finite>(b.data()).value);
    }
    return (a >= b) ? a : b;
}

inline Cardinal operator*(const Cardinal& a, const Cardinal& b) {
    if (std::holds_alternative<Finite>(a.data()) && std::get<Finite>(a.data()).value == 0) return Cardinal(0);
    if (std::holds_alternative<Finite>(b.data()) && std::get<Finite>(b.data()).value == 0) return Cardinal(0);

    if (std::holds_alternative<Finite>(a.data()) && std::holds_alternative<Finite>(b.data())) {
        return Cardinal(std::get<Finite>(a.data()).value * std::get<Finite>(b.data()).value);
    }
    return (a >= b) ? a : b;
}

inline Cardinal power(const Cardinal& base, const Cardinal& exp) {
    if (std::holds_alternative<Finite>(exp.data()) && std::get<Finite>(exp.data()).value == 0) return Cardinal(1);
    if (std::holds_alternative<Finite>(base.data()) && std::get<Finite>(base.data()).value == 0) return Cardinal(0);
    if (std::holds_alternative<Finite>(base.data()) && std::get<Finite>(base.data()).value == 1) return Cardinal(1);

    if (std::holds_alternative<Finite>(base.data()) && std::holds_alternative<Finite>(exp.data())) {
        uint64_t b = std::get<Finite>(base.data()).value;
        uint64_t e = std::get<Finite>(exp.data()).value;
        uint64_t res = 1;
        for (uint64_t i = 0; i < e; ++i) res *= b;
        return Cardinal(res);
    }

    if (std::holds_alternative<Finite>(base.data()) && std::get<Finite>(base.data()).value >= 2) {
        if (std::holds_alternative<Aleph>(exp.data())) {
            return Cardinal::make_beth(std::get<Aleph>(exp.data()).index + 1);
        }
        if (std::holds_alternative<Beth>(exp.data())) {
            return Cardinal::make_beth(std::get<Beth>(exp.data()).index + 1);
        }
    }

    if (base <= exp) {
        if (std::holds_alternative<Aleph>(exp.data())) {
            return Cardinal::make_beth(std::get<Aleph>(exp.data()).index + 1);
        }
        if (std::holds_alternative<Beth>(exp.data())) {
            return Cardinal::make_beth(std::get<Beth>(exp.data()).index + 1);
        }
    }

    return base;
}

} // namespace cardinal

int main() {
    using namespace cardinal;

    auto aleph0 = Cardinal::make_aleph(0);
    auto aleph1 = Cardinal::make_aleph(1);
    auto c = Cardinal::continuum();
    auto ten = Cardinal(10);
    auto two = Cardinal(2);

    std::cout << "1. Aleph_0 + 10 = " << (aleph0 + ten).to_string() << "\n";
    std::cout << "2. Aleph_0 * Aleph_1 = " << (aleph0 * aleph1).to_string() << "\n";
    std::cout << "3. 2 ^ Aleph_0 = " << power(two, aleph0).to_string() << "\n";
    std::cout << "4. c ^ Aleph_0 = " << power(c, aleph0).to_string() << "\n";
    std::cout << "5. 2 ^ c = " << power(two, c).to_string() << "\n";

    return 0;
}
