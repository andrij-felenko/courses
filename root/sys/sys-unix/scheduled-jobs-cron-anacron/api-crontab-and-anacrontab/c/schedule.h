/* Розклад cron у бітових масках: розбір п'яти часових полів, зіставлення з
   часом, розрахунок сну без дрейфу та стеження за змінами таблиць. */
#ifndef MINICRON_SCHEDULE_H
#define MINICRON_SCHEDULE_H

#include "daymatch.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>

/* CRON_DOM_STAR і CRON_DOW_STAR оголошені в daymatch.h — правило дня їхнє. */
#define CRON_AT_REBOOT 0x04u /* макрос @reboot: один запуск під час старту демона */

typedef struct {
    uint64_t minute_mask; /* біти 0..59 */
    uint32_t hour_mask;   /* біти 0..23 */
    uint32_t dom_mask;    /* біти 1..31 */
    uint16_t month_mask;  /* біти 1..12 */
    uint8_t  dow_mask;    /* біти 0..6, неділя == 0 */
    unsigned flags;
} cron_schedule_t;

/* Розбирає початок рядка: п'ять часових полів або макрос @… .
   rest отримує вказівник на перший символ після розкладу (звідти йде команда
   або, у системній таблиці, ім'я користувача).
   Повертає false і заповнює err текстом на кшталт "bad minute: …". */
bool cron_schedule_parse(const char *line, cron_schedule_t *out, const char **rest,
                         char *err, size_t err_size);

/* Зіставлення з локальним часом: хвилина, година, місяць — прості біти,
   день — правило з daymatch.h. */
bool cron_schedule_matches(const cron_schedule_t *sched, const struct tm *tm_now);

/* Скільки секунд лишилося до нульової секунди наступної хвилини. Демон спить
   саме цей залишок, а не фіксовані 60 с, — інакше розклад дрейфував би. */
unsigned cron_seconds_to_next_minute(time_t now);

/* Спостерігач за таблицями: inotify там, де він доступний, інакше опитування
   st_mtime під час кожного хвилинного пробудження. */
typedef struct cron_watch cron_watch_t;

cron_watch_t *cron_watch_open(const char *const *paths, size_t count);
/* Дескриптор inotify для epoll або -1, якщо працює резервне опитування. */
int  cron_watch_fd(const cron_watch_t *watch);
/* Витягує накопичені події (або звіряє мітки часу) і каже, чи щось змінилося. */
bool cron_watch_changed(cron_watch_t *watch);
void cron_watch_close(cron_watch_t *watch);

#endif /* MINICRON_SCHEDULE_H */
