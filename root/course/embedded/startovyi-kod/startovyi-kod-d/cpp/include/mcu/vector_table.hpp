#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace mcu {

using vector_handler = void (*)();

/* Перший запис таблиці — не функція, а вершина стека. Об'єднання дає
   покласти в один масив обидва види значень і, головне, лишити
   ініціалізацію СТАТИЧНОЮ: reinterpret_cast не є константним виразом,
   тож таблиця з ним поїхала б у динамічну ініціалізацію — тобто
   заповнювалася б кодом, який ще не має права виконуватись. */
union vector_entry {
    void* stack_top;
    vector_handler handler;
};

inline constexpr std::size_t core_vector_count = 16; /* винятки ядра */
inline constexpr std::size_t irq_vector_count = 43;  /* STM32F4: WWDG…OTG_FS_WKUP */
inline constexpr std::size_t vector_count = core_vector_count + irq_vector_count;

/* Вирівнювання під VTOR: не менше 128 байтів і не менше за розмір
   таблиці, округлений до степеня двійки (59 × 4 = 236 → 256).
   Беремо 512 із запасом на нові вектори. */
inline constexpr std::size_t vector_table_align = 512;

} // namespace mcu

extern "C" {

extern std::uint32_t _estack; /* вершина стека зі скрипта лінкера */

/* Сама таблиця; на неї ж наводимо VTOR у Reset_Handler */
extern const std::array<mcu::vector_entry, mcu::vector_count> g_vector_table;

/* Винятки ядра Cortex-M */
void Reset_Handler();
void Default_Handler();
void NMI_Handler();
void HardFault_Handler();
void MemManage_Handler();
void BusFault_Handler();
void UsageFault_Handler();
void SVC_Handler();
void DebugMon_Handler();
void PendSV_Handler();
void SysTick_Handler();

/* Переривання периферії, позиції NVIC 0…42 — суворо в порядку заліза */
void WWDG_IRQHandler();
void PVD_IRQHandler();
void TAMP_STAMP_IRQHandler();
void RTC_WKUP_IRQHandler();
void FLASH_IRQHandler();
void RCC_IRQHandler();
void EXTI0_IRQHandler();
void EXTI1_IRQHandler();
void EXTI2_IRQHandler();
void EXTI3_IRQHandler();
void EXTI4_IRQHandler();
void DMA1_Stream0_IRQHandler();
void DMA1_Stream1_IRQHandler();
void DMA1_Stream2_IRQHandler();
void DMA1_Stream3_IRQHandler();
void DMA1_Stream4_IRQHandler();
void DMA1_Stream5_IRQHandler();
void DMA1_Stream6_IRQHandler();
void ADC_IRQHandler();
void CAN1_TX_IRQHandler();
void CAN1_RX0_IRQHandler();
void CAN1_RX1_IRQHandler();
void CAN1_SCE_IRQHandler();
void EXTI9_5_IRQHandler();
void TIM1_BRK_TIM9_IRQHandler();
void TIM1_UP_TIM10_IRQHandler();
void TIM1_TRG_COM_TIM11_IRQHandler();
void TIM1_CC_IRQHandler();
void TIM2_IRQHandler();
void TIM3_IRQHandler();
void TIM4_IRQHandler();
void I2C1_EV_IRQHandler();
void I2C1_ER_IRQHandler();
void I2C2_EV_IRQHandler();
void I2C2_ER_IRQHandler();
void SPI1_IRQHandler();
void SPI2_IRQHandler();
void USART1_IRQHandler();
void USART2_IRQHandler();
void USART3_IRQHandler();
void EXTI15_10_IRQHandler();
void RTC_Alarm_IRQHandler();
void OTG_FS_WKUP_IRQHandler();

} // extern "C"
