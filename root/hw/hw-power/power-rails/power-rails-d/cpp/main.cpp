// Межі шин апарата (з даташитів і розрахунку дерева)
constexpr float VBAT_MIN_V  =  13.6f;  // 4S: ~3.4 В/комірку — час сідати
constexpr float I_MOTOR_MAX = 120.0f;  // стеля силової гілки, А (4×25 А + запас)
constexpr float V5_MIN_V    =   4.75f; // просадка 5 В нижче → логіка ненадійна

bool power_ok(float vbat, float i_total, float v5) {
    return vbat >= VBAT_MIN_V       // батарея ще тримає
        && i_total <= I_MOTOR_MAX   // не перевантажуємо силову гілку
        && v5 >= V5_MIN_V;          // логічна шина не просіла
}
