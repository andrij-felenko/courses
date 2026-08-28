float gain = 1.0f;                 // поточне підсилення
const float target = 3000.0f;      // цільовий RMS (близько −20 dBFS від 32767)

void agc_process(int16_t *buf, int n) {
    float level = rms_level(buf, n) * gain;   // рівень ПІСЛЯ поточного підсилення
    if (level > 1.0f)                          // не ділити на нуль на тиші
        gain *= target / level;                // підтягнути підсилення до цілі
    for (int i = 0; i < n; i++) {
        int32_t y = (int32_t)(buf[i] * gain);
        if (y >  32767) y =  32767;            // насичення на краю
        if (y < -32768) y = -32768;
        buf[i] = (int16_t)y;
    }
}
