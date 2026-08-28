#define PPR  1024                 // щілин на диску (з паспорта енкодера)
#define CPR  (4 * PPR)            // кроків на оберт після квадратури = 4096

// Поточний кут вала в градусах (0..360), із прив'язкою до мітки Z.
float encoder_angle_deg(void) {
    int32_t c = position % CPR;            // лишок у межах одного оберту
    if (c < 0) c += CPR;                   // тримаємо в [0, CPR)
    return (360.0f * c) / CPR;             // частка оберту → градуси
}

// Швидкість в обертах за хвилину за період dt_ms між двома вимірами.
// Викликати періодично; pos_now — знімок position на цей момент.
float encoder_rpm(int32_t pos_now, int32_t pos_prev, float dt_ms) {
    int32_t dcounts = pos_now - pos_prev;          // скільки кроків за dt
    float rev = (float)dcounts / CPR;              // у обертах
    return rev * (60000.0f / dt_ms);               // об/хв (60000 мс = 1 хв)
}
