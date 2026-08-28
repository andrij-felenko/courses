#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <linux/if_packet.h>

#define MAX_ENTRIES 256
#define GARP_BURST_LIMIT 3
#define FLIP_THRESHOLD_SEC 30

typedef struct {
    uint32_t ip;
    uint8_t mac[6];
    time_t last_seen;
    int garp_count;
    time_t garp_window_start;
    bool is_active;
} HostBinding;

static HostBinding g_bindings[MAX_ENTRIES];
static volatile sig_atomic_t g_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    g_running = 0;
}

static void format_mac(const uint8_t *mac, char *buf, size_t len) {
    snprintf(buf, len, "%02x:%02x:%02x:%02x:%02x:%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

static void format_ip(uint32_t ip, char *buf, size_t len) {
    struct in_addr addr;
    addr.s_addr = ip;
    inet_ntop(AF_INET, &addr, buf, len);
}

static HostBinding* find_or_create_binding(uint32_t ip, const uint8_t *mac, time_t now) {
    int free_slot = -1;
    for (int i = 0; i < MAX_ENTRIES; ++i) {
        if (g_bindings[i].is_active && g_bindings[i].ip == ip) {
            return &g_bindings[i];
        }
        if (!g_bindings[i].is_active && free_slot == -1) {
            free_slot = i;
        }
    }
    if (free_slot != -1) {
        g_bindings[free_slot].ip = ip;
        memcpy(g_bindings[free_slot].mac, mac, 6);
        g_bindings[free_slot].last_seen = now;
        g_bindings[free_slot].garp_count = 0;
        g_bindings[free_slot].garp_window_start = now;
        g_bindings[free_slot].is_active = true;
        return &g_bindings[free_slot];
    }
    return NULL;
}

static void inspect_arp_packet(const uint8_t *buffer, ssize_t len, uint32_t gateway_ip, const uint8_t *gateway_mac) {
    if (len < (ssize_t)(sizeof(struct ethhdr) + sizeof(struct ether_arp))) {
        return;
    }

    const struct ethhdr *eth = (const struct ethhdr *)buffer;
    const struct ether_arp *arp = (const struct ether_arp *)(buffer + sizeof(struct ethhdr));

    if (ntohs(eth->h_proto) != ETH_P_ARP) {
        return;
    }

    uint16_t htype = ntohs(arp->ea_hdr.ar_hrd);
    uint16_t ptype = ntohs(arp->ea_hdr.ar_pro);
    uint16_t opcode = ntohs(arp->ea_hdr.ar_op);

    if (htype != ARPHRD_ETHER || ptype != ETHERTYPE_IP) {
        return;
    }

    const uint8_t *eth_src = eth->h_source;
    const uint8_t *arp_sha = arp->arp_sha;
    uint32_t sender_ip;
    uint32_t target_ip;
    memcpy(&sender_ip, arp->arp_spa, sizeof(uint32_t));
    memcpy(&target_ip, arp->arp_tpa, sizeof(uint32_t));

    time_t now = time(NULL);
    char ip_str[INET_ADDRSTRLEN];
    char mac_str[18];
    char eth_mac_str[18];
    format_ip(sender_ip, ip_str, sizeof(ip_str));
    format_mac(arp_sha, mac_str, sizeof(mac_str));
    format_mac(eth_src, eth_mac_str, sizeof(eth_mac_str));

    /* Перевірка 1: відповідність MAC-адрес Ethernet та ARP */
    if (memcmp(eth_src, arp_sha, 6) != 0) {
        printf("[АЛАРМ: ПІДМІНА ЗАГОЛОВКА] Eth Src (%s) != ARP SHA (%s) для IP %s!\n",
               eth_mac_str, mac_str, ip_str);
    }

    /* Перевірка 2: захист шлюзу за замовчуванням */
    if (gateway_ip != 0 && sender_ip == gateway_ip) {
        if (memcmp(arp_sha, gateway_mac, 6) != 0) {
            char gw_mac_str[18];
            format_mac(gateway_mac, gw_mac_str, sizeof(gw_mac_str));
            printf("[КРИТИЧНИЙ АЛАРМ: ARP SPOOFING ШЛЮЗУ] Хост %s заявив IP шлюзу %s! Легітимний MAC: %s\n",
                   mac_str, ip_str, gw_mac_str);
            return;
        }
    }

    /* Перевірка 3: станковий аналіз змін MAC для динамічних хостів */
    HostBinding *entry = find_or_create_binding(sender_ip, arp_sha, now);
    if (entry != NULL) {
        if (memcmp(entry->mac, arp_sha, 6) != 0) {
            char old_mac_str[18];
            format_mac(entry->mac, old_mac_str, sizeof(old_mac_str));
            double diff = difftime(now, entry->last_seen);
            if (diff < FLIP_THRESHOLD_SEC) {
                printf("[АЛАРМ: MAC FLIP-FLOP] IP %s змінила прив'язку: %s -> %s за %.1f с!\n",
                       ip_str, old_mac_str, mac_str, diff);
            }
            memcpy(entry->mac, arp_sha, 6);
        }
        entry->last_seen = now;

        /* Перевірка 4: частота незапитаних Gratuitous ARP */
        if (sender_ip == target_ip && opcode == ARPOP_REPLY) {
            if (difftime(now, entry->garp_window_start) > 1.0) {
                entry->garp_window_start = now;
                entry->garp_count = 1;
            } else {
                entry->garp_count++;
                if (entry->garp_count > GARP_BURST_LIMIT) {
                    printf("[АЛАРМ: ШТОРМ GARP] Хост %s (%s) згенерував %d GARP за 1 с!\n",
                           ip_str, mac_str, entry->garp_count);
                }
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <інтерфейс> [шлюз_IP] [шлюз_MAC]\n", argv[0]);
        return 1;
    }

    const char *if_name = argv[1];
    uint32_t gw_ip = 0;
    uint8_t gw_mac[6] = {0};

    if (argc >= 4) {
        inet_pton(AF_INET, argv[2], &gw_ip);
        sscanf(argv[3], "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
               &gw_mac[0], &gw_mac[1], &gw_mac[2], &gw_mac[3], &gw_mac[4], &gw_mac[5]);
    }

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    int sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ARP));
    if (sock < 0) {
        perror("Помилка відкриття сокета AF_PACKET (потрібні права root / CAP_NET_RAW)");
        return 1;
    }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, if_name, IFNAMSIZ - 1);
    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("Помилка отримання індексу інтерфейсу");
        close(sock);
        return 1;
    }

    struct sockaddr_ll sll;
    memset(&sll, 0, sizeof(sll));
    sll.sll_family = AF_PACKET;
    sll.sll_ifindex = ifr.ifr_ifindex;
    sll.sll_protocol = htons(ETH_P_ARP);

    if (bind(sock, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
        perror("Помилка прив'язки сокета до інтерфейсу");
        close(sock);
        return 1;
    }

    printf("L2 ARP-монітор запущено на інтерфейсі %s...\n", if_name);
    uint8_t buffer[2048];

    while (g_running) {
        ssize_t bytes_read = recvfrom(sock, buffer, sizeof(buffer), 0, NULL, NULL);
        if (bytes_read > 0) {
            inspect_arp_packet(buffer, bytes_read, gw_ip, gw_mac);
        }
    }

    printf("\nЗупинка монітора...\n");
    close(sock);
    return 0;
}
