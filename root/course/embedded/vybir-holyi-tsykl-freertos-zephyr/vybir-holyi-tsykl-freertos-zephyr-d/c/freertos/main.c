/* Той самий прилад на FreeRTOS: три задачі, черга між ними, статична пам'ять.
   Уся ціна багатозадачності тут видима очима — вона у визначеннях нижче. */
#include "app.h"

#include "stm32g0xx.h"

QueueHandle_t g_samples;
TaskHandle_t  g_sensor_task;
TaskHandle_t  g_display_task;
TaskHandle_t  g_supervisor_task;

/* Стеки й службові структури — статичні: динамічної купи в прошивці немає,
   а бюджет RAM має бути видний лінкеру, а не з'ясовуватися в полі. */
static StackType_t s_sensor_stack[STACK_WORDS_SENSOR];
static StackType_t s_display_stack[STACK_WORDS_DISPLAY];
static StackType_t s_supervisor_stack[STACK_WORDS_SUPERVISOR];
static StaticTask_t s_sensor_tcb;
static StaticTask_t s_display_tcb;
static StaticTask_t s_supervisor_tcb;

static uint8_t s_queue_storage[SAMPLE_QUEUE_LEN * sizeof(sample_t)];
static StaticQueue_t s_queue_ctl;

/* Стеки службових задач ядра (див. hooks.c) теж рахуємо в бюджет. */
#define SYSTEM_STACK_WORDS (configMINIMAL_STACK_SIZE + configTIMER_TASK_STACK_DEPTH)
#define TOTAL_STACK_BYTES  ((STACK_WORDS_SENSOR + STACK_WORDS_DISPLAY + \
                             STACK_WORDS_SUPERVISOR + SYSTEM_STACK_WORDS) * sizeof(StackType_t))

/* На чипі 8 КБ RAM. Якщо стеки перевалять за половину — збірка має впасти
   тут, а не проявитися випадковим HardFault на столі замовника. */
_Static_assert(TOTAL_STACK_BYTES <= 4096u, "стеки задач не влазять у бюджет RAM");

void board_init(void)
{
    RCC->IOPENR  |= RCC_IOPENR_GPIOAEN | RCC_IOPENR_GPIOBEN;
    RCC->APBENR1 |= RCC_APBENR1_I2C1EN;
    RCC->APBENR2 |= RCC_APBENR2_SPI1EN;

    /* PB6/PB7 — I2C1, відкритий стік, AF6. */
    GPIOB->MODER = (GPIOB->MODER & ~(GPIO_MODER_MODE6 | GPIO_MODER_MODE7))
                 | (2u << GPIO_MODER_MODE6_Pos) | (2u << GPIO_MODER_MODE7_Pos);
    GPIOB->OTYPER |= GPIO_OTYPER_OT6 | GPIO_OTYPER_OT7;
    GPIOB->PUPDR = (GPIOB->PUPDR & ~(GPIO_PUPDR_PUPD6 | GPIO_PUPDR_PUPD7))
                 | (1u << GPIO_PUPDR_PUPD6_Pos) | (1u << GPIO_PUPDR_PUPD7_Pos);
    GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(GPIO_AFRL_AFSEL6 | GPIO_AFRL_AFSEL7))
                  | (6u << GPIO_AFRL_AFSEL6_Pos) | (6u << GPIO_AFRL_AFSEL7_Pos);

    I2C1->CR1     = 0u;
    I2C1->TIMINGR = 0x00303D5Bu; /* 100 кГц при PCLK = 16 МГц */
    I2C1->CR1     = I2C_CR1_PE;

    /* PA5/PA7 — SPI1, PA1/PA2/PA4 — D/C, RES, CS. */
    GPIOA->MODER = (GPIOA->MODER & ~(GPIO_MODER_MODE5 | GPIO_MODER_MODE7))
                 | (2u << GPIO_MODER_MODE5_Pos) | (2u << GPIO_MODER_MODE7_Pos);
    GPIOA->MODER = (GPIOA->MODER & ~(GPIO_MODER_MODE1 | GPIO_MODER_MODE2 | GPIO_MODER_MODE4))
                 | (1u << GPIO_MODER_MODE1_Pos) | (1u << GPIO_MODER_MODE2_Pos)
                 | (1u << GPIO_MODER_MODE4_Pos);
    GPIOA->OSPEEDR |= (2u << GPIO_OSPEEDR_OSPEED5_Pos) | (2u << GPIO_OSPEEDR_OSPEED7_Pos);
    GPIOA->BSRR = GPIO_BSRR_BS4;

    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (5u << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_DS_0 | SPI_CR2_DS_1 | SPI_CR2_DS_2 | SPI_CR2_FRXTH;
    SPI1->CR1 |= SPI_CR1_SPE;
}

void watchdog_start(void)
{
    RCC->CSR |= RCC_CSR_LSION;
    while ((RCC->CSR & RCC_CSR_LSIRDY) == 0u) { }

    IWDG->KR  = 0x0000CCCCu;
    IWDG->KR  = 0x00005555u;
    IWDG->PR  = 4u;
    IWDG->RLR = 500u; /* ≈ 1 с */
    while (IWDG->SR != 0u) { }
    IWDG->KR = 0x0000AAAAu;
}

void watchdog_kick(void)
{
    IWDG->KR = 0x0000AAAAu;
}

int main(void)
{
    board_init();
    watchdog_start();

    g_samples = xQueueCreateStatic(SAMPLE_QUEUE_LEN, sizeof(sample_t),
                                   s_queue_storage, &s_queue_ctl);
    configASSERT(g_samples != NULL);

    g_supervisor_task = xTaskCreateStatic(task_supervisor, "supervisor",
                                          STACK_WORDS_SUPERVISOR, NULL,
                                          PRIO_SUPERVISOR, s_supervisor_stack,
                                          &s_supervisor_tcb);
    g_sensor_task = xTaskCreateStatic(task_sensor, "sensor", STACK_WORDS_SENSOR, NULL,
                                      PRIO_SENSOR, s_sensor_stack, &s_sensor_tcb);
    g_display_task = xTaskCreateStatic(task_display, "display", STACK_WORDS_DISPLAY, NULL,
                                       PRIO_DISPLAY, s_display_stack, &s_display_tcb);
    configASSERT(g_supervisor_task && g_sensor_task && g_display_task);

    vTaskStartScheduler();

    /* Сюди планувальник не повертається. Якщо повернувся — ядру бракує пам'яті;
       нічого розумного вже не зробиш, лишається дати спрацювати watchdog. */
    for (;;) { }
}
