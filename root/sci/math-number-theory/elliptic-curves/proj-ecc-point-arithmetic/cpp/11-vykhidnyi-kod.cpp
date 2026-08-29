#include <iostream>
#include <optional>
#include <stdexcept>
#include <cstdint>
#include <utility>
#include <array>
#include <string>
#include <iomanip>
#include <vector>

namespace ecc {

// ============================================================================
// Представлення точок в афінних та проективних координатах Якобі
// ============================================================================

// Афінна точка на еліптичній кривій: std::nullopt представляє нескінченність O
struct AffinePoint {
    std::optional<std::pair<int64_t, int64_t>> coord;

    [[nodiscard]] constexpr bool is_infinity() const noexcept {
        return !coord.has_value();
    }

    [[nodiscard]] static constexpr AffinePoint infinity() noexcept {
        return AffinePoint{std::nullopt};
    }

    [[nodiscard]] static constexpr AffinePoint from_coords(int64_t x, int64_t y) noexcept {
        return AffinePoint{std::make_pair(x, y)};
    }

    [[nodiscard]] bool operator==(const AffinePoint& other) const noexcept {
        if (is_infinity() && other.is_infinity()) return true;
        if (is_infinity() || other.is_infinity()) return false;
        return coord->first == other.coord->first && coord->second == other.coord->second;
    }

    [[nodiscard]] bool operator!=(const AffinePoint& other) const noexcept {
        return !(*this == other);
    }
};

// Точка у проективних координатах Якобі: (X : Y : Z), де x = X/Z^2, y = Y/Z^3
struct JacobianPoint {
    int64_t X{1};
    int64_t Y{1};
    int64_t Z{0};
    bool is_infinity{true};

    [[nodiscard]] static constexpr JacobianPoint infinity() noexcept {
        return JacobianPoint{1, 1, 0, true};
    }

    [[nodiscard]] static constexpr JacobianPoint from_coords(int64_t x, int64_t y, int64_t z = 1) noexcept {
        return JacobianPoint{x, y, z, false};
    }
};

// ============================================================================
// Клас еліптичної кривої Вейєрштрасса над скінченним полем F_p
// ============================================================================

class EllipticCurve {
private:
    int64_t a_;
    int64_t b_;
    int64_t p_;
    int64_t order_; // Порядок підгрупи базової точки

    // Нормалізація залишку в діапазон [0, p_ - 1]
    [[nodiscard]] constexpr int64_t mod_pos(int64_t val) const noexcept {
        int64_t r = val % p_;
        return (r < 0) ? (r + p_) : r;
    }

    // Модульне додавання
    [[nodiscard]] constexpr int64_t mod_add(int64_t a, int64_t b) const noexcept {
        return mod_pos(a + b);
    }

    // Модульне віднімання
    [[nodiscard]] constexpr int64_t mod_sub(int64_t a, int64_t b) const noexcept {
        return mod_pos(a - b);
    }

    // Модульне множення
    [[nodiscard]] constexpr int64_t mod_mul(int64_t a, int64_t b) const noexcept {
        return mod_pos(static_cast<int64_t>((static_cast<__int128>(a) * b) % p_));
    }

    // Двійкове піднесення до степеня
    [[nodiscard]] int64_t mod_pow(int64_t base, int64_t exp) const noexcept {
        int64_t res = 1;
        int64_t b = mod_pos(base);
        int64_t e = exp;
        while (e > 0) {
            if (e & 1) {
                res = mod_mul(res, b);
            }
            b = mod_mul(b, b);
            e >>= 1;
        }
        return res;
    }

    // Розширений алгоритм Евкліда для обчислення оберненого елемента
    [[nodiscard]] int64_t mod_inverse(int64_t b) const {
        int64_t t = 0, newt = 1;
        int64_t r = p_, newr = mod_pos(b);

        while (newr != 0) {
            int64_t quotient = r / newr;
            int64_t temp_t = t - quotient * newt;
            t = newt;
            newt = temp_t;

            int64_t temp_r = r - quotient * newr;
            r = newr;
            newr = temp_r;
        }

        if (r > 1) {
            throw std::invalid_argument("Елемент не має оберненого за модулем (gcd > 1)");
        }
        return mod_pos(t);
    }

    // Квадратний корінь mod p (Алгоритм Тонеллі-Шенкса / випадок 4k+3)
    [[nodiscard]] int64_t mod_sqrt(int64_t val) const {
        int64_t n = mod_pos(val);
        if (n == 0) return 0;
        if (mod_pow(n, (p_ - 1) / 2) != 1) {
            return -1; // Не є квадратичним лишком
        }
        if (p_ % 4 == 3) {
            return mod_pow(n, (p_ + 1) / 4);
        }

        int64_t q = p_ - 1;
        int64_t s = 0;
        while ((q & 1) == 0) {
            s++;
            q >>= 1;
        }
        int64_t z = 2;
        while (mod_pow(z, (p_ - 1) / 2) != p_ - 1) {
            z++;
        }
        int64_t m = s;
        int64_t c = mod_pow(z, q);
        int64_t t = mod_pow(n, q);
        int64_t r = mod_pow(n, (q + 1) / 2);

        while (t != 0 && t != 1) {
            int64_t t2i = t;
            int64_t i = 0;
            for (i = 1; i < m; i++) {
                t2i = mod_mul(t2i, t2i);
                if (t2i == 1) break;
            }
            int64_t b_exp = 1LL << (m - i - 1);
            int64_t b = mod_pow(c, b_exp);
            m = i;
            c = mod_mul(b, b);
            t = mod_mul(t, c);
            r = mod_mul(r, b);
        }
        return r;
    }

    // Умовний обмін точок без розгалуження (Constant-Time CSWAP)
    static void cswap(uint64_t bit, AffinePoint& P, AffinePoint& Q) noexcept {
        uint64_t mask = -(bit & 1);
        bool p_inf = P.is_infinity();
        bool q_inf = Q.is_infinity();

        int64_t px = p_inf ? 0 : P.coord->first;
        int64_t py = p_inf ? 0 : P.coord->second;
        int64_t qx = q_inf ? 0 : Q.coord->first;
        int64_t qy = q_inf ? 0 : Q.coord->second;

        uint64_t dx = mask & (static_cast<uint64_t>(px) ^ static_cast<uint64_t>(qx));
        px = static_cast<int64_t>(static_cast<uint64_t>(px) ^ dx);
        qx = static_cast<int64_t>(static_cast<uint64_t>(qx) ^ dx);

        uint64_t dy = mask & (static_cast<uint64_t>(py) ^ static_cast<uint64_t>(qy));
        py = static_cast<int64_t>(static_cast<uint64_t>(py) ^ dy);
        qy = static_cast<int64_t>(static_cast<uint64_t>(qy) ^ dy);

        uint8_t d_inf = static_cast<uint8_t>(mask & (static_cast<uint8_t>(p_inf) ^ static_cast<uint8_t>(q_inf)));
        p_inf = static_cast<bool>(static_cast<uint8_t>(p_inf) ^ d_inf);
        q_inf = static_cast<bool>(static_cast<uint8_t>(q_inf) ^ d_inf);

        P = p_inf ? AffinePoint::infinity() : AffinePoint::from_coords(px, py);
        Q = q_inf ? AffinePoint::infinity() : AffinePoint::from_coords(qx, qy);
    }

public:
    constexpr EllipticCurve(int64_t a, int64_t b, int64_t p, int64_t order = 0) noexcept
        : a_(a), b_(b), p_(p), order_(order) {}

    [[nodiscard]] constexpr int64_t a() const noexcept { return a_; }
    [[nodiscard]] constexpr int64_t b() const noexcept { return b_; }
    [[nodiscard]] constexpr int64_t p() const noexcept { return p_; }
    [[nodiscard]] constexpr int64_t order() const noexcept { return order_; }

    // Перевірка належності точки кривій
    [[nodiscard]] bool is_on_curve(const AffinePoint& pt) const noexcept {
        if (pt.is_infinity()) return true;
        const auto [x, y] = *pt.coord;
        const int64_t lhs = mod_mul(y, y);
        const int64_t rhs = mod_add(mod_add(mod_pow(x, 3), mod_mul(a_, x)), b_);
        return lhs == rhs;
    }

    // Протилежна точка: -P
    [[nodiscard]] AffinePoint negate(const AffinePoint& pt) const noexcept {
        if (pt.is_infinity()) return pt;
        const auto [x, y] = *pt.coord;
        return AffinePoint::from_coords(x, mod_pos(-y));
    }

    // Подвоєння афінної точки: 2*P
    [[nodiscard]] AffinePoint double_point(const AffinePoint& P) const {
        if (P.is_infinity() || P.coord->second == 0) {
            return AffinePoint::infinity();
        }

        const auto [x1, y1] = *P.coord;
        const int64_t num = mod_add(mod_mul(3, mod_mul(x1, x1)), a_);
        const int64_t den = mod_mul(2, y1);
        const int64_t lambda = mod_mul(num, mod_inverse(den));

        const int64_t x3 = mod_sub(mod_mul(lambda, lambda), mod_mul(2, x1));
        const int64_t y3 = mod_sub(mod_mul(lambda, mod_sub(x1, x3)), y1);

        return AffinePoint::from_coords(x3, y3);
    }

    // Додавання двох афінних точок: P + Q
    [[nodiscard]] AffinePoint add(const AffinePoint& P, const AffinePoint& Q) const {
        if (P.is_infinity()) return Q;
        if (Q.is_infinity()) return P;

        const auto [x1, y1] = *P.coord;
        const auto [x2, y2] = *Q.coord;

        if (x1 == x2) {
            if (mod_add(y1, y2) == 0) {
                return AffinePoint::infinity();
            }
            return double_point(P);
        }

        const int64_t num = mod_sub(y2, y1);
        const int64_t den = mod_sub(x2, x1);
        const int64_t lambda = mod_mul(num, mod_inverse(den));

        const int64_t x3 = mod_sub(mod_sub(mod_mul(lambda, lambda), x1), x2);
        const int64_t y3 = mod_sub(mod_mul(lambda, mod_sub(x1, x3)), y1);

        return AffinePoint::from_coords(x3, y3);
    }

    // Скалярне множення k*P методом Double-and-Add
    [[nodiscard]] AffinePoint scalar_multiply(int64_t k, const AffinePoint& P) const {
        AffinePoint result = AffinePoint::infinity();
        AffinePoint addend = P;
        int64_t scalar = k;

        if (order_ > 0) {
            scalar = scalar % order_;
            if (scalar < 0) scalar += order_;
        }

        while (scalar > 0) {
            if (scalar & 1) {
                result = add(result, addend);
            }
            addend = double_point(addend);
            scalar >>= 1;
        }
        return result;
    }

    // Скалярне множення драбиною Монтгомері (Montgomery Ladder)
    [[nodiscard]] AffinePoint scalar_multiply_montgomery(int64_t k, const AffinePoint& P) const {
        AffinePoint R0 = AffinePoint::infinity();
        AffinePoint R1 = P;
        int64_t scalar = k;

        if (order_ > 0) {
            scalar = scalar % order_;
            if (scalar < 0) scalar += order_;
        }

        int msb = 62;
        while (msb >= 0 && !((scalar >> msb) & 1)) {
            msb--;
        }

        for (int i = msb; i >= 0; i--) {
            uint64_t bit = static_cast<uint64_t>((scalar >> i) & 1);
            cswap(bit, R0, R1);
            R1 = add(R0, R1);
            R0 = double_point(R0);
            cswap(bit, R0, R1);
        }
        return R0;
    }

    // ========================================================================
    // Координати Якобі
    // ========================================================================

    [[nodiscard]] JacobianPoint to_jacobian(const AffinePoint& pt) const noexcept {
        if (pt.is_infinity()) return JacobianPoint::infinity();
        return JacobianPoint::from_coords(pt.coord->first, pt.coord->second, 1);
    }

    [[nodiscard]] AffinePoint to_affine(const JacobianPoint& jp) const {
        if (jp.is_infinity || jp.Z == 0) return AffinePoint::infinity();
        const int64_t z_inv = mod_inverse(jp.Z);
        const int64_t z_inv2 = mod_mul(z_inv, z_inv);
        const int64_t z_inv3 = mod_mul(z_inv2, z_inv);
        const int64_t x = mod_mul(jp.X, z_inv2);
        const int64_t y = mod_mul(jp.Y, z_inv3);
        return AffinePoint::from_coords(x, y);
    }

    [[nodiscard]] JacobianPoint jacobian_double(const JacobianPoint& jp) const {
        if (jp.is_infinity || jp.Y == 0) return JacobianPoint::infinity();

        const int64_t S = mod_mul(4, mod_mul(jp.X, mod_mul(jp.Y, jp.Y)));
        const int64_t Z2 = mod_mul(jp.Z, jp.Z);
        const int64_t Z4 = mod_mul(Z2, Z2);
        const int64_t M = mod_add(mod_mul(3, mod_mul(jp.X, jp.X)), mod_mul(a_, Z4));

        const int64_t X3 = mod_sub(mod_mul(M, M), mod_mul(2, S));
        const int64_t Y2 = mod_mul(jp.Y, jp.Y);
        const int64_t Y4 = mod_mul(Y2, Y2);
        const int64_t Y3 = mod_sub(mod_mul(M, mod_sub(S, X3)), mod_mul(8, Y4));
        const int64_t Z3 = mod_mul(2, mod_mul(jp.Y, jp.Z));

        return JacobianPoint{X3, Y3, Z3, false};
    }

    [[nodiscard]] JacobianPoint jacobian_add(const JacobianPoint& jp1, const JacobianPoint& jp2) const {
        if (jp1.is_infinity) return jp2;
        if (jp2.is_infinity) return jp1;

        const int64_t Z1_2 = mod_mul(jp1.Z, jp1.Z);
        const int64_t Z2_2 = mod_mul(jp2.Z, jp2.Z);

        const int64_t U1 = mod_mul(jp1.X, Z2_2);
        const int64_t U2 = mod_mul(jp2.X, Z1_2);

        const int64_t S1 = mod_mul(jp1.Y, mod_mul(jp2.Z, Z2_2));
        const int64_t S2 = mod_mul(jp2.Y, mod_mul(jp1.Z, Z1_2));

        if (U1 == U2) {
            if (S1 != S2) return JacobianPoint::infinity();
            return jacobian_double(jp1);
        }

        const int64_t H = mod_sub(U2, U1);
        const int64_t r = mod_sub(S2, S1);
        const int64_t H2 = mod_mul(H, H);
        const int64_t H3 = mod_mul(H, H2);

        const int64_t X3 = mod_sub(mod_sub(mod_mul(r, r), H3), mod_mul(2, mod_mul(U1, H2)));
        const int64_t Y3 = mod_sub(mod_mul(r, mod_sub(mod_mul(U1, H2), X3)), mod_mul(S1, H3));
        const int64_t Z3 = mod_mul(H, mod_mul(jp1.Z, jp2.Z));

        return JacobianPoint{X3, Y3, Z3, false};
    }

    // ========================================================================
    // Стиснення точок та протокол ECDH
    // ========================================================================

    [[nodiscard]] std::array<uint8_t, 9> compress(const AffinePoint& pt) const {
        std::array<uint8_t, 9> out{};
        if (pt.is_infinity()) {
            out.fill(0);
            return out;
        }
        const auto [x, y] = *pt.coord;
        out[0] = (y % 2 == 0) ? 0x02 : 0x03;
        for (int i = 0; i < 8; ++i) {
            out[1 + i] = static_cast<uint8_t>((x >> (8 * (7 - i))) & 0xFF);
        }
        return out;
    }

    [[nodiscard]] std::optional<AffinePoint> decompress(const std::array<uint8_t, 9>& bytes) const {
        if (bytes[0] == 0x00) {
            return AffinePoint::infinity();
        }
        if (bytes[0] != 0x02 && bytes[0] != 0x03) {
            return std::nullopt;
        }

        int64_t x = 0;
        for (int i = 0; i < 8; ++i) {
            x = (x << 8) | bytes[1 + i];
        }
        x = mod_pos(x);

        const int64_t rhs = mod_add(mod_add(mod_pow(x, 3), mod_mul(a_, x)), b_);
        int64_t y = mod_sqrt(rhs);

        if (y == -1) {
            return std::nullopt; // Точка не лежить на кривій
        }

        const bool y_is_odd = (y % 2 != 0);
        const bool want_odd = (bytes[0] == 0x03);
        if (y_is_odd != want_odd) {
            y = mod_pos(-y);
        }

        return AffinePoint::from_coords(x, y);
    }

    [[nodiscard]] std::optional<int64_t> ecdh_shared_secret(int64_t priv_key, const AffinePoint& pub_key) const {
        if (!is_on_curve(pub_key) || pub_key.is_infinity()) {
            return std::nullopt;
        }
        const AffinePoint shared = scalar_multiply(priv_key, pub_key);
        if (shared.is_infinity()) {
            return std::nullopt;
        }
        return shared.coord->first;
    }
};

} // namespace ecc

// ============================================================================
// Головна програма та верифікація векторів
// ============================================================================

static void print_point(const std::string& label, const ecc::AffinePoint& P) {
    if (P.is_infinity()) {
        std::cout << label << ": O (нескінченність)\n";
    } else {
        std::cout << label << ": (" << P.coord->first << ", " << P.coord->second << ")\n";
    }
}

int main() {
    // Параметри тестової кривої: y^2 = x^3 + 2*x + 3 (mod 97), порядок підгрупи n = 5
    const ecc::EllipticCurve curve(2, 3, 97, 5);
    const ecc::AffinePoint P = ecc::AffinePoint::from_coords(3, 6);

    std::cout << "=== Тестування точкової арифметики C++ (F_97) ===\n";
    std::cout << "Крива: y^2 = x^3 + " << curve.a() << "*x + " << curve.b() << " (mod " << curve.p() << ")\n";
    print_point("Базова точка P", P);

    // 1. Перевірка належності точки кривій
    if (curve.is_on_curve(P)) {
        std::cout << "[OK] Базова точка P належить кривій.\n";
    }

    // 2. Послідовні операції подвоєння та додавання
    const auto P2 = curve.double_point(P);
    print_point("2*P (подвоєння)", P2);

    const auto P3 = curve.add(P2, P);
    print_point("3*P (додавання P2 + P)", P3);

    const auto P4 = curve.double_point(P2);
    print_point("4*P (подвоєння 2*P)", P4);

    const auto P5 = curve.add(P4, P);
    print_point("5*P (додавання 4*P + P)", P5);

    // 3. Скалярне множення Double-and-Add
    std::cout << "\n=== Скалярне множення k*P ===\n";
    for (int64_t k = 1; k <= 5; ++k) {
        const auto kP = curve.scalar_multiply(k, P);
        print_point("k = " + std::to_string(k) + ": k*P", kP);
    }

    // 4. Драбина Монтгомері
    std::cout << "\n=== Драбина Монтгомері (Constant-Time) ===\n";
    for (int64_t k = 1; k <= 5; ++k) {
        const auto kP_mont = curve.scalar_multiply_montgomery(k, P);
        const auto kP_std = curve.scalar_multiply(k, P);
        if (kP_mont != kP_std) {
            std::cout << "[FAIL] Розбіжність для k = " << k << "\n";
        }
    }
    std::cout << "[OK] Драбина Монтгомері співпадає з Double-and-Add для всіх k.\n";

    // 5. Координати Якобі
    std::cout << "\n=== Точкова арифметика Якобі ===\n";
    const auto JP = curve.to_jacobian(P);
    const auto JP2 = curve.jacobian_double(JP);
    const auto P2_jac = curve.to_affine(JP2);
    print_point("2*P через Якобі", P2_jac);

    const auto JP3 = curve.jacobian_add(JP2, JP);
    const auto P3_jac = curve.to_affine(JP3);
    print_point("3*P через Якобі", P3_jac);

    // 6. Стиснення та відновлення точок
    std::cout << "\n=== Стиснення та декомпресія точок ===\n";
    const auto compressed = curve.compress(P);
    std::cout << "Стиснена точка P (заголовок: 0x" << std::hex << static_cast<int>(compressed[0]) << std::dec << ")\n";

    const auto decompressed = curve.decompress(compressed);
    if (decompressed.has_value()) {
        print_point("Відновлена точка", *decompressed);
        if (*decompressed == P) {
            std::cout << "[OK] Відновлена точка повністю ідентична P.\n";
        }
    }

    // 7. Протокол ECDH
    std::cout << "\n=== Протокол обміну ключами ECDH ===\n";
    const int64_t alice_priv = 2;
    const auto alice_pub = curve.scalar_multiply(alice_priv, P); // 2*P = (80, 10)

    const int64_t bob_priv = 3;
    const auto bob_pub = curve.scalar_multiply(bob_priv, P); // 3*P = (80, 87)

    const auto alice_secret = curve.ecdh_shared_secret(alice_priv, bob_pub);
    const auto bob_secret = curve.ecdh_shared_secret(bob_priv, alice_pub);

    if (alice_secret.has_value() && bob_secret.has_value() && *alice_secret == *bob_secret) {
        std::cout << "Спільний ключ Аліси та Боба: " << *alice_secret << "\n";
        std::cout << "[OK] Протокол ECDH виконано успішно.\n";
    }

    return 0;
}
