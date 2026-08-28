#define _GNU_SOURCE
#include <aio.h>

void aio_init(const struct aioinit *init);

struct aioinit {
    int aio_threads;    /* стеля робочих потоків;      усталено 20, мінімум 1  */
    int aio_num;        /* очікуваних одночасних запитів; усталено 64, мін. 32 */
    int aio_locks;      /* не вживається */
    int aio_usedba;     /* не вживається */
    int aio_debug;      /* не вживається */
    int aio_numusers;   /* не вживається */
    int aio_idle_time;  /* секунд простою до смерті потоку; усталено 1         */
    int aio_reserved;
};
