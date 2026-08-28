#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <sys/socket.h>

#define MSG_TYPE_DATA 0x01
#define MSG_TYPE_PING 0x02
#define MSG_TYPE_PONG 0x03

typedef struct {
    int fd;
    time_t last_rx_time;
    time_t ping_sent_time;
    int ping_pending;
    int ping_interval_sec;
    int pong_timeout_sec;
} heartbeat_tracker_t;

void heartbeat_init(heartbeat_tracker_t *hb, int fd, int interval_sec, int timeout_sec) {
    hb->fd = fd;
    hb->last_rx_time = time(NULL);
    hb->ping_sent_time = 0;
    hb->ping_pending = 0;
    hb->ping_interval_sec = interval_sec;
    hb->pong_timeout_sec = timeout_sec;
}

void heartbeat_on_rx(heartbeat_tracker_t *hb, unsigned char msg_type) {
    hb->last_rx_time = time(NULL);
    if (msg_type == MSG_TYPE_PONG) {
        hb->ping_pending = 0;
    } else if (msg_type == MSG_TYPE_PING) {
        // Негайно відповідаємо PONG у відповідь на PING
        unsigned char pong = MSG_TYPE_PONG;
        send(hb->fd, &pong, 1, MSG_NOSIGNAL);
    }
}

int heartbeat_tick(heartbeat_tracker_t *hb) {
    time_t now = time(NULL);

    if (hb->ping_pending) {
        if (now - hb->ping_sent_time >= hb->pong_timeout_sec) {
            // Таймаут очікування PONG перевищено — з'єднання мертве
            return -1;
        }
    } else {
        if (now - hb->last_rx_time >= hb->ping_interval_sec) {
            // Прийшов час надіслати PING
            unsigned char ping = MSG_TYPE_PING;
            if (send(hb->fd, &ping, 1, MSG_NOSIGNAL) == 1) {
                hb->ping_pending = 1;
                hb->ping_sent_time = now;
            } else {
                return -1;
            }
        }
    }
    return 0;
}
