#include <sys/auxv.h>
#include <stdio.h>
#include <errno.h>

void safe_get_auxv(void) {
    errno = 0;
    unsigned long val = getauxval(AT_SECURE);
    int err = errno;

    if (val == 0 && err == ENOENT) {
        printf("Ключ AT_SECURE відсутній у auxv\n");
    } else {
        printf("Значення AT_SECURE: %lu\n", val);
    }
}
