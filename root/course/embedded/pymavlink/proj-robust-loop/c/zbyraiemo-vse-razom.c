#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <time.h>
#include <signal.h>
#include <termios.h>
#include <unistd.h>
#include <common/mavlink.h>          // згенерована бібліотека MAVLink (діалект common)

#define DEVICE     "/dev/ttyUSB0"    // серійний до контролера
#define BAUD       B57600
#define LOOP_HZ    50                // такт головного циклу
#define LOOP_DT    (1.0 / LOOP_HZ)
#define MY_SYSID   1
#define MY_COMPID  MAV_COMP_ID_ONBOARD_COMPUTER

// --- дрібні помічники ---
static void sleep_s(double s) {
    struct timespec ts = { (time_t)s, (long)((s - (time_t)s) * 1e9) };
    nanosleep(&ts, NULL);
}
static int wait_readable(int fd, double timeout_s) {   // poll: >0 є дані, 0 таймаут, <0 помилка
    struct pollfd pfd = { .fd = fd, .events = POLLIN };
    return poll(&pfd, 1, (int)(timeout_s * 1000));
}
static int open_serial(const char *dev, speed_t baud) {
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);   // одразу неблокуючий
    if (fd < 0) return -1;
    struct termios tio;
    if (tcgetattr(fd, &tio) != 0) { close(fd); return -1; }
    cfmakeraw(&tio);                     // без обробки — сирі байти
    cfsetispeed(&tio, baud);
    cfsetospeed(&tio, baud);
    tio.c_cflag |= CLOCAL | CREAD;
    tio.c_cflag &= ~CRTSCTS;
    if (tcsetattr(fd, TCSANOW, &tio) != 0) { close(fd); return -1; }
    return fd;
}
static void send_own_heartbeat(int fd) {   // свій heartbeat: контролер бачить бортовий комп живим
    mavlink_message_t msg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_msg_heartbeat_pack(MY_SYSID, MY_COMPID, &msg,
        MAV_TYPE_ONBOARD_CONTROLLER, MAV_AUTOPILOT_INVALID, 0, 0, MAV_STATE_ACTIVE);
    uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);
    write(fd, buf, len);
}

int main(void) {
    signal(SIGINT, on_sigint);           // Ctrl+C → g_stop, а не миттєва смерть

    LinkState st;
    link_state_init(&st);
    rate_init(&setpoint_rate, 5.0);

    int fd = link_reconnect(DEVICE, -1, &st);   // перше підключення (той самий backoff)
    bool prev_alive = true;                      // link_connect уже стамкнув час → лінія жива
    RateLimiter own_hb;
    rate_init(&own_hb, 1.0);                      // СВІЙ heartbeat раз на секунду

    while (!g_stop) {
        // 5) ТРИМАТИ ТАКТ згори: poll блокує щонайбільше на LOOP_DT, але будить
        //    раніше, щойно прийшли дані — цикл не крутиться вхолосту й не спить наосліп
        wait_readable(fd, LOOP_DT);

        drain_link(fd, &st);                     // 1) ВИЧЕРПАТИ лінію (неблокуюче)

        bool alive = check_link(fd, &st, prev_alive);   // 2) ДЕТЕКТОР ОБРИВУ (за часом heartbeat)
        prev_alive = alive;

        if (!alive) {                            // 3) РЕКОНЕКТ (закривши стару лінію!)
            fd = link_reconnect(DEVICE, fd, &st);
            prev_alive = true;                   // link_connect стамкнув час → узгоджено з link_alive()
            continue;
        }

        if (rate_ready(&own_hb))                 // 4) ВЛАСНІ КОМАНДИ (rate-limited)
            send_own_heartbeat(fd);
        maybe_send_setpoint(fd, &st);            // навігаційні уставки, теж rate-limited
    }

    shutdown_link(fd, &st);                      // роззброїти (на землі) і закрити лінію
    return 0;
}
