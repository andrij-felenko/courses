/* link_monitor.c — Моніторинг параметрів PHY та виявлення Duplex Mismatch */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

#define ETH_GSTRING_LEN 32

/* Структура для збереження лічильників помилок */
struct error_stats {
    unsigned long long late_collisions;
    unsigned long long crc_errors;
    unsigned long long align_errors;
    unsigned long long tx_packets;
};

/* Отримання назв статистичних лічильників адаптера */
static struct ethtool_gstrings* get_stat_strings(int fd, const char* ifname, int* n_stats) {
    struct {
        struct ethtool_sset_info hdr;
        unsigned int buf[1];
    } sset_info;
    memset(&sset_info, 0, sizeof(sset_info));
    sset_info.hdr.cmd = ETHTOOL_GSSET_INFO;
    sset_info.hdr.sset_mask = 1ULL << ETH_SS_STATS;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)&sset_info;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        return NULL;
    }
    if (!sset_info.hdr.sset_mask) {
        return NULL;
    }

    *n_stats = sset_info.hdr.data[0];
    if (*n_stats == 0) {
        return NULL;
    }

    size_t sz = sizeof(struct ethtool_gstrings) + (*n_stats) * ETH_GSTRING_LEN;
    struct ethtool_gstrings* strings = (struct ethtool_gstrings*)malloc(sz);
    if (!strings) {
        return NULL;
    }

    memset(strings, 0, sz);
    strings->cmd = ETHTOOL_GSTRINGS;
    strings->string_set = ETH_SS_STATS;
    strings->len = *n_stats;

    ifr.ifr_data = (char*)strings;
    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        free(strings);
        return NULL;
    }

    return strings;
}

/* Зчитування поточних значень лічильників помилок */
static int read_error_stats(int fd, const char* ifname, const struct ethtool_gstrings* strings,
                            int n_stats, struct error_stats* out_stats) {
    memset(out_stats, 0, sizeof(*out_stats));
    if (!strings || n_stats <= 0) {
        return -1;
    }

    size_t sz = sizeof(struct ethtool_stats) + n_stats * sizeof(unsigned long long);
    struct ethtool_stats* stats = (struct ethtool_stats*)malloc(sz);
    if (!stats) {
        return -1;
    }

    memset(stats, 0, sz);
    stats->cmd = ETHTOOL_GSTATS;
    stats->n_stats = n_stats;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)stats;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        free(stats);
        return -1;
    }

    for (int i = 0; i < n_stats; ++i) {
        const char* name = (const char*)&strings->data[i * ETH_GSTRING_LEN];
        unsigned long long val = stats->data[i];

        if (strstr(name, "late_collision") || strstr(name, "tx_late_collision")) {
            out_stats->late_collisions += val;
        } else if (strstr(name, "crc_error") || strstr(name, "rx_crc_errors")) {
            out_stats->crc_errors += val;
        } else if (strstr(name, "align_error") || strstr(name, "rx_align_errors")) {
            out_stats->align_errors += val;
        } else if (strstr(name, "tx_packets") || strstr(name, "tx_ok")) {
            out_stats->tx_packets += val;
        }
    }

    free(stats);
    return 0;
}

/* Опитування параметрів лінка через ETHTOOL_GSET */
static int print_link_status(int fd, const char* ifname, int* out_duplex) {
    struct ethtool_cmd ecmd;
    memset(&ecmd, 0, sizeof(ecmd));
    ecmd.cmd = ETHTOOL_GSET;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)&ecmd;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        perror("Помилка ioctl(ETHTOOL_GSET)");
        return -1;
    }

    *out_duplex = ecmd.duplex;
    unsigned int speed = ethtool_cmd_speed(&ecmd);

    printf("=== Інтерфейс %s ===\n", ifname);
    printf("Швидкість:        ");
    if (speed == (unsigned int)-1 || speed == 0) {
        printf("Невідома (Link Down)\n");
    } else {
        printf("%u Мбіт/с\n", speed);
    }

    printf("Дуплекс:          %s\n", (ecmd.duplex == DUPLEX_FULL) ? "Full Duplex" :
                                      (ecmd.duplex == DUPLEX_HALF) ? "Half Duplex" : "Невідомо");
    printf("Автопогодження:   %s\n", (ecmd.autoneg == AUTONEG_ENABLE) ? "Увімкнено (Enabled)" : "Вимкнено (Disabled)");

    printf("Режим MDI/MDI-X:  ");
    switch (ecmd.eth_tp_mdix) {
        case ETH_TP_MDI:   printf("MDI (прямий)\n"); break;
        case ETH_TP_MDI_X: printf("MDI-X (перехресний)\n"); break;
        default:           printf("Автовизначення / Не підтримується\n"); break;
    }

    return 0;
}

int main(int argc, char** argv) {
    const char* ifname = (argc > 1) ? argv[1] : "eth0";

    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        perror("Не вдалося створити діагностичний сокет");
        return 1;
    }

    int duplex_mode = DUPLEX_HALF;
    if (print_link_status(fd, ifname, &duplex_mode) < 0) {
        close(fd);
        return 1;
    }

    int n_stats = 0;
    struct ethtool_gstrings* strings = get_stat_strings(fd, ifname, &n_stats);
    if (!strings) {
        printf("Апаратна статистика ETHTOOL_GSTATS недоступна для %s\n", ifname);
        close(fd);
        return 0;
    }

    printf("\nЗапуск моніторингу помилок Duplex Mismatch (Ctrl+C для виходу)...\n");
    struct error_stats prev_stats, curr_stats;
    read_error_stats(fd, ifname, strings, n_stats, &prev_stats);

    for (int sec = 1; sec <= 10; ++sec) {
        sleep(1);
        if (read_error_stats(fd, ifname, strings, n_stats, &curr_stats) < 0) {
            break;
        }

        unsigned long long d_late = curr_stats.late_collisions - prev_stats.late_collisions;
        unsigned long long d_crc = curr_stats.crc_errors - prev_stats.crc_errors;

        if (d_late > 0 || d_crc > 0) {
            printf("[УВАГА +%ds] Пізні колізії: +%llu, Помилки CRC: +%llu -> ",
                   sec, d_late, d_crc);
            if (d_late > 5 && duplex_mode == DUPLEX_HALF) {
                printf("КРИТИЧНО: Duplex Mismatch (ми в Half Duplex, партнер у Full Duplex)!\n");
            } else if (d_crc > 5 && duplex_mode == DUPLEX_FULL) {
                printf("КРИТИЧНО: Duplex Mismatch (ми у Full Duplex, партнер у Half Duplex)!\n");
            } else {
                printf("Зафіксовано поодинокі збої лінії.\n");
            }
        } else {
            printf("[OK +%ds] Колізій та помилок CRC немає.\n", sec);
        }

        prev_stats = curr_stats;
    }

    free(strings);
    close(fd);
    return 0;
}
