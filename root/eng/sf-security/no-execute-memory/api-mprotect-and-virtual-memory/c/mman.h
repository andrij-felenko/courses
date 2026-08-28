#define _GNU_SOURCE
#include <sys/mman.h>

/* Виділення апаратного ключа захисту (повертає числовий індекс 1..15) */
int pkey_alloc(unsigned int flags, unsigned int access_rights);

/* Звільнення раніше виділеного ключа */
int pkey_free(int pkey);

/* Прив'язка діапазону сторінок до ключа pkey */
int pkey_mprotect(void *addr, size_t len, int prot, int pkey);
