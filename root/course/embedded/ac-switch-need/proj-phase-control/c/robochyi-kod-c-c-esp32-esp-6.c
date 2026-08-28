#include <math.h>

// Простий, ІНТУЇТИВНИЙ, але нелінійний за яскравістю варіант:
// відсоток прямо відображається в затримку. Годиться, коли лінійність не критична.
static uint32_t percent_to_delay_linear(uint8_t percent)
{
    if (percent >= 100) return DELAY_MIN_US;         // повна потужність
    if (percent == 0)   return DELAY_MAX_US;         // вимкнено
    // 0 % → максимальна затримка, 100 % → мінімальна
    uint32_t span = DELAY_MAX_US - DELAY_MIN_US;
    return DELAY_MAX_US - (span * percent) / 100;
}

// Правильний варіант: спершу знайти кут α, що дає задану частку потужності,
// потім перевести кут у затримку. Формулу P(α) обертаємо наближено (бісекція),
// бо аналітично вона не обертається.
static uint32_t percent_to_delay_true_power(uint8_t percent)
{
    if (percent >= 100) return DELAY_MIN_US;
    if (percent == 0)   return DELAY_MAX_US;

    float target = percent / 100.0f;                 // бажана P/Pmax
    float lo = 0.0f, hi = (float)M_PI;               // шукаємо α у [0, π]
    for (int i = 0; i < 20; i++) {                   // 20 ітерацій — з надлишком
        float a = 0.5f * (lo + hi);
        float p = (1.0f / M_PI) * ((M_PI - a) + 0.5f * sinf(2.0f * a));
        if (p > target) lo = a; else hi = a;         // P спадає зі зростанням α
    }
    float alpha = 0.5f * (lo + hi);
    // Кут → затримка: π радіан = HALF_PERIOD_US мкс
    uint32_t d = (uint32_t)(alpha / M_PI * HALF_PERIOD_US);

    // Затиснути в безпечні межі
    if (d < DELAY_MIN_US) d = DELAY_MIN_US;
    if (d > DELAY_MAX_US) d = DELAY_MAX_US;
    return d;
}

void phase_control_set_power(uint8_t percent)
{
    uint32_t delay = percent_to_delay_true_power(percent);

    g_fire_delay_us  = delay;         // обробник підхопить на наступному нулі
    g_output_enabled = (percent > 0); // 0 % — повністю зупинити імпульси
}
