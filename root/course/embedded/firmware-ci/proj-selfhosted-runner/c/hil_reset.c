// hil_reset.c — фізичний скид плати смиканням лінії DTR (припаяна до NRST).
// Це «кнопка reset», натиснута програмно: гарантує ВІДОМИЙ стан перед прогоном.

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <termios.h>

// Притиснути NRST (чіп у скиді) на hold_ms, тоді відпустити (чіп стартує).
int hil_pulse_reset(const char *port, int hold_ms) {
    int fd = open(port, O_RDWR | O_NOCTTY);
    if (fd < 0) return -1;

    int flag = TIOCM_DTR;
    // Увага на полярність: на більшості USB-UART притиснутий DTR = LOW на піні,
    // а NRST активний саме LOW. Тому "set DTR" тягне чіп у скид. Якщо ваша плата
    // інвертує (буферами чи транзистором) — поміняйте set/clr місцями.
    ioctl(fd, TIOCMBIS, &flag);   // set DTR   → NRST LOW  → чіп у скиді
    usleep(hold_ms * 1000);
    ioctl(fd, TIOCMBIC, &flag);   // clr DTR   → NRST HIGH → чіп стартує

    close(fd);
    return 0;
}
