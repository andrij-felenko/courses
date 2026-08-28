/* consumer.c:  cc -std=c11 -O2 consumer.c -o consumer -lrt -pthread */
#define _POSIX_C_SOURCE 200809L
#include "pc.h"
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static void nap(void) { struct timespec t = { 0, 1000000 }; nanosleep(&t, NULL); }

static void wait_retry(sem_t *s)
{
    while (sem_wait(s) == -1) {
        if (errno == EINTR) continue;
        perror("sem_wait");
        _exit(1);
    }
}

int main(void)
{
    int fd;
    while ((fd = shm_open(SHM_NAME, O_RDWR, 0)) == -1 && errno == ENOENT)
        nap();                               /* області ще нема — виробник не стартував */
    if (fd == -1) { perror("shm_open"); return 1; }

    struct stat st;                          /* доки ftruncate не дав розміру, сторінок за файлом нема */
    while (fstat(fd, &st) == 0 && (size_t) st.st_size < sizeof(struct ring))
        nap();

    struct ring *r = mmap(NULL, sizeof *r, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (r == MAP_FAILED) { perror("mmap"); return 1; }

    while (atomic_load_explicit(&r->ready, memory_order_acquire) != READY)
        nap();                               /* доки sem_init не завершено — семафорів ще нема */

    for (;;) {
        char msg[MSGLEN];
        wait_retry(&r->filled);              /* 1: чи є що брати */
        wait_retry(&r->mutex);               /* 2: індекси мої */
        memcpy(msg, r->slot[r->head], MSGLEN);
        r->head = (r->head + 1) % SLOTS;
        sem_post(&r->mutex);
        sem_post(&r->free_slots);            /* слот повернуто в обіг */

        if (msg[0] == '\0') break;
        puts(msg);
    }

    munmap(r, sizeof *r);
    return 0;
}
