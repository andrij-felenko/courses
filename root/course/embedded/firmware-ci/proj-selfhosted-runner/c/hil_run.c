// hil_run.c — раннер боку хоста: чекає банер (чіп ожив?), читає вердикт із плати.
// Код виходу: 0 — PASS, 1 — FAIL (тести), 2 — чіп не ожив (карантин), 3 — ввід/вивід.

#include <stdio.h>
#include <stdlib.h>    // atoi, system
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <time.h>

#define BANNER  "HIL-READY v1"
#define PASS    "RESULT: PASS"
#define FAILPFX "RESULT: FAIL "

// Скид живе в hil_reset.c — лінкуємо разом; тут лише прототип.
int hil_pulse_reset(const char *port, int hold_ms);

// Налаштувати порт: 115200 8N1, сирий режим, читання з таймаутом.
static int open_serial(const char *port) {
    int fd = open(port, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) return -1;
    struct termios tio;
    if (tcgetattr(fd, &tio) != 0) { close(fd); return -1; }
    cfmakeraw(&tio);                       // без обробки — байти як є
    cfsetispeed(&tio, B115200);
    cfsetospeed(&tio, B115200);
    tio.c_cflag |= (CLOCAL | CREAD);       // ігнорувати модемні лінії, дозволити читання
    tcsetattr(fd, TCSANOW, &tio);
    return fd;
}

// Монотонний час у мілісекундах — щоб таймаут не збився від переводу годинника.
static long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

// Читати рядки з fd до deadline_ms; викликати on_line() на кожен повний рядок.
// Повертає 0, якщо on_line() сказав «досить» (повернув !=0), або -1 на таймауті.
static int read_lines_until(int fd, long deadline_ms,
                            int (*on_line)(const char *line, void *ctx), void *ctx) {
    char buf[256];
    size_t len = 0;
    while (now_ms() < deadline_ms) {
        char c;
        ssize_t r = read(fd, &c, 1);
        if (r == 1) {
            if (c == '\n' || len == sizeof(buf) - 1) {
                buf[len] = '\0';
                // прибрати хвостовий '\r' від "\r\n"
                if (len && buf[len - 1] == '\r') buf[len - 1] = '\0';
                if (on_line(buf, ctx)) return 0;   // рядок-мета знайдено
                len = 0;
            } else if (c != '\r') {
                buf[len++] = c;
            }
        } else {
            usleep(2000);   // порт порожній — не крутити CPU намарно
        }
    }
    return -1;   // дійшли до дедлайну, не знайшовши того, що шукали
}
