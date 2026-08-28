// Інтегральна складова регулятора = ОП-інтегратор у прошивці.
// Накопичуємо похибку в часі, з обмеженням проти "розгону" (windup).
#include <algorithm>

static float integ = 0.0f;
constexpr float Ki  = 0.8f;
constexpr float dt  = 0.1f;     // крок інтегрування, с
constexpr float LIM = 50.0f;    // межа накопичення (аналог насичення схеми)

float integrator_step(float error)
{
    integ += Ki * error * dt;              // ∫: додаємо внесок за крок dt
    integ = std::clamp(integ, -LIM, LIM);  // не даємо накопиченню втекти у стелю
    return integ;
}
