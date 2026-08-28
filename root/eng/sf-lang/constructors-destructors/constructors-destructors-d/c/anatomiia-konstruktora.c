#include <stdlib.h>
#include <string.h>

typedef struct {
    char* name;
    int* data;
    size_t size;
} GoodBufferC;

// У мові C ініціалізація завжди записується явно у функції
void good_buffer_init(GoodBufferC* buf, const char* name, const int* data, size_t size) {
    size_t name_len = strlen(name) + 1;
    buf->name = (char*)malloc(name_len);
    if (buf->name) memcpy(buf->name, name, name_len);

    buf->size = size;
    buf->data = (int*)malloc(size * sizeof(int));
    if (buf->data && data) memcpy(buf->data, data, size * sizeof(int));
}

void good_buffer_free(GoodBufferC* buf) {
    free(buf->name);
    free(buf->data);
    buf->name = NULL;
    buf->data = NULL;
    buf->size = 0;
}
