#ifndef SLIP_RING_MONITOR_H
#define SLIP_RING_MONITOR_H

#include <stdint.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>

#define MAX_PACKET_SIZE 1024
#define DEFAULT_PORT 8080

typedef struct {
    uint64_t sequence_number;
    uint64_t send_timestamp_ns;
    uint32_t rotation_angle_mdeg; // Міліградуси повороту підвісу
} slip_ring_packet_t;

typedef struct {
    uint64_t total_sent;
    uint64_t total_received;
    uint64_t total_lost;
    uint64_t min_latency_ns;
    uint64_t max_latency_ns;
    uint64_t avg_latency_ns;
    uint32_t current_angle_mdeg;
} slip_ring_stats_t;

int init_monitor_socket(const char *ip, int port, struct sockaddr_in *dest_addr);
uint64_t get_time_ns(void);
void update_stats(slip_ring_stats_t *stats, uint64_t latency_ns, int lost, uint32_t angle);

#endif // SLIP_RING_MONITOR_H
