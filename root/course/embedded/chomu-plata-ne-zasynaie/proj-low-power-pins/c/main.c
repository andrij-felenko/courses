/* Цикл «прокинувся — виміряв — заснув» на STM32L4.
 *
 * Порядок операцій тут і є предметом статті, тому він виписаний в одному
 * місці й у тому самому вигляді, що й у переліку кроків: шини, датчики,
 * ключ, виводи, джерела пробудження, налагоджувач, WFI.
 */
#include "bus_quiesce.h"
#include "low_power_pins.h"
#include "mcu.h"
#include "sensor_power.h"
#include "wakeup.h"

#define SLEEP_SECONDS 10U

/* --------------------------- журнал у UART ----------------------------- */

/* Модуль UART після сну лишається вимкненим, а вивід PA2 — аналоговим.
 * Тому кожен запис починається з перевірки: чи є чим писати. */
static void log_ready(void)
{
    if ((USART2->CR1 & USART_CR1_UE) == 0U) {
        gpio_af(GPIOA, 2U, 7U); /* PA2 = USART2_TX, альтернативна функція 7 */
        USART2->CR1 = USART_CR1_UE | USART_CR1_TE;
    }
}

static void log_str(const char *s)
{
    log_ready();
    while (*s != '\0') {
        while ((USART2->ISR & USART_ISR_TXE) == 0U) {
        }
        USART2->TDR = (uint32_t)(uint8_t)(*s);
        s++;
    }
}

static void log_i32(int32_t v)
{
    char buf[12];
    unsigned pos = sizeof(buf);
    uint32_t mag = (v < 0) ? (uint32_t)(-(int64_t)v) : (uint32_t)v;

    buf[--pos] = '\0';
    do {
        buf[--pos] = (char)('0' + (mag % 10U));
        mag /= 10U;
    } while (mag != 0U);

    if (v < 0) {
        buf[--pos] = '-';
    }
    log_str(&buf[pos]);
}

/* ------------------------- початкова розкладка ------------------------- */

static void board_init(void)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN | RCC_AHB2ENR_GPIOCEN;
    RCC->APB1ENR1 |= RCC_APB1ENR1_USART2 | RCC_APB1ENR1_I2C1EN | RCC_APB1ENR1_PWREN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;

    /* Силовий ключ. Спершу рівень, потім режим виходу: якщо зробити навпаки,
     * затвор на мить дістане старий вміст засувки й ключ моргне. */
    gpio_write(RAIL_SWITCH_PORT, RAIL_SWITCH_PIN, true); /* закритий */
    gpio_mode(RAIL_SWITCH_PORT, RAIL_SWITCH_PIN, MODE_OUTPUT);

    /* UART для журналу: PA2 — TX, PA3 — RX. */
    gpio_af(GPIOA, 2U, 7U);
    gpio_af(GPIOA, 3U, 7U);
    USART2->BRR = CPU_HZ / 115200U; /* 4 МГц / 115200 = 35, похибка близько 2% */
    USART2->CR1 = USART_CR1_UE | USART_CR1_TE;

    /* I2C1: PB8 — SCL, PB9 — SDA, обидва з відкритим стоком.
     * Підтяжки — зовнішні, на шині датчиків, і зникають разом із нею. */
    gpio_open_drain(GPIOB, 8U, true);
    gpio_open_drain(GPIOB, 9U, true);
    gpio_af(GPIOB, 8U, 4U);
    gpio_af(GPIOB, 9U, 4U);
    I2C1->TIMINGR = 0x00420F13UL; /* 100 кГц від 4 МГц */
    I2C1->CR1 = I2C_CR1_PE;

    /* SPI1 на PA5/PA6/PA7 — зовнішня флеш-пам'ять журналу. У цьому прикладі
     * вона не читається, але вона є на платі, і перед сном її шину теж треба
     * зупиняти: незакінчений кадр SPI лишає ведений із піднятим CS. */
    gpio_af(GPIOA, 5U, 5U);
    gpio_af(GPIOA, 6U, 5U);
    gpio_af(GPIOA, 7U, 5U);
    SPI1->CR1 = 0U;
}

/* --------------------------- цикл глибокого сну ------------------------ */

static void deep_sleep_cycle(uint16_t seconds)
{
    /* 1–4. Датчики в standby, шини зупинені, ключ розімкнений, ємності розряджені. */
    rail_status_t rst = sensor_rail_shutdown();
    if (rst != RAIL_OK) {
        /* Засинаємо все одно: інакше виріб на батарейці не засне ніколи через
         * одну німу мікросхему. Але причину лишаємо в журналі. */
        log_str("sleep: ");
        log_str(rail_status_str(rst));
        log_str("\r\n");
    }

    /* 6. Джерело пробудження — ДО ізоляції виводів і до заборони переривань. */
    wakeup_arm_rtc(seconds);

    /* 5, 7. Виводи в аналоговий режим, DBGMCU очищено. Після цього рядка
     * писати в журнал нема куди: PA2 більше не UART. */
    lp_pins_enter_sleep();

    /* Режим Stop 2: ядро й більшість тактування зупинені, вміст пам'яті цілий. */
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS_MASK) | PWR_CR1_LPMS_STOP2;
    PWR->SCR = PWR_SCR_CWUF;
    SCB_SCR |= SCB_SCR_SLEEPDEEP;

    /* 8. Заборона переривань довкола WFI — не для швидкодії. Між очищенням
     * черги й самим WFI не має бути щілини, у якій ядро дістане прапорець і
     * прокинеться до того, як тактове дерево зупинилося. Замаскований WFI
     * усе одно прокидається, а обробник виконається на cpsie нижче. */
    mcu_irq_disable();
    wakeup_clear_pending();
    mcu_dsb();
    mcu_wfi();
    mcu_isb();
    mcu_irq_enable(); /* саме тут відпрацює обробник, який нас розбудив */

    SCB_SCR &= ~SCB_SCR_SLEEPDEEP;

    /* Пробудження: конфігурація виводів повертається у зворотному порядку. */
    lp_pins_restore();
}

int main(void)
{
    board_init();
    wakeup_init();

    log_str("\r\nстарт\r\n");

    for (;;) {
        rail_status_t st = sensor_rail_power_up();
        if (st != RAIL_OK) {
            log_str("живлення датчиків: ");
            log_str(rail_status_str(st));
            log_str("\r\n");
            /* Шина могла лишитися заклиненою після зриву попередньої
             * транзакції — пробуємо розклинити її дев'ятьма тактами. */
            if (bus_recover_i2c() != BUS_OK) {
                log_str("i2c не розклинилася\r\n");
            }
        } else {
            int32_t raw = 0;
            st = sensor_read_temperature_raw(&raw);
            if (st == RAIL_OK) {
                log_str("t_raw=");
                log_i32(raw);
                log_str("\r\n");
            } else {
                log_str("вимір: ");
                log_str(rail_status_str(st));
                log_str("\r\n");
            }
        }

        deep_sleep_cycle(SLEEP_SECONDS);

        log_str("прокинулися: ");
        log_str(wake_reason_str(wakeup_last_reason()));
        log_str("\r\n");
    }
}
