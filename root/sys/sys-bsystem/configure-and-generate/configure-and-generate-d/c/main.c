#include <stdio.h>
#include <stdlib.h>
#include "config.h"

#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif

void* allocate_page_aligned(size_t size) {
    void* ptr = NULL;
#if defined(HAVE_POSIX_MEMALIGN)
    if (posix_memalign(&ptr, 4096, size) != 0) {
        return NULL;
    }
#elif defined(HAVE_ALIGNED_ALLOC)
    ptr = aligned_alloc(4096, size);
#else
    ptr = malloc(size);
#endif
    return ptr;
}
