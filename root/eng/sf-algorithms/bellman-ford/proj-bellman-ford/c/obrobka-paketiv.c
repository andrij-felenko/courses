#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define RIP_INFINITY 16
#define MAX_ROUTES 256

typedef struct {
    uint32_t dest_ip;
    uint32_t metric;
} RipEntry;

typedef struct {
    uint8_t command; // 1 = Request, 2 = Response
    uint8_t version; // 2
    uint16_t zero;
    RipEntry entries[25];
    uint8_t num_entries;
} RipPacket;

typedef struct {
    uint32_t dest_ip;
    uint32_t next_hop;
    uint32_t metric;
    uint32_t timeout_seconds;
} RouteTableEntry;

void process_rip_update(RouteTableEntry* table, int* table_size, uint32_t sender_ip, const RipPacket* packet) {
    for (int i = 0; i < packet->num_entries; ++i) {
        uint32_t dest = packet->entries[i].dest_ip;
        uint32_t new_metric = packet->entries[i].metric + 1;
        if (new_metric > RIP_INFINITY) new_metric = RIP_INFINITY;

        bool found = false;
        for (int j = 0; j < *table_size; ++j) {
            if (table[j].dest_ip == dest) {
                found = true;
                // Релаксація Беллмана-Форда
                if (table[j].next_hop == sender_ip || new_metric < table[j].metric) {
                    table[j].metric = new_metric;
                    table[j].next_hop = sender_ip;
                    table[j].timeout_seconds = 180; // Скидання таймера
                }
                break;
            }
        }

        if (!found && new_metric < RIP_INFINITY && *table_size < MAX_ROUTES) {
            table[*table_size].dest_ip = dest;
            table[*table_size].next_hop = sender_ip;
            table[*table_size].metric = new_metric;
            table[*table_size].timeout_seconds = 180;
            (*table_size)++;
        }
    }
}
