#include <cmath>

// Показник Пойкерта з двох вимірів (I1,t1) і (I2,t2) — часи до відсічки.
// Бери струми близько робочого діапазону, НЕ біля паспортного C/20,
// якщо апарат працює на великому струмі.
float peukert_k_from_two(float i1, float t1, float i2, float t2)
{
    // k = ln(t1/t2) / ln(i2/i1)   — виведено з I1^k·t1 = I2^k·t2
    return std::log(t1 / t2) / std::log(i2 / i1);
}
