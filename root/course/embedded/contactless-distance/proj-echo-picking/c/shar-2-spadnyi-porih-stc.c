#include <stdint.h>

#define THR_MAX     3200      // поріг одразу після бланка (гучне близьке)
#define THR_MIN      280      // поріг наприкінці вікна (кволе далеке)
#define TIMEOUT_US  20000     // макс. час польоту (20 мс ≈ 3.4 м стелі)

// Спадний поріг STC у момент t (мкс від пуску): лінійно THR_MAX → THR_MIN.
static inline uint16_t stc_threshold(uint32_t t) {
    if (t >= TIMEOUT_US) return THR_MIN;
    // лінійна інтерполяція; множимо ДО ділення, щоб не втратити точність
    uint32_t span = (uint32_t)(THR_MAX - THR_MIN);
    return (uint16_t)(THR_MIN + span * (TIMEOUT_US - t) / TIMEOUT_US);
}
