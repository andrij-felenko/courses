#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define COW_MAGIC 0x434F5731
#define COW_VERSION 1
#define SECTOR_SIZE 512
#define MAX_PATH_LEN 256

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint32_t version;
    uint64_t total_sectors;
    uint64_t bitmap_offset;
    uint64_t bitmap_bytes;
    uint64_t data_offset;
    char backing_path[MAX_PATH_LEN];
    uint8_t reserved[216];
} CowHeader;
#pragma pack(pop)

typedef struct CowNode {
    int fd;
    bool is_overlay;
    CowHeader header;
    uint8_t *bitmap;
    struct CowNode *backing_node;
} CowNode;

static inline bool bitmap_test(const uint8_t *bm, uint64_t sector) {
    return (bm[sector / 8] & (1 << (sector % 8))) != 0;
}

static inline void bitmap_set(uint8_t *bm, uint64_t sector) {
    bm[sector / 8] |= (1 << (sector % 8));
}
