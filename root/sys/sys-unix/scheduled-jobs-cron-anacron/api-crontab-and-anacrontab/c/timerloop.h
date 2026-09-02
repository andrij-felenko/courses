/* Мультиплексор подій: timerfd плюс сторонні дескриптори в одному epoll,
   без сигналів і без sleep(). */
#ifndef MINICRON_TIMERLOOP_H
#define MINICRON_TIMERLOOP_H

#include <stdint.h>
#include <time.h>

typedef void (*timer_handler_t)(uint64_t expirations, void *user_data);
typedef void (*fd_handler_t)(int fd, void *user_data);

typedef struct timer_loop timer_loop_t;

timer_loop_t *timer_loop_create(void);
void timer_loop_destroy(timer_loop_t *loop);

/* flags — 0 (відносний час) або TFD_TIMER_ABSTIME (можна разом із
   TFD_TIMER_CANCEL_ON_SET на CLOCK_REALTIME). Повертає 0 або -1. */
int timer_loop_add_timer(timer_loop_t *loop, int clockid,
                         const struct itimerspec *spec, int flags,
                         timer_handler_t handler, void *user_data);

/* Чужий дескриптор (inotify, сокет, канал): цикл лише будить обробник,
   вичитує дані сам обробник. Дескриптор лишається у власності викликача. */
int timer_loop_add_fd(timer_loop_t *loop, int fd, fd_handler_t handler,
                      void *user_data);

int timer_loop_run(timer_loop_t *loop);

/* Безпечно викликати з обробника сигналу: пише в sig_atomic_t. */
void timer_loop_stop(timer_loop_t *loop);

/* Вікно коалесценції для ПОТОЧНОГО потоку (prctl(PR_SET_TIMERSLACK)): ядро
   має право затримати спрацьовування на стільки наносекунд, щоб збігтися з
   уже запланованим пробудженням процесора. Нуль повертає типове значення. */
int  timer_loop_set_slack_ns(unsigned long slack_ns);
/* Чинне вікно потоку або -1 з errno. */
long timer_loop_read_slack_ns(void);

#endif /* MINICRON_TIMERLOOP_H */
