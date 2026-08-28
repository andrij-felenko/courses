#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int fd = open("/var/lib/app", O_TMPFILE | O_RDWR, 0600);
/* … пишемо в fd скільки треба; файл ніде не видно … */

char proc[64];
snprintf(proc, sizeof proc, "/proc/self/fd/%d", fd);
linkat(AT_FDCWD, proc, AT_FDCWD, "/var/lib/app/data.bin", AT_SYMLINK_FOLLOW);
