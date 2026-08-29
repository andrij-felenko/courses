#ifndef NODE_H
#define NODE_H

/* Спільні типи вузла телеметрії: запис, прапорці стану, черга подій, час.
 *
 * Карта плати (STM32L476, HSE 8 МГц → PLL 80 МГц):
 *   PA0      INT/SQW DS3231 — меандр 1 Гц, спадний фронт, EXTI0
 *   PB6/PB7  I2C1 SCL/SDA — BME280 (0x76) і DS3231 (0x68)
 *   PA4      CS NOR Flash W25Q128JV
 *   PA5..PA7 SPI1 SCK/MISO/MOSI
 *   PA8      DE трансивера RS-485 (знімаємо строго по TC)
 *   PA9/PA10 USART1 TX/RX
 */

#include <stdint.h>
#include <stdbool.h>

/* ── Геометрія пам'яті W25Q128JV ─────────────────────────────────────────── */

#define FLASH_PAGE_SIZE     256u
#define FLASH_SECTOR_SIZE   4096u
#define FLASH_TOTAL_SIZE    0x1000000u                          /* 16 МБ */
#define FLASH_SECTOR_COUNT  (FLASH_TOTAL_SIZE / FLASH_SECTOR_SIZE)
#define RECORDS_PER_PAGE    10u   /* 10 × 24 = 240 Б, хвіст сторінки лишається 0xFF */

/* ── Телеметричний запис ─────────────────────────────────────────────────── */

#define STATUS_SENSOR_BME_OK 0x0001u  /* вимірювання BME280 валідні            */
#define STATUS_RTC_SYNC_OK   0x0002u  /* мітка часу від DS3231, генератор не зривався */
#define STATUS_FLASH_LOG_OK  0x0004u  /* попередня сторінка лягла у Flash без помилки */
#define STATUS_RS485_ACTIVE  0x0008u  /* ведучий опитував вузол нещодавно      */

#define RS485_ACTIVE_WINDOW_MS 60000u

typedef struct __attribute__((packed)) {
    uint32_t timestamp;    /* Unix-час від DS3231            */
    int32_t  temperature;  /* °C × 100                        */
    uint32_t pressure;     /* Па × 100                        */
    uint32_t humidity;     /* %RH × 1024                      */
    uint16_t sequence_id;  /* порядковий номер зрізу          */
    uint16_t status_flags; /* прапорці стану вузла            */
    uint16_t crc16;        /* CRC-16 по перших 22 байтах      */
} telemetry_record_t;

_Static_assert(sizeof(telemetry_record_t) == 24, "запис мусить бути рівно 24 байти");
_Static_assert(RECORDS_PER_PAGE * sizeof(telemetry_record_t) <= FLASH_PAGE_SIZE,
               "пачка записів не влазить у сторінку");

/* ── Черга подій ─────────────────────────────────────────────────────────── */

typedef enum {
    NODE_EVENT_NONE = 0,
    NODE_EVENT_RTC_TICK,     /* спадний фронт 1 Гц з DS3231           */
    NODE_EVENT_RS485_FRAME,  /* USART зафіксував паузу t3.5 — кадр цілий */
    NODE_EVENT_RS485_SENT,   /* відповідь дійшла до останнього стоп-біта  */
    NODE_EVENT_FLASH_IDLE    /* Flash звільнилася після стирання/запису   */
} node_event_t;

/* Черга заповнюється з переривань, спорожнюється головним циклом. */
void events_push(node_event_t ev);
bool events_pop(node_event_t *ev);
bool events_empty(void);
uint32_t events_lost(void);

/* ── Час і сторожовий таймер ─────────────────────────────────────────────── */

void     systick_init(uint32_t hclk_hz);
uint32_t millis(void);
void     delay_us(uint32_t us);          /* лічильник тактів DWT, без таймера */

void watchdog_init(void);                /* IWDG на 2.0 с                     */
void watchdog_kick(void);

/* ── CRC-16 (поліном Modbus 0xA001) ──────────────────────────────────────── */

uint16_t crc16_modbus(const uint8_t *data, uint16_t len);

#endif /* NODE_H */
