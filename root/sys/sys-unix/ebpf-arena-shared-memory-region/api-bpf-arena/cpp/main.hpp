#ifndef SHARED_ARENA_TYPES_H
#define SHARED_ARENA_TYPES_H

#include <stdint.h>

#if defined(__cplusplus)
extern "C" {
#endif

#if defined(__BPF__)
  #define BPF_ARENA_PTR(type) type __attribute__((address_space(1))) *
#else
  #define BPF_ARENA_PTR(type) type *
#endif

struct arena_header {
    uint32_t magic;
    uint32_t version;
    uint64_t total_pages;
    uint64_t allocated_bytes;
};

struct arena_node {
    uint64_t id;
    uint64_t payload;
    BPF_ARENA_PTR(struct arena_node) next;
};

#if defined(__cplusplus)
}
#endif

#endif /* SHARED_ARENA_TYPES_H */
