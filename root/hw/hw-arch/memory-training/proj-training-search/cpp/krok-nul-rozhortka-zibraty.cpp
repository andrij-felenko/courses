constexpr int RANGE_MAX = 64;    // скільки кодів у ручки (0 .. RANGE_MAX-1)

// Заповнює map[i] результатом пробника за коду затримки i.
// Повертає кількість зібраних точок (== RANGE_MAX).
int sweep(bool map[], int range_max)
{
    for (int code = 0; code < range_max; code++) {
        knob_set(code);          // виставили ручку
        settle();                // пауза на встановлення лінії затримки
        map[code] = probe_once();
    }
    return range_max;
}
