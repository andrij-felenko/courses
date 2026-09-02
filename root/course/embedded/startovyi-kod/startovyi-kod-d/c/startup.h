#ifndef STARTUP_H
#define STARTUP_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Вирівнювання таблиці векторів. Cortex-M вимагає щонайменше 128 байтів
   і не менше за розмір самої таблиці, округлений угору до степеня двійки.
   У нас 59 векторів × 4 = 236 байтів, тож беремо 512 із запасом. */
#define VECTOR_TABLE_ALIGN 512U

/* Символи, які розставляє скрипт лінкера. Значення в них не має сенсу —
   сенс має АДРЕСА символу, тому всюди беремо &. */
extern uint32_t _estack; /* вершина стека: остання адреса RAM + 1 */
extern uint32_t _sidata; /* образ .data у Flash (LMA) */
extern uint32_t _sdata;  /* початок .data у RAM (VMA) */
extern uint32_t _edata;  /* кінець .data у RAM  */
extern uint32_t _sbss;   /* початок .bss у RAM  */
extern uint32_t _ebss;   /* кінець .bss у RAM   */

typedef void (*vector_handler_t)(void);

/* Сама таблиця векторів; на неї ж наводимо VTOR */
extern const vector_handler_t g_pfnVectors[];

/* Фази стартового коду — порядок виклику задає Reset_Handler */
bool startup_relocate_vectors(const void *table_base);
void startup_init_memory(void);
bool startup_enable_fpu(void);
void startup_run_init_array(void);
_Noreturn void startup_trap(void);

/* Тактування: справжня частота ядра після SystemInit() */
extern uint32_t SystemCoreClock;
bool SystemInit(void);

int main(void);

/* Системні вектори ядра Cortex-M */
void Reset_Handler(void);
void Default_Handler(void);
void NMI_Handler(void);
void HardFault_Handler(void);
void MemManage_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);
void SVC_Handler(void);
void DebugMon_Handler(void);
void PendSV_Handler(void);
void SysTick_Handler(void);

/* Вектори периферії STM32F4, позиції NVIC 0…42, суворо в порядку заліза.
   X-макрос розкривається тричі: в оголошення, у слабкі синоніми
   (handlers.c) і в саму таблицю (vectors.c) — щоб той самий перелік
   не розповзся по трьох файлах у трьох різних редакціях. */
#define MCU_IRQ_VECTORS(X)           \
    X(WWDG_IRQHandler)               \
    X(PVD_IRQHandler)                \
    X(TAMP_STAMP_IRQHandler)         \
    X(RTC_WKUP_IRQHandler)           \
    X(FLASH_IRQHandler)              \
    X(RCC_IRQHandler)                \
    X(EXTI0_IRQHandler)              \
    X(EXTI1_IRQHandler)              \
    X(EXTI2_IRQHandler)              \
    X(EXTI3_IRQHandler)              \
    X(EXTI4_IRQHandler)              \
    X(DMA1_Stream0_IRQHandler)       \
    X(DMA1_Stream1_IRQHandler)       \
    X(DMA1_Stream2_IRQHandler)       \
    X(DMA1_Stream3_IRQHandler)       \
    X(DMA1_Stream4_IRQHandler)       \
    X(DMA1_Stream5_IRQHandler)       \
    X(DMA1_Stream6_IRQHandler)       \
    X(ADC_IRQHandler)                \
    X(CAN1_TX_IRQHandler)            \
    X(CAN1_RX0_IRQHandler)           \
    X(CAN1_RX1_IRQHandler)           \
    X(CAN1_SCE_IRQHandler)           \
    X(EXTI9_5_IRQHandler)            \
    X(TIM1_BRK_TIM9_IRQHandler)      \
    X(TIM1_UP_TIM10_IRQHandler)      \
    X(TIM1_TRG_COM_TIM11_IRQHandler) \
    X(TIM1_CC_IRQHandler)            \
    X(TIM2_IRQHandler)               \
    X(TIM3_IRQHandler)               \
    X(TIM4_IRQHandler)               \
    X(I2C1_EV_IRQHandler)            \
    X(I2C1_ER_IRQHandler)            \
    X(I2C2_EV_IRQHandler)            \
    X(I2C2_ER_IRQHandler)            \
    X(SPI1_IRQHandler)               \
    X(SPI2_IRQHandler)               \
    X(USART1_IRQHandler)             \
    X(USART2_IRQHandler)             \
    X(USART3_IRQHandler)             \
    X(EXTI15_10_IRQHandler)          \
    X(RTC_Alarm_IRQHandler)          \
    X(OTG_FS_WKUP_IRQHandler)

#define MCU_DECLARE_HANDLER(name) void name(void);
MCU_IRQ_VECTORS(MCU_DECLARE_HANDLER)
#undef MCU_DECLARE_HANDLER

#endif /* STARTUP_H */
