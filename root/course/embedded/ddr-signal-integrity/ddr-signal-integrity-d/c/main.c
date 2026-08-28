// Псевдорегістри контролера DDR: ширина ока на байтову смугу (в кроках
// лінії затримки) після тренування читання. Перевіряємо, чи є запас.
#include <stdint.h>
#include <stdio.h>

#define DDR_TRAIN_EYE(lane)  (*(volatile uint32_t *)(0x4000C100u + (lane) * 4u))
#define EYE_STEP_PS          10u   // один крок лінії затримки ≈ 10 пс
#define EYE_MIN_PS           150u  // нижче — плата на межі, чекай збоїв

int ddr_eye_margin_ok(unsigned lanes) {
    int ok = 1;
    for (unsigned lane = 0; lane < lanes; lane++) {
        uint32_t steps = DDR_TRAIN_EYE(lane) & 0xFFu;
        uint32_t eye_ps = steps * EYE_STEP_PS;
        if (eye_ps < EYE_MIN_PS) {
            printf("DDR: смуга %u — вузьке око %u пс (<%u)\n",
                   lane, eye_ps, EYE_MIN_PS);
            ok = 0;
        }
    }
    return ok;   // 0 → плата на межі: перевір розведення й термінацію
}
