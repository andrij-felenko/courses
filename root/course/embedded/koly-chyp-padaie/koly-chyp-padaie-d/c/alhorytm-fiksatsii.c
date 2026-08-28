#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef enum {
    RESET_CAUSE_UNKNOWN      = 0,
    RESET_CAUSE_POWER_ON     = (1 << 0),
    RESET_CAUSE_BROWNOUT     = (1 << 1),
    RESET_CAUSE_PIN_RESET    = (1 << 2),
    RESET_CAUSE_WATCHDOG_I   = (1 << 3),
    RESET_CAUSE_WATCHDOG_W   = (1 << 4),
    RESET_CAUSE_SOFTWARE     = (1 << 5),
    RESET_CAUSE_LOW_POWER    = (1 << 6)
} ResetCause_t;

ResetCause_t System_CaptureResetCause(void) {
    uint32_t csr = RCC->CSR;
    ResetCause_t cause = RESET_CAUSE_UNKNOWN;

    if (csr & RCC_CSR_LPWRRSTF) cause |= RESET_CAUSE_LOW_POWER;
    if (csr & RCC_CSR_WWDGRSTF) cause |= RESET_CAUSE_WATCHDOG_W;
    if (csr & RCC_CSR_IWDGRSTF) cause |= RESET_CAUSE_WATCHDOG_I;
    if (csr & RCC_CSR_SFTRSTF)  cause |= RESET_CAUSE_SOFTWARE;
    if (csr & RCC_CSR_PORRSTF)  cause |= RESET_CAUSE_POWER_ON;
    if (csr & RCC_CSR_PINRSTF)  cause |= RESET_CAUSE_PIN_RESET;
    if (csr & RCC_CSR_BORRSTF)  cause |= RESET_CAUSE_BROWNOUT;

    // Обов'язкове очищення прапорців: запис 1 у біт RMVF
    RCC->CSR |= RCC_CSR_RMVF;

    return cause;
}
