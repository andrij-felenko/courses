typedef struct { uint32_t last_us; bool healthy; } SensorHealth;
static SensorHealth baro_health;

// Корекція висоти барометром — осаджує ЛИШЕ вертикальний зріз стану.
static void correct_altitude(State *x, const BaroSample *baro, uint32_t now_us)
{
    float innov = baro->alt - x->alt;      // інновація: вимір - передбачення
    float S     = x->P_alt + baro->var;    // дисперсія інновації = хмара + шум давача

    if (innov * innov > 25.0f * S)         // брама: викид далі 5 сигм (5^2 = 25) — відкинути
        return;                            // «глітч» до стану не потрапляє

    float K  = x->P_alt / S;               // підсилення: хмара проти шуму барометра
    x->alt  += K * innov;                  // висоту підтягуємо до виміру
    x->P_alt = (1.0f - K) * x->P_alt;      // хмара висоти стискається

    baro_health.last_us = now_us;          // відлік прийнято — давач живий
    baro_health.healthy = true;
}
