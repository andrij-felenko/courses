#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>

#define NUM_TRANSFERS 500000

SafeAccount g_acc1;
SafeAccount g_acc2;

void* worker_1_to_2(void *arg) {
    (void)arg;
    for (int i = 0; i < NUM_TRANSFERS; ++i) {
        safe_account_transfer(&g_acc1, &g_acc2, 10);
    }
    return NULL;
}

void* worker_2_to_1(void *arg) {
    (void)arg;
    for (int i = 0; i < NUM_TRANSFERS; ++i) {
        safe_account_transfer(&g_acc2, &g_acc1, 10);
    }
    return NULL;
}

int main(void) {
    safe_account_init(&g_acc1, 100000);
    safe_account_init(&g_acc2, 100000);

    pthread_t threads[8];
    for (int i = 0; i < 4; ++i) {
        pthread_create(&threads[i], NULL, worker_1_to_2, NULL);
        pthread_create(&threads[i + 4], NULL, worker_2_to_1, NULL);
    }

    for (int i = 0; i < 8; ++i) {
        pthread_join(threads[i], NULL);
    }

    int64_t total = g_acc1.balance + g_acc2.balance;
    printf("Баланс 1: %lld, Баланс 2: %lld, Разом: %lld (Очікувалося: 200000)\n",
           (long long)g_acc1.balance, (long long)g_acc2.balance, (long long)total);

    safe_account_destroy(&g_acc1);
    safe_account_destroy(&g_acc2);
    return (total == 200000) ? 0 : 1;
}
