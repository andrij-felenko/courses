#include "vector_table_types.h"
#include <stdio.h>

extern vtm_status_t vtm_initialize(void);
extern vtm_status_t vtm_register_handler(int16_t irq_num, isr_vector_t new_handler, isr_vector_t *previous_handler);
extern vtm_status_t vtm_unregister_handler(int16_t irq_num);
extern uintptr_t vtm_get_sram_table_address(void);

#define DEMO_TIM3_IRQN          29
#define TIM3_SR_REGISTER_ADDR   0x40000410UL

static volatile uint32_t g_timer_events_count = 0;
static volatile bool g_mpu_violation_caught = false;

/* Динамічний обробник таймера TIM3 */
void dynamic_tim3_isr(void) {
    g_timer_events_count++;
    volatile uint32_t *tim3_sr = (volatile uint32_t*)TIM3_SR_REGISTER_ADDR;
    *tim3_sr = 0; /* Очищення прапорця переривання */
}

/* Обробник порушення захисту пам'яті MemManage */
void MemManage_Handler(void) {
    g_mpu_violation_caught = true;

    /* Скидання прапорця порушення в SCB->CFSR (MMFSR) */
    volatile uint32_t *cfsr = (volatile uint32_t*)0xE000ED28;
    *cfsr = 0xFF;

    /* Вихід з обробника */
}

int main(void) {
    /* 1. Ініціалізація динамічного менеджера векторів у SRAM */
    vtm_status_t status = vtm_initialize();
    if (status != VTM_STATUS_OK) {
        while (1) { __asm__ volatile ("bkpt #0"); }
    }

    /* 2. Реєстрація динамічного обробника для TIM3 */
    isr_vector_t original_isr = NULL;
    status = vtm_register_handler(DEMO_TIM3_IRQN, dynamic_tim3_isr, &original_isr);
    if (status != VTM_STATUS_OK) {
        while (1) { __asm__ volatile ("bkpt #0"); }
    }

    /* 3. Очікування обробки 500 подій переривань */
    while (g_timer_events_count < 500) {
        __asm__ volatile ("wfi");
    }

    /* 4. Тестування захисту MPU: пряма спроба затерти таблицю векторів */
    uintptr_t table_addr = vtm_get_sram_table_address();
    volatile uint32_t *raw_table_ptr = (volatile uint32_t*)table_addr;

    /* Цей запис має викликати MemManage Fault, оскільки MPU захищає таблицю як Read-Only */
    *raw_table_ptr = 0xDEADBEEFUL;

    /* 5. Відновлення заводського обробника */
    status = vtm_unregister_handler(DEMO_TIM3_IRQN);
    if (status != VTM_STATUS_OK) {
        while (1) { __asm__ volatile ("bkpt #0"); }
    }

    while (1) {
        __asm__ volatile ("wfi");
    }
}
