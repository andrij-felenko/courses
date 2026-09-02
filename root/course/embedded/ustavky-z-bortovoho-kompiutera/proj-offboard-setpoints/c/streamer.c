#include "streamer.h"

#include <errno.h>
#include <math.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>

#include "serial.h"

#define STREAM_HZ            20
#define TICK_NS              (1000000000L / STREAM_HZ)
#define TICK_DT              (1.0f / (float)STREAM_HZ)
#define PRESTREAM_FRAMES     16      /* 800 мс потоку до запиту режиму */
#define PLANNER_TIMEOUT_MS   250
#define HEARTBEAT_DIVIDER    20      /* власний HEARTBEAT раз на секунду */
#define MODE_RETRY_TICKS     20      /* повтор DO_SET_MODE раз на секунду */
#define MODE_MAX_ATTEMPTS    5
#define FCU_LINK_TIMEOUT_MS  3000
#define BRAKE_ACCEL          2.0f    /* м/с²: 0.1 м/с за такт при 20 Гц */
#define ZERO_SPEED_EPS       0.01f
#define RT_PRIORITY          45

uint64_t now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

int streamer_init(offboard_streamer_t *s, const char *port, speed_t baud,
                  uint8_t sys_id, uint8_t comp_id) {
    memset(s, 0, sizeof(*s));
    s->uart_fd = -1;
    s->timer_fd = -1;
    s->sys_id = sys_id;
    s->comp_id = comp_id;
    s->state = STREAMER_IDLE;

    if (pthread_mutex_init(&s->target.lock, NULL) != 0) {
        return -1;
    }

    s->uart_fd = serial_open(port, baud);
    if (s->uart_fd < 0) {
        fprintf(stderr, "[streamer] %s: %s\n", port, strerror(errno));
        pthread_mutex_destroy(&s->target.lock);
        return -1;
    }

    /* Таймер БЛОКУВАЛЬНИЙ: read() спить до такту. З TFD_NONBLOCK цикл
     * перетворився б на бездумне обертання процесора. */
    s->timer_fd = timerfd_create(CLOCK_MONOTONIC, 0);
    if (s->timer_fd < 0) {
        fprintf(stderr, "[streamer] timerfd_create: %s\n", strerror(errno));
        serial_close(s->uart_fd);
        pthread_mutex_destroy(&s->target.lock);
        return -1;
    }

    atomic_store(&s->running, true);
    return 0;
}

void streamer_destroy(offboard_streamer_t *s) {
    if (s->timer_fd >= 0) {
        close(s->timer_fd);
        s->timer_fd = -1;
    }
    serial_close(s->uart_fd);
    s->uart_fd = -1;
    pthread_mutex_destroy(&s->target.lock);
}

void streamer_set_target(offboard_streamer_t *s, float vx, float vy, float vz, float yaw) {
    pthread_mutex_lock(&s->target.lock);
    s->target.vx = vx;
    s->target.vy = vy;
    s->target.vz = vz;
    s->target.yaw = yaw;
    s->target.stamp_ms = now_ms();
    s->target.valid = true;
    pthread_mutex_unlock(&s->target.lock);
}

void streamer_begin_mission(offboard_streamer_t *s) {
    atomic_store(&s->mission, true);
}

void streamer_request_shutdown(offboard_streamer_t *s) {
    atomic_store(&s->shutdown, true);
}

bool streamer_running(offboard_streamer_t *s) {
    return atomic_load(&s->running);
}

static void apply_rt_priority(void) {
    struct sched_param param;
    memset(&param, 0, sizeof(param));
    param.sched_priority = RT_PRIORITY;

    int rc = pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
    if (rc != 0) {
        /* Найчастіше це EPERM без CAP_SYS_NICE. Летіти можна, але потік
         * тепер витісняє будь-який фоновий процес — джитер зросте. */
        fprintf(stderr, "[streamer] SCHED_FIFO недоступний (%s): "
                        "працюємо у звичайному SCHED_OTHER\n", strerror(rc));
    }
}

static void tx_check(offboard_streamer_t *s, int rc) {
    if (rc == 0) {
        return;
    }
    s->tx_errors++;
    /* Кожен такт скаржитись не можна: на 20 Гц журнал сам стане
     * джерелом затримки. Пишемо перший збій і далі раз на секунду. */
    if (s->tx_errors % STREAM_HZ == 1) {
        fprintf(stderr, "[streamer] запис у UART не вдався: %s (усього %u)\n",
                strerror(errno), s->tx_errors);
    }
}

static void send_current(offboard_streamer_t *s) {
    tx_check(s, mav_send_setpoint(s->uart_fd, s->sys_id, s->comp_id,
                                  s->sent_vx, s->sent_vy, s->sent_vz, s->sent_yaw));
}

/* Лінійний зріз: за такт швидкість падає щонайбільше на a_brake·Δt. */
static float ramp_to_zero(float v, float dv_max) {
    if (fabsf(v) <= dv_max) {
        return 0.0f;
    }
    return v - copysignf(dv_max, v);
}

static void brake_step(offboard_streamer_t *s) {
    const float dv = BRAKE_ACCEL * TICK_DT;
    s->sent_vx = ramp_to_zero(s->sent_vx, dv);
    s->sent_vy = ramp_to_zero(s->sent_vy, dv);
    s->sent_vz = ramp_to_zero(s->sent_vz, dv);
    /* Курс не гальмуємо: тримаємо той, що був у момент втрати даних. */
}

static bool stopped(const offboard_streamer_t *s) {
    return fabsf(s->sent_vx) < ZERO_SPEED_EPS &&
           fabsf(s->sent_vy) < ZERO_SPEED_EPS &&
           fabsf(s->sent_vz) < ZERO_SPEED_EPS;
}

/* Автопілот міг вийти з Offboard сам: пілот узяв керування, спрацював
 * failsafe або обірвався лінк. Тиснути далі уставками — воювати з
 * пілотом, тому просто замовкаємо. */
static bool fcu_lost_control(offboard_streamer_t *s, uint64_t now) {
    if (!s->fcu.link_alive || now - s->fcu.last_heartbeat_ms > FCU_LINK_TIMEOUT_MS) {
        fprintf(stderr, "[streamer] автопілот мовчить понад %d мс — стоп\n",
                FCU_LINK_TIMEOUT_MS);
        return true;
    }
    if (!s->fcu.offboard) {
        fprintf(stderr, "[streamer] FCU вийшов з OFFBOARD (пілот або failsafe) — стоп\n");
        return true;
    }
    return false;
}

void *streamer_thread(void *arg) {
    offboard_streamer_t *s = (offboard_streamer_t *)arg;

    apply_rt_priority();

    /* Абсолютний періодичний таймер ядра: період не «пливе» від того,
     * скільки тривало тіло циклу — на відміну від usleep(). */
    struct itimerspec period;
    memset(&period, 0, sizeof(period));
    period.it_interval.tv_nsec = TICK_NS;
    period.it_value = period.it_interval;
    if (timerfd_settime(s->timer_fd, 0, &period, NULL) != 0) {
        fprintf(stderr, "[streamer] timerfd_settime: %s\n", strerror(errno));
        atomic_store(&s->running, false);
        return NULL;
    }

    while (atomic_load(&s->running)) {
        uint64_t ticks = 0;
        ssize_t n = read(s->timer_fd, &ticks, sizeof(ticks));
        if (n != (ssize_t)sizeof(ticks)) {
            if (errno == EINTR) {
                continue;
            }
            fprintf(stderr, "[streamer] read(timerfd): %s\n", strerror(errno));
            break;
        }
        if (ticks > 1) {
            /* Ядро повідомило про пропущені такти — ми не встигли. */
            s->late_ticks += (uint32_t)(ticks - 1);
            fprintf(stderr, "[streamer] проспано %llu тактів (усього %u)\n",
                    (unsigned long long)(ticks - 1), s->late_ticks);
        }
        s->tick++;

        uint64_t now = now_ms();
        mav_poll(s->uart_fd, &s->fcu, now);
        if (s->tick % HEARTBEAT_DIVIDER == 0) {
            tx_check(s, mav_send_heartbeat(s->uart_fd, s->sys_id, s->comp_id));
        }

        /* Знімок цілі планувальника разом з оцінкою свіжості. */
        float tvx = 0.0f, tvy = 0.0f, tvz = 0.0f, tyaw = 0.0f;
        bool is_fresh = false;
        pthread_mutex_lock(&s->target.lock);
        tyaw = s->target.yaw;
        if (s->target.valid && now - s->target.stamp_ms <= PLANNER_TIMEOUT_MS) {
            tvx = s->target.vx;
            tvy = s->target.vy;
            tvz = s->target.vz;
            is_fresh = true;
        }
        pthread_mutex_unlock(&s->target.lock);

        if (atomic_load(&s->shutdown)) {
            /* Зупинка: свіжі цілі більше не цікавлять, гальмуємо. */
            is_fresh = false;
            if (s->state == STREAMER_PRESTREAM || s->state == STREAMER_REQUEST_MODE) {
                s->state = STREAMER_IDLE;
            } else if (s->state == STREAMER_ACTIVE) {
                s->state = STREAMER_HOLD;
            }
        }

        if ((s->state == STREAMER_ACTIVE || s->state == STREAMER_HOLD) &&
            fcu_lost_control(s, now)) {
            s->state = STREAMER_IDLE;
        }

        switch (s->state) {
        case STREAMER_IDLE:
            if (atomic_load(&s->shutdown)) {
                atomic_store(&s->running, false);
            } else if (atomic_load(&s->mission)) {
                if (!s->fcu.link_alive) {
                    /* Без жодного HEARTBEAT просити режим марно. */
                    break;
                }
                fprintf(stderr, "[streamer] старт місії: розганяємо потік уставок\n");
                s->state = STREAMER_PRESTREAM;
                s->prestream_count = 0;
                s->sent_vx = s->sent_vy = s->sent_vz = 0.0f;
                s->sent_yaw = tyaw;
                atomic_store(&s->mission, false);
            }
            break;

        case STREAMER_PRESTREAM:
            /* FCU приймає перехід в Offboard, лише коли до запиту він
             * бачив стабільний потік уставок щонайменше 500 мс. */
            s->sent_vx = s->sent_vy = s->sent_vz = 0.0f;
            s->sent_yaw = tyaw;
            send_current(s);
            if (++s->prestream_count >= PRESTREAM_FRAMES) {
                s->state = STREAMER_REQUEST_MODE;
                s->mode_attempts = 0;
                s->mode_tick = s->tick - MODE_RETRY_TICKS; /* перший запит одразу */
            }
            break;

        case STREAMER_REQUEST_MODE:
            /* Потік НЕ переривається, поки триває узгодження режиму. */
            s->sent_yaw = tyaw;
            send_current(s);

            if (s->fcu.offboard) {
                fprintf(stderr, "[streamer] OFFBOARD підтверджено (%u спроб)\n",
                        s->mode_attempts);
                s->state = STREAMER_ACTIVE;
                break;
            }
            if (s->fcu.mode_ack_seen) {
                s->fcu.mode_ack_seen = false;
                if (!s->fcu.mode_ack_ok) {
                    fprintf(stderr, "[streamer] DO_SET_MODE відхилено, MAV_RESULT=%u\n",
                            s->fcu.mode_ack_result);
                }
            }
            if (s->tick - s->mode_tick >= MODE_RETRY_TICKS) {
                if (s->mode_attempts >= MODE_MAX_ATTEMPTS) {
                    fprintf(stderr, "[streamer] автопілот не пускає в OFFBOARD — місію скасовано\n");
                    s->state = STREAMER_IDLE;
                    break;
                }
                tx_check(s, mav_send_offboard_request(s->uart_fd, s->sys_id, s->comp_id));
                s->mode_attempts++;
                s->mode_tick = s->tick;
            }
            break;

        case STREAMER_ACTIVE:
            if (is_fresh) {
                s->sent_vx = tvx;
                s->sent_vy = tvy;
                s->sent_vz = tvz;
                s->sent_yaw = tyaw;
                send_current(s);
            } else {
                fprintf(stderr, "[streamer] ціль старша за %d мс — гальмування\n",
                        PLANNER_TIMEOUT_MS);
                s->state = STREAMER_HOLD;
                brake_step(s);
                send_current(s);
            }
            break;

        case STREAMER_HOLD:
            if (is_fresh) {
                fprintf(stderr, "[streamer] планувальник ожив — повертаємось у потік\n");
                s->state = STREAMER_ACTIVE;
                s->sent_vx = tvx;
                s->sent_vy = tvy;
                s->sent_vz = tvz;
                s->sent_yaw = tyaw;
                send_current(s);
            } else {
                brake_step(s);
                send_current(s);
                if (atomic_load(&s->shutdown) && stopped(s)) {
                    /* Апарат стоїть. Припиняємо потік: через 500 мс FCU
                     * сам вибиває Offboard і йде в Hold — це і є
                     * штатна передача керування автопілоту. */
                    fprintf(stderr, "[streamer] зупинено, віддаємо керування FCU\n");
                    s->state = STREAMER_IDLE;
                }
            }
            break;
        }
    }

    fprintf(stderr, "[streamer] вихід: тактів %u, проспано %u, збоїв TX %u, втрачено пакетів %u\n",
            s->tick, s->late_ticks, s->tx_errors, s->fcu.rx_drops);
    atomic_store(&s->running, false);
    return NULL;
}
