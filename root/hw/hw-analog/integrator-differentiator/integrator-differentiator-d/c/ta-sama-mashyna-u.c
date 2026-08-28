// Інтегральна складова регулятора = ОП-інтегратор у прошивці.
// Накопичуємо похибку в часі, з обмеженням проти "розгону" (windup).
static float integ = 0.0f;
const float Ki  = 0.8f;
const float dt  = 0.1f;     // крок інтегрування, с
const float LIM = 50.0f;    // межа накопичення (аналог насичення схеми)

float integrator_step(float error)
{
    integ += Ki * error * dt;          // ∫: додаємо внесок за крок dt
    if (integ >  LIM) integ =  LIM;    // не даємо накопиченню втекти у стелю
    if (integ < -LIM) integ = -LIM;
    return integ;
}
