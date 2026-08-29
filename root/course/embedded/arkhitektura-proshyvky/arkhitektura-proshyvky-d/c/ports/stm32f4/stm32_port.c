/* ports/stm32f4/stm32_port.c — збірка плати на STM32F401.
 * Тут живуть системний час, критична секція, сон ядра, передавач
 * телеметрії та board_init(), що зшиває це все в структуру board_t.
 * Жоден шар вище не має права включати цей файл. */
#include "include/board.h"
#include "include/sys_config.h"
#include "hal/hal_critical.h"
#include "hal/hal_time.h"
#include "ports/stm32f4/stm32_port.h"
#include "services/event_queue.h"

#include "stm32f4xx.h"

#define BOARD_LED_PIN        0u   /* PB0, світлодіод підключений анодом */
#define UART_BAUDRATE        115200u
#define APB1_CLOCK_HZ        42000000u

static volatile uint32_t  g_tick_ms;
static volatile uint32_t  g_next_tick_event_ms;
static event_queue_t     *g_queue;
static board_t            g_board;

/* --- hal/hal_time.h --- */

uint32_t hal_time_now_ms(void)
{
    return g_tick_ms;
}

void hal_cpu_sleep(void)
{
    /* Ядро спиняється до найближчого переривання. Струм споживання падає
     * з десятків міліампер до одиниць — саме заради цього рядка вся
     * подійна архітектура й будувалася. */
    __asm volatile("wfi");
}

void hal_time_delay_ms(uint32_t ms)
{
    const uint32_t started = g_tick_ms;
    while ((g_tick_ms - started) < ms) {
        __asm volatile("nop");
    }
}

/* --- hal/hal_critical.h --- */

uint32_t hal_critical_enter(void)
{
    uint32_t primask;
    __asm volatile("mrs %0, primask" : "=r"(primask));
    __asm volatile("cpsid i" ::: "memory");
    return primask;
}

void hal_critical_exit(uint32_t saved_state)
{
    /* Вмикаємо переривання лише якщо вони були ввімкнені до входу:
     * інакше вкладена критична секція відкрила б їх передчасно. */
    if ((saved_state & 1u) == 0u) {
        __asm volatile("cpsie i" ::: "memory");
    }
}

/* --- Системний таймер --- */

void SysTick_Handler(void)
{
    g_tick_ms++;

    /* Тік застосунку рідший за такт таймера: подія раз на 100 мс, а не
     * тисяча подій на секунду, яких ніхто не встигне розібрати. */
    if ((int32_t)(g_tick_ms - g_next_tick_event_ms) >= 0) {
        g_next_tick_event_ms = g_tick_ms + SYS_TICK_PERIOD_MS;

        event_queue_t *queue = g_queue;
        if (queue != 0) {
            const sys_event_t evt = sys_event_make(EVT_ID_TICK_100MS, g_tick_ms);
            (void)event_queue_post_from_isr(queue, &evt);
        }
    }
}

static void systick_init(void)
{
    SysTick->LOAD = (SystemCoreClock / 1000u) - 1u;
    SysTick->VAL  = 0u;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk |
                    SysTick_CTRL_TICKINT_Msk |
                    SysTick_CTRL_ENABLE_Msk;
    g_next_tick_event_ms = SYS_TICK_PERIOD_MS;
}

/* --- include/board.h --- */

void board_bind_event_queue(struct event_queue *queue)
{
    const uint32_t state = hal_critical_enter();
    g_queue = queue;
    hal_critical_exit(state);
}

struct event_queue *board_event_queue(void)
{
    return g_queue;
}

/* --- Передавач телеметрії --- */

static void uart_put_char(char c)
{
    while ((USART2->SR & USART_SR_TXE) == 0u) {
    }
    USART2->DR = (uint8_t)c;
}

static void uart_put_str(const char *s)
{
    while (*s != '\0') {
        uart_put_char(*s++);
    }
}

static void uart_put_uint(uint32_t value)
{
    char buf[11];
    int i = 0;

    if (value == 0u) {
        uart_put_char('0');
        return;
    }
    while (value != 0u && i < (int)sizeof buf) {
        buf[i++] = (char)('0' + (value % 10u));
        value /= 10u;
    }
    while (i-- > 0) {
        uart_put_char(buf[i]);
    }
}

/* Друк числа з двома знаками після коми без printf: повний форматувальник
 * з підтримкою float тягне у прошивку кілька десятків кілобайтів. */
static void uart_put_fixed2(float value)
{
    if (value < 0.0f) {
        uart_put_char('-');
        value = -value;
    }
    const uint32_t scaled = (uint32_t)(value * 100.0f + 0.5f);
    uart_put_uint(scaled / 100u);
    uart_put_char('.');
    const uint32_t frac = scaled % 100u;
    if (frac < 10u) {
        uart_put_char('0');
    }
    uart_put_uint(frac);
}

void stm32_uart_init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    /* PA2 — вихід передавача, альтернативна функція 7. */
    GPIOA->MODER  &= ~(3u << (2u * 2u));
    GPIOA->MODER  |=  (2u << (2u * 2u));
    GPIOA->AFR[0] &= ~(0xFu << (2u * 4u));
    GPIOA->AFR[0] |=  (7u << (2u * 4u));

    USART2->BRR = APB1_CLOCK_HZ / UART_BAUDRATE;
    USART2->CR1 = USART_CR1_TE | USART_CR1_UE;
}

void stm32_uart_report_record(void *ctx, const telemetry_record_t *rec)
{
    (void)ctx;
    if (rec == 0) {
        return;
    }

    uart_put_str("T=");
    uart_put_fixed2(rec->temp_avg_c);
    uart_put_str("C H=");
    uart_put_fixed2(rec->humidity_avg_rh);
    uart_put_str("% P=");
    uart_put_fixed2(rec->pressure_avg_hpa);
    uart_put_str("hPa VIB=");
    uart_put_fixed2(rec->vibration_rms_g);
    uart_put_str("g PEAK=");
    uart_put_fixed2(rec->vibration_peak_g);
    uart_put_str("g N=");
    uart_put_uint(rec->sample_count);
    uart_put_str(" ERR=");
    uart_put_uint(rec->fault_count);
    uart_put_str("\r\n");
}

const board_t *board_init(void)
{
    SystemCoreClockUpdate();
    systick_init();
    stm32_uart_init();

    const hal_i2c_bus_t *bus = stm32_i2c1_init();
    if (bus == 0) {
        return 0;
    }

    stm32_button_exti_init();

    g_board.env_bus   = bus;
    g_board.accel_bus = bus;   /* обидві мікросхеми на одній шині */

    g_board.led_status.ops        = stm32_gpio_ops();
    g_board.led_status.ctx        = stm32_gpio_port_b();
    g_board.led_status.pin        = BOARD_LED_PIN;
    g_board.led_status.active_low = false;

    g_board.report_record = stm32_uart_report_record;
    g_board.report_ctx    = 0;

    return &g_board;
}
