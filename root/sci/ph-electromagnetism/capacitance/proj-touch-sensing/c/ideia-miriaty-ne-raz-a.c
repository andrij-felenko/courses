#include <stdint.h>

#define N_CYCLES 200u     // скільки заряд–розрядів усереднюємо (N ~ 100…1000)
#define TIMEOUT  10000u   // стеля лічби — щоб не зависнути на обриві

// Апаратний шар (реалізація залежить від конкретного МК):
extern void pad_discharge(void);        // притиснути вивід майданчика до землі й витримати паузу
extern void pad_release(void);          // відпустити: майданчик заряджається через R до живлення
extern int  pad_above_threshold(void);  // 1, коли напруга перетнула логічний поріг входу

// Один сирий відлік: сумарна лічба тактів заряду за N циклів. Пропорційна ємності.
uint32_t raw_reading(void)
{
    uint32_t sum = 0;
    for (uint16_t i = 0; i < N_CYCLES; i++) {
        pad_discharge();                        // майданчик у нулі
        pad_release();                          // старт заряду через R
        uint16_t ticks = 0;
        while (!pad_above_threshold() && ticks < TIMEOUT)
            ticks++;                            // лічимо такти до порога
        sum += ticks;
    }
    return sum;                                 // ∝ C; випадковий шум поділено на √N
}
