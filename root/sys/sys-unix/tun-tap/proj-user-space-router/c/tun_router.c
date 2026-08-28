/* tun_router.c — Реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <linux/if.h>
#include <linux/if_tun.h>

#define MAX_EVENTS 8
#define BUF_SIZE 2048

/* Обчислення контрольної суми IP/ICMP за формулою доповнення до одиниці */
static uint16_t checksum(const void *data, size_t len) {
    const uint16_t *buf = (const uint16_t *)data;
    uint32_t sum = 0;
    while (len > 1) {
        sum += *buf++;
        len -= 2;
    }
    if (len == 1) {
        sum += *(const uint8_t *)buf;
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum);
}

/* Відкриття та налаштування TUN пристрою */
static int tun_alloc(char *dev, int flags) {
    struct ifreq ifr;
    int fd, err;

    if ((fd = open("/dev/net/tun", O_RDWR)) < 0) {
        perror("Failed to open /dev/net/tun");
        return -1;
    }

    memset(&ifr, 0, sizeof(ifr));
    ifr.ifr_flags = flags;

    if (*dev) {
        strncpy(ifr.ifr_name, dev, IFNAMSIZ - 1);
    }

    if ((err = ioctl(fd, TUNSETIFF, (void *)&ifr)) < 0) {
        perror("ioctl(TUNSETIFF) failed");
        close(fd);
        return -1;
    }

    strcpy(dev, ifr.ifr_name);
    return fd;
}

/* Переведення файлового дескриптора в неблокуючий режим */
static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* Обробка IPv4 пакета та генерація ICMP Echo Reply */
static void process_packet(int tun_fd, uint8_t *buf, ssize_t len) {
    if (len < (ssize_t)sizeof(struct iphdr)) return;

    struct iphdr *iph = (struct iphdr *)buf;
    if (iph->version != 4 || iph->protocol != IPPROTO_ICMP) return;

    size_t ip_hdr_len = iph->ihl * 4;
    if (len < (ssize_t)(ip_hdr_len + sizeof(struct icmphdr))) return;

    struct icmphdr *icmph = (struct icmphdr *)(buf + ip_hdr_len);

    /* Перевіряємо, чи це ICMP Echo Request */
    if (icmph->type == ICMP_ECHO) {
        /* Міняємо місцями Src IP та Dst IP */
        uint32_t tmp_ip = iph->saddr;
        iph->saddr = iph->daddr;
        iph->daddr = tmp_ip;

        /* Міняємо тип ICMP на Echo Reply */
        icmph->type = ICMP_ECHOREPLY;
        icmph->checksum = 0;
        
        /* Перераховуємо контрольну суму ICMP */
        size_t icmp_len = len - ip_hdr_len;
        icmph->checksum = checksum(icmph, icmp_len);

        /* Перераховуємо контрольну суму IP */
        iph->check = 0;
        iph->check = checksum(iph, ip_hdr_len);

        /* Відправляємо пакет назад у TUN */
        ssize_t written = write(tun_fd, buf, len);
        if (written > 0) {
            printf("[C] ICMP Echo Reply sent back (%zd bytes)\n", written);
        }
    }
}

int main(void) {
    char dev_name[IFNAMSIZ] = "tun0";
    int tun_fd = tun_alloc(dev_name, IFF_TUN | IFF_NO_PI);
    if (tun_fd < 0) return EXIT_FAILURE;

    printf("[C] TUN interface %s created (fd=%d)\n", dev_name, tun_fd);
    if (set_nonblocking(tun_fd) < 0) {
        perror("Failed to set non-blocking");
        close(tun_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1 failed");
        close(tun_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = tun_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, tun_fd, &ev) < 0) {
        perror("epoll_ctl failed");
        close(epoll_fd);
        close(tun_fd);
        return EXIT_FAILURE;
    }

    uint8_t buffer[BUF_SIZE];
    printf("[C] Event loop started. Run in terminal:\n");
    printf("    sudo ip link set %s up\n", dev_name);
    printf("    sudo ip addr add 10.0.0.1/24 dev %s\n", dev_name);
    printf("    ping 10.0.0.2\n");

    for (int i = 0; i < 5; ++i) { /* Обробляємо кілька подій для демонстрації */
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 5000);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait error");
            break;
        }

        for (int n = 0; n < nfds; ++n) {
            if (events[n].data.fd == tun_fd) {
                while (1) {
                    ssize_t bytes_read = read(tun_fd, buffer, sizeof(buffer));
                    if (bytes_read < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        perror("read from tun failed");
                        break;
                    }
                    process_packet(tun_fd, buffer, bytes_read);
                }
            }
        }
    }

    close(epoll_fd);
    close(tun_fd);
    printf("[C] TUN router finished cleanly.\n");
    return EXIT_SUCCESS;
}
