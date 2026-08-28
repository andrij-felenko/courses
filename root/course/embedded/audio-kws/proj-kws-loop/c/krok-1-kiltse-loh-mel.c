#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define N_FRAMES  49     // стовпчиків у секундному вікні (= вхід моделі по часу)
#define N_MEL     40     // лог-мел-смуг у стовпчику (= вхід моделі по частоті)
#define N_CLASS    8     // виходів моделі: команди + «чуже» + «тиша»

// Кільце лог-мел-стовпчиків. Числа з комою, у своїх одиницях (ще НЕ квантовані).
static float ring[N_FRAMES][N_MEL];
static int   head  = 0;    // куди ляже НАСТУПНИЙ стовпчик (він же — найстаріший зараз)
static int   fill  = 0;    // скільки комірок уже заповнено (для «холодного» старту)

// Кладе один свіжий лог-мел-стовпчик у кільце, затираючи найстаріший.
// Викликати на КОЖЕН новий стовпчик з аудіотракту (≈ раз на 20 мс).
static void ring_push(const float col[N_MEL]) {
    memcpy(ring[head], col, N_MEL * sizeof(float));   // перезапис однієї комірки
    head = (head + 1) % N_FRAMES;                     // вказівник по колу
    if (fill < N_FRAMES) fill++;                       // рахуємо, доки кільце не повне
}
