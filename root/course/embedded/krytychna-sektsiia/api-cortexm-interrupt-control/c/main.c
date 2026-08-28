#include "cmsis_compiler.h"
#include <stdint.h>
#include <stdbool.h>

/*
 * Приклад опитування та безпечного маскування переривань через CMSIS
 */
void cmsis_demonstration(void) {
    /* 1. Глобальне маскування через PRIMASK */
    uint32_t saved_primask = __get_PRIMASK();
    __disable_irq();
    
    // Перевірка, чи активні переривання в системі
    bool interrupts_were_enabled = (saved_primask == 0U);
    (void)interrupts_were_enabled;
    
    __set_PRIMASK(saved_primask); // Точне відновлення

    /* 2. Селективне маскування через BASEPRI (лише Cortex-M3/M4/M7/M33) */
#if (__CORTEX_M >= 3U)
    uint32_t saved_basepri = __get_BASEPRI();
    
    // Маскуємо переривання з пріоритетом 4 і нижче (0x40 для 4 біт NVIC)
    __set_BASEPRI(0x40U);
    
    // Безпечне вкладене маскування
    __set_BASEPRI_MAX(0x20U); // Підвищуємо поріг до пріоритету 2
    
    __set_BASEPRI(saved_basepri); // Відновлюємо початковий стан
#endif

    /* 3. Перевірка контексту виконання */
    uint32_t active_exception = __get_IPSR();
    if (active_exception == 0U) {
        // Код виконується у фоновому потоці (Thread Mode / main / RTOS task)
    } else {
        // Код виконується всередині ISR з номером active_exception
    }
}
