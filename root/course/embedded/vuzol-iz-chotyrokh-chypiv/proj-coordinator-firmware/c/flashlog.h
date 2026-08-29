#ifndef FLASHLOG_H
#define FLASHLOG_H

/* Кільцевий журнал у NOR Flash: записи збираються по десять у сторінковий
 * буфер ОЗП, сектор під наступну сторінку стирається наперед, а голова
 * кільця після перезавантаження шукається скануванням заголовків секторів. */

#include "node.h"

typedef enum {
    LOG_IDLE = 0,
    LOG_PROGRAMMING,   /* сторінка в польоті: чип зайнятий ~0.7 мс */
    LOG_ERASING        /* стирання сектора: 45 мс типово, до 400 мс */
} log_state_t;

typedef struct {
    uint32_t    write_addr;                  /* адреса сторінки, куди пишемо */
    uint16_t    page_used;                   /* байтів у буфері сторінки     */
    uint8_t     page_records;                /* записів у буфері             */
    uint8_t     page_buf[FLASH_PAGE_SIZE];
    bool        page_pending;                /* буфер повний, чекає на Flash */
    log_state_t state;
    uint32_t    op_started_ms;
    uint32_t    records_total;
    uint32_t    sectors_erased;
    uint32_t    write_errors;
    bool        last_write_ok;
    bool        mounted;
} flash_log_t;

/* Знаходить голову кільця й номер останнього запису. newest може бути NULL. */
bool flashlog_mount(flash_log_t *log, telemetry_record_t *newest);

/* Кладе запис у сторінковий буфер. false — попередня сторінка ще не лягла. */
bool flashlog_append(flash_log_t *log, const telemetry_record_t *rec);

/* Крок автомата: жодного очікування, лише перевірка BUSY і запуск наступного. */
void flashlog_poll(flash_log_t *log);

bool flashlog_idle(const flash_log_t *log);

#endif /* FLASHLOG_H */
