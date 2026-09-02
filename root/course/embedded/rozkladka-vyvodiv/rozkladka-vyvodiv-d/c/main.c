#include "pin_config.h"

#define COUNT_OF(a) (sizeof(a) / sizeof((a)[0]))

#define LED_PORT GPIOB
#define LED_PIN  6U

/*
 * Таблиця виводів плати — одне джерело правди, звірене зі схемою.
 * Рядки SWDIO/SWCLK стоять у таблиці навмисно: розпіновка мусить
 * називати системні ніжки, інакше їх «знайде» хтось інший.
 */
static const pin_desc_t board_layout[] = {
    { "SWDIO",       GPIOA, 13U, PIN_MODE_ALT,    0U, PIN_SPEED_VERY_HIGH, PIN_PULL_UP,   PIN_PUSH_PULL,  PIN_CLASS_SYSTEM, 0U },
    { "SWCLK",       GPIOA, 14U, PIN_MODE_ALT,    0U, PIN_SPEED_VERY_HIGH, PIN_PULL_DOWN, PIN_PUSH_PULL,  PIN_CLASS_SYSTEM, 0U },
    { "SPI1_SCK",    GPIOA,  5U, PIN_MODE_ALT,    5U, PIN_SPEED_HIGH,      PIN_PULL_NONE, PIN_PUSH_PULL,  PIN_CLASS_TTA,    0U },
    { "SPI1_MISO",   GPIOA,  6U, PIN_MODE_ALT,    5U, PIN_SPEED_HIGH,      PIN_PULL_NONE, PIN_PUSH_PULL,  PIN_CLASS_TTA,    0U },
    { "SPI1_MOSI",   GPIOA,  7U, PIN_MODE_ALT,    5U, PIN_SPEED_HIGH,      PIN_PULL_NONE, PIN_PUSH_PULL,  PIN_CLASS_TTA,    0U },
    { "FLASH_CS",    GPIOB,  0U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_MEDIUM,    PIN_PULL_UP,   PIN_PUSH_PULL,  PIN_CLASS_TTA,    0U },
    { "USART1_TX",   GPIOA,  9U, PIN_MODE_ALT,    7U, PIN_SPEED_MEDIUM,    PIN_PULL_UP,   PIN_PUSH_PULL,  PIN_CLASS_FT,     0U },
    { "USART1_RX",   GPIOA, 10U, PIN_MODE_ALT,    7U, PIN_SPEED_MEDIUM,    PIN_PULL_UP,   PIN_PUSH_PULL,  PIN_CLASS_FT,     0U },
    { "I2C1_SCL",    GPIOB,  8U, PIN_MODE_ALT,    4U, PIN_SPEED_MEDIUM,    PIN_PULL_NONE, PIN_OPEN_DRAIN, PIN_CLASS_FT,     0U },
    { "I2C1_SDA",    GPIOB,  9U, PIN_MODE_ALT,    4U, PIN_SPEED_MEDIUM,    PIN_PULL_NONE, PIN_OPEN_DRAIN, PIN_CLASS_FT,     0U },
    { "VBAT_SENSE",  GPIOA,  0U, PIN_MODE_ANALOG, 0U, PIN_SPEED_LOW,       PIN_PULL_NONE, PIN_PUSH_PULL,  PIN_CLASS_TTA,    0U },
    { "LED_STATUS",  LED_PORT, LED_PIN, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT,     8U },
    { "RTC_TICK",    GPIOC, 13U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW,       PIN_PULL_NONE, PIN_PUSH_PULL,  PIN_CLASS_BACKUP, 1U },
};

/* Хибний запит 1: підсвічування дисплея повісили на лінію даних SWD. */
static const pin_desc_t request_backlight[] = {
    { "BACKLIGHT_EN", GPIOA, 13U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 0U },
};

/* Хибний запит 2: світлодіод на 8 мА у домені резервного живлення. */
static const pin_desc_t request_rtc_led[] = {
    { "LED_ALARM", GPIOC, 13U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_BACKUP, 8U },
};

/* Хибний запит 3: вісім індикаторів по 15 мА на одному порту = 120 мА. */
static const pin_desc_t request_led_bank[] = {
    { "LED_BAR0", GPIOE, 0U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR1", GPIOE, 1U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR2", GPIOE, 2U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR3", GPIOE, 3U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR4", GPIOE, 4U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR5", GPIOE, 5U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR6", GPIOE, 6U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
    { "LED_BAR7", GPIOE, 7U, PIN_MODE_OUTPUT, 0U, PIN_SPEED_LOW, PIN_PULL_NONE, PIN_PUSH_PULL, PIN_CLASS_FT, 15U },
};

/*
 * Звіт лишається в пам'яті: SWO ми щойно віддали під GPIO, тож дивитися
 * на нього треба відлагоджувачем (у карті пам'яті — g_report).
 */
typedef struct {
    const char*  trial;
    bool         accepted;
    pin_status_t code;
    const char*  reason;
    const char*  signal;
    const char*  rival;
    uint32_t     value;
    uint32_t     limit;
} trial_result_t;

static trial_result_t g_report[5];
static volatile size_t   g_report_len;
static volatile uint16_t g_rejected;
static volatile uint16_t g_port_b_ma;
static volatile uint16_t g_chip_ma;

static bool record(const char* trial, bool accepted, const pin_error_t* err)
{
    if (g_report_len < COUNT_OF(g_report)) {
        trial_result_t* r = &g_report[g_report_len++];
        r->trial    = trial;
        r->accepted = accepted;
        r->code     = err->code;
        r->reason   = pin_status_text(err->code);
        r->signal   = err->signal;
        r->rival    = err->rival;
        r->value    = err->value;
        r->limit    = err->limit;
    }
    if (!accepted) {
        ++g_rejected;
    }
    return accepted;
}

static void delay_ticks(uint32_t ticks)
{
    for (volatile uint32_t i = 0U; i < ticks; ++i) {
        __NOP();
    }
}

static void led_blink(uint16_t times)
{
    for (uint16_t i = 0U; i < times; ++i) {
        LED_PORT->BSRR = (1U << LED_PIN);            /* увімкнути  */
        delay_ticks(400000U);
        LED_PORT->BSRR = (1U << (LED_PIN + 16U));    /* вимкнути   */
        delay_ticks(400000U);
    }
}

int main(void)
{
    pin_error_t err;

    /* Спершу розкладка плати, потім замок: замкнені ніжки вже не змінити. */
    const bool board_ok = record("таблиця плати",
                                 pin_apply_layout(board_layout, COUNT_OF(board_layout), &err),
                                 &err);

    if (board_ok) {
        (void)record("замок SWD", pin_secure_debug_port(&err), &err);
    }

    /* Три хибні запити. Кожен відкидається ще до запису в регістр. */
    (void)record("підсвічування на PA13",
                 pin_apply_layout(request_backlight, COUNT_OF(request_backlight), &err), &err);
    (void)record("LED 8 мА на PC13",
                 pin_apply_layout(request_rtc_led, COUNT_OF(request_rtc_led), &err), &err);
    (void)record("вісім LED по 15 мА",
                 pin_apply_layout(request_led_bank, COUNT_OF(request_led_bank), &err), &err);

    g_port_b_ma = pin_port_budget_ma(GPIOB);
    g_chip_ma   = pin_chip_budget_ma();

    for (;;) {
        if (!board_ok) {
            /* Плата не зійшлася з межами — світимо безперервно, не працюємо. */
            LED_PORT->BSRR = (1U << LED_PIN);
            delay_ticks(2000000U);
            continue;
        }
        led_blink(g_rejected);   /* стільки спалахів, скільки запитів відкинуто */
        delay_ticks(3000000U);
    }
}
