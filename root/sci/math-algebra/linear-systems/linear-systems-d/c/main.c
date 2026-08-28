#include <stdbool.h>

// Розв'язати  a11*x + a12*y = b1
//             a21*x + a22*y = b2
// Повертає true й кладе результат у *x,*y; false — якщо розв'язок не єдиний.
bool solve2x2(double a11, double a12, double b1,
              double a21, double a22, double b2,
              double *x, double *y)
{
    double det = a11 * a22 - a12 * a21;   // визначник: 0 ⇒ прямі паралельні
    if (det == 0.0)
        return false;                     // нема єдиного розв'язку

    *x = (b1 * a22 - a12 * b2) / det;
    *y = (a11 * b2 - b1 * a21) / det;
    return true;
}
