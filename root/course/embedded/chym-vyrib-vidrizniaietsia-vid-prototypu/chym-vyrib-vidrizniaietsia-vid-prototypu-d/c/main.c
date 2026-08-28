#include <stdint.h>
#include <stdbool.h>

/* Реєстр прапорців збереженого стану в Retained RAM (не затирається при рестарті) */
typedef struct {
    uint32_t boot_count;
    uint32_t last_reset_reason;
    uint32_t hardfault_pc;
    uint16_t checksum;
} retain_crash_log_t;

__attribute__((section(".retained_ram"))) 
static retain_crash_log_t g_crash_log;

/* Апаратний перехід виконавчих органів у безпечний стан */
void hardware_enter_safe_state(void) {
    /* 1. Миттєво вимикаємо всі силові ШІМ-генератори та драйвери мостів */
    // TIM1->BDTR &= ~TIM_BDTR_MOE; // Примусове апаратне вимкнення виходів
    
    /* 2. Переводимо лінії керування нагрівачами й клапанами у вхід з підтяжкою до землі */
    // GPIOA->MODER &= ~(GPIO_MODER_MODE5_Msk | GPIO_MODER_MODE6_Msk);
}

/* Обробник критичного збою з фіксацією діагностики */
void application_panic_handler(uint32_t reason, uint32_t pc) {
    hardware_enter_safe_state();

    g_crash_log.boot_count++;
    g_crash_log.last_reset_reason = reason;
    g_crash_log.hardfault_pc = pc;
    g_crash_log.checksum = (uint16_t)(g_crash_log.boot_count ^ reason ^ pc);

    /* Примусовий перезапуск через сторожовий таймер або системний запит */
    // NVIC_SystemReset();
    while (1) {
        /* Очікування скидання сторожем */
    }
}
