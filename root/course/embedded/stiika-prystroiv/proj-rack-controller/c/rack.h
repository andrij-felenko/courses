/* Спільні дрібниці демона стійки: коди повернення, монотонний час, прапорець зупинки. */
#ifndef RACK_H
#define RACK_H

/* Один раз на весь проєкт: нам потрібні clock_gettime, nanosleep, dprintf. */
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

typedef enum {
    RACK_OK = 0,  /* усе вийшло */
    RACK_BUSY,    /* слот тримає інший процес */
    RACK_TIMEOUT, /* плата не сказала очікуваного вчасно */
    RACK_FAIL     /* апаратна або системна помилка */
} rack_status_t;

/* Ставить обробник SIGINT/SIGTERM у main.c; його бачать усі цикли очікування,
   інакше `kill` демона лишив би плату під напругою до кінця таймауту. */
extern volatile sig_atomic_t rack_stop;

/* Монотонний годинник: CLOCK_REALTIME стрибає при синхронізації часу, а стійка
   працює добами, і стрибок назад підвісив би очікування банера на години. */
static inline uint64_t rack_now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000u + (uint64_t)ts.tv_nsec / 1000000u;
}

static inline void rack_sleep_ms(unsigned ms)
{
    struct timespec req = { .tv_sec = (time_t)(ms / 1000u),
                            .tv_nsec = (long)(ms % 1000u) * 1000000L };
    /* Сигнал рве nanosleep — досипаємо залишок, інакше пауза знеструмлення
       виходить коротшою за задану, а саме її тривалість і розряджає ємності. */
    while (nanosleep(&req, &req) != 0 && errno == EINTR) {
    }
}

#endif /* RACK_H */
