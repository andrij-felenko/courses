#include <cstdint>
#include <array>
#include <iostream>
#include <iomanip>
#include <stdexcept>

class Gf28 {
public:
    uint8_t val;

    constexpr Gf28() noexcept : val(0) {}
    constexpr explicit Gf28(uint8_t v) noexcept : val(v) {}

    // Додавання та віднімання в GF(2^8) збігаються (XOR)
    constexpr Gf28 operator+(Gf28 other) const noexcept {
        return Gf28(val ^ other.val);
    }

    constexpr Gf28 operator-(Gf28 other) const noexcept {
        return Gf28(val ^ other.val);
    }

    // Множення на x (xtime) з редукцією за модулем x^8 + x^4 + x^3 + x + 1 (0x11B)
    static constexpr uint8_t xtime(uint8_t a) noexcept {
        return static_cast<uint8_t>((a << 1) ^ ((a & 0x80) ? 0x1B : 0x00));
    }

    // Звичайне множення поліномів через зсуви
    constexpr Gf28 operator*(Gf28 other) const noexcept {
        uint8_t res = 0;
        uint8_t a = val;
        uint8_t b = other.val;
        while (b > 0) {
            if (b & 1) {
                res ^= a;
            }
            a = xtime(a);
            b >>= 1;
        }
        return Gf28(res);
    }

    // Автоморфізм Фробеніуса σ(a) = a^2
    [[nodiscard]] constexpr Gf28 frobenius() const noexcept {
        return (*this) * (*this);
    }

    // Слід елемента Tr(a) = sum_{i=0}^7 a^{2^i}
    [[nodiscard]] constexpr uint8_t trace() const noexcept {
        Gf28 tr = *this;
        Gf28 cur = *this;
        for (int i = 1; i < 8; ++i) {
            cur = cur.frobenius();
            tr = tr + cur;
        }
        return tr.val;
    }

    // Норма елемента N(a) = prod_{i=0}^7 a^{2^i} = a^255
    [[nodiscard]] constexpr uint8_t norm() const noexcept {
        return (val == 0) ? 0 : 1;
    }

    // Мультиплікативне обернення через розширений алгоритм Евкліда
    [[nodiscard]] Gf28 inverse() const {
        if (val == 0) {
            throw std::domain_error("Division by zero in GF(2^8)");
        }

        uint32_t r0 = 0x11B, r1 = val;
        uint32_t v0 = 0, v1 = 1;

        auto poly_deg = [](uint32_t p) noexcept -> int {
            int deg = -1;
            while (p > 0) { deg++; p >>= 1; }
            return deg;
        };

        while (r1 > 0) {
            int d0 = poly_deg(r0);
            int d1 = poly_deg(r1);
            int shift = d0 - d1;

            if (shift < 0) {
                std::swap(r0, r1);
                std::swap(v0, v1);
                shift = -shift;
            }

            r0 ^= (r1 << shift);
            v0 ^= (v1 << shift);
        }

        return Gf28(static_cast<uint8_t>(v0));
    }

    Gf28 operator/(Gf28 other) const {
        return (*this) * other.inverse();
    }

    constexpr bool operator==(Gf28 other) const noexcept { return val == other.val; }
    constexpr bool operator!=(Gf28 other) const noexcept { return val != other.val; }
};

// Генерація таблиць логарифмів та експонент під час компіляції (constexpr)
struct Gf28Tables {
    std::array<uint8_t, 256> exp{};
    std::array<uint8_t, 256> log{};

    constexpr Gf28Tables() noexcept {
        uint8_t val = 1;
        for (int i = 0; i < 255; ++i) {
            exp[i] = val;
            log[val] = static_cast<uint8_t>(i);
            val = (Gf28(val) * Gf28(0x03)).val; // генератор g = 0x03
        }
        exp[255] = exp[0];
        log[0] = 0;
    }
};

inline constexpr Gf28Tables TABLES{};

// Швидке множення через попередньо обчислені таблиці
inline Gf28 mul_fast(Gf28 a, Gf28 b) noexcept {
    if (a.val == 0 || b.val == 0) return Gf28(0);
    int sum = TABLES.log[a.val] + TABLES.log[b.val];
    if (sum >= 255) sum -= 255;
    return Gf28(TABLES.exp[sum]);
}

int main() {
    Gf28 a(0x57); // x^6 + x^4 + x^2 + x + 1
    Gf28 b(0x83); // x^7 + x + 1

    Gf28 prod_slow = a * b;
    Gf28 prod_fast = mul_fast(a, b);
    Gf28 a_inv = a.inverse();
    Gf28 one = a * a_inv;
    uint8_t tr_a = a.trace();

    std::cout << std::hex << std::uppercase;
    std::cout << "a = 0x" << std::setw(2) << std::setfill('0') << static_cast<int>(a.val) << "\n";
    std::cout << "b = 0x" << std::setw(2) << std::setfill('0') << static_cast<int>(b.val) << "\n";
    std::cout << "a * b (xtime)  = 0x" << static_cast<int>(prod_slow.val) << " (очікується 0xC1)\n";
    std::cout << "a * b (fast)   = 0x" << static_cast<int>(prod_fast.val) << "\n";
    std::cout << "inv(a)         = 0x" << static_cast<int>(a_inv.val) << "\n";
    std::cout << "a * inv(a)     = 0x" << static_cast<int>(one.val) << " (очікується 0x01)\n";
    std::cout << std::dec;
    std::cout << "Tr(a)          = " << static_cast<int>(tr_a) << "\n";

    return 0;
}
