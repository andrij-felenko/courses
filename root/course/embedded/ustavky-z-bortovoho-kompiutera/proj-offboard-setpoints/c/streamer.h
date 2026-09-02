#ifndef STREAMER_H
#define STREAMER_H

#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <termios.h>

#include "mavlink_io.h"

/* П'ятифазний автомат безпечного входу в Offboard. */
typedef enum {
    STREAMER_IDLE,          /* порт відкрито, уставок не шлемо */
    STREAMER_PRESTREAM,     /* 16 кадрів нулів, щоб FCU побачив потік */
    STREAMER_REQUEST_MODE,  /* потік не рвемо і просимо режим Offboard */
    STREAMER_ACTIVE,        /* трансляція цілей планувальника */
    STREAMER_HOLD           /* планувальник відстав — гальмуємо до нуля */
} streamer_state_t;

/* Спільний буфер між повільним планувальником і RT-генератором.
 * Штамп часу тут головніший за самі числа: без нього ми б транслювали
 * протухлу ціль, поки планувальник лежить під page fault. */
typedef struct {
    pthread_mutex_t lock;
    float vx;
    float vy;
    float vz;
    float yaw;
    uint64_t stamp_ms;
    bool valid;
} shared_target_t;

typedef struct {
    int uart_fd;
    int timer_fd;
    uint8_t sys_id;
    uint8_t comp_id;

    shared_target_t target;
    fcu_status_t fcu;

    streamer_state_t state;
    uint32_t tick;
    uint32_t prestream_count;
    uint32_t mode_attempts;
    uint32_t mode_tick;
    uint32_t late_ticks;   /* такти, які ми проспали */
    uint32_t tx_errors;

    /* Остання НАДІСЛАНА уставка — від неї рахується гальмування. */
    float sent_vx;
    float sent_vy;
    float sent_vz;
    float sent_yaw;

    atomic_bool running;
    atomic_bool mission;   /* команда «почати місію» з іншого потоку */
    atomic_bool shutdown;  /* команда «загальмувати й вийти» */
} offboard_streamer_t;

uint64_t now_ms(void);

int  streamer_init(offboard_streamer_t *s, const char *port, speed_t baud,
                   uint8_t sys_id, uint8_t comp_id);
void streamer_destroy(offboard_streamer_t *s);

/* Викликає планувальник зі свого потоку, коли має нову ціль. */
void streamer_set_target(offboard_streamer_t *s, float vx, float vy, float vz, float yaw);

void streamer_begin_mission(offboard_streamer_t *s);
void streamer_request_shutdown(offboard_streamer_t *s);
bool streamer_running(offboard_streamer_t *s);

/* Тіло RT-потоку: pthread_create(&t, NULL, streamer_thread, &streamer). */
void *streamer_thread(void *arg);

#endif /* STREAMER_H */
