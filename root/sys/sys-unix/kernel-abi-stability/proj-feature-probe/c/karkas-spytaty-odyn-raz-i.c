#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/statfs.h>
#include <sys/syscall.h>
#include <unistd.h>

/* Клітинка стану: 0 — ще не питали, 1 — є, -1 — немає. */
static int probe_once(int *slot, int (*probe)(void))
{
    int v = __atomic_load_n(slot, __ATOMIC_ACQUIRE);
    if (v == 0) {
        int saved = errno;          /* проба не має права псувати чужий errno */
        v = probe() ? 1 : -1;
        errno = saved;
        __atomic_store_n(slot, v, __ATOMIC_RELEASE);
    }
    return v > 0;
}
