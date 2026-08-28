#include <fcntl.h>          /* O_PATH вимагає _GNU_SOURCE */

int dir = open("/proc/4242", O_PATH | O_DIRECTORY | O_CLOEXEC);
/* …через якийсь час, перед самим пострілом: */
int st = openat(dir, "stat", O_RDONLY | O_CLOEXEC);
if (st < 0) {
    /* та сама задача вже мертва — стріляти нікуди */
} else {
    /* жива; звіряємо ще й час старту (поле 22) — і одразу kill(pid, SIGTERM) */
}
