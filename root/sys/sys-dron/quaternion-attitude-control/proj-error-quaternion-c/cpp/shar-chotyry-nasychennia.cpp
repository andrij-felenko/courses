#define THR_MIN 0.0f
#define THR_MAX 1.0f

// затиснути команди моторів, зберігши напрямок сумарного моменту
void saturate_preserve(float motor[N_MOTORS]) {
    float hi = motor[0], lo = motor[0];
    for (int i = 1; i < N_MOTORS; ++i) {
        if (motor[i] > hi) hi = motor[i];
        if (motor[i] < lo) lo = motor[i];
    }
    // якщо розмах вилазить за [MIN,MAX] — стиснути всі до одного масштабу
    float span = hi - lo;
    float room = THR_MAX - THR_MIN;
    if (span > room && span > 1e-6f) {
        float scale = room / span;
        for (int i = 0; i < N_MOTORS; ++i)
            motor[i] = (motor[i] - lo) * scale + THR_MIN;
    } else {
        // просто підняти/опустити в діапазон, не міняючи різниць
        float shift = 0.0f;
        if (lo < THR_MIN) shift = THR_MIN - lo;
        else if (hi > THR_MAX) shift = THR_MAX - hi;
        for (int i = 0; i < N_MOTORS; ++i) motor[i] += shift;
    }
}
