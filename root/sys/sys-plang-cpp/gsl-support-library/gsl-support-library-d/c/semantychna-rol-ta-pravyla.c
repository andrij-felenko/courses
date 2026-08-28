#include <stdlib.h>

typedef struct {
    int* data;
    size_t count;
} IntBuffer;

/* Застарілий C-підхід: відповідальність за free не зафіксована */
IntBuffer* create_buffer_c(size_t count) {
    IntBuffer* buf = (IntBuffer*)malloc(sizeof(IntBuffer));
    if (!buf) return NULL;
    buf->data = (int*)malloc(count * sizeof(int));
    buf->count = count;
    return buf; /* Хто і як має звільняти buf->data та buf? */
}
