#include <iostream>
#include <optional>
#include <stdexcept>
#include <cstdint>

// Клас моделювання скінченного поля F_p та точкової арифметики
class EllipticCurve {
public:
    struct Point {
        std::optional<std::pair<int64_t, int64_t>> coord; // nullopt відповідає точці O

        [[nodiscard]] bool is_infinity() const noexcept {
            return !coord.has_value();
        }
    };

private:
    int64_t a_;
    int64_t b_;
    int64_t p_;

    [[nodiscard]] static int64_t mod_pos(int64_t val, int64_t p) noexcept {
        int64_t r = val % p;
        return r < 0 ? r + p : r;
    }

    [[nodiscard]] static int64_t mod_inverse(int64_t b, int64_t p) {
        int64_t t = 0, newt = 1;
        int64_t r = p, newr = mod_pos(b, p);

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
            throw std::invalid_argument("Елемент не має оберненого за модулем");
        }
        return mod_pos(t, p);
    }

public:
    EllipticCurve(int64_t a, int64_t b, int64_t p) : a_(a), b_(b), p_(p) {}

    [[nodiscard]] Point double_point(const Point& P) const {
        if (P.is_infinity() || P.coord->second == 0) {
            return Point{std::nullopt};
        }

        const auto [x1, y1] = *P.coord;
        const int64_t num = mod_pos(3 * x1 * x1 + a_, p_);
        const int64_t den = mod_pos(2 * y1, p_);
        const int64_t lambda = mod_pos(num * mod_inverse(den, p_), p_);

        const int64_t x3 = mod_pos(lambda * lambda - 2 * x1, p_);
        const int64_t y3 = mod_pos(lambda * (x1 - x3) - y1, p_);

        return Point{std::make_pair(x3, y3)};
    }

    [[nodiscard]] Point add(const Point& P, const Point& Q) const {
        if (P.is_infinity()) return Q;
        if (Q.is_infinity()) return P;

        const auto [x1, y1] = *P.coord;
        const auto [x2, y2] = *Q.coord;

        if (x1 == x2) {
            if (mod_pos(y1 + y2, p_) == 0) {
                return Point{std::nullopt};
            }
            return double_point(P);
        }

        const int64_t num = mod_pos(y2 - y1, p_);
        const int64_t den = mod_pos(x2 - x1, p_);
        const int64_t lambda = mod_pos(num * mod_inverse(den, p_), p_);

        const int64_t x3 = mod_pos(lambda * lambda - x1 - x2, p_);
        const int64_t y3 = mod_pos(lambda * (x1 - x3) - y1, p_);

        return Point{std::make_pair(x3, y3)};
    }

    [[nodiscard]] Point scalar_multiply(int64_t k, const Point& P) const {
        Point result{std::nullopt};
        Point addend = P;

        while (k > 0) {
            if (k & 1) {
                result = add(result, addend);
            }
            addend = double_point(addend);
            k >>= 1;
        }
        return result;
    }
};

int main() {
    // Крива y^2 = x^3 + 2*x + 3 (mod 97)
    EllipticCurve curve(2, 3, 97);
    EllipticCurve::Point P{std::make_pair(3, 6)};

    std::cout << "Початкова точка P: (" << P.coord->first << ", " << P.coord->second << ")\n";

    auto P2 = curve.double_point(P);
    std::cout << "2*P: (" << P2.coord->first << ", " << P2.coord->second << ")\n";

    auto P3 = curve.add(P2, P);
    std::cout << "3*P: (" << P3.coord->first << ", " << P3.coord->second << ")\n";

    auto P5 = curve.scalar_multiply(5, P);
    std::cout << "5*P (через Double-and-Add): (" << P5.coord->first << ", " << P5.coord->second << ")\n";

    return 0;
}
