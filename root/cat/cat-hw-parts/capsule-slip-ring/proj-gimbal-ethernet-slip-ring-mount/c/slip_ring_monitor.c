#include "slip_ring_monitor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>

uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

int init_monitor_socket(const char *ip, int port, struct sockaddr_in *dest_addr) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("Помилка створення сокета");
        return -1;
    }

    memset(dest_addr, 0, sizeof(*dest_addr));
    dest_addr->sin_family = AF_INET;
    dest_addr->sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &dest_addr->sin_addr) <= 0) {
        perror("Недійсна IP-адреса");
        close(sock);
        return -1;
    }

    return sock;
}

void update_stats(slip_ring_stats_t *stats, uint64_t latency_ns, int lost, uint32_t angle) {
    stats->current_angle_mdeg = angle;
    if (lost) {
        stats->total_sent++;
        stats->total_lost++;
    } else {
        stats->total_sent++;
        stats->total_received++;
        
        if (stats->min_latency_ns == 0 || latency_ns < stats->min_latency_ns) {
            stats->min_latency_ns = latency_ns;
        }
        if (latency_ns > stats->max_latency_ns) {
            stats->max_latency_ns = latency_ns;
        }
        
        // Потокове оновлення середнього
        stats->avg_latency_ns += (latency_ns - stats->avg_latency_ns) / stats->total_received;
    }
}

int main(int argc, char *argv[]) {
    const char *target_ip = (argc > 1) ? argv[1] : "127.0.0.1";
    int port = (argc > 2) ? atoi(argv[2]) : DEFAULT_PORT;

    struct sockaddr_in dest_addr;
    int sock = init_monitor_socket(target_ip, port, &dest_addr);
    if (sock < 0) {
        fprintf(stderr, "Не вдалося ініціалізувати мережевий сокет моніторингу ковзного кільця.\n");
        return 1;
    }

    printf("Моніторинг зв'язку через капсульне ковзне кільце запущено (адреса: %s:%d)\n", target_ip, port);

    slip_ring_stats_t stats = {0};
    uint64_t seq = 0;

    // Головний цикл моніторингу (симуляція роботи під час обертання)
    for (int i = 0; i < 100; i++) {
        slip_ring_packet_t pkt;
        pkt.sequence_number = seq++;
        pkt.send_timestamp_ns = get_time_ns();
        pkt.rotation_angle_mdeg = (i * 3600) % 360000; // Імітація обертання від 0 до 360 градусів

        ssize_t sent = sendto(sock, &pkt, sizeof(pkt), 0,
                              (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        if (sent < 0) {
            perror("Помилка надсилання пакету через ковзне кільце");
            update_stats(&stats, 0, 1, pkt.rotation_angle_mdeg);
        } else {
            // Симуляція отримання з невеликою затримкою та можливими втратами при обертанні
            uint64_t latency = 1200000ULL + (rand() % 800000ULL); // ~1.2-2.0 мс
            int lost = (rand() % 100 < 2); // 2% втрат через механічні вібрації контактів
            update_stats(&stats, latency, lost, pkt.rotation_angle_mdeg);
        }

        usleep(50000); // 50 мс інтервал між тестовими пакетами
    }

    printf("--- Підсумкова статистика ковзного кільця ---\n");
    printf("Всього надіслано: %llu\n", (unsigned long long)stats.total_sent);
    printf("Отримано: %llu\n", (unsigned long long)stats.total_received);
    printf("Втрачено пакетів: %llu (%.2f%%)\n", 
           (unsigned long long)stats.total_lost,
           stats.total_sent > 0 ? ((float)stats.total_lost / stats.total_sent) * 100.0f : 0.0f);
    printf("Мін затримка: %llu нс\n", (unsigned long long)stats.min_latency_ns);
    printf("Макс затримка: %llu нс\n", (unsigned long long)stats.max_latency_ns);
    printf("Середня затримка: %llu нс\n", (unsigned long long)stats.avg_latency_ns);

    close(sock);
    return 0;
}
