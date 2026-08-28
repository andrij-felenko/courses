#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <cstdint>

namespace koblitz {

// Арифметика поля GF(2⁴) з незвідним многочленом x⁴ + x + 1 (маска 0x13)
class Field16 {
public:
    static constexpr uint8_t Poly = 0x13;
    static constexpr uint8_t Mask = 0x0F;

    static constexpr uint8_t add(uint8_t a, uint8_t b) noexcept {
        return (a ^ b) & Mask;
    }

    static uint8_t mul(uint8_t a, uint8_t b) noexcept {
        uint8_t res = 0;
        a &= Mask;
        b &= Mask;
        while (b > 0) {
            if (b & 1) {
                res ^= a;
            }
            bool carry = (a & 0x08) != 0;
            a = (a << 1) & Mask;
            if (carry) {
                a ^= (Poly & Mask);
            }
            b >>= 1;
        }
        return res;
    }

    // Оператор Фробеніуса для поля: піднесення до квадрата z ↦ z²
    static uint8_t sqr(uint8_t a) noexcept {
        return mul(a, a);
    }

    // Знаходження оберненого елемента a¹⁴ = a⁻¹ за малою теоремою Ферма
    static uint8_t inv(uint8_t a) noexcept {
        if (a == 0) return 0;
        uint8_t a2 = sqr(a);
        uint8_t a4 = sqr(a2);
        uint8_t a8 = sqr(a4);
        return mul(a8, mul(a4, a2));
    }
};

// Точка на кривій Кобліца y² + xy = x³ + x² + 1 над GF(2⁴)
struct Point {
    uint8_t x{0};
    uint8_t y{0};
    bool is_infinity{true};

    static Point infinity() noexcept {
        return Point{0, 0, true};
    }

    static Point affine(uint8_t x_val, uint8_t y_val) noexcept {
        return Point{x_val, y_val, false};
    }

    bool operator==(const Point& other) const noexcept {
        if (is_infinity && other.is_infinity) return true;
        if (is_infinity || other.is_infinity) return false;
        return x == other.x && y == other.y;
    }

    // Протилежна точка на двійковій кривій: -P = (x, x + y)
    Point operator-() const noexcept {
        if (is_infinity) return *this;
        return Point::affine(x, Field16::add(x, y));
    }

    // Дія автоморфізму Фробеніуса: τ(x, y) = (x², y²)
    Point frobenius() const noexcept {
        if (is_infinity) return *this;
        return Point::affine(Field16::sqr(x), Field16::sqr(y));
    }

    // Додавання точок на кривій Кобліца
    Point operator+(const Point& other) const noexcept {
        if (is_infinity) return other;
        if (other.is_infinity) return *this;

        if (x == other.x) {
            if (y != other.y || x == 0) {
                return Point::infinity();
            }
            // Подвоєння точки: λ = x + y / x
            uint8_t lambda = Field16::add(x, Field16::mul(y, Field16::inv(x)));
            uint8_t x3 = Field16::add(Field16::add(Field16::sqr(lambda), lambda), 1);
            uint8_t y3 = Field16::add(Field16::add(Field16::mul(lambda, Field16::add(x, x3)), x3), y);
            return Point::affine(x3, y3);
        }

        uint8_t dx = Field16::add(x, other.x);
        uint8_t dy = Field16::add(y, other.y);
        uint8_t lambda = Field16::mul(dy, Field16::inv(dx));
        uint8_t x3 = Field16::add(Field16::add(Field16::add(Field16::sqr(lambda), lambda), dx), 1);
        uint8_t y3 = Field16::add(Field16::add(Field16::mul(lambda, Field16::add(x, x3)), x3), y);

        return Point::affine(x3, y3);
    }
};

// Обчислення τ-NAF розкладу скаляра k (μ = 1 для кривої з параметром a = 1)
inline std::vector<int8_t> compute_tau_naf(int k) {
    std::vector<int8_t> naf;
    int r0 = k;
    int r1 = 0;
    constexpr int mu = 1;

    while (r0 != 0 || r1 != 0) {
        if (r0 % 2 != 0) {
            int val = 2 - ((r0 - 2 * r1) % 4);
            if (val < -1) val += 4;
            if (val > 1)  val -= 4;
            naf.push_back(static_cast<int8_t>(val));
            r0 -= val;
        } else {
            naf.push_back(0);
        }
        int next_r0 = r1 + mu * (r0 / 2);
        int next_r1 = -(r0 / 2);
        r0 = next_r0;
        r1 = next_r1;
    }
    return naf;
}

// Скалярне множення через автоморфізм Фробеніуса (нуль подвоєнь точок)
inline Point scalar_mul_tau_naf(const Point& p, int k) {
    if (k == 0 || p.is_infinity) {
        return Point::infinity();
    }
    const auto naf = compute_tau_naf(k);
    Point q = Point::infinity();

    for (auto it = naf.rbegin(); it != naf.rend(); ++it) {
        q = q.frobenius(); // Заміна операції подвоєння точки на піднесення до квадрата
        if (*it == 1) {
            q = q + p;
        } else if (*it == -1) {
            q = q + (-p);
        }
    }
    return q;
}

} // namespace koblitz

int main() {
    using namespace koblitz;

    const Point p = Point::affine(2, 8);
    constexpr int k = 7;

    const auto naf = compute_tau_naf(k);
    std::cout << "Скаляр k = " << k << " у τ-NAF поданні:\nu = [ ";
    for (auto it = naf.rbegin(); it != naf.rend(); ++it) {
        std::cout << static_cast<int>(*it) << " ";
    }
    std::cout << "] (довжина розкладу: " << naf.size() << ")\n";

    const Point res = scalar_mul_tau_naf(p, k);
    std::cout << "Результат скалярного множення " << k << " · P = (" 
              << static_cast<int>(res.x) << ", " 
              << static_cast<int>(res.y) << ")\n";

    return 0;
}
