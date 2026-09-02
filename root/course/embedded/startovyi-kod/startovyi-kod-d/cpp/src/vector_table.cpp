#include "mcu/vector_table.hpp"

namespace {
/* Зарезервовані архітектурою місця лишаються порожніми */
constexpr mcu::vector_entry reserved{.handler = nullptr};
}

/* Секцію на початок образу кладе скрипт лінкера рядком
   KEEP(*(.isr_vector)), `used` не дає викинути символ, на який ніхто не
   посилається з коду, а `constinit` — це перевірка компілятором: якщо
   хоч один запис не є константним виразом, збірка стане тут, а не
   перетвориться на мовчазну динамічну ініціалізацію. */
extern "C"
[[gnu::section(".isr_vector"), gnu::used, gnu::aligned(mcu::vector_table_align)]]
constinit const std::array<mcu::vector_entry, mcu::vector_count> g_vector_table = {{
    {.stack_top = &_estack},      /* 0x00: початкове значення MSP */
    {.handler = Reset_Handler},   /* 0x04: точка входу стартового коду */
    {.handler = NMI_Handler},     /* 0x08: збій кварцу, аварія живлення */
    {.handler = HardFault_Handler},  /* 0x0C: критичний системний збій */
    {.handler = MemManage_Handler},  /* 0x10: порушення правил MPU */
    {.handler = BusFault_Handler},   /* 0x14: помилка шини */
    {.handler = UsageFault_Handler}, /* 0x18: INVSTATE, NOCP, ділення на 0 */
    reserved, reserved, reserved, reserved, /* 0x1C…0x28 */
    {.handler = SVC_Handler},     /* 0x2C: системний виклик */
    {.handler = DebugMon_Handler},/* 0x30: монітор налагодження */
    reserved,                     /* 0x34 */
    {.handler = PendSV_Handler},  /* 0x38: відкладене перемикання задач */
    {.handler = SysTick_Handler}, /* 0x3C: системний таймер */

    /* 0x40 і далі: переривання периферії, позиції NVIC 0…42. Решта
       векторів STM32F407 (43…81) тут не перелічена — жодне з тих
       переривань у прикладі не вмикається, а NVIC читає запис лише
       для дозволеного переривання. */
    {.handler = WWDG_IRQHandler},
    {.handler = PVD_IRQHandler},
    {.handler = TAMP_STAMP_IRQHandler},
    {.handler = RTC_WKUP_IRQHandler},
    {.handler = FLASH_IRQHandler},
    {.handler = RCC_IRQHandler},
    {.handler = EXTI0_IRQHandler},
    {.handler = EXTI1_IRQHandler},
    {.handler = EXTI2_IRQHandler},
    {.handler = EXTI3_IRQHandler},
    {.handler = EXTI4_IRQHandler},
    {.handler = DMA1_Stream0_IRQHandler},
    {.handler = DMA1_Stream1_IRQHandler},
    {.handler = DMA1_Stream2_IRQHandler},
    {.handler = DMA1_Stream3_IRQHandler},
    {.handler = DMA1_Stream4_IRQHandler},
    {.handler = DMA1_Stream5_IRQHandler},
    {.handler = DMA1_Stream6_IRQHandler},
    {.handler = ADC_IRQHandler},
    {.handler = CAN1_TX_IRQHandler},
    {.handler = CAN1_RX0_IRQHandler},
    {.handler = CAN1_RX1_IRQHandler},
    {.handler = CAN1_SCE_IRQHandler},
    {.handler = EXTI9_5_IRQHandler},
    {.handler = TIM1_BRK_TIM9_IRQHandler},
    {.handler = TIM1_UP_TIM10_IRQHandler},
    {.handler = TIM1_TRG_COM_TIM11_IRQHandler},
    {.handler = TIM1_CC_IRQHandler},
    {.handler = TIM2_IRQHandler},
    {.handler = TIM3_IRQHandler},
    {.handler = TIM4_IRQHandler},
    {.handler = I2C1_EV_IRQHandler},
    {.handler = I2C1_ER_IRQHandler},
    {.handler = I2C2_EV_IRQHandler},
    {.handler = I2C2_ER_IRQHandler},
    {.handler = SPI1_IRQHandler},
    {.handler = SPI2_IRQHandler},
    {.handler = USART1_IRQHandler},
    {.handler = USART2_IRQHandler},
    {.handler = USART3_IRQHandler},
    {.handler = EXTI15_10_IRQHandler},
    {.handler = RTC_Alarm_IRQHandler},
    {.handler = OTG_FS_WKUP_IRQHandler},
}};
