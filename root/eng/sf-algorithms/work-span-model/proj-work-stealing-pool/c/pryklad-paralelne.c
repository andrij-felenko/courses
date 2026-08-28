typedef struct SumArgs {
    const int *arr;
    size_t start;
    size_t end;
    long long *result;
    pthread_mutex_t *sync_lock;
    int *pending_count;
} SumArgs;

void parallel_sum_task(void *raw_args);

void parallel_sum_task(void *raw_args) {
    SumArgs *args = (SumArgs*)raw_args;
    size_t len = args->end - args->start;

    // Базовий випадок (послідовне підсумовування при малому розмірі)
    if (len <= 1000) {
        long long local_sum = 0;
        for (size_t i = args->start; i < args->end; ++i) {
            local_sum += args->arr[i];
        }
        pthread_mutex_lock(args->sync_lock);
        *args->result += local_sum;
        (*args->pending_count)--;
        pthread_mutex_unlock(args->sync_lock);
        free(args);
        return;
    }

    size_t mid = args->start + len / 2;
    SumArgs *left_args = (SumArgs*)malloc(sizeof(SumArgs));
    left_args->arr = args->arr;
    left_args->start = args->start;
    left_args->end = mid;
    left_args->result = args->result;
    left_args->sync_lock = args->sync_lock;
    left_args->pending_count = args->pending_count;

    SumArgs *right_args = (SumArgs*)malloc(sizeof(SumArgs));
    right_args->arr = args->arr;
    right_args->start = mid;
    right_args->end = args->end;
    right_args->result = args->result;
    right_args->sync_lock = args->sync_lock;
    right_args->pending_count = args->pending_count;

    pthread_mutex_lock(args->sync_lock);
    (*args->pending_count) += 2;
    (*args->pending_count)--; // поточна задача завершена
    pthread_mutex_unlock(args->sync_lock);

    parallel_sum_task(left_args);
    parallel_sum_task(right_args);

    free(args);
}
