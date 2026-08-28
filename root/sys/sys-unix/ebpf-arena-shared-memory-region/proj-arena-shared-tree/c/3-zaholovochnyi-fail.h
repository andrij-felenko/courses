#ifndef SHARED_TREE_H
#define SHARED_TREE_H

#include <stdint.h>

#if defined(__BPF__)
  #define BPF_ARENA_PTR(type) type __attribute__((address_space(1))) *
#else
  #define BPF_ARENA_PTR(type) type *
#endif

#define RADIX_BRANCHES 2

struct radix_node {
    uint32_t prefix;
    uint8_t prefix_len;
    uint8_t action; /* 0 = PASS (пропустити), 1 = DROP (заблокувати) */
    uint16_t pad;
    BPF_ARENA_PTR(struct radix_node) child[RADIX_BRANCHES];
};

struct arena_root_header {
    uint32_t magic;
    uint32_t version;
    uint64_t total_lookups;
    uint64_t total_matches;
    BPF_ARENA_PTR(struct radix_node) root;
};

#define ARENA_MAGIC 0x4152454E /* Магічна константа "AREN" */

#endif /* SHARED_TREE_H */
