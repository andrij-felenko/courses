// Стан у 32 бітах — зайві біти внизу гасять граничні цикли.
static int32_t x_prev = 0;   // попередній вхід, Q0 (цілий відлік)
static int64_t y_prev = 0;   // попередній вихід, Q16 (широкий, з дробовою частиною)

// a = 1 - alpha у форматі Q16; для alpha = 1/256: a = 65536 - 256 = 65280
static const int64_t A_Q16 = 65280;

void dc_block(int16_t *buf, int n) {
    for (int i = 0; i < n; i++) {
        int32_t x = buf[i];
        // y[n] = a*(y[n-1] + x[n] - x[n-1])
        int64_t inner = y_prev + (((int64_t)(x - x_prev)) << 16);  // усе в Q16
        y_prev = (A_Q16 * inner) >> 16;    // множення Q16*Q16 → зсув назад у Q16
        x_prev = x;
        int32_t y = (int32_t)(y_prev >> 16);   // назад у цілий відлік
        if (y >  32767) y =  32767;
        if (y < -32768) y = -32768;
        buf[i] = (int16_t)y;
    }
}
