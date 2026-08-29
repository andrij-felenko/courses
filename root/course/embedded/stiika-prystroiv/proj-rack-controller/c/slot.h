/* Сесія слота: монопольне володіння, консоль, послідовності живлення. */
#ifndef RACK_SLOT_H
#define RACK_SLOT_H

#include <stddef.h>

#include "power.h"
#include "rack.h"

/* Скільки консольного логу тримаємо в пам'яті. Старіше витісняється хвостом:
   у прогоні на кілька годин цікавий свіжий кінець, а банер уже зловлено. */
#define RACK_LOG_CAP (256u * 1024u)

typedef struct {
    int id;
    int lock_fd;
    int uart_fd;
    int mirror_fd; /* куди дублювати потік наживо (stdout), -1 — нікуди */
    rack_power_t power;
    char log[RACK_LOG_CAP];
    size_t log_len;
    size_t scan_from;  /* звідки шукати шаблон, щоб не перечитувати весь лог */
    int empty_reads;   /* поспіль порожніх читань — ознака зниклого моста */
    bool log_trimmed;
} rack_slot_t;

/* Захопити слот. Чекає до wait_ms мілісекунд, далі повертає RACK_BUSY. */
rack_status_t rack_slot_acquire(rack_slot_t *s, int slot_id, unsigned wait_ms);

/* Відкрити залізо слота в канонічному порядку: спершу консоль, потім живлення. */
rack_status_t rack_slot_open_hw(rack_slot_t *s, int mirror_fd);

rack_status_t rack_slot_power_cycle(rack_slot_t *s, unsigned off_ms);
rack_status_t rack_slot_expect(rack_slot_t *s, const char *pattern, unsigned timeout_ms);
rack_status_t rack_slot_drain(rack_slot_t *s, unsigned duration_ms);

rack_status_t rack_slot_boot(rack_slot_t *s, const char *banner, unsigned timeout_ms);
rack_status_t rack_slot_flash(rack_slot_t *s, const char *image_path);
rack_status_t rack_slot_unbrick(rack_slot_t *s);

void rack_slot_release(rack_slot_t *s);

#endif /* RACK_SLOT_H */
