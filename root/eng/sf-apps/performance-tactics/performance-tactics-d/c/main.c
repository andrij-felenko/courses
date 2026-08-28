// Пул із N потоків тягне спільну чергу. Тепер водночас
// обробляється N запитів — чекання в черзі падає приблизно в N разів.
#define WORKERS 4

void *worker_loop(void *arg) {
    queue_t *q = (queue_t *)arg;
    request_t req;
    while (dequeue_blocking(q, &req)) {   // безпечний забір із черги
        handle_request(&req);             // чотири такі йдуть ОДНОЧАСНО
    }
    return NULL;
}

void serve_all_parallel(queue_t *q) {
    pthread_t th[WORKERS];
    for (int i = 0; i < WORKERS; i++)
        pthread_create(&th[i], NULL, worker_loop, q);
    for (int i = 0; i < WORKERS; i++)
        pthread_join(th[i], NULL);
}
