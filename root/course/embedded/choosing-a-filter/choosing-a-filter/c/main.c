#include <stdint.h>

// медіана трьох останніх відліків (вбиває поодинокий спайк)
static float median3(float a, float b, float c) {
    float hi = a > b ? a : b;
    float lo = a > b ? b : a;       // lo ≤ hi
    if (c > hi) return hi;          // c найбільше → середнє = hi
    if (c < lo) return lo;          // c найменше → середнє = lo
    return c;                       // c між ними → середнє = c
}

float range_filter(float raw) {
    static float w0 = 0, w1 = 0, w2 = 0;   // вікно з 3 сирих відліків
    static float ema = 0;                  // стан EMA
    static int   primed = 0;               // чи заповнене вікно й EMA

    w2 = w1; w1 = w0; w0 = raw;            // зсунути вікно, новий — у w0
    float m = median3(w0, w1, w2);

    if (!primed) { ema = m; primed = 1; }  // перший відлік: без стрибка від нуля
    else         { ema += 0.3f * (m - ema); }   // EMA: новий = старий + α·(вхід − старий)
    return ema;
}
