#define _GNU_SOURCE
#include "thread_sum.h"

#include "chunks.h"

#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <sys/syscall.h>
#include <unistd.h>

#define MAX_WORKERS 64

/* Глобальна змінна: одна комірка на ВЕСЬ процес. Усі потоки пишуть саме в неї,
   тому доступ треба серіалізувати замком — інакше це перегони даних. */
static long long g_visits = 0;
static pthread_mutex_t g_visits_lock = PTHREAD_MUTEX_INITIALIZER;

/* А це — приватна копія на КОЖЕН потік. Компонувальник кладе її в сегмент TLS,
   доступ іде через сегментний регістр FS (x86-64) чи TPIDR_EL0 (ARM64).
   Замок тут не потрібен: сусідній потік цієї комірки просто не бачить. */
static __thread long long tls_processed = 0;

typedef struct {
    const int *data;   /* той самий покажчик, що й у головного потоку */
    chunk_t range;
    long long partial; /* комірку пише лише свій потік — перегонів немає */
    pid_t tid;         /* ідентифікатор задачі в ядрі: у кожного потоку свій */
} worker_t;

static void *worker_main(void *arg)
{
    worker_t *w = (worker_t *)arg;

    /* getpid() поверне TGID — спільний для всіх потоків процесу;
       gettid() — унікальний номер саме цієї задачі ядра. */
    w->tid = (pid_t)syscall(SYS_gettid);

    w->partial = sum_range(w->data, w->range);
    tls_processed += (long long)(w->range.end - w->range.start);

    pthread_mutex_lock(&g_visits_lock);
    g_visits += 1;
    pthread_mutex_unlock(&g_visits_lock);

    return NULL;
}

int thread_sum(const int *data, size_t n, size_t workers, long long *out)
{
    if (workers == 0 || workers > MAX_WORKERS)
        return EINVAL;

    chunk_t ranges[MAX_WORKERS];
    worker_t work[MAX_WORKERS];
    pthread_t threads[MAX_WORKERS];

    chunk_split(n, workers, ranges);
    for (size_t i = 0; i < workers; ++i) {
        work[i].data = data;
        work[i].range = ranges[i];
        work[i].partial = 0;
        work[i].tid = 0;
    }
    g_visits = 0;

    /* Частку 0 бере на себе головний потік: змушувати його просто чекати
       на інших — марно палити ядро процесора. */
    size_t started = 0;
    int rc = 0;
    for (size_t i = 1; i < workers; ++i) {
        /* pthread_* повертають КОД помилки, а не -1 з errno. */
        rc = pthread_create(&threads[i], NULL, worker_main, &work[i]);
        if (rc != 0)
            break;
        ++started;
    }

    worker_main(&work[0]);

    /* Навіть якщо створення обірвалося на півдорозі, уже запущені потоки
       треба приєднати: вони пишуть у наші стекові структури. */
    for (size_t i = 1; i <= started; ++i)
        pthread_join(threads[i], NULL);

    if (rc != 0)
        return rc;

    long long total = 0;
    printf("  PID процесу: %d (однаковий для всіх потоків)\n", (int)getpid());
    for (size_t i = 0; i < workers; ++i) {
        total += work[i].partial;
        printf("  потік TID=%d: [%zu..%zu) -> %lld\n",
               (int)work[i].tid, work[i].range.start, work[i].range.end,
               work[i].partial);
    }
    printf("  спільна g_visits = %lld (усі потоки писали в ту саму комірку)\n",
           g_visits);
    printf("  tls_processed головного потоку = %lld з %zu"
           " (у кожного потоку своя копія)\n", tls_processed, n);

    *out = total;
    return 0;
}
