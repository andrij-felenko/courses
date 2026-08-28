#define _GNU_SOURCE
#include <fcntl.h>

struct flock fl = {
    .l_type   = F_WRLCK,
    .l_whence = SEEK_SET,
    .l_start  = 0,
    .l_len    = 0,       /* 0 — до кінця файлу */
    .l_pid    = 0        /* Обов'язково 0 для OFD */
};

/* Взяти OFD-замок */
fcntl(fd, F_OFD_SETLKW, &fl);
