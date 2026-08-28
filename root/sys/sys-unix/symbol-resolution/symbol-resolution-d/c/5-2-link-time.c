#include <stdio.h>
#include <stdlib.h>

void *__real_malloc(size_t size);

/* Перехоплювач на етапі компонування */
void *__wrap_malloc(size_t size) {
    printf("[link-time wrap] malloc(%zu)\n", size);
    return __real_malloc(size);
}
