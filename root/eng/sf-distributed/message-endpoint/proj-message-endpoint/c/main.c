#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_WORKERS 3
#define QUEUE_CAPACITY 100
#define MAX_ID_LEN 64

typedef enum { ACK_UNPROCESSED, ACK_ACKED, ACK_NACKED, ACK_DLQ } AckStatus;

typedef struct {
    char id[MAX_ID_LEN];
    char partition_key[MAX_ID_LEN];
    char account_id[MAX_ID_LEN];
    char action[16];
    unsigned long amount_cents;
} CMessage;

typedef struct {
    char message_id[MAX_ID_LEN];
    AckStatus status;
} CAckHandle;

typedef struct {
    CMessage items[QUEUE_CAPACITY];
    CAckHandle handles[QUEUE_CAPACITY];
    int head, tail, count;
    pthread_mutex_t lock;
    pthread_cond_t cv;
    pthread_t thread;
    bool running;
} CWorkerQueue;

typedef struct {
    char ids[1000][MAX_ID_LEN];
    int count;
    pthread_mutex_t lock;
} CInbox;

CInbox g_inbox;
CWorkerQueue g_workers[NUM_WORKERS];

bool inbox_try_claim(const char* id) {
    pthread_mutex_lock(&g_inbox.lock);
    for (int i = 0; i < g_inbox.count; ++i) {
        if (strcmp(g_inbox.ids[i], id) == 0) {
            pthread_mutex_unlock(&g_inbox.lock);
            return false; // Дубль
        }
    }
    if (g_inbox.count < 1000) {
        strncpy(g_inbox.ids[g_inbox.count++], id, MAX_ID_LEN - 1);
    }
    pthread_mutex_unlock(&g_inbox.lock);
    return true;
}

unsigned int hash_key(const char* s) {
    unsigned int h = 5381;
    while (*s) h = ((h << 5) + h) + (unsigned char)(*s++);
    return h % NUM_WORKERS;
}

void* worker_thread_func(void* arg) {
    int wid = (int)(intptr_t)arg;
    CWorkerQueue* q = &g_workers[wid];

    while (true) {
        CMessage msg;
        CAckHandle handle;

        pthread_mutex_lock(&q->lock);
        while (q->count == 0 && q->running) {
            pthread_cond_wait(&q->cv, &q->lock);
        }
        if (!q->running && q->count == 0) {
            pthread_mutex_unlock(&q->lock);
            break;
        }

        msg = q->items[q->head];
        handle = q->handles[q->head];
        q->head = (q->head + 1) % QUEUE_CAPACITY;
        q->count--;
        pthread_mutex_unlock(&q->lock);

        // Дедуплікація
        if (!inbox_try_claim(msg.id)) {
            printf("  [C-Worker %d] ДУБЛІКАТ %s -> ACK\n", wid, msg.id);
            continue;
        }

        // Бізнес-логіка
        if (msg.amount_cents == 0 && strcmp(msg.action, "CREATE") != 0) {
            printf("  [C-Worker %d] ОТРУЙНИЙ ПАКЕТ %s -> DLQ\n", wid, msg.id);
        } else {
            printf("  [C-Worker %d] Оброблено %s для %s (%lu коп.) -> ACK\n", 
                   wid, msg.action, msg.account_id, msg.amount_cents);
        }
    }
    return NULL;
}

int main(void) {
    printf("=== C11 Реалізація Message Endpoint ===\n\n");
    pthread_mutex_init(&g_inbox.lock, NULL);
    g_inbox.count = 0;

    for (intptr_t i = 0; i < NUM_WORKERS; ++i) {
        g_workers[i].head = g_workers[i].tail = g_workers[i].count = 0;
        g_workers[i].running = true;
        pthread_mutex_init(&g_workers[i].lock, NULL);
        pthread_cond_init(&g_workers[i].cv, NULL);
        pthread_create(&g_workers[i].thread, NULL, worker_thread_func, (void*)i);
    }

    CMessage test_msgs[] = {
        {"c-msg-1", "Acc#10", "Acc#10", "CREATE", 0},
        {"c-msg-2", "Acc#10", "Acc#10", "DEPOSIT", 5000},
        {"c-msg-2", "Acc#10", "Acc#10", "DEPOSIT", 5000}, // Дубль
        {"c-msg-3", "Acc#10", "Acc#10", "WITHDRAW", 0}   // Отруйний
    };

    for (int i = 0; i < 4; ++i) {
        unsigned int wid = hash_key(test_msgs[i].partition_key);
        CWorkerQueue* q = &g_workers[wid];
        pthread_mutex_lock(&q->lock);
        q->items[q->tail] = test_msgs[i];
        strncpy(q->handles[q->tail].message_id, test_msgs[i].id, MAX_ID_LEN - 1);
        q->tail = (q->tail + 1) % QUEUE_CAPACITY;
        q->count++;
        pthread_cond_signal(&q->cv);
        pthread_mutex_unlock(&q->lock);
    }

    usleep(200000); // 200 мс

    for (int i = 0; i < NUM_WORKERS; ++i) {
        pthread_mutex_lock(&g_workers[i].lock);
        g_workers[i].running = false;
        pthread_cond_signal(&g_workers[i].cv);
        pthread_mutex_unlock(&g_workers[i].lock);
        pthread_join(g_workers[i].thread, NULL);
    }
    printf("\nУсі C-воркери завершили роботу.\n");
    return 0;
}
