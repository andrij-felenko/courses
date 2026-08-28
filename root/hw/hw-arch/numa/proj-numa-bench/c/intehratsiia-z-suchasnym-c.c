// У мові C аналогом PMR є структура з покажчиками на функції виділення й звільнення
#include <numa.h>
#include <stdlib.h>

typedef struct {
    int node;
} numa_allocator_t;

static void* numa_allocator_alloc(numa_allocator_t *alloc, size_t bytes) {
    return numa_alloc_onnode(bytes, alloc->node);
}

static void numa_allocator_free(numa_allocator_t *alloc, void *ptr, size_t bytes) {
    numa_free(ptr, bytes);
}
