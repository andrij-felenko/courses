#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <poll.h>

// ── Відкрити UART борту в неблокувальному режимі на потрібній швидкості ──
static int open_uart(const char *dev, speed_t baud) {
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) return -1;
    struct termios tio;
    tcgetattr(fd, &tio);
    cfmakeraw(&tio);                 // 8N1, без обробки — чисті байти MAVLink
    cfsetispeed(&tio, baud);
    cfsetospeed(&tio, baud);
    tcsetattr(fd, TCSANOW, &tio);
    return fd;
}

// ── Відкрити UDP-сокет, що СЛУХАЄ свій порт (станція шле нам сюди)
//    і запам'ятати адресу станції, коли від неї прийде перший кадр. ──
static int open_udp_listen(uint16_t port) {
    int s = socket(AF_INET, SOCK_DGRAM, 0);
    int yes = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in a = {0};
    a.sin_family = AF_INET;
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    a.sin_port = htons(port);
    bind(s, (struct sockaddr *)&a, sizeof(a));
    fcntl(s, F_SETFL, O_NONBLOCK);
    return s;
}

int main(void) {
    int fc = open_uart("/dev/serial0", B921600);     // борт
    int gcs1 = open_udp_listen(14550);               // станція 1
    int gcs2 = open_udp_listen(14551);               // станція 2

    // Куди слати станціям: дізнаємось із першого пакета кожної (поки не знаємо — мовчимо ЇЙ).
    struct sockaddr_in addr1 = {0}, addr2 = {0};
    socklen_t l1 = sizeof(addr1), l2 = sizeof(addr2);
    bool have1 = false, have2 = false;

    struct pollfd fds[3] = {
        { fc,   POLLIN, 0 },
        { gcs1, POLLIN, 0 },
        { gcs2, POLLIN, 0 },
    };
    uint8_t buf[2048];

    for (;;) {
        if (poll(fds, 3, 100) <= 0) continue;        // чекаємо на будь-яке джерело

        // 1) Від борту → копіюємо в ОБИДВІ станції (якщо знаємо їхні адреси).
        if (fds[0].revents & POLLIN) {
            ssize_t n = read(fc, buf, sizeof(buf));
            if (n > 0) {
                if (have1) sendto(gcs1, buf, n, 0, (struct sockaddr *)&addr1, l1);
                if (have2) sendto(gcs2, buf, n, 0, (struct sockaddr *)&addr2, l2);
            }
        }
        // 2) Від станції 1 → у борт (і фіксуємо її адресу для відповідей).
        if (fds[1].revents & POLLIN) {
            ssize_t n = recvfrom(gcs1, buf, sizeof(buf), 0,
                                 (struct sockaddr *)&addr1, &l1);
            if (n > 0) { have1 = true; write(fc, buf, n); }
        }
        // 3) Від станції 2 → у борт.
        if (fds[2].revents & POLLIN) {
            ssize_t n = recvfrom(gcs2, buf, sizeof(buf), 0,
                                 (struct sockaddr *)&addr2, &l2);
            if (n > 0) { have2 = true; write(fc, buf, n); }
        }
    }
}
