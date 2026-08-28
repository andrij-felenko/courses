#include <cmath>

// Власна частота пружинного маятника, що його моделює машина.
// k — жорсткість (Н/м), m — маса (кг); повертає рад/с.
float spring_omega(float k, float m)
{
    return std::sqrt(k / m);      // ω = √(k/m)
}

// Масштаб блоку зворотного зв'язку k/m задаємо відношенням резисторів R_fb/R_in.
float feedback_gain(float k, float m)
{
    return k / m;                 // напр. 8/2 = 4  → R_fb : R_in = 4 : 1
}
// spring_omega(8, 2) -> 2.0 рад/с;  feedback_gain(8, 2) -> 4.0
