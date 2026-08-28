/*
 * RSS Toeplitz Hash & RETA Simulator (C Edition)
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RSS_KEY_SIZE 40
#define RETA_SIZE 128
#define MAX_QUEUES 8

/* Стандартний секретний ключ RSS (Microsoft NDIS default key) */
static const uint8_t default_rss_key[RSS_KEY_SIZE] = {
    0x6d, 0x5a, 0x56, 0xda, 0x25, 0x5b, 0x0e, 0xc2,
    0x41, 0x67, 0x25, 0x3d, 0x43, 0xa3, 0x8f, 0x00,
    0xd0, 0x29, 0x4b, 0x7d, 0x3d, 0x14, 0x4e, 0x69,
    0x9f, 0xac, 0xe5, 0x42, 0x1d, 0x64, 0x52, 0x72,
    0x0f, 0x4c, 0xf7, 0xad, 0x55, 0x54, 0x03, 0xb9
};

/* Структура 4-tuple для TCP/IPv4 */
typedef struct {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t src_port;
    uint16_t dst_port;
} flow_tuple_v4_t;

/* Обчислення Toeplitz Hash для довільного бінарного буфера */
uint32_t calculate_toeplitz_hash(const uint8_t *input, size_t input_len, const uint8_t *key) {
    uint32_t hash = 0;
    
    for (size_t byte_idx = 0; byte_idx < input_len; byte_idx++) {
        uint8_t byte = input[byte_idx];
        for (int bit = 7; bit >= 0; bit--) {
            if ((byte >> bit) & 1) {
                /* Витягуємо 32-бітний шматок ключа, починаючи з поточного біта */
                size_t key_byte_idx = byte_idx + (7 - bit) / 8;
                int key_bit_shift = (7 - bit) % 8;
                
                uint32_t key_window = 
                    ((uint32_t)key[key_byte_idx] << (24 + key_bit_shift)) |
                    ((uint32_t)key[key_byte_idx + 1] << (16 + key_bit_shift)) |
                    ((uint32_t)key[key_byte_idx + 2] << (8 + key_bit_shift)) |
                    ((uint32_t)key[key_byte_idx + 3] << key_bit_shift);
                
                if (key_bit_shift > 0) {
                    key_window |= ((uint32_t)key[key_byte_idx + 4] >> (8 - key_bit_shift));
                }
                
                hash ^= key_window;
            }
        }
    }
    
    return hash;
}

/* Ініціалізація RETA таблиці рівномірним розподілом */
void init_reta_equal(uint8_t reta[RETA_SIZE], uint8_t num_queues) {
    for (int i = 0; i < RETA_SIZE; i++) {
        reta[i] = (uint8_t)(i % num_queues);
    }
}

int main(void) {
    uint8_t reta[RETA_SIZE];
    init_reta_equal(reta, 4); /* 4 апаратні черги: Rx 0..3 */

    /* Прямий потік: Client (192.168.1.50:49152) -> Server (10.0.0.1:80) */
    flow_tuple_v4_t flow_fwd = {
        .src_ip = 0xC0A80132,   /* 192.168.1.50 */
        .dst_ip = 0x0A000001,   /* 10.0.0.1 */
        .src_port = 0xC000,     /* 49152 */
        .dst_port = 0x0050      /* 80 */
    };

    /* Зворотний потік: Server (10.0.0.1:80) -> Client (192.168.1.50:49152) */
    flow_tuple_v4_t flow_rev = {
        .src_ip = 0x0A000001,   /* 10.0.0.1 */
        .dst_ip = 0xC0A80132,   /* 192.168.1.50 */
        .src_port = 0x0050,     /* 80 */
        .dst_port = 0xC000      /* 49152 */
    };

    /* Упаковка 4-tuple у байтовий масив для Toeplitz (12 байтів для IPv4 4-tuple) */
    uint8_t input_fwd[12];
    uint8_t input_rev[12];

    /* Формат NDIS IPv4 4-tuple: SrcIP (4B), DstIP (4B), SrcPort (2B), DstPort (2B) */
    memcpy(&input_fwd[0], &flow_fwd.src_ip, 4);
    memcpy(&input_fwd[4], &flow_fwd.dst_ip, 4);
    memcpy(&input_fwd[8], &flow_fwd.src_port, 2);
    memcpy(&input_fwd[10], &flow_fwd.dst_port, 2);

    memcpy(&input_rev[0], &flow_rev.src_ip, 4);
    memcpy(&input_rev[4], &flow_rev.dst_ip, 4);
    memcpy(&input_rev[8], &flow_rev.src_port, 2);
    memcpy(&input_rev[10], &flow_rev.dst_port, 2);

    uint32_t hash_fwd = calculate_toeplitz_hash(input_fwd, sizeof(input_fwd), default_rss_key);
    uint32_t hash_rev = calculate_toeplitz_hash(input_rev, sizeof(input_rev), default_rss_key);

    /* Індекс RETA: 7 молодших бітів (LSB) */
    uint8_t reta_idx_fwd = hash_fwd & 0x7F;
    uint8_t reta_idx_rev = hash_rev & 0x7F;

    printf("FWD Flow Hash: 0x%08X -> RETA Index: %3d -> Target Rx Queue: %d\n",
           hash_fwd, reta_idx_fwd, reta[reta_idx_fwd]);
    printf("REV Flow Hash: 0x%08X -> RETA Index: %3d -> Target Rx Queue: %d\n",
           hash_rev, reta_idx_rev, reta[reta_idx_rev]);

    return 0;
}
