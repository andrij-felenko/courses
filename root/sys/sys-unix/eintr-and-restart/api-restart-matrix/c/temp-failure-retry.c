#define _GNU_SOURCE
#include <errno.h>
#include <unistd.h>

/* так це визначено в glibc: */
#define TEMP_FAILURE_RETRY(expression)                     \
    (__extension__ ({ long int __result;                   \
       do __result = (long int) (expression);              \
       while (__result == -1L && errno == EINTR);          \
       __result; }))

ssize_t n = TEMP_FAILURE_RETRY(read(fd, buf, len));
