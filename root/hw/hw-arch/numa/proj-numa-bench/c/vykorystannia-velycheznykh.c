#define _GNU_SOURCE
#include <sys/mman.h>
#include <numaif.h>
#include <stdio.h>
#include <stdlib.h>

void* alloc_hugepages_on_node(size_t size_2mb_aligned, int node) {
    void *ptr = mmap(NULL, size_2mb_aligned,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                     -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap MAP_HUGETLB failed");
        return NULL;
    }

    unsigned long nodemask = (1UL << node);
    if (mbind(ptr, size_2mb_aligned, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) != 0) {
        perror("mbind failed");
        munmap(ptr, size_2mb_aligned);
        return NULL;
    }

    return ptr;
}
