#include "reset_cause.h"
#include "diag_out.h"

#include "stm32f4xx.h"   /* CMSIS: RCC, RCC_CSR_* */

/* У старіших заголовках STM32F1/F4 прапорець піна NRST зветься PADRSTF,
 * у нових — PINRSTF. Зводимо до одного імені, щоб таблиця нижче не залежала
 * від версії CMSIS-пакета. */
#ifndef RCC_CSR_PINRSTF
#define RCC_CSR_PINRSTF RCC_CSR_PADRSTF
#endif

static const struct diag_flag k_reset_flags[] = {
    { RCC_CSR_LPWRRSTF, "LPWRRSTF", "скидання з режиму низького споживання (Standby/Stop)" },
    { RCC_CSR_WWDGRSTF, "WWDGRSTF", "віконний сторож: оновлення поза дозволеним вікном" },
    { RCC_CSR_IWDGRSTF, "IWDGRSTF", "незалежний сторож: таймаут, код завис" },
    { RCC_CSR_SFTRSTF,  "SFTRSTF",  "програмне скидання (SYSRESETREQ / NVIC_SystemReset)" },
    { RCC_CSR_PORRSTF,  "PORRSTF",  "подача живлення або провал нижче порогу POR/PDR" },
    { RCC_CSR_PINRSTF,  "PINRSTF",  "зовнішній низький рівень на виводі NRST" },
    { RCC_CSR_BORRSTF,  "BORRSTF",  "детектор brown-out: напруга просіла нижче порогу" },
};

uint32_t reset_cause_read(void)
{
    /* RCC на STM32F4 живе в AHB1ENR-домені й тактується завжди — окремого
     * ввімкнення такту для читання CSR не треба. */
    return RCC->CSR;
}

void reset_cause_clear(void)
{
    RCC->CSR |= RCC_CSR_RMVF;

    /* RMVF самоочищається апаратно; знімаємо його явно, щоб наступне читання
     * CSR не показувало артефакт власного запису. */
    RCC->CSR &= ~RCC_CSR_RMVF;
}

void reset_cause_report(uint32_t csr)
{
    diag_puts("Причина скидання:\n");
    diag_reg("RCC->CSR", csr);

    const size_t n = sizeof k_reset_flags / sizeof k_reset_flags[0];
    if (diag_flags(k_reset_flags, n, csr) == 0u) {
        /* Порожній CSR — не помилка: хтось уже стер прапорці (наприклад,
         * завантажувач до нас) або відладчик підняв ядро без апаратного
         * скидання, і тоді жодне джерело не встигло відзначитись. */
        diag_puts("    * жодного прапорця: CSR уже очищено раніше\n");
    }

    /* Одночасно можуть стояти кілька бітів: PORRSTF і PINRSTF майже завжди
     * приходять парою, бо внутрішній супервізор смикає лінію NRST. Судимо за
     * найбільш «сильним» джерелом, а не за першим знайденим. */
    if (reset_cause_is_watchdog(csr)) {
        diag_puts("  => попередній прогін ЗАВИС (сторож), шукай нескінченний цикл\n");
    } else if (reset_cause_is_cold(csr)) {
        diag_puts("  => холодний старт: вміст RAM недійсний\n");
    } else if ((csr & RCC_CSR_SFTRSTF) != 0u) {
        diag_puts("  => перезапуск замовила сама прошивка\n");
    }
}

bool reset_cause_is_watchdog(uint32_t csr)
{
    return (csr & (RCC_CSR_IWDGRSTF | RCC_CSR_WWDGRSTF)) != 0u;
}

bool reset_cause_is_cold(uint32_t csr)
{
    return (csr & (RCC_CSR_PORRSTF | RCC_CSR_BORRSTF)) != 0u;
}
