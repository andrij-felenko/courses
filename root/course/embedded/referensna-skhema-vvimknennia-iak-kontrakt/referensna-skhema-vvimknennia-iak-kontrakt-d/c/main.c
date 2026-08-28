// Діагностика джерела скидання та захист тактування (C99, CMSIS / STM32)
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    RESET_CAUSE_UNKNOWN = 0,
    RESET_CAUSE_LOW_POWER_RESET,
    RESET_CAUSE_WINDOW_WATCHDOG,
    RESET_CAUSE_INDEPENDENT_WATCHDOG,
    RESET_CAUSE_SOFTWARE_RESET,
    RESET_CAUSE_POWER_ON_RESET,
    RESET_CAUSE_EXTERNAL_PIN_RESET,
    RESET_CAUSE_BROWNOUT_RESET
} mcu_reset_cause_t;

// Зчитування та очищення прапорців регістру керування скиданням (RCC_CSR)
mcu_reset_cause_t mcu_get_and_clear_reset_cause(void) {
    mcu_reset_cause_t cause = RESET_CAUSE_UNKNOWN;
    
    // Припустимо читання регістру CSR контролера тактування (RCC->CSR)
    uint32_t csr = 0x2C000000; // Показове значення регістру RCC_CSR

    #define RCC_CSR_LPWRRSTF (1UL << 31)
    #define RCC_CSR_WWDGRSTF (1UL << 30)
    #define RCC_CSR_IWDGRSTF (1UL << 29)
    #define RCC_CSR_SFTRSTF  (1UL << 28)
    #define RCC_CSR_PORRSTF  (1UL << 27)
    #define RCC_CSR_PINRSTF  (1UL << 26)
    #define RCC_CSR_BORRSTF  (1UL << 25)

    if (csr & RCC_CSR_LPWRRSTF) {
        cause = RESET_CAUSE_LOW_POWER_RESET;
    } else if (csr & RCC_CSR_WWDGRSTF) {
        cause = RESET_CAUSE_WINDOW_WATCHDOG;
    } else if (csr & RCC_CSR_IWDGRSTF) {
        cause = RESET_CAUSE_INDEPENDENT_WATCHDOG;
    } else if (csr & RCC_CSR_SFTRSTF) {
        cause = RESET_CAUSE_SOFTWARE_RESET;
    } else if (csr & RCC_CSR_PORRSTF) {
        cause = RESET_CAUSE_POWER_ON_RESET;
    } else if (csr & RCC_CSR_BORRSTF) {
        cause = RESET_CAUSE_BROWNOUT_RESET;
    } else if (csr & RCC_CSR_PINRSTF) {
        cause = RESET_CAUSE_EXTERNAL_PIN_RESET;
    }

    // Скидання прапорців стану для наступного циклу
    // RCC->CSR |= RCC_CSR_RMVF;
    return cause;
}

// Обробник переривання системи безпеки тактування (Clock Security System NMI Handler)
void NMI_Handler(void) {
    // Якщо спрацювала система CSS: зовнішній кварц HSE зірвав генерацію
    // Апаратна частина МК автоматично перемкнула тактування на внутрішній HSI
    
    // Перевірка прапорця CSS у регістрі RCC_CIR / RCC_CIFR
    bool css_failure = true; // Імітація перевірки біта CSSF

    if (css_failure) {
        // Аварійне переведення виконавчих пристроїв (моторів, реле) у безпечний стан
        // Збереження діагностичного коду помилки в енергонезалежну пам'ять
        // Спроба перезапуску або аварійна сигналізація
        while (1) {
            // Безпечний аварійний цикл
        }
    }
}
