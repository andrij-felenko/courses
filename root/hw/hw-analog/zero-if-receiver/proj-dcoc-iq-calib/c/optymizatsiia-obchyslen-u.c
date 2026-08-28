#include <stdint.h>

/* Стан фільтра DCOC Q15 */
typedef struct {
    int32_t acc_i;
    int32_t acc_q;
    uint8_t shift_k;
} dcoc_q15_t;

void dcoc_q15_init(dcoc_q15_t *dcoc, uint8_t shift_k) {
    dcoc->acc_i = 0;
    dcoc->acc_q = 0;
    dcoc->shift_k = shift_k;
}

/* Кроковий обчислювач DCOC у форматі Q15 */
void dcoc_q15_process(dcoc_q15_t *dcoc, int16_t *i_buf, int16_t *q_buf, size_t count) {
    const uint8_t k = dcoc->shift_k;

    for (size_t n = 0; n < count; ++n) {
        dcoc->acc_i += (int32_t)i_buf[n] - (dcoc->acc_i >> k);
        dcoc->acc_q += (int32_t)q_buf[n] - (dcoc->acc_q >> k);

        i_buf[n] -= (int16_t)(dcoc->acc_i >> k);
        q_buf[n] -= (int16_t)(dcoc->acc_q >> k);
    }
}
