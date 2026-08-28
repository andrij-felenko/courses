// Порогові значення — з фізики апарата (тут як приклад типових величин).
#define LAND_VZ_MAX_CMS      50      // |верт. швидкість| < 0.5 м/с — «нерухомо по вертикалі»
#define LAND_ACC_MAX_CMS2    100     // збурення прискорення < 1 м/с² — «не трясе»
#define LAND_HOLD_TICKS      50      // умови мусять протриматись 50 тактів поспіль
//                                      (при 50 Гц це рівно 1 секунда)

// true — ЛИШЕ якщо всі ознаки посадки протрималися LAND_HOLD_TICKS тактів підряд.
// Один зрив будь-якої ознаки скидає лік у нуль (пружний підскок нас не обдурить).
bool land_detected(void) {
    static uint16_t stable = 0;      // скільки тактів поспіль «схоже на землю»

    // Три незалежні ознаки того, що апарат СТОЇТЬ на землі:
    bool low_thrust  = throttle_out() <= throttle_min();      // контур уже не тримає
    bool no_vspeed   = abs_i(climb_rate_cms()) < LAND_VZ_MAX_CMS;   // не лізе й не падає
    bool still       = accel_disturb_cms2() < LAND_ACC_MAX_CMS2;    // не трясе / не обдуває

    if (low_thrust && no_vspeed && still) {
        if (stable < LAND_HOLD_TICKS)
            stable++;                // ще один тихий такт — присуваємось до впевненості
    } else {
        stable = 0;                  // ХОЧ ОДНА ознака зірвалась → лік з нуля
    }

    return stable >= LAND_HOLD_TICKS;   // впевнені лише коли витримали всі N тактів
}
