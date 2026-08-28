#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_NODES 64
#define MAX_KEYS_PER_NODE 32
#define MAX_STR_LEN 64
#define MTU_PAYLOAD_LIMIT 1200

/* Окремий атрибут стану вузла */
typedef struct {
    char key[MAX_STR_LEN];
    char value[MAX_STR_LEN];
    uint64_t version;
} VersionedValue;

/* Повний стан одного конкретного вузла */
typedef struct {
    char node_id[MAX_STR_LEN];
    uint64_t generation;
    uint64_t max_version;
    VersionedValue values[MAX_KEYS_PER_NODE];
    size_t value_count;
} EndpointState;

/* Елемент дайджесту для швидкого порівняння версій */
typedef struct {
    char node_id[MAX_STR_LEN];
    uint64_t generation;
    uint64_t max_version;
} GossipDigest;

/* Окреме оновлення конкретного ключа для передачі мережею */
typedef struct {
    char node_id[MAX_STR_LEN];
    uint64_t generation;
    char key[MAX_STR_LEN];
    char value[MAX_STR_LEN];
    uint64_t version;
} GossipDelta;

/* Локальне сховище знань про весь кластер */
typedef struct {
    char local_node_id[MAX_STR_LEN];
    EndpointState nodes[MAX_NODES];
    size_t node_count;
} ScuttlebuttEngine;
