// Дисциплінований приймач UART на STM32F407: C++23, без винятків і RTTI,
// без купи взагалі. Тактування ставить SystemInit() зі стартового файла
// постачальника; тут ми займаємось предметом теми — пріоритетами NVIC
// і поділом роботи на верхню та нижню половини.
#include "FreeRTOS.h"
#include "task.h"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_bus.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_i2c.h"
#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_usart.h"

#include "isr/i2c_relay.hpp"
#include "isr/timer.hpp"
#include "isr/uart_bridge.hpp"

#include <array>
#include <cstdint>

namespace {

// Найвищий пріоритет, з якого ще дозволено кликати API з суфіксом FromISR.
// Обробник із МЕНШИМ числом (тобто логічно вищий) планувальника не бачить:
// аварійні лінії живуть саме там і працюють без RTOS.
constexpr std::uint32_t kSyscallIrqPriority = 5;

void enable_cycle_counter() noexcept
{
    // DWT дає лічильник тактів ядра — ним обробник міряє сам себе.
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void gpio_init() noexcept
{
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOD);

    LL_GPIO_InitTypeDef uart_pins{};
    uart_pins.Pin = LL_GPIO_PIN_9 | LL_GPIO_PIN_10; // USART1 TX/RX
    uart_pins.Mode = LL_GPIO_MODE_ALTERNATE;
    uart_pins.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
    uart_pins.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    uart_pins.Pull = LL_GPIO_PULL_UP;
    uart_pins.Alternate = LL_GPIO_AF_7;
    LL_GPIO_Init(GPIOA, &uart_pins);

    uart_pins.Pin = LL_GPIO_PIN_2 | LL_GPIO_PIN_3; // USART2 TX/RX
    LL_GPIO_Init(GPIOA, &uart_pins);

    LL_GPIO_InitTypeDef i2c_pins{};
    i2c_pins.Pin = LL_GPIO_PIN_6 | LL_GPIO_PIN_9; // I2C1 SCL/SDA
    i2c_pins.Mode = LL_GPIO_MODE_ALTERNATE;
    i2c_pins.Speed = LL_GPIO_SPEED_FREQ_HIGH;
    i2c_pins.OutputType = LL_GPIO_OUTPUT_OPENDRAIN;
    i2c_pins.Pull = LL_GPIO_PULL_UP;
    i2c_pins.Alternate = LL_GPIO_AF_4;
    LL_GPIO_Init(GPIOB, &i2c_pins);

    LL_GPIO_InitTypeDef led{};
    led.Pin = LL_GPIO_PIN_12;
    led.Mode = LL_GPIO_MODE_OUTPUT;
    led.Speed = LL_GPIO_SPEED_FREQ_LOW;
    led.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    led.Pull = LL_GPIO_PULL_NO;
    LL_GPIO_Init(GPIOD, &led);
}

void uart_init() noexcept
{
    LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_USART1);
    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_USART2);

    LL_USART_InitTypeDef cfg{};
    cfg.BaudRate = 115200;
    cfg.DataWidth = LL_USART_DATAWIDTH_8B;
    cfg.StopBits = LL_USART_STOPBITS_1;
    cfg.Parity = LL_USART_PARITY_NONE;
    cfg.TransferDirection = LL_USART_DIRECTION_TX_RX;
    cfg.HardwareFlowControl = LL_USART_HWCONTROL_NONE;
    cfg.OverSampling = LL_USART_OVERSAMPLING_16;

    // USART1 живе на APB2, USART2 — на APB1. Сплутати частоти шин означає
    // перекошений бод, який виглядає як «іноді приходить сміття».
    cfg.PeriphClock = SystemCoreClock / 2;
    LL_USART_Init(USART1, &cfg);
    cfg.PeriphClock = SystemCoreClock / 4;
    LL_USART_Init(USART2, &cfg);

    LL_USART_Enable(USART1);
    LL_USART_Enable(USART2);
    LL_USART_EnableIT_RXNE(USART1);
    LL_USART_EnableIT_RXNE(USART2);
}

void i2c_init() noexcept
{
    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_I2C1);

    LL_I2C_InitTypeDef cfg{};
    cfg.PeripheralMode = LL_I2C_MODE_I2C;
    cfg.ClockSpeed = 100000;
    cfg.DutyCycle = LL_I2C_DUTYCYCLE_2;
    cfg.OwnAddress1 = 0;
    cfg.TypeAcknowledge = LL_I2C_ACK;
    cfg.OwnAddrSize = LL_I2C_OWNADDRESS1_7BIT;
    LL_I2C_Init(I2C1, &cfg);

    // Переривань I2C не вмикаємо свідомо: цю шину обслуговує завдання,
    // а не обробник. Уся тема саме про це.
}

void tim2_init() noexcept
{
    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_TIM2);

    LL_TIM_InitTypeDef cfg{};
    // Таймери APB1 на F407 дістають подвоєну частоту шини, тобто
    // SystemCoreClock/2. Ділимо до 1 МГц і рахуємо до 1000 — вийде 1 кГц.
    cfg.Prescaler = static_cast<std::uint16_t>((SystemCoreClock / 2) / 1000000 - 1);
    cfg.CounterMode = LL_TIM_COUNTERMODE_UP;
    cfg.Autoreload = 999;
    cfg.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
    LL_TIM_Init(TIM2, &cfg);

    LL_TIM_ClearFlag_UPDATE(TIM2);
    LL_TIM_EnableIT_UPDATE(TIM2);
    LL_TIM_EnableCounter(TIM2);
}

void nvic_init() noexcept
{
    // Групування 4: усі чотири біти пріоритету віддано витісненню,
    // підпріоритетів немає жодного. Підпріоритет упорядковує лише
    // ОДНОЧАСНІ запити й нікого не витісняє, а плутанина «чому мій обробник
    // не перервав сусіда» коштує днів. FreeRTOS вимагає саме такої схеми.
    NVIC_SetPriorityGrouping(0x03);

    const std::uint32_t group = NVIC_GetPriorityGrouping();
    NVIC_SetPriority(USART1_IRQn, NVIC_EncodePriority(group, kSyscallIrqPriority, 0));
    NVIC_SetPriority(USART2_IRQn, NVIC_EncodePriority(group, kSyscallIrqPriority + 1, 0));
    NVIC_SetPriority(TIM2_IRQn, NVIC_EncodePriority(group, kSyscallIrqPriority + 2, 0));

    NVIC_EnableIRQ(USART1_IRQn);
    NVIC_EnableIRQ(USART2_IRQn);
    NVIC_EnableIRQ(TIM2_IRQn);
}

[[noreturn]] void halt() noexcept
{
    taskDISABLE_INTERRUPTS();
    for (;;) {
        __BKPT(0);
    }
}

} // namespace

int main()
{
    SystemCoreClockUpdate();

    enable_cycle_counter();
    gpio_init();
    uart_init();
    i2c_init();
    tim2_init();

    // Спершу нижні половини: дескриптори завдань мусять існувати раніше,
    // ніж NVIC пустить у верхню половину перший байт.
    isr::UartBridge::start();
    isr::I2cRelay::start();

    nvic_init();

    vTaskStartScheduler();

    // Сюди потрапляють лише тоді, коли планувальнику забракло пам'яті.
    // Мовчазний while(1) був би найгіршим виходом: пристрій виглядав би живим.
    halt();
}

// ---------------------------------------------------------------------------
// Гачки FreeRTOS. Купи в проєкті немає: завдання створюються статично,
// і пам'ять під службові задачі системи теж віддаємо ми.
// ---------------------------------------------------------------------------
extern "C" void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{
    static_cast<void>(task);
    static_cast<void>(name);
    // Найчастіша причина — вкладені переривання плюс великі локальні масиви
    // в обробнику. Зупиняємось голосно.
    halt();
}

extern "C" void vApplicationGetIdleTaskMemory(StaticTask_t **tcb, StackType_t **stack,
                                              std::uint32_t *words)
{
    static StaticTask_t idle_tcb;
    static std::array<StackType_t, configMINIMAL_STACK_SIZE> idle_stack;

    *tcb = &idle_tcb;
    *stack = idle_stack.data();
    *words = configMINIMAL_STACK_SIZE;
}

#if (configUSE_TIMERS == 1)
extern "C" void vApplicationGetTimerTaskMemory(StaticTask_t **tcb, StackType_t **stack,
                                               std::uint32_t *words)
{
    static StaticTask_t timer_tcb;
    static std::array<StackType_t, configTIMER_TASK_STACK_DEPTH> timer_stack;

    *tcb = &timer_tcb;
    *stack = timer_stack.data();
    *words = configTIMER_TASK_STACK_DEPTH;
}
#endif
