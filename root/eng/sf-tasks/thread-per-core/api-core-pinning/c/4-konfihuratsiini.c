#include <liburing.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Ініціалізація екземпляра io_uring для потоку ядра */
int init_tpc_ring(struct io_uring *ring, unsigned entries, int cpu_id) {
    struct io_uring_params params;
    memset(&params, 0, sizeof(params));
    params.flags = IORING_SETUP_SQPOLL | IORING_SETUP_SQ_AFFINITY;
    params.sq_thread_cpu = cpu_id;
    params.sq_thread_idle = 2000; /* Час очікування ядра в мілісекундах */

    return io_uring_queue_init_params(entries, ring, &params);
}
