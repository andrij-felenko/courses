#include <math.h>

/* Опорна потужність шкали (наприклад, мінімум чутливості). */
static const float P_REF   = 1.0f;
/* Дно шкали, коли сигналу фактично немає (lg(0) = −∞). */
static const float DB_FLOOR = -120.0f;

/* Рівень потужності P у децибелах відносно P_REF. */
float power_to_db(float p)
{
    if (p <= 0.0f) {
        return DB_FLOOR;          /* логарифм нуля/від'ємного не існує */
    }
    return 10.0f * log10f(p / P_REF);
}
