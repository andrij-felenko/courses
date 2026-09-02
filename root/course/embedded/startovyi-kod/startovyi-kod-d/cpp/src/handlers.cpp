#include <cstdint>

#include "mcu/registers.hpp"
#include "mcu/vector_table.hpp"

namespace {
/* Номер вектора, який привів нас у пастку: ядро тримає його в IPSR.
   Змінна глобальна й volatile — щоб її було видно в налагоджувачі
   навіть після оптимізації. */
volatile std::uint32_t g_trapped_vector = 0;

[[nodiscard]] std::uint32_t current_vector() noexcept
{
    std::uint32_t ipsr = 0;
    asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    return ipsr;
}
} // namespace

extern "C" {

/* Єдиний обробник за замовчуванням. Сюди потрапляє будь-яке переривання,
   яке ввімкнули в NVIC, але забули написати для нього функцію. */
void Default_Handler()
{
    g_trapped_vector = current_vector();

    if (mcu::scb::dhcsr::all_set(mcu::scb::debugger_attached)) {
        mcu::breakpoint(); /* зупиняємо ядро для розбору */
    }
    for (;;) {
        mcu::wait_for_interrupt();
    }
}

/* Слабкий синонім: символ у таблиці розв'язується в Default_Handler,
   але щойно десь у проєкті з'явиться звичайна функція з такою назвою,
   лінкер віддасть перевагу їй — сильний символ витісняє слабкий. */
#define MCU_WEAK_HANDLER(name) \
    [[gnu::weak, gnu::alias("Default_Handler")]] void name()

MCU_WEAK_HANDLER(NMI_Handler);
MCU_WEAK_HANDLER(HardFault_Handler);
MCU_WEAK_HANDLER(MemManage_Handler);
MCU_WEAK_HANDLER(BusFault_Handler);
MCU_WEAK_HANDLER(UsageFault_Handler);
MCU_WEAK_HANDLER(SVC_Handler);
MCU_WEAK_HANDLER(DebugMon_Handler);
MCU_WEAK_HANDLER(PendSV_Handler);
MCU_WEAK_HANDLER(SysTick_Handler);

MCU_WEAK_HANDLER(WWDG_IRQHandler);
MCU_WEAK_HANDLER(PVD_IRQHandler);
MCU_WEAK_HANDLER(TAMP_STAMP_IRQHandler);
MCU_WEAK_HANDLER(RTC_WKUP_IRQHandler);
MCU_WEAK_HANDLER(FLASH_IRQHandler);
MCU_WEAK_HANDLER(RCC_IRQHandler);
MCU_WEAK_HANDLER(EXTI0_IRQHandler);
MCU_WEAK_HANDLER(EXTI1_IRQHandler);
MCU_WEAK_HANDLER(EXTI2_IRQHandler);
MCU_WEAK_HANDLER(EXTI3_IRQHandler);
MCU_WEAK_HANDLER(EXTI4_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream0_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream1_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream2_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream3_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream4_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream5_IRQHandler);
MCU_WEAK_HANDLER(DMA1_Stream6_IRQHandler);
MCU_WEAK_HANDLER(ADC_IRQHandler);
MCU_WEAK_HANDLER(CAN1_TX_IRQHandler);
MCU_WEAK_HANDLER(CAN1_RX0_IRQHandler);
MCU_WEAK_HANDLER(CAN1_RX1_IRQHandler);
MCU_WEAK_HANDLER(CAN1_SCE_IRQHandler);
MCU_WEAK_HANDLER(EXTI9_5_IRQHandler);
MCU_WEAK_HANDLER(TIM1_BRK_TIM9_IRQHandler);
MCU_WEAK_HANDLER(TIM1_UP_TIM10_IRQHandler);
MCU_WEAK_HANDLER(TIM1_TRG_COM_TIM11_IRQHandler);
MCU_WEAK_HANDLER(TIM1_CC_IRQHandler);
MCU_WEAK_HANDLER(TIM2_IRQHandler);
MCU_WEAK_HANDLER(TIM3_IRQHandler);
MCU_WEAK_HANDLER(TIM4_IRQHandler);
MCU_WEAK_HANDLER(I2C1_EV_IRQHandler);
MCU_WEAK_HANDLER(I2C1_ER_IRQHandler);
MCU_WEAK_HANDLER(I2C2_EV_IRQHandler);
MCU_WEAK_HANDLER(I2C2_ER_IRQHandler);
MCU_WEAK_HANDLER(SPI1_IRQHandler);
MCU_WEAK_HANDLER(SPI2_IRQHandler);
MCU_WEAK_HANDLER(USART1_IRQHandler);
MCU_WEAK_HANDLER(USART2_IRQHandler);
MCU_WEAK_HANDLER(USART3_IRQHandler);
MCU_WEAK_HANDLER(EXTI15_10_IRQHandler);
MCU_WEAK_HANDLER(RTC_Alarm_IRQHandler);
MCU_WEAK_HANDLER(OTG_FS_WKUP_IRQHandler);

#undef MCU_WEAK_HANDLER

} // extern "C"
