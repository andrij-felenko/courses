#include <assert.h>
#include <stdlib.h>

void verify_equivalence(void) {
    set_calibration(2048, 3300, 4095);
    uint16_t buf[1024];
    // Прогнати на випадкових і на межових входах (0, макс 12 біт).
    for (int trial = 0; trial < 64; trial++) {
        for (int i = 0; i < 1024; i++)
            buf[i] = (trial == 0) ? 0
                   : (trial == 1) ? 4095
                   : (uint16_t)(rand() & 0x0FFF);
        float a = compute_rms_mA(buf, 1024);       // наївна — еталон
        float b = compute_rms_mA_fast(buf, 1024);  // швидка
        assert(fabsf(a - b) <= 0.5f);              // допуск: пів мА
    }
}
