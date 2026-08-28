#include <stdint.h>
#include <string.h>

#define NSTAGE 6                 // щаблів «1.5 біта»
#define NBITS  (NSTAGE + 2)      // повний код = 8 розрядів (6 щаблів + 2-бітний хвіст)
#define LAT    (NSTAGE - 1)      // затримка вирівнювання, тактів (найглибша черга)

// Один щабель «1.5 біта»: пороги ±Vref/4, три цифри D∈{0,1,2}.
// Повертає цифру, а через vres — залишок = 2·Vвх − (D−1)·Vref (той самий формат Q15).
static uint8_t stage_15bit(int32_t vin_q15, int32_t offset_q15, int32_t *vres_q15) {
    const int32_t VREF = 1 << 15;                 // 1.0 у Q15
    int32_t t_lo = -(VREF >> 2) + offset_q15;     // −Vref/4 (+ зсув компаратора)
    int32_t t_hi =  (VREF >> 2) + offset_q15;     // +Vref/4
    uint8_t d = (vin_q15 < t_lo) ? 0 : (vin_q15 < t_hi) ? 1 : 2;
    *vres_q15 = 2 * vin_q15 - (int32_t)(d - 1) * VREF;   // −Vref, 0 або +Vref, тоді ×2
    return d;
}
