#include <sys/mman.h>
#include <errno.h>
#include <stdio.h>

/* Стан генератора випадкових чисел дитині не потрібен і шкідливий. */
int wipe_on_fork(void *area, size_t len)
{
        if (madvise(area, len, MADV_WIPEONFORK) == 0)
                return 0;
        if (errno == EINVAL) {
                /* Ділянка не приватна анонімна — цієї поради тут не буде НІКОЛИ.
                   Отже, або перевідображати, або обнуляти стан вручну після fork. */
                return -1;
        }
        perror("madvise(MADV_WIPEONFORK)");
        return -1;
}
