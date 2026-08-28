#define _GNU_SOURCE
#include <sys/mman.h>

/* терабайт адрес під розріджений індекс: у режимах 0 і 1 стелі обліку не займає */
void *sparse = mmap(NULL, 1UL << 40, PROT_READ | PROT_WRITE,
                    MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);

/* заплатити зараз, а не при першому запису: сторінки підставляють одразу */
void *hot = mmap(NULL, 64UL << 20, PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE, -1, 0);

if (sparse == MAP_FAILED || hot == MAP_FAILED) { /* errno == ENOMEM */ }
