/* Дисциплінований приймач UART на STM32F407, bare-metal з бібліотекою LL.
 *
 * Тактування ядра ставить SystemInit() зі стартового файла постачальника;
 * тут ми займаємось тим, що є предметом теми: пріоритетами NVIC і поділом
 * роботи на верхню та нижню половини.
 */
#include "FreeRTOS.h"
#include "task.h"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_bus.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_i2c.h"
#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_usart.h"

#include "busy_wait_trap.h"
#include "timer_isr.h"
#include "uart_isr.h"

/* Найвищий пріоритет, з якого ще дозволено кликати API з суфіксом FromISR.
 * Обробник, чий числовий пріоритет МЕНШИЙ за це число (тобто логічно вищий),
 * планувальника не бачить — і будь-який виклик FromISR звідти зламає чергу
 * готовності. Аварійні лінії живуть саме там і працюють без RTOS. */
#define SYSCALL_IRQ_PRIORITY 5u
#define EMERGENCY_IRQ_PRIORITY 1u

static void enable_cycle_counter(void)
{
    /* DWT дає лічильник тактів ядра — ним ISR міряє сама себе. */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0u;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

static void gpio_init(void)
{
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
    LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOD);

    LL_GPIO_InitTypeDef gpio = {0};

    /* PA9/PA10 — USART1 TX/RX (AF7): основний потік кадрів. */
    gpio.Pin = LL_GPIO_PIN_9 | LL_GPIO_PIN_10;
    gpio.Mode = LL_GPIO_MODE_ALTERNATE;
    gpio.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    gpio.Pull = LL_GPIO_PULL_UP;
    gpio.Alternate = LL_GPIO_AF_7;
    LL_GPIO_Init(GPIOA, &gpio);

    /* PA2/PA3 — USART2 TX/RX (AF7): лінія, яку ретранслюємо в I2C. */
    gpio.Pin = LL_GPIO_PIN_2 | LL_GPIO_PIN_3;
    LL_GPIO_Init(GPIOA, &gpio);

    /* PB6/PB9 — I2C1 SCL/SDA (AF4), відкритий стік із підтяжкою. */
    gpio.Pin = LL_GPIO_PIN_6 | LL_GPIO_PIN_9;
    gpio.OutputType = LL_GPIO_OUTPUT_OPENDRAIN;
    gpio.Alternate = LL_GPIO_AF_4;
    LL_GPIO_Init(GPIOB, &gpio);

    /* PD12 — світлодіод, який блимає з TIM2. */
    gpio.Pin = LL_GPIO_PIN_12;
    gpio.Mode = LL_GPIO_MODE_OUTPUT;
    gpio.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
    gpio.Pull = LL_GPIO_PULL_NO;
    gpio.Alternate = LL_GPIO_AF_0;
    LL_GPIO_Init(GPIOD, &gpio);
}

static void uart_init(void)
{
    LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_USART1);
    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_USART2);

    LL_USART_InitTypeDef cfg = {0};
    cfg.BaudRate = 115200u;
    cfg.DataWidth = LL_USART_DATAWIDTH_8B;
    cfg.StopBits = LL_USART_STOPBITS_1;
    cfg.Parity = LL_USART_PARITY_NONE;
    cfg.TransferDirection = LL_USART_DIRECTION_TX_RX;
    cfg.HardwareFlowControl = LL_USART_HWCONTROL_NONE;
    cfg.OverSampling = LL_USART_OVERSAMPLING_16;

    /* USART1 висить на APB2, USART2 — на APB1: у LL частота шини
     * передається окремим полем, і сплутати їх означає перекошений бод. */
    cfg.PeriphClock = SystemCoreClock / 2u;
    LL_USART_Init(USART1, &cfg);
    cfg.PeriphClock = SystemCoreClock / 4u;
    LL_USART_Init(USART2, &cfg);

    LL_USART_Enable(USART1);
    LL_USART_Enable(USART2);
    LL_USART_EnableIT_RXNE(USART1);
    LL_USART_EnableIT_RXNE(USART2);
}

static void i2c_init(void)
{
    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_I2C1);

    LL_I2C_InitTypeDef cfg = {0};
    cfg.PeripheralMode = LL_I2C_MODE_I2C;
    cfg.ClockSpeed = 100000u;
    cfg.DutyCycle = LL_I2C_DUTYCYCLE_2;
    cfg.OwnAddress1 = 0u;
    cfg.TypeAcknowledge = LL_I2C_ACK;
    cfg.OwnAddrSize = LL_I2C_OWNADDRESS1_7BIT;
    LL_I2C_Init(I2C1, &cfg);

    /* Переривань I2C не вмикаємо свідомо: цю шину обслуговує завдання,
     * а не обробник. Уся стаття про те, чому саме так. */
}

static void tim2_init(void)
{
    LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_TIM2);

    LL_TIM_InitTypeDef cfg = {0};
    /* APB1 на F407 ділиться на 4, але таймери на ньому дістають ×2,
     * тобто SystemCoreClock/2. Ділимо до 1 МГц і рахуємо до 1000. */
    cfg.Prescaler = (uint16_t)((SystemCoreClock / 2u) / 1000000u - 1u);
    cfg.CounterMode = LL_TIM_COUNTERMODE_UP;
    cfg.Autoreload = 999u; /* 1 кГц */
    cfg.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
    LL_TIM_Init(TIM2, &cfg);

    LL_TIM_ClearFlag_UPDATE(TIM2);
    LL_TIM_EnableIT_UPDATE(TIM2);
    LL_TIM_EnableCounter(TIM2);
}

static void nvic_init(void)
{
    /* Групування 4: усі чотири біти пріоритету віддано витісненню,
     * підпріоритетів немає жодного. Підпріоритет упорядковує лише
     * ОДНОЧАСНІ запити й нічого не витісняє, а плутанина «чому мій
     * обробник не перервав сусіда» коштує днів налагодження.
     * FreeRTOS до того ж вимагає саме такої конфігурації. */
    NVIC_SetPriorityGrouping(0x03u);

    NVIC_SetPriority(USART1_IRQn,
                     NVIC_EncodePriority(NVIC_GetPriorityGrouping(), SYSCALL_IRQ_PRIORITY, 0u));
    NVIC_SetPriority(USART2_IRQn,
                     NVIC_EncodePriority(NVIC_GetPriorityGrouping(), SYSCALL_IRQ_PRIORITY + 1u, 0u));
    NVIC_SetPriority(TIM2_IRQn,
                     NVIC_EncodePriority(NVIC_GetPriorityGrouping(), SYSCALL_IRQ_PRIORITY + 2u, 0u));

    NVIC_EnableIRQ(USART1_IRQn);
    NVIC_EnableIRQ(USART2_IRQn);
    NVIC_EnableIRQ(TIM2_IRQn);
}

int main(void)
{
    SystemCoreClockUpdate();

    enable_cycle_counter();
    gpio_init();
    uart_init();
    i2c_init();
    tim2_init();

    /* Спершу нижні половини — щоб дескриптори завдань існували раніше,
     * ніж NVIC пустить перший байт у верхню. */
    uart_bridge_start();
    i2c_relay_start();

    nvic_init();

    vTaskStartScheduler();

    /* Сюди потрапляють лише тоді, коли планувальнику забракло пам'яті
     * під власні структури. Мовчки крутитись у while(1) — найгірше,
     * що можна зробити: пристрій виглядатиме живим. */
    for (;;) {
        __BKPT(0);
    }
}

/* --------------------------------------------------------------------------
 * Гачки FreeRTOS. Купи в проєкті немає, тож завдання створюються статично,
 * а самій системі пам'ять під службові задачі теж віддаємо ми.
 * ------------------------------------------------------------------------ */
void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{
    (void)task;
    (void)name;
    /* Найчастіша причина — вкладені переривання плюс великі локальні
     * масиви в обробнику. Зупиняємось голосно. */
    taskDISABLE_INTERRUPTS();
    for (;;) {
        __BKPT(0);
    }
}

void vApplicationGetIdleTaskMemory(StaticTask_t **tcb, StackType_t **stack, uint32_t *words)
{
    static StaticTask_t idle_tcb;
    static StackType_t idle_stack[configMINIMAL_STACK_SIZE];

    *tcb = &idle_tcb;
    *stack = idle_stack;
    *words = configMINIMAL_STACK_SIZE;
}

#if (configUSE_TIMERS == 1)
void vApplicationGetTimerTaskMemory(StaticTask_t **tcb, StackType_t **stack, uint32_t *words)
{
    static StaticTask_t timer_tcb;
    static StackType_t timer_stack[configTIMER_TASK_STACK_DEPTH];

    *tcb = &timer_tcb;
    *stack = timer_stack;
    *words = configTIMER_TASK_STACK_DEPTH;
}
#endif
