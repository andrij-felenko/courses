#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define CHAR_OFFSET 31
#define BLOCK_SIZE 64
#define HASH_TABLE_SIZE 1024

/* 64-бітний сильний хеш FNV-1a для демонстрації */
static uint64_t fnv1a_64(const uint8_t *data, size_t len) {
    uint64_t hash = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < len; ++i) {
        hash ^= data[i];
        hash *= 0x100000001b3ULL;
    }
    return hash;
}

/* Структура 32-бітного ковзного хешу rollsum */
typedef struct {
    uint16_t a;
    uint16_t b;
} Rollsum;

static inline void rollsum_init(Rollsum *r, const uint8_t *buf, size_t len) {
    uint32_t a = 0;
    uint32_t b = 0;
    for (size_t i = 0; i < len; ++i) {
        uint32_t val = (uint32_t)buf[i] + CHAR_OFFSET;
        a += val;
        b += (uint32_t)(len - i) * val;
    }
    r->a = (uint16_t)(a & 0xffff);
    r->b = (uint16_t)(b & 0xffff);
}

static inline void rollsum_rotate(Rollsum *r, uint8_t out_byte, uint8_t in_byte, size_t len) {
    uint32_t out_val = (uint32_t)out_byte + CHAR_OFFSET;
    uint32_t in_val = (uint32_t)in_byte + CHAR_OFFSET;
    
    r->a = (uint16_t)((r->a - out_val + in_val) & 0xffff);
    r->b = (uint16_t)((r->b - (uint32_t)len * out_val + r->a) & 0xffff);
}

static inline uint32_t rollsum_digest(const Rollsum *r) {
    return ((uint32_t)r->b << 16) | (uint32_t)r->a;
}

/* Сигнатура блоку цільового файлу */
typedef struct BlockSig {
    uint32_t block_index;
    uint32_t rollsum;
    uint64_t strong_hash;
    struct BlockSig *next;
} BlockSig;

typedef struct {
    BlockSig *buckets[HASH_TABLE_SIZE];
} SigTable;

static void sig_table_init(SigTable *table) {
    memset(table->buckets, 0, sizeof(table->buckets));
}

static void sig_table_insert(SigTable *table, uint32_t index, uint32_t rsum, uint64_t strong) {
    uint32_t bucket = (rsum ^ (rsum >> 10)) % HASH_TABLE_SIZE;
    BlockSig *node = (BlockSig *)malloc(sizeof(BlockSig));
    if (!node) return;
    node->block_index = index;
    node->rollsum = rsum;
    node->strong_hash = strong;
    node->next = table->buckets[bucket];
    table->buckets[bucket] = node;
}

static int sig_table_find(const SigTable *table, uint32_t rsum, uint64_t strong) {
    uint32_t bucket = (rsum ^ (rsum >> 10)) % HASH_TABLE_SIZE;
    for (BlockSig *curr = table->buckets[bucket]; curr; curr = curr->next) {
        if (curr->rollsum == rsum && curr->strong_hash == strong) {
            return (int)curr->block_index;
        }
    }
    return -1;
}

static void sig_table_free(SigTable *table) {
    for (size_t i = 0; i < HASH_TABLE_SIZE; ++i) {
        BlockSig *curr = table->buckets[i];
        while (curr) {
            BlockSig *tmp = curr->next;
            free(curr);
            curr = tmp;
        }
        table->buckets[i] = NULL;
    }
}

/* Генерація дельти між двома буферами в пам'яті */
static void generate_delta(const uint8_t *target, size_t target_len,
                           const uint8_t *source, size_t source_len) {
    SigTable table;
    sig_table_init(&table);

    /* 1. Фаза побудови сигнатур цільового файлу B */
    size_t num_blocks = (target_len + BLOCK_SIZE - 1) / BLOCK_SIZE;
    for (size_t i = 0; i < num_blocks; ++i) {
        size_t offset = i * BLOCK_SIZE;
        size_t b_len = (offset + BLOCK_SIZE <= target_len) ? BLOCK_SIZE : (target_len - offset);
        
        Rollsum r;
        rollsum_init(&r, target + offset, b_len);
        uint64_t strong = fnv1a_64(target + offset, b_len);
        
        sig_table_insert(&table, (uint32_t)i, rollsum_digest(&r), strong);
    }

    /* 2. Фаза сканування джерела A ковзним вікном */
    size_t src_pos = 0;
    size_t literal_start = 0;
    size_t literal_len = 0;

    Rollsum window_sum;
    bool window_valid = false;

    while (src_pos + BLOCK_SIZE <= source_len) {
        if (!window_valid) {
            rollsum_init(&window_sum, source + src_pos, BLOCK_SIZE);
            window_valid = true;
        } else {
            rollsum_rotate(&window_sum, source[src_pos - 1], source[src_pos + BLOCK_SIZE - 1], BLOCK_SIZE);
        }

        uint32_t rsum = rollsum_digest(&window_sum);
        int matched_block = -1;

        /* Швидка перевірка: чи є такий rollsum у таблиці */
        uint32_t bucket = (rsum ^ (rsum >> 10)) % HASH_TABLE_SIZE;
        if (table.buckets[bucket]) {
            uint64_t strong = fnv1a_64(source + src_pos, BLOCK_SIZE);
            matched_block = sig_table_find(&table, rsum, strong);
        }

        if (matched_block >= 0) {
            /* Якщо були накопичені літеральні байти, видаємо їх */
            if (literal_len > 0) {
                printf("[LITERAL %zu байтів на зміщенні %zu]\n", literal_len, literal_start);
                literal_len = 0;
            }
            printf("[MATCH блок %d на зміщенні %zu]\n", matched_block, src_pos);
            src_pos += BLOCK_SIZE;
            window_valid = false;
            literal_start = src_pos;
        } else {
            if (literal_len == 0) literal_start = src_pos;
            literal_len++;
            src_pos++;
        }
    }

    /* Залишкові байти в кінці файлу */
    literal_len += (source_len - src_pos);
    if (literal_len > 0) {
        printf("[LITERAL %zu байтів на зміщенні %zu]\n", literal_len, literal_start);
    }

    sig_table_free(&table);
}

int main(void) {
    const uint8_t target[] = "The quick brown fox jumps over the lazy dog. "
                             "Systems programming with rsync and ssh provides "
                             "reliable data transfer for all production systems.";
    const uint8_t source[] = "PREFIX_INSERTED_DATA: "
                             "The quick brown fox jumps over the lazy dog. "
                             "Systems programming with rsync and ssh provides "
                             "MODIFIED data transfer for all production systems.";

    generate_delta(target, strlen((const char *)target),
                   source, strlen((const char *)source));
    return 0;
}
