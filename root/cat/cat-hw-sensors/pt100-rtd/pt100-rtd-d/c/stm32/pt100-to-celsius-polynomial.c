#include <math.h>
#include <stdint.h>

// Константи рівняння Каллендара - Ван Дюзена
#define PT100_R0 100.0f
#define PT100_A  3.9083e-3f
#define PT100_B  -5.775e-7f

// Обчислення температури через аналітичне обернення квадратного рівняння (T >= 0 °C)
float pt100_to_celsius_polynomial(float r_measured) {
    if (r_measured < PT100_R0) {
        return (r_measured - PT100_R0) / (PT100_R0 * PT100_A);
    }
    float poly_c = 1.0f - (r_measured / PT100_R0);
    float discriminant = (PT100_A * PT100_A) - (4.0f * PT100_B * poly_c);
    return (-PT100_A + sqrtf(discriminant)) / (2.0f * PT100_B);
}
