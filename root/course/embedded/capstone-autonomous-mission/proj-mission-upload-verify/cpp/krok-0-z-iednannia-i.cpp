// mission_upload_verify.c — завантажити місію, зчитати назад, звірити, стежити.
// Той самий протокол, що й на pymavlink, але руками на MAVLink C library — так
// його пишуть у прошивці чи на компаньйон-компі, де pymavlink немає.
// Збірка: cc mission_upload_verify.c -I<тека_згенерованих_mavlink_заголовків> -lm
#include <mavlink/common/mavlink.h>   // згенеровані mavlink_msg_* (діалект common)
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>

#define SYSID  255                        // наш id як наземної станції (звично 255)
#define COMPID MAV_COMP_ID_MISSIONPLANNER
#define MTYPE  MAV_MISSION_TYPE_MISSION    // звичайна місія (не гео/ралі)

static int sock;
static struct sockaddr_in peer;           // куди відповідати: звідки прийшов пакет
static uint8_t TSYS, TCMP;                // id борту — дізнаємось із HEARTBEAT

static double now(void) {                 // монотонний час у секундах
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void open_udp(const char *ip, int port) {   // 'udpin' у pymavlink — це воно
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in a = {0};
    a.sin_family = AF_INET; a.sin_addr.s_addr = inet_addr(ip); a.sin_port = htons(port);
    bind(sock, (struct sockaddr*)&a, sizeof(a));
}

static void send_msg(mavlink_message_t *m) {        // спакувати й надіслати борту
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buf, m);
    sendto(sock, buf, len, 0, (struct sockaddr*)&peer, sizeof(peer));
}

// Головний помічник: чекати повне повідомлення з msgid ∈ want[], але НЕ довше timeout.
// Це C-відповідник pymavlink-івського recv_match(type=..., timeout=...).
static int recv_match(const uint8_t *want, int nwant,
                      mavlink_message_t *out, double timeout) {
    double deadline = now() + timeout;
    mavlink_message_t msg; mavlink_status_t st;
    for (;;) {
        double left = deadline - now();
        if (left <= 0) return 0;                    // таймаут — саме те, що рятує від зависання
        fd_set r; FD_ZERO(&r); FD_SET(sock, &r);
        struct timeval tv = { (long)left, (long)((left - (long)left) * 1e6) };
        if (select(sock + 1, &r, NULL, NULL, &tv) <= 0) return 0;
        uint8_t b[512]; socklen_t sl = sizeof(peer);
        int n = recvfrom(sock, b, sizeof(b), 0, (struct sockaddr*)&peer, &sl);
        for (int i = 0; i < n; i++)                 // згодувати байти парсеру
            if (mavlink_parse_char(MAVLINK_COMM_0, b[i], &msg, &st))   // зібрався кадр?
                for (int w = 0; w < nwant; w++)
                    if (msg.msgid == want[w]) { *out = msg; return 1; }
    }
}

static void wait_heartbeat(void) {        // без цього TSYS/TCMP невідомі
    mavlink_message_t hb;
    const uint8_t want[] = { MAVLINK_MSG_ID_HEARTBEAT };
    while (!recv_match(want, 1, &hb, 5.0)) { }      // чекати, поки не прийде
    TSYS = hb.sysid; TCMP = hb.compid;
    printf("звʼязок є: system=%u component=%u\n", TSYS, TCMP);
}
