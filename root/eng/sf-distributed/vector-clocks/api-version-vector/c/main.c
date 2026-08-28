#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define VV_FLAG_NONE       0x0000
#define VV_FLAG_PRUNED     0x0001
#define VV_FLAG_DVV        0x0002
#define VV_FLAG_COMPRESSED 0x0004

typedef enum {
    VV_CMP_EQUAL,       /* Вектори повністю ідентичні (A == B) */
    VV_CMP_DOMINATES,   /* Вектор A є новішим нащадком вектора B (A > B) */
    VV_CMP_DOMINATED,   /* Вектор A застарів і передує вектору B (A < B) */
    VV_CMP_CONCURRENT   /* Вектори мають паралельні зміни (A || B) */
} VersionCompareResult;

typedef struct {
    uint32_t node_id;
    uint64_t counter;
} VersionEntry;

typedef struct {
    uint16_t flags;
    uint32_t author_node_id; /* Для DVV: ідентифікатор вузла останнього запису */
    uint64_t author_counter; /* Для DVV: лічильник останнього запису */
    size_t count;
    size_t capacity;
    VersionEntry *entries;
} VersionVector;
