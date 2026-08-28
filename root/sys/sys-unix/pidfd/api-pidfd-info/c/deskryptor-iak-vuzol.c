#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>

static int same_process(int a, int b, int *same) {
    struct statx sa, sb;
    if (statx(a, "", AT_EMPTY_PATH, STATX_INO, &sa) < 0) return -1;
    if (statx(b, "", AT_EMPTY_PATH, STATX_INO, &sb) < 0) return -1;
    *same = (sa.stx_ino == sb.stx_ino);
    return 0;
}
