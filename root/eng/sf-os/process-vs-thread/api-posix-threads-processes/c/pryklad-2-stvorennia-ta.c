#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

typedef struct {
    int input_val;
    int result_val;
} ThreadData;

static void *worker_func(void *arg) {
    ThreadData *data = (ThreadData *)arg;
    printf("[Потік worker] Отримано значення: %d\n", data->input_val);
    data->result_val = data->input_val * 2;
    return (void *)(intptr_t)data->result_val;
}

int main(void) {
    pthread_t thread;
    ThreadData data = { .input_val = 21, .result_val = 0 };

    int err = pthread_create(&thread, NULL, worker_func, &data);
    if (err != 0) {
        fprintf(stderr, "Помилка pthread_create: %d\n", err);
        return EXIT_FAILURE;
    }

    void *retval = NULL;
    pthread_join(thread, &retval);

    printf("[Головний потік] Результат із пам'яті: %d, через retval: %ld\n",
           data.result_val, (long)(intptr_t)retval);

    return EXIT_SUCCESS;
}
