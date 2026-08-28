#include <math.h>

// Довжини — міліметри, час — секунди.
#define LAMBDA_SI  0.1f      // теплопровідність кремнію, Вт/(мм·К)
#define A_SI       55.0f     // температуропровідність кремнію, мм²/с

// Час, за який підсилення петлі доростає до одиниці:
//   M(t) = U_DS · (dJ/dT) · (2/λ) · sqrt(a·t/π) = k·sqrt(t) = 1
float t_crit(float U_DS, float dJdT)   // В, А/(К·мм²)
{
    float k = U_DS * dJdT * (2.0f / LAMBDA_SI) * sqrtf(A_SI / 3.14159f);
    return 1.0f / (k * k);             // секунди
}

float delta(float t) { return sqrtf(A_SI * t); }   // глибина прогріву, мм

// t_crit(20.0f,  0.002f) = 0.089 с  → пляма delta = 2.2 мм
// t_crit(50.0f,  0.002f) = 0.014 с  → пляма delta = 0.89 мм
// t_crit(100.0f, 0.002f) = 0.0036 с → пляма delta = 0.44 мм
