#include "attenuator.h"

#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#define ACK_TIMEOUT_MS  250.0
#define MAX_RETRIES     3

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec * 1e-6;
}

static bool port_configure(int fd)
{
    struct termios tio;
    if (tcgetattr(fd, &tio) != 0) { perror("tcgetattr"); return false; }

    cfmakeraw(&tio);                       /* прилад чекає байти, а не рядки термінала */
    cfsetispeed(&tio, B115200);
    cfsetospeed(&tio, B115200);
    tio.c_cflag |= CLOCAL | CREAD;
    tio.c_cflag &= ~(unsigned)CRTSCTS;
    tio.c_cflag &= ~(unsigned)PARENB;
    tio.c_cflag &= ~(unsigned)CSTOPB;
    tio.c_cc[VMIN]  = 0;
    tio.c_cc[VTIME] = 0;                   /* читання неблокуюче, чекає автомат */

    if (tcsetattr(fd, TCSANOW, &tio) != 0) { perror("tcsetattr"); return false; }
    tcflush(fd, TCIOFLUSH);
    return true;
}

/* Синхронний обмін лише на етапі відкриття: тут ще можна дозволити собі чекати. */
static bool ask_identity(int fd, char *out, size_t out_size)
{
    static const char q[] = "*IDN?\n";
    if (write(fd, q, sizeof q - 1) != (ssize_t)(sizeof q - 1)) {
        perror("write *IDN?");
        return false;
    }

    size_t got = 0;
    double until = now_ms() + 1000.0;
    while (now_ms() < until) {
        ssize_t r = read(fd, out + got, out_size - 1 - got);
        if (r > 0) {
            got += (size_t)r;
            out[got] = '\0';
            if (memchr(out, '\n', got)) return true;
            if (got + 1 >= out_size) break;
        } else if (r < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("read *IDN?");
            return false;
        } else {
            struct timespec pause = {0, 5 * 1000 * 1000};
            nanosleep(&pause, NULL);
        }
    }
    fprintf(stderr, "атенюатор мовчить на *IDN?\n");
    return false;
}

bool attenuator_open(attenuator_t *a, const char *device)
{
    memset(a, 0, sizeof *a);
    a->fd = -1;

    int fd = open(device, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) { perror(device); return false; }
    if (!port_configure(fd)) { close(fd); return false; }

    char idn[128] = {0};
    if (!ask_identity(fd, idn, sizeof idn)) { close(fd); return false; }
    for (char *p = idn; *p; ++p) if (*p == '\r' || *p == '\n') { *p = '\0'; break; }
    fprintf(stderr, "атенюатор: %s\n", idn);

    a->fd = fd;
    a->state = ATT_IDLE;
    a->current_db = ATT_MAX_DB;

    /* Стартуємо з максимального загасання: доки рівень не порахований,
     * вхідний малошумний підсилювач приймача не повинен бачити нічого. */
    if (!attenuator_request(a, ATT_MAX_DB)) { attenuator_close(a); return false; }
    while (attenuator_busy(a)) {
        attenuator_poll(a);
        if (a->state == ATT_FAILED) { attenuator_close(a); return false; }
    }
    return true;
}

void attenuator_close(attenuator_t *a)
{
    if (a->fd >= 0) {
        /* Останній рух — знову в максимум, щоб від'єднання не лишило
         * приймач під повним рівнем із SDR. */
        char cmd[32];
        int n = snprintf(cmd, sizeof cmd, ":ATT:VAL %.2f\n", ATT_MAX_DB);
        if (n > 0) (void)write(a->fd, cmd, (size_t)n);
        close(a->fd);
        a->fd = -1;
    }
    a->state = ATT_IDLE;
}

bool attenuator_request(attenuator_t *a, double db)
{
    if (a->state == ATT_FAILED) return false;
    if (a->state != ATT_IDLE)   return false;      /* попередня команда ще в дорозі */

    if (db < 0.0)        db = 0.0;
    if (db > ATT_MAX_DB) db = ATT_MAX_DB;
    db = round(db / ATT_STEP_DB) * ATT_STEP_DB;    /* прилад крокує по 0.25 дБ */

    if (fabs(db - a->current_db) < ATT_STEP_DB / 2.0) return true;   /* нічого не змінилось */

    a->pending_db = db;
    /* «;*OPC?» змушує прилад підтвердити, що крок відпрацював, — без цього
     * ми не знаємо, коли рівень справді змінився. */
    int n = snprintf(a->tx, sizeof a->tx, ":ATT:VAL %.2f;*OPC?\n", db);
    if (n <= 0 || (size_t)n >= sizeof a->tx) {
        fprintf(stderr, "команда SCPI не вміщується в буфер\n");
        return false;
    }
    a->tx_len = (size_t)n;
    a->tx_sent = 0;
    a->rx_len = 0;
    a->retries = 0;
    a->state = ATT_SENDING;
    return true;
}

static void restart_command(attenuator_t *a)
{
    a->tx_sent = 0;
    a->rx_len = 0;
    a->state = ATT_SENDING;
    tcflush(a->fd, TCIFLUSH);
}

void attenuator_poll(attenuator_t *a)
{
    if (a->state == ATT_IDLE || a->state == ATT_FAILED) return;

    if (a->state == ATT_SENDING) {
        while (a->tx_sent < a->tx_len) {
            ssize_t w = write(a->fd, a->tx + a->tx_sent, a->tx_len - a->tx_sent);
            if (w > 0) {
                a->tx_sent += (size_t)w;
            } else if (w < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
                return;                     /* буфер драйвера повний, доб'ємо наступного разу */
            } else {
                perror("write SCPI");
                a->state = ATT_FAILED;
                return;
            }
        }
        a->commands++;
        a->deadline_ms = now_ms() + ACK_TIMEOUT_MS;
        a->state = ATT_WAIT_ACK;
    }

    if (a->state == ATT_WAIT_ACK) {
        for (;;) {
            if (a->rx_len + 1 >= sizeof a->rx) {   /* сміття без переводу рядка */
                a->rx_len = 0;
            }
            ssize_t r = read(a->fd, a->rx + a->rx_len, sizeof a->rx - 1 - a->rx_len);
            if (r > 0) {
                a->rx_len += (size_t)r;
                a->rx[a->rx_len] = '\0';
                char *nl = memchr(a->rx, '\n', a->rx_len);
                if (nl) {
                    *nl = '\0';
                    if (strchr(a->rx, '1')) {
                        a->current_db = a->pending_db;
                        a->state = ATT_IDLE;
                    } else {
                        fprintf(stderr, "атенюатор відповів «%s» замість підтвердження\n", a->rx);
                        a->state = ATT_FAILED;
                    }
                    return;
                }
                continue;
            }
            if (r < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
                perror("read SCPI");
                a->state = ATT_FAILED;
                return;
            }
            break;                                   /* даних поки немає */
        }

        if (now_ms() > a->deadline_ms) {
            a->timeouts++;
            if (++a->retries >= MAX_RETRIES) {
                fprintf(stderr, "атенюатор не підтвердив %.2f дБ після %d спроб\n",
                        a->pending_db, MAX_RETRIES);
                a->state = ATT_FAILED;
            } else {
                restart_command(a);
            }
        }
    }
}
