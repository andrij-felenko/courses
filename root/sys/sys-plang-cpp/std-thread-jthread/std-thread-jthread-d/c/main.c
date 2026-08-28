#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

void* worker_routine(void* arg) {
    int id = *(int*)arg;
    free(arg);
    printf("C worker thread %d is running\n", id);
    return NULL;
}

int launch_c_thread(int thread_id) {
    pthread_t thread_handle;
    int* arg = malloc(sizeof(int));
    if (!arg) return -1;
    *arg = thread_id;

    if (pthread_create(&thread_handle, NULL, worker_routine, arg) != 0) {
        free(arg);
        return -1;
    }

    // Блокуюче чекання завершення в стилі C
    pthread_join(thread_handle, NULL);
    return 0;
}
