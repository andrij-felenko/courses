#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

struct hdr { pthread_mutex_t lock; /* … далі дані, які захищає замок … */ };

int  repair(struct hdr *h);        /* привести стан до ладу; 0 — вдалося */
void work  (struct hdr *h);

/* 0 — усередині, стан цілий;  1 — усередині, стан треба лагодити;
  -1 — не ввійшли, причина в *err. */
static int robust_lock(pthread_mutex_t *m, long ms, int *err)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);           /* монотонний: перевід годинника не страшний */
    ts.tv_nsec += (ms % 1000) * 1000000L;
    ts.tv_sec  += ms / 1000 + ts.tv_nsec / 1000000000L;
    ts.tv_nsec %= 1000000000L;

    int r = pthread_mutex_clocklock(m, CLOCK_MONOTONIC, &ts);
    if (r == 0)          return 0;
    if (r == EOWNERDEAD) return 1;                 /* замок наш, дані під сумнівом */
    *err = r;            return -1;                /* ETIMEDOUT / ENOTRECOVERABLE / EINVAL */
}

int use_segment(struct hdr *h)
{
    int err = 0;
    int st  = robust_lock(&h->lock, 200, &err);

    if (st < 0) {
        fprintf(stderr, "не ввійшли: %s\n", strerror(err));  /* НЕ perror */
        return -1;
    }
    if (st == 1) {
        if (repair(h) != 0) {                  /* полагодити не вдалося */
            pthread_mutex_unlock(&h->lock);    /* далі всім — ENOTRECOVERABLE */
            return -1;
        }
        pthread_mutex_consistent(&h->lock);    /* знімаємо тавро */
    }

    work(h);
    pthread_mutex_unlock(&h->lock);
    return 0;
}
