#ifndef LOGSTORE_H
#define LOGSTORE_H

#include <stdbool.h>
#include <stdint.h>

#include "platform.h"

// Чорна скринька у Flash. Кільце секторів приймає рутинну телеметрію й
// затирається по колу; окремий пул наприкінці мікросхеми тримає критичні
// події, і кільце туди не дотягується ніколи.
#define LOG_RECORD_SIZE       24U
#define LOG_SLOTS_PER_SECTOR  (FLASH_SECTOR_SIZE / LOG_RECORD_SIZE)
#define LOG_BLACKBOX_SECTORS  3U
#define LOG_RING_SECTORS      (FLASH_SECTOR_COUNT - LOG_BLACKBOX_SECTORS)
#define LOG_RING_CAPACITY     (LOG_RING_SECTORS * LOG_SLOTS_PER_SECTOR)
#define LOG_BLACKBOX_CAPACITY (LOG_BLACKBOX_SECTORS * LOG_SLOTS_PER_SECTOR)

// Період сирих семплів давача та поріг фонового передстирання.
#define LOG_SAMPLE_PERIOD_MS  20U
#define LOG_PREERASE_PERCENT  80U

#define LOG_EV_SAMPLE  0x10U
#define LOG_NO_TARGET  0xFFFFU

typedef struct {
    uint32_t t_ms;
    uint8_t  event;
    uint8_t  critical;
    uint16_t count;    // скільки сирих семплів згорнуто в цю пачку
    float    min;
    float    max;
    float    avg;
    float    rms;
} log_record_t;

typedef struct {
    uint32_t write_idx;    // наскрізні номери записів кільця
    uint32_t read_idx;     // покажчик зливу в ефір
    uint32_t bb_idx;       // наскрізний номер запису чорної скриньки
    bool     dirty[FLASH_SECTOR_COUNT];
    uint16_t preerase_target;

    uint32_t win_start_ms; // акумулятор проріджування
    uint16_t win_count;
    float    w_min;
    float    w_max;
    float    w_sum;
    float    w_sq;

    uint32_t written;
    uint32_t overwritten;
    uint32_t dropped;
    uint32_t blocking_erases;
} logstore_t;

void logstore_init(logstore_t *s);
void logstore_sample(logstore_t *s, uint32_t t_ms, float value, uint32_t offline_ms);
void logstore_event(logstore_t *s, uint32_t t_ms, uint8_t event, bool critical);
void logstore_background(logstore_t *s);
size_t logstore_drain(logstore_t *s, size_t budget_bytes);
uint32_t logstore_pending(const logstore_t *s);
uint32_t logstore_blackbox_count(const logstore_t *s);
bool logstore_blackbox_get(const logstore_t *s, uint32_t index, log_record_t *out);

#endif /* LOGSTORE_H */
