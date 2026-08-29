/* Координатор вузла: один неблокуючий цикл подій на чотири чипи.
 *
 * Секундний меандр DS3231 будить ядро зі Stop 2 і кладе в чергу подію
 * вимірювання; BME280 міряє свої десять мілісекунд, поки цикл займається
 * іншим; повні сторінки записів лягають у W25Q128 автоматом, який ніде не
 * чекає в while; кадри Modbus RTU приходять і йдуть через переривання
 * USART, а лінію DE знімає обробник TC. Ніде немає ані delay(), ані
 * очікування прапорця без тайм-ауту. */

#include <string.h>

#include "stm32l4xx.h"
#include "node.h"
#include "i2c.h"
#include "devices.h"
#include "flashlog.h"
#include "rs485.h"

#define SYSCLK_HZ      80000000u
#define HSI16_HZ       16000000u
#define SAMPLE_LIMIT_MS 50u     /* BME280 на ×1 міряє ~10 мс */

static flash_log_t        logger;
static telemetry_record_t last_record;
static uint16_t           seq_counter;

static bool     sampling;
static uint32_t sample_started_ms;
static bool     sensor_alive;
static bool     rtc_alive;   /* меандр 1 Гц живий — інакше вузол не прокинеться */
static uint32_t last_sample_ms;

/* ── Тактування ──────────────────────────────────────────────────────────── */

/* Викликається на старті й після кожного виходу зі Stop 2: прокидається
 * ядро на MSI, а нам потрібні ті самі 80 МГц від HSE через PLL. */
static void clock_config(void)
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;

    FLASH->ACR = FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN |
                 FLASH_ACR_LATENCY_4WS;

    RCC->CR |= RCC_CR_HSEON;
    uint32_t guard = 0;
    while ((RCC->CR & RCC_CR_HSERDY) == 0u) {
        if (++guard > 1000000u) {
            /* Кварц не завівся — лишаємося на MSI. Вузол працюватиме
             * повільніше, але це краще, ніж вічний цикл. */
            return;
        }
    }

    RCC->CR &= ~RCC_CR_PLLON;
    while ((RCC->CR & RCC_CR_PLLRDY) != 0u) { }

    /* HSE 8 МГц → /1 → ×20 = 160 МГц у VCO → /2 = 80 МГц на SYSCLK. */
    RCC->PLLCFGR = (3u << RCC_PLLCFGR_PLLSRC_Pos) |
                   (0u << RCC_PLLCFGR_PLLM_Pos) |
                   (20u << RCC_PLLCFGR_PLLN_Pos) |
                   (0u << RCC_PLLCFGR_PLLR_Pos) |
                   RCC_PLLCFGR_PLLREN;
    RCC->CR |= RCC_CR_PLLON;
    while ((RCC->CR & RCC_CR_PLLRDY) == 0u) { }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }
}

/* ── Секундний фронт від DS3231 ──────────────────────────────────────────── */

static void rtc_tick_input_init(void)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    GPIOA->MODER &= ~3u;                    /* PA0 — вхід */
    GPIOA->PUPDR = (GPIOA->PUPDR & ~3u) | 1u;   /* підтяжка: вихід чипа з відкритим стоком */

    SYSCFG->EXTICR[0] &= ~SYSCFG_EXTICR1_EXTI0;  /* лінія EXTI0 з порту A */
    EXTI->FTSR1 |= EXTI_FTSR1_FT0;               /* спадний фронт меандра 1 Гц */
    EXTI->RTSR1 &= ~EXTI_RTSR1_RT0;
    EXTI->IMR1  |= EXTI_IMR1_IM0;

    NVIC_SetPriority(EXTI0_IRQn, 1u);
    NVIC_EnableIRQ(EXTI0_IRQn);
}

void EXTI0_IRQHandler(void)
{
    EXTI->PR1 = EXTI_PR1_PIF0;
    events_push(NODE_EVENT_RTC_TICK);
}

/* ── Сон ─────────────────────────────────────────────────────────────────── */

static void enter_stop2(void)
{
    /* У Stop 2 гасне все високочастотне — HSE, PLL, SysTick. Живими
     * лишаються LSI зі сторожовим таймером, приймач USART на HSI16 і
     * вхід EXTI0. Прокидає нас або секунда від DS3231, або старт-біт
     * від ведучого на лінії RS-485. */
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | PWR_CR1_LPMS_STOP2;
    SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;

    __DSB();
    __WFI();

    SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    clock_config();
}

/* ── Збирання запису ─────────────────────────────────────────────────────── */

static void start_sample(void)
{
    if (sampling) return;                  /* попереднє ще не забрали */

    if (!bme280_start()) {
        /* Шина мовчить — найімовірніше завис ведений. Розблоковуємо й
         * піднімаємо датчик наново; не вийде — запишемо зріз без нього. */
        i2c_bus_recover();
        sensor_alive = bme280_init() && bme280_start();
    } else {
        sensor_alive = true;
    }

    sampling = true;
    sample_started_ms = millis();
    last_sample_ms = sample_started_ms;
}

static void finish_sample(bool sensor_ok)
{
    telemetry_record_t rec;
    uint16_t flags = 0;

    memset(&rec, 0, sizeof(rec));

    if (sensor_ok && bme280_fetch(&rec.temperature, &rec.pressure, &rec.humidity)) {
        flags |= STATUS_SENSOR_BME_OK;
    }

    uint32_t unix_time = 0;
    bool     clock_valid = false;

    if (ds3231_time(&unix_time, &clock_valid)) {
        rtc_alive = true;
        rec.timestamp = unix_time;
        if (clock_valid) {
            flags |= STATUS_RTC_SYNC_OK;
        }
    } else {
        /* Годинник не відповів: мітку доводиться рахувати від попередньої.
         * Запис від цього не зникає — зникає лише довіра до його часу.
         * Піднімаємо чип наново: разом із його налаштуваннями могла зникнути
         * і секундна «мітка» на INT/SQW, а без неї вузол більше не прокинеться. */
        rtc_alive = false;
        rec.timestamp = last_record.timestamp + 1u;
        i2c_bus_recover();
        rtc_alive = ds3231_init();
    }

    if (logger.last_write_ok) {
        flags |= STATUS_FLASH_LOG_OK;      /* стан ОСТАННЬОЇ завершеної сторінки */
    }
    if (rs485_master_active()) {
        flags |= STATUS_RS485_ACTIVE;
    }

    rec.sequence_id  = ++seq_counter;
    rec.status_flags = flags;
    rec.crc16 = crc16_modbus((const uint8_t *)&rec, (uint16_t)(sizeof(rec) - 2u));

    last_record = rec;
    flashlog_append(&logger, &rec);
    sampling = false;
}

/* ── Головний цикл ───────────────────────────────────────────────────────── */

int main(void)
{
    clock_config();
    systick_init(SYSCLK_HZ);
    watchdog_init();

    i2c_init();
    flash_init();
    rs485_init(HSI16_HZ);
    rtc_tick_input_init();

    sensor_alive = bme280_init();
    rtc_alive    = ds3231_init();

    telemetry_record_t newest;
    memset(&newest, 0, sizeof(newest));

    if (flashlog_mount(&logger, &newest)) {
        /* Нумерацію продовжуємо з останнього запису в кільці, щоб ведучий
         * не побачив після перезавантаження стрибок номерів назад. */
        seq_counter = newest.sequence_id;
        last_record = newest;
    }

    for (;;) {
        watchdog_kick();
        flashlog_poll(&logger);

        node_event_t ev;
        while (events_pop(&ev)) {
            switch (ev) {
            case NODE_EVENT_RTC_TICK:
                start_sample();
                break;

            case NODE_EVENT_RS485_FRAME:
                rs485_service(&last_record);
                break;

            case NODE_EVENT_RS485_SENT:
            case NODE_EVENT_FLASH_IDLE:
            default:
                break;                     /* автомати вже все зробили */
            }
        }

        if (sampling) {
            if (!sensor_alive) {
                finish_sample(false);
            } else if (bme280_ready()) {
                finish_sample(true);
            } else if ((millis() - sample_started_ms) > SAMPLE_LIMIT_MS) {
                /* Датчик не звільнив прапорець measuring за вчетверо довший
                 * час, ніж обіцяє паспорт: пишемо зріз без нього. */
                sensor_alive = false;
                finish_sample(false);
            }
        }

        /* Аварійний ритм: секундна мітка від DS3231 зникла. Спати тепер не
         * можна — прокидатися немає від чого; такт відміряє SysTick, а
         * годинник пробуємо підняти на кожному зрізі. */
        if (!rtc_alive) {
            if (!sampling && (millis() - last_sample_ms) >= 1000u) {
                start_sample();
            }
            continue;
        }

        /* Спати можна лише коли не лишилося ані події в черзі, ані
         * незавершеної роботи в жодного з чотирьох чипів. */
        if (events_empty() && !sampling &&
            flashlog_idle(&logger) && !rs485_tx_busy() && !rs485_frame_waiting()) {
            enter_stop2();
        }
    }
}
