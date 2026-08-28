// Ті самі межі: нижче ~150 Гц KY-006 ледь чутний, найдзвінкіше — коло 2 кГц.
#define TONE_MIN_HZ  200
#define TONE_MAX_HZ  2000

// Готової map()/constrain() тут немає — пропорція й затиск пишуться в рядок.
static int32_t map_i(int32_t x, int32_t inMin, int32_t inMax,
                     int32_t outMin, int32_t outMax)
{
    return (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}
static int32_t clamp_i(int32_t x, int32_t lo, int32_t hi)
{
    return x < lo ? lo : (x > hi ? hi : x);
}

// Заспівати значення value з діапазону [valMin; valMax].
// invert=true → більше значення дає НИЖЧИЙ тон (як паркрадар: ближче → вище).
void sonify(int32_t value, int32_t valMin, int32_t valMax, bool invert)
{
    value = clamp_i(value, valMin, valMax);   // ← 1) затиснути в межі ОБОВ'ЯЗКОВО
    int32_t f = invert
        ? map_i(value, valMin, valMax, TONE_MAX_HZ, TONE_MIN_HZ)
        : map_i(value, valMin, valMax, TONE_MIN_HZ, TONE_MAX_HZ);
    buzzerTone((uint32_t)f);   // тон «їздить» за значенням; buzzerOff() коли не треба
}

void app_main(void)
{
    buzzerBegin();
    while (1) {
        buzzerUpdate();
        int32_t dist = read_distance_cm();       // напр. 5…100 см
        sonify(dist, 5, 100, /*invert=*/true);   // ближче стіна → вищий писк
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
