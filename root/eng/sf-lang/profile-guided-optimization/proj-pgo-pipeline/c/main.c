// main.c — Диспетчер мережевих пакетів мовою C
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

typedef enum {
    PKT_DATA = 0,
    PKT_CONTROL = 1,
    PKT_CORRUPTED = 2
} PacketType;

typedef struct Packet {
    PacketType type;
    uint32_t payload_len;
    uint8_t payload[64];
} Packet;

typedef struct PacketHandler {
    uint64_t (*process)(const Packet* pkt, void* ctx);
    void* ctx;
} PacketHandler;

static uint64_t handle_data(const Packet* pkt, void* ctx) {
    (void)ctx;
    uint64_t acc = 0;
    for (uint32_t i = 0; i < pkt->payload_len; ++i) {
        acc = (acc * 33) ^ pkt->payload[i];
    }
    return acc;
}

static uint64_t handle_control(const Packet* pkt, void* ctx) {
    (void)ctx;
    return (uint64_t)pkt->payload_len * 0x9e3779b97f4a7c15ULL;
}

static uint64_t handle_corrupted(const Packet* pkt, void* ctx) {
    (void)ctx;
    // Холодний шлях: імітація складного логування
    fprintf(stderr, "Log error: corrupted packet length %u\n", pkt->payload_len);
    return 0;
}

#define TOTAL_PACKETS 5000000

int main(int argc, char** argv) {
    PacketHandler handlers[3] = {
        { handle_data, NULL },
        { handle_control, NULL },
        { handle_corrupted, NULL }
    };

    Packet* stream = (Packet*)malloc(sizeof(Packet) * TOTAL_PACKETS);
    if (!stream) return 1;

    // Ініціалізація нерівномірного розподілу трафіку (98% data, 1.5% control, 0.5% corrupted)
    srand(42);
    for (size_t i = 0; i < TOTAL_PACKETS; ++i) {
        int r = rand() % 1000;
        if (r < 980) {
            stream[i].type = PKT_DATA;
            stream[i].payload_len = 32;
        } else if (r < 995) {
            stream[i].type = PKT_CONTROL;
            stream[i].payload_len = 16;
        } else {
            stream[i].type = PKT_CORRUPTED;
            stream[i].payload_len = 4;
        }
        for (uint32_t j = 0; j < stream[i].payload_len; ++j) {
            stream[i].payload[j] = (uint8_t)(j + i);
        }
    }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    uint64_t total_checksum = 0;
    for (size_t i = 0; i < TOTAL_PACKETS; ++i) {
        PacketHandler* h = &handlers[stream[i].type];
        // Поліморфний непрямий виклик через покажчик
        total_checksum += h->process(&stream[i], h->ctx);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) * 1e-9;

    printf("Checksum: 0x%llx, Time: %.4f s\n", (unsigned long long)total_checksum, elapsed);

    free(stream);
    return 0;
}
