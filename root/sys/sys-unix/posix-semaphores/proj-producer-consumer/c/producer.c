/* producer.c:  cc -std=c11 -O2 producer.c -o producer -lrt -pthread */
#define _POSIX_C_SOURCE 200809L
#include "pc.h"
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static void wait_retry(sem_t *s)
{
    while (sem_wait(s) == -1) {
        if (errno == EINTR) continue;        /* сигнал обірвав очікування — чекаємо далі */
        perror("sem_wait");
        _exit(1);
    }
}

static void put(struct ring *r, const char *msg)
{
    wait_retry(&r->free_slots);              /* 1: чи є куди класти */
    wait_retry(&r->mutex);                   /* 2: індекси мої */
    memcpy(r->slot[r->tail], msg, MSGLEN);
    r->tail = (r->tail + 1) % SLOTS;
    sem_post(&r->mutex);
    sem_post(&r->filled);                    /* аж тепер запис видно споживачеві */
}

int main(void)
{
    shm_unlink(SHM_NAME);                    /* залишок попереднього запуску — геть */
    int fd = shm_open(SHM_NAME, O_CREAT | O_EXCL | O_RDWR, 0600);
    if (fd == -1) { perror("shm_open"); return 1; }
    if (ftruncate(fd, sizeof(struct ring)) == -1) { perror("ftruncate"); return 1; }

    struct ring *r = mmap(NULL, sizeof *r, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (r == MAP_FAILED) { perror("mmap"); return 1; }

    sem_init(&r->free_slots, 1, SLOTS);      /* 1 — «семафором користуються різні процеси» */
    sem_init(&r->filled,     1, 0);
    sem_init(&r->mutex,      1, 1);
    r->head = r->tail = 0;
    atomic_store_explicit(&r->ready, READY, memory_order_release);

    char msg[MSGLEN];
    for (unsigned i = 0; i < 1000; i++) {
        snprintf(msg, sizeof msg, "кадр %u", i);
        put(r, msg);
    }

    memset(msg, 0, sizeof msg);
    put(r, msg);                             /* порожній запис — знак «більше не буде» */

    for (unsigned i = 0; i < SLOTS; i++)     /* усі слоти знову вільні ⇒ споживач уже нічого не чекає */
        wait_retry(&r->free_slots);

    sem_destroy(&r->free_slots);
    sem_destroy(&r->filled);
    sem_destroy(&r->mutex);
    munmap(r, sizeof *r);
    shm_unlink(SHM_NAME);
    return 0;
}
