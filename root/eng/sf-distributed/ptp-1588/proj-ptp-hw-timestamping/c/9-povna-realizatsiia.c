#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/net_tstamp.h>
#include <linux/ptp_clock.h>
#include <time.h>

#define PTP_EVENT_PORT 319
#define PTP_MULTICAST_IP "224.0.1.129"
#define FD_TO_CLOCKID(fd) ((clockid_t)((((unsigned int) ~fd) << 3) | 3))

static int configure_hwtstamp(int sock, const char *ifname) {
    struct hwtstamp_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.tx_type = HWTSTAMP_TX_ON;
    cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1);
    ifr.ifr_data = (char *)&cfg;

    if (ioctl(sock, SIOCSHWTSTAMP, &ifr) < 0) {
        perror("SIOCSHWTSTAMP");
        return -1;
    }
    return 0;
}

static int extract_hw_timestamp(struct msghdr *msg, struct timespec *out_ts) {
    for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(msg); cmsg != NULL; cmsg = CMSG_NXTHDR(msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct timespec *ts_arr = (struct timespec *)CMSG_DATA(cmsg);
            // ts_arr[2] - сира апаратна мітка від PHC
            if (ts_arr[2].tv_sec != 0 || ts_arr[2].tv_nsec != 0) {
                *out_ts = ts_arr[2];
                return 0;
            }
        }
    }
    return -1;
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";
    const char *ptp_dev = (argc > 2) ? argv[2] : "/dev/ptp0";

    // 1. Відкриття PTP сокета
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    // Дозвіл повторного використання порту
    int reuse = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    // Прив'язка до порту подій 319
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PTP_EVENT_PORT);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        return EXIT_FAILURE;
    }

    // 2. Налаштування апаратного фільтра PHY/MAC
    if (configure_hwtstamp(sock, ifname) < 0) {
        fprintf(stderr, "Попередження: апаратний таймстемпінг недоступний на %s\n", ifname);
    }

    // 3. Увімкнення SO_TIMESTAMPING
    int ts_flags = SOF_TIMESTAMPING_TX_HARDWARE |
                   SOF_TIMESTAMPING_RX_HARDWARE |
                   SOF_TIMESTAMPING_RAW_HARDWARE |
                   SOF_TIMESTAMPING_OPT_TSONLY;
    if (setsockopt(sock, SOL_SOCKET, SO_TIMESTAMPING, &ts_flags, sizeof(ts_flags)) < 0) {
        perror("setsockopt SO_TIMESTAMPING");
        close(sock);
        return EXIT_FAILURE;
    }

    // 4. Підключення до апаратного годинника PHC
    int ptp_fd = open(ptp_dev, O_RDWR);
    if (ptp_fd >= 0) {
        clockid_t clkid = FD_TO_CLOCKID(ptp_fd);
        struct timespec cur_time;
        if (clock_gettime(clkid, &cur_time) == 0) {
            printf("Поточний час PHC (%s): %ld.%09ld s\n", ptp_dev, cur_time.tv_sec, cur_time.tv_nsec);
        }
        close(ptp_fd);
    }

    // 5. Відправлення тестового повідомлення Sync (44 байти)
    uint8_t ptp_sync_msg[44];
    memset(ptp_sync_msg, 0, sizeof(ptp_sync_msg));
    ptp_sync_msg[0] = 0x00; // messageType = 0 (Sync)
    ptp_sync_msg[1] = 0x02; // versionPTP = 2
    ptp_sync_msg[2] = 0x00;
    ptp_sync_msg[3] = 44;   // messageLength = 44
    ptp_sync_msg[6] = 0x02; // flagField[0] = twoStepFlag (0x02)

    struct sockaddr_in dst_addr;
    memset(&dst_addr, 0, sizeof(dst_addr));
    dst_addr.sin_family = AF_INET;
    dst_addr.sin_port = htons(PTP_EVENT_PORT);
    inet_pton(AF_INET, PTP_MULTICAST_IP, &dst_addr.sin_addr);

    ssize_t sent = sendto(sock, ptp_sync_msg, sizeof(ptp_sync_msg), 0,
                          (struct sockaddr *)&dst_addr, sizeof(dst_addr));
    if (sent < 0) {
        perror("sendto");
    } else {
        printf("Відправлено повідомлення Sync (%zd байтів)\n", sent);
    }

    // 6. Отримання TX-мітки з MSG_ERRQUEUE через poll
    struct pollfd pfd;
    pfd.fd = sock;
    pfd.events = POLLERR | POLLPRI;
    pfd.revents = 0;

    int poll_res = poll(&pfd, 1, 500); // 500 мс таймаут
    if (poll_res > 0 && (pfd.revents & (POLLERR | POLLPRI))) {
        char control_buf[512];
        struct msghdr err_msg;
        struct iovec err_iov;
        uint8_t err_data[256];

        memset(&err_msg, 0, sizeof(err_msg));
        err_iov.iov_base = err_data;
        err_iov.iov_len = sizeof(err_data);
        err_msg.msg_iov = &err_iov;
        err_msg.msg_iovlen = 1;
        err_msg.msg_control = control_buf;
        err_msg.msg_controllen = sizeof(control_buf);

        if (recvmsg(sock, &err_msg, MSG_ERRQUEUE) >= 0) {
            struct timespec tx_ts;
            if (extract_hw_timestamp(&err_msg, &tx_ts) == 0) {
                printf("Успішно захоплено точну мітку TX (t1): %ld.%09ld s\n", tx_ts.tv_sec, tx_ts.tv_nsec);
            }
        }
    }

    close(sock);
    return EXIT_SUCCESS;
}
