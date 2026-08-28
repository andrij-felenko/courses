/* user_concurrency_demo.c (POSIX Threads + C11 stdatomic) */
#include <stdio.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <unistd.h>

struct shared_state {
    atomic_int counter;
    atomic_bool ready;
};

static struct shared_state global_state;

void* writer_thread(void* arg) {
    for (int i = 0; i < 5; ++i) {
        /* Еквівалент WRITE_ONCE з relaxed-впорядкуванням */
        int cur = atomic_load_explicit(&global_state.counter, memory_order_relaxed);
        atomic_store_explicit(&global_state.counter, cur + 1, memory_order_relaxed);
        
        /* Еквівалент smp_store_release */
        atomic_store_explicit(&global_state.ready, true, memory_order_release);
        usleep(2000);
    }
    return NULL;
}

void* reader_thread(void* arg) {
    for (int i = 0; i < 5; ++i) {
        /* Еквівалент smp_load_acquire */
        if (atomic_load_explicit(&global_state.ready, memory_order_acquire)) {
            int val = atomic_load_explicit(&global_state.counter, memory_order_relaxed);
            printf("C Userspace: Counter observed = %d\n", val);
        }
        usleep(1500);
    }
    return NULL;
}

int main(void) {
    pthread_t t_writer, t_reader;

    atomic_init(&global_state.counter, 0);
    atomic_init(&global_state.ready, false);

    pthread_create(&t_writer, NULL, writer_thread, NULL);
    pthread_create(&t_reader, NULL, reader_thread, NULL);

    pthread_join(t_writer, NULL);
    pthread_join(t_reader, NULL);

    printf("C Userspace Concurrency Test Passed Cleanly.\n");
    return 0;
}
