#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_ITERATIONS 100000

typedef struct {
    int user_id;
    long long hits;
    char *session_tag;
} UserStats;

static UserStats *g_stats = NULL;
static int g_enable_probe_logging = 0;

void *worker_updater(void *arg) {
    long thread_id = (long)arg;
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            // Спостережницький ефект: виклик I/O серіалізує доступ
            // і затримує потік на системному виклику write()
            printf("[Thread %ld] Processing iteration %d\n", thread_id, i);
        }

        UserStats *s = g_stats;
        if (s != NULL) {
            // Гонка даних: паралельний запис без синхронізації
            s->hits++;
            if (i % 1000 == 0) {
                // Тимчасове перепризначення вказівника
                char *old_tag = s->session_tag;
                s->session_tag = (i % 2000 == 0) ? "session_alpha" : "session_beta";
                // Потенційне читання розірваного значення іншим потоком
                (void)old_tag;
            }
        }
    }
    return NULL;
}

void *worker_allocator(void *arg) {
    (void)arg;
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            printf("[Allocator] Reallocating buffer at %d\n", i);
        }

        UserStats *fresh = (UserStats *)malloc(sizeof(UserStats));
        if (!fresh) continue;
        fresh->user_id = 42;
        fresh->hits = 0;
        fresh->session_tag = "session_init";

        UserStats *old = g_stats;
        // Неатомарна публікація нового вказівника
        g_stats = fresh;

        if (old != NULL) {
            // Коротка затримка або негайне звільнення
            free(old);
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc > 1 && argv[1][0] == '1') {
        g_enable_probe_logging = 1;
        printf("[INFO] Probe logging ENABLED (Observation mode)\n");
    } else {
        printf("[INFO] Running in NATIVE mode (No logging)\n");
    }

    g_stats = (UserStats *)malloc(sizeof(UserStats));
    g_stats->user_id = 42;
    g_stats->hits = 0;
    g_stats->session_tag = "root";

    pthread_t t1, t2;
    pthread_create(&t1, NULL, worker_updater, (void *)1);
    pthread_create(&t2, NULL, worker_allocator, (void *)2);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    if (g_stats) free(g_stats);
    printf("[DONE] Completed test successfully.\n");
    return 0;
}
