#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <errno.h>
#include <linux/futex.h>
#include <sys/syscall.h>
#include <time.h>

static inline int sys_futex_waitv(struct futex_waitv *waiters, unsigned int nr_futexes,
                                  unsigned int flags, struct timespec *timo, clockid_t clockid) {
    return syscall(SYS_futex_waitv, waiters, nr_futexes, flags, timo, clockid);
}

static inline int sys_futex_wake(uint32_t *uaddr, int val) {
    return syscall(SYS_futex, uaddr, FUTEX_WAKE | FUTEX_PRIVATE_FLAG, val, NULL, NULL, 0);
}

uint32_t f_task_done = 0;
uint32_t f_shutdown = 0;

void *worker_thread(void *arg) {
    printf("[Worker] Виконую обчислення...\n");
    usleep(200000); /* Імітація роботи 200 мс */
    
    printf("[Worker] Завдання виконано. Сигналізую futex...\n");
    __atomic_store_n(&f_task_done, 1, __ATOMIC_RELEASE);
    sys_futex_wake(&f_task_done, 1);
    
    return NULL;
}

int main(void) {
    pthread_t thread;
    struct futex_waitv waiters[2];

    waiters[0].uaddr = (uint64_t)&f_task_done;
    waiters[0].val = 0;
    waiters[0].flags = FUTEX_32 | FUTEX_PRIVATE_FLAG;
    waiters[0].__reserved = 0;

    waiters[1].uaddr = (uint64_t)&f_shutdown;
    waiters[1].val = 0;
    waiters[1].flags = FUTEX_32 | FUTEX_PRIVATE_FLAG;
    waiters[1].__reserved = 0;

    if (pthread_create(&thread, NULL, worker_thread, NULL) != 0) {
        perror("pthread_create");
        return EXIT_FAILURE;
    }

    printf("[Main] Засинаю на futex_waitv (чекаю f_task_done або f_shutdown)...\n");
    int ret = sys_futex_waitv(waiters, 2, 0, NULL, 0);

    if (ret < 0) {
        perror("[Main] futex_waitv помилка");
    } else {
        printf("[Main] Прокинувся! Індекс розбудженого futex: %d\n", ret);
        if (ret == 0) {
            printf("[Main] Подія: f_task_done завершилася успішно.\n");
        } else if (ret == 1) {
            printf("[Main] Подія: отримано команду shutdown.\n");
        }
    }

    pthread_join(thread, NULL);
    return EXIT_SUCCESS;
}
