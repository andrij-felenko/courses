#include <optional>
#include <utility>

// Розв'язати  a11*x + a12*y = b1
//             a21*x + a22*y = b2
// Повертає пару (x, y); std::nullopt — якщо розв'язок не єдиний.
std::optional<std::pair<double, double>>
solve2x2(double a11, double a12, double b1,
         double a21, double a22, double b2)
{
    double det = a11 * a22 - a12 * a21;   // визначник: 0 ⇒ прямі паралельні
    if (det == 0.0)
        return std::nullopt;              // нема єдиного розв'язку

    double x = (b1 * a22 - a12 * b2) / det;
    double y = (a11 * b2 - b1 * a21) / det;
    return std::make_pair(x, y);
}
