#include "pins.h"

/* Повний план плати. Кожен вивід має роль — «забули налаштувати» тут неможливо,
 * бо все, чого немає в таблиці, автоматично їде в аналоговий режим. */
static const pin_plan_t k_plan[] = {
    { GPIOA,  0, PIN_ROLE_WAKEUP,   "PA0  WKUP1, кнопка, зовнішня підтяжка 470 кОм" },
    { GPIOA,  2, PIN_ROLE_PARK_LOW, "PA2  USART2_TX до мосту USB-UART"              },
    { GPIOA,  3, PIN_ROLE_ANALOG,   "PA3  USART2_RX"                                },
    { GPIOA,  4, PIN_ROLE_PARK_LOW, "PA4  SPI1_CS зовнішньої Flash (активний 0)"    },
    { GPIOA,  5, PIN_ROLE_PARK_LOW, "PA5  SPI1_SCK"                                 },
    { GPIOA,  6, PIN_ROLE_ANALOG,   "PA6  SPI1_MISO"                                },
    { GPIOA,  7, PIN_ROLE_PARK_LOW, "PA7  SPI1_MOSI"                                },
    { GPIOA, 13, PIN_ROLE_ANALOG,   "PA13 SWDIO — у релізі гасимо"                  },
    { GPIOA, 14, PIN_ROLE_ANALOG,   "PA14 SWCLK — у релізі гасимо"                  },
    { GPIOB,  1, PIN_ROLE_SENSE,    "PB1  дільник 1:2 з шини 3V3_SW"                },
    { GPIOB,  3, PIN_ROLE_ANALOG,   "PB3  SWO — драйвер трасування вимкнено"        },
    { GPIOB,  6, PIN_ROLE_PARK_LOW, "PB6  I2C1_SCL, підтяжки живляться з 3V3_SW"    },
    { GPIOB,  7, PIN_ROLE_PARK_LOW, "PB7  I2C1_SDA"                                 },
    { GPIOB, 12, PIN_ROLE_KEEP_HIGH,"PB12 затвор ключа 3V3_SW (1 = знеструмлено)"   },
    { GPIOC, 13, PIN_ROLE_PARK_LOW, "PC13 світлодіод"                               },
};
#define PLAN_LEN (sizeof(k_plan) / sizeof(k_plan[0]))

#define LED_PORT GPIOC
#define LED_PIN  13u
#define SENSE_PORT GPIOB
#define SENSE_PIN  1u

/* ---------- елементарні операції над виводом ---------- */

void pin_mode(gpio_t *port, uint8_t pin, uint32_t mode)
{
    port->MODER = (port->MODER & ~(3u << (pin * 2u))) | (mode << (pin * 2u));
}

void pin_pull(gpio_t *port, uint8_t pin, uint32_t pull)
{
    port->PUPDR = (port->PUPDR & ~(3u << (pin * 2u))) | (pull << (pin * 2u));
}

void pin_af(gpio_t *port, uint8_t pin, uint32_t af)
{
    const uint8_t idx = pin >> 3u;
    const uint8_t shift = (pin & 7u) * 4u;
    port->AFR[idx] = (port->AFR[idx] & ~(0xFu << shift)) | (af << shift);
}

void pin_write(gpio_t *port, uint8_t pin, bool level)
{
    port->BSRR = level ? (1u << pin) : (1u << (pin + 16u));
}

bool pin_read(gpio_t *port, uint8_t pin)
{
    return (port->IDR & (1u << pin)) != 0u;
}

/* Такт після Stop2 — MSI 4 МГц. Цикл підібрано під цю частоту: точності тут
 * не треба, треба гарантована пауза не менша за задану. */
void board_delay_ms(uint32_t ms)
{
    for (uint32_t i = 0; i < ms; ++i) {
        for (volatile uint32_t k = 0; k < 400u; ++k) {
            __asm volatile("nop");
        }
    }
}

/* ---------- ініціалізація ---------- */

void board_clocks_init(void)
{
    RCC_AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN | RCC_AHB2ENR_GPIOCEN;
    RCC_APB1ENR1 |= RCC_APB1ENR1_PWREN;
    (void)RCC_APB1ENR1; /* затримка синхронізації шини */
}

void board_pins_init(void)
{
    /* Спершу гарантовано розмикаємо ключ: після скидання затвор іще не заданий,
     * а датчик не повинен живитися, поки прошивка не вирішила його ввімкнути. */
    pin_write(RAIL_GATE_PORT, RAIL_GATE_PIN, true);
    pin_pull(RAIL_GATE_PORT, RAIL_GATE_PIN, PULL_NONE);
    pin_mode(RAIL_GATE_PORT, RAIL_GATE_PIN, MODE_OUTPUT);

    board_pins_to_analog();

    /* Світлодіод — вихід у нулі. */
    pin_write(LED_PORT, LED_PIN, false);
    pin_mode(LED_PORT, LED_PIN, MODE_OUTPUT);

    /* Кнопка пробудження: зовнішній резистор 470 кОм уже задає рівень,
     * внутрішню підтяжку не вмикаємо — це були б іще 80 мкА. */
    pin_pull(GPIOA, 0, PULL_NONE);
    pin_mode(GPIOA, 0, MODE_INPUT);
}

/* ---------- комутована шина ---------- */

void board_rail_on(void)
{
    pin_write(RAIL_GATE_PORT, RAIL_GATE_PIN, false);
    board_delay_ms(3); /* заряд блокувальних ємностей датчика */
}

void board_rail_off(void)
{
    pin_write(RAIL_GATE_PORT, RAIL_GATE_PIN, true);
    board_delay_ms(2); /* розряд ємностей через власне навантаження */
}

bool board_rail_is_discharged(void)
{
    /* Вхід вмикаємо на мить: постійно тримати його цифровим — самому собі
     * влаштувати той наскрізний струм, який ми ловимо. */
    pin_pull(SENSE_PORT, SENSE_PIN, PULL_NONE);
    pin_mode(SENSE_PORT, SENSE_PIN, MODE_INPUT);
    for (volatile uint32_t k = 0; k < 40u; ++k) {
        __asm volatile("nop");
    }
    const bool still_hot = pin_read(SENSE_PORT, SENSE_PIN);
    pin_mode(SENSE_PORT, SENSE_PIN, MODE_ANALOG);
    return !still_hot;
}

/* ---------- підготовка до сну ---------- */

void board_park_switched_domain(void)
{
    /* Порядок критичний: лінії до знеструмлюваного вузла притискаємо в нуль,
     * ПОКИ його шина ще під напругою. Інакше вихідний драйвер МК почне
     * живити датчик через верхній ESD-діод. */
    for (unsigned i = 0; i < PLAN_LEN; ++i) {
        if (k_plan[i].role != PIN_ROLE_PARK_LOW) {
            continue;
        }
        pin_write(k_plan[i].port, k_plan[i].pin, false);
        pin_pull(k_plan[i].port, k_plan[i].pin, PULL_NONE);
        pin_mode(k_plan[i].port, k_plan[i].pin, MODE_OUTPUT);
    }
}

static pin_role_t role_of(const gpio_t *port, uint8_t pin)
{
    for (unsigned i = 0; i < PLAN_LEN; ++i) {
        if (k_plan[i].port == port && k_plan[i].pin == pin) {
            return k_plan[i].role;
        }
    }
    return PIN_ROLE_ANALOG; /* не згаданий у плані = невживаний = аналог */
}

static void port_to_analog(gpio_t *port)
{
    uint32_t moder = port->MODER;
    uint32_t pupdr = port->PUPDR;

    for (uint8_t pin = 0; pin < 16u; ++pin) {
        const uint32_t shift = pin * 2u;
        switch (role_of(port, pin)) {
        case PIN_ROLE_KEEP_HIGH:
            moder = (moder & ~(3u << shift)) | (MODE_OUTPUT << shift);
            pupdr &= ~(3u << shift);
            break;
        case PIN_ROLE_WAKEUP:
            /* Лишаємо як є: рівень задає зовнішній резистор. */
            break;
        case PIN_ROLE_ANALOG:
        case PIN_ROLE_PARK_LOW:
        case PIN_ROLE_SENSE:
        default:
            moder |= (MODE_ANALOG << shift);
            pupdr &= ~(3u << shift);
            break;
        }
    }

    port->MODER = moder;
    port->PUPDR = pupdr;
    port->ASCR = 0u; /* аналоговий комутатор розімкнений: до АЦП нічого не тягнеться */
}

void board_pins_to_analog(void)
{
    port_to_analog(GPIOA);
    port_to_analog(GPIOB);
    port_to_analog(GPIOC);
}

void board_apply_standby_pulls(void)
{
    /* У Standby конфігурація GPIO втрачається, і рівні на виводах задають
     * окремі регістри блока живлення. Затвор ключа мусить лишитися високим,
     * інакше шина датчика оживе разом зі сном. */
    PWR_PUCRA = 0u;
    PWR_PDCRA = 0u;
    PWR_PUCRB = (1u << RAIL_GATE_PIN);
    PWR_PDCRB = 0u;
    PWR_PUCRC = 0u;
    PWR_PDCRC = 0u;
    PWR_CR3 |= PWR_CR3_APC;
}

/* ---------- самоаудит ---------- */

static unsigned audit_port(gpio_t *port, uint32_t *mask)
{
    unsigned found = 0;
    uint32_t bits = 0;

    for (uint8_t pin = 0; pin < 16u; ++pin) {
        const uint32_t shift = pin * 2u;
        const uint32_t mode = (port->MODER >> shift) & 3u;
        const uint32_t pull = (port->PUPDR >> shift) & 3u;

        if (mode != MODE_INPUT || pull != PULL_NONE) {
            continue;
        }
        if (role_of(port, pin) == PIN_ROLE_WAKEUP) {
            continue; /* зміщений зовнішнім резистором — не плаває */
        }
        bits |= (1u << pin);
        ++found;
    }

    *mask = bits;
    return found;
}

unsigned board_audit_floating(uint32_t *mask_a, uint32_t *mask_b, uint32_t *mask_c)
{
    return audit_port(GPIOA, mask_a)
         + audit_port(GPIOB, mask_b)
         + audit_port(GPIOC, mask_c);
}

void board_led(bool on)
{
    pin_mode(LED_PORT, LED_PIN, MODE_OUTPUT);
    pin_write(LED_PORT, LED_PIN, on);
}
