#include <fcntl.h>
#include <string.h>

/* 0 — поспали й прокинулися; 1 — подія завадила; -1 — помилка. */
static int suspend_if_idle(void)
{
    char buf[32];
    int fd, n;

    /* Читання блокується, поки ядро дообробляє події, що вже в польоті. */
    fd = open("/sys/power/wakeup_count", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    n = read(fd, buf, sizeof buf - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = '\0';

    /* ... тут ухвалюємо рішення: чи справді нам немає чого робити ... */

    fd = open("/sys/power/wakeup_count", O_WRONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    n = write(fd, buf, strlen(buf));
    close(fd);
    if (n < 0)
        return errno == EINVAL ? 1 : -1;

    fd = open("/sys/power/state", O_WRONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    n = write(fd, "mem", 3);           /* повернеться вже після пробудження */
    close(fd);
    return n < 0 ? -1 : 0;
}
