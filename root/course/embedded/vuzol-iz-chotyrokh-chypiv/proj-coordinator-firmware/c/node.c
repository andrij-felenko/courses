/* Черга подій, системний час, сторожовий таймер, CRC-16.
 * Усе, що потрібне решті модулів і не належить жодному конкретному чипу. */

#include "stm32l4xx.h"
#include "node.h"

/* ── Черга подій ─────────────────────────────────────────────────────────── */

#define EVENT_QUEUE_LEN 16u   /* степінь двійки: маска замість ділення */

static volatile node_event_t queue[EVENT_QUEUE_LEN];
static volatile uint32_t     q_head;   /* пишуть переривання */
static volatile uint32_t     q_tail;   /* читає головний цикл */
static volatile uint32_t     q_lost;

/* Виклики йдуть з різних переривань (EXTI0, USART1), тому голову рухаємо
 * під забороною переривань — інакше два обробники затруть один одного. */
void events_push(node_event_t ev)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    uint32_t next = (q_head + 1u) & (EVENT_QUEUE_LEN - 1u);
    if (next == q_tail) {
        /* Переповнення — головний цикл десь застряг. Подію втрачаємо свідомо
         * і рахуємо: сторожовий таймер довше двох секунд цього не терпітиме. */
        q_lost++;
    } else {
        queue[q_head] = ev;
        q_head = next;
    }

    __set_PRIMASK(primask);
}

bool events_pop(node_event_t *ev)
{
    bool got = false;

    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    if (q_tail != q_head) {
        *ev = queue[q_tail];
        q_tail = (q_tail + 1u) & (EVENT_QUEUE_LEN - 1u);
        got = true;
    }

    __set_PRIMASK(primask);
    return got;
}

bool events_empty(void)
{
    return q_tail == q_head;
}

uint32_t events_lost(void)
{
    return q_lost;
}

/* ── Системний час ───────────────────────────────────────────────────────── */

static volatile uint32_t ms_ticks;
static uint32_t          cycles_per_us = 80u;

void SysTick_Handler(void)
{
    ms_ticks++;
}

void systick_init(uint32_t hclk_hz)
{
    cycles_per_us = hclk_hz / 1000000u;

    /* Лічильник тактів ядра — з нього робимо мікросекундні паузи для
     * ручного тактування шини I2C під час розблокування. */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    SysTick->LOAD = (hclk_hz / 1000u) - 1u;
    SysTick->VAL  = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk |
                    SysTick_CTRL_TICKINT_Msk |
                    SysTick_CTRL_ENABLE_Msk;
}

uint32_t millis(void)
{
    return ms_ticks;
}

void delay_us(uint32_t us)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = us * cycles_per_us;
    while ((DWT->CYCCNT - start) < ticks) {
        /* різниця беззнакова, тож переповнення CYCCNT нічого не ламає */
    }
}

/* ── Сторожовий таймер ───────────────────────────────────────────────────── */

void watchdog_init(void)
{
    /* LSI ≈ 32 кГц, дільник 32 → тик 1 мс, перезавантаження 2000 → 2.0 с.
     * IWDG живиться від LSI й переживає режим Stop 2, тому зависання в
     * обробнику події перезавантажить вузол навіть уві сні. */
    RCC->CSR |= RCC_CSR_LSION;
    while ((RCC->CSR & RCC_CSR_LSIRDY) == 0u) { }

    IWDG->KR  = 0x5555u;                       /* доступ до регістрів */
    IWDG->PR  = 3u;                            /* /32 */
    IWDG->RLR = 2000u - 1u;
    while (IWDG->SR != 0u) { }                 /* чекаємо застосування */
    IWDG->KR  = 0xAAAAu;                       /* перезарядити */
    IWDG->KR  = 0xCCCCu;                       /* пуск; вимкнути вже не можна */
}

void watchdog_kick(void)
{
    IWDG->KR = 0xAAAAu;
}

/* ── CRC-16 ──────────────────────────────────────────────────────────────── */

uint16_t crc16_modbus(const uint8_t *data, uint16_t len)
{
    uint16_t crc = 0xFFFFu;

    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            crc = (crc & 1u) ? (uint16_t)((crc >> 1) ^ 0xA001u) : (uint16_t)(crc >> 1);
        }
    }
    return crc;
}
