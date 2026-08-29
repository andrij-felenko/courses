#include "reset_cause.h"

#include "trace.h"
#include "stm32f4xx.h"

typedef struct {
    uint32_t    csr_bit; /* апаратний біт у RCC->CSR */
    uint32_t    src;     /* наш прапорець RESET_SRC_* */
    const char *name;
} reset_bit_t;

/*
 * Порядок навмисний: від найцікавішого для розслідування до найбуденнішого.
 * PORRSTF стоїть наприкінці, бо після холодного старту він горить завжди
 * і сам собою нічого не пояснює.
 */
static const reset_bit_t k_reset_bits[] = {
    { RCC_CSR_IWDGRSTF, RESET_SRC_IWDG,      "IWDGRSTF  незалежний сторож: програма зависла" },
    { RCC_CSR_WWDGRSTF, RESET_SRC_WWDG,      "WWDGRSTF  віконний сторож: порушено таймінг" },
    { RCC_CSR_SFTRSTF,  RESET_SRC_SOFTWARE,  "SFTRSTF   програмне скидання (SYSRESETREQ)" },
    { RCC_CSR_BORRSTF,  RESET_SRC_BROWNOUT,  "BORRSTF   просідання живлення нижче порогу" },
    { RCC_CSR_LPWRRSTF, RESET_SRC_LOW_POWER, "LPWRRSTF  збій виходу з режиму низького споживання" },
    { RCC_CSR_PINRSTF,  RESET_SRC_PIN,       "PINRSTF   зовнішній сигнал на піні NRST" },
    { RCC_CSR_PORRSTF,  RESET_SRC_POWER_ON,  "PORRSTF   холодний старт (подача живлення)" }
};

#define RESET_BIT_COUNT (sizeof(k_reset_bits) / sizeof(k_reset_bits[0]))

static uint32_t s_mask;
static uint32_t s_raw_csr;
static bool     s_captured;

uint32_t reset_cause_capture(void)
{
    if (s_captured) {
        return s_mask; /* прапорці вже стерті — апаратуру перепитувати марно */
    }

    const uint32_t csr  = RCC->CSR;
    uint32_t       mask = 0u;

    for (uint32_t i = 0u; i < RESET_BIT_COUNT; ++i) {
        if ((csr & k_reset_bits[i].csr_bit) != 0u) {
            mask |= k_reset_bits[i].src;
        }
    }

    /*
     * Стираємо липкі прапорці одразу після зчитування. Інакше PORRSTF від
     * найпершого ввімкнення на заводі житиме роками й змішається з реальною
     * причиною завтрашньої аварії в полі.
     */
    RCC->CSR |= RCC_CSR_RMVF;
    __DSB();

    s_raw_csr  = csr;
    s_mask     = mask;
    s_captured = true;
    return mask;
}

uint32_t reset_cause_last(void)
{
    return s_mask;
}

uint32_t reset_cause_raw_csr(void)
{
    return s_raw_csr;
}

void reset_cause_print(uint32_t mask)
{
    trace_kv("RCC->CSR", s_raw_csr);

    if (mask == 0u) {
        /*
         * Жодного відомого біта. Найчастіше це означає, що прапорці вже
         * стер хтось інший — стартовий код виробника чи попередній запуск.
         */
        trace_str("причина скидання: невідома (прапорці вже стерті)\r\n");
        return;
    }

    for (uint32_t i = 0u; i < RESET_BIT_COUNT; ++i) {
        if ((mask & k_reset_bits[i].src) != 0u) {
            trace_str("  * ");
            trace_str(k_reset_bits[i].name);
            trace_str("\r\n");
        }
    }
}

bool reset_cause_is_crash(uint32_t mask)
{
    return (mask & (RESET_SRC_IWDG | RESET_SRC_WWDG | RESET_SRC_SOFTWARE)) != 0u;
}
