#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/prctl.h>

typedef struct {
    uint64_t account_id;
    double balance;
    pthread_mutex_t lock;
} Account;

typedef struct {
    uint64_t tx_id;
    Account *src;
    Account *dst;
    double amount;
    volatile bool cancel_flag;
} TransferTask;

static Account g_account_a = { .account_id = 101, .balance = 10000.0, .lock = PTHREAD_MUTEX_INITIALIZER };
static Account g_account_b = { .account_id = 202, .balance = 10000.0, .lock = PTHREAD_MUTEX_INITIALIZER };

static void *worker_thread_1(void *arg) {
    TransferTask *task = (TransferTask *)arg;
    pthread_setname_np(pthread_self(), "tx-worker-A2B");

    printf("[Worker 1] Стартує переказ #%lu: рахунок %lu -> %lu\n",
           task->tx_id, task->src->account_id, task->dst->account_id);

    pthread_mutex_lock(&task->src->lock);
    printf("[Worker 1] Захоплено рахунок %lu, пауза перед наступним захопленням...\n", task->src->account_id);
    usleep(100000); // 100 мс затримки для надійного відтворення гонитви

    printf("[Worker 1] Спроба захопити рахунок %lu...\n", task->dst->account_id);
    pthread_mutex_lock(&task->dst->lock);

    // Критична секція переказу коштів
    task->src->balance -= task->amount;
    task->dst->balance += task->amount;

    pthread_mutex_unlock(&task->dst->lock);
    pthread_mutex_unlock(&task->src->lock);

    printf("[Worker 1] Переказ #%lu успішно завершено!\n", task->tx_id);
    return NULL;
}

static void *worker_thread_2(void *arg) {
    TransferTask *task = (TransferTask *)arg;
    pthread_setname_np(pthread_self(), "tx-worker-B2A");

    printf("[Worker 2] Стартує переказ #%lu: рахунок %lu -> %lu\n",
           task->tx_id, task->src->account_id, task->dst->account_id);

    pthread_mutex_lock(&task->src->lock);
    printf("[Worker 2] Захоплено рахунок %lu, пауза перед наступним захопленням...\n", task->src->account_id);
    usleep(100000); // 100 мс затримки

    printf("[Worker 2] Спроба захопити рахунок %lu...\n", task->dst->account_id);
    pthread_mutex_lock(&task->dst->lock);

    // Критична секція переказу коштів
    task->src->balance -= task->amount;
    task->dst->balance += task->amount;

    pthread_mutex_unlock(&task->dst->lock);
    pthread_mutex_unlock(&task->src->lock);

    printf("[Worker 2] Переказ #%lu успішно завершено!\n", task->tx_id);
    return NULL;
}

int main(void) {
    // Дозволяємо трасування не-нащадкам для сумісності з Yama ptrace_scope=1
    prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);

    printf("=== Платіжний вузол запущено (PID: %d) ===\n", getpid());
    printf("Адреси м'ютексів: Account A (%p), Account B (%p)\n",
           (void *)&g_account_a.lock, (void *)&g_account_b.lock);

    TransferTask task1 = { .tx_id = 9001, .src = &g_account_a, .dst = &g_account_b, .amount = 150.0, .cancel_flag = false };
    TransferTask task2 = { .tx_id = 9002, .src = &g_account_b, .dst = &g_account_a, .amount = 300.0, .cancel_flag = false };

    pthread_t th1, th2;
    pthread_create(&th1, NULL, worker_thread_1, &task1);
    pthread_create(&th2, NULL, worker_thread_2, &task2);

    pthread_join(th1, NULL);
    pthread_join(th2, NULL);

    printf("Усі транзакції завершено. Баланс A: %.2f, B: %.2f\n",
           g_account_a.balance, g_account_b.balance);
    return 0;
}
