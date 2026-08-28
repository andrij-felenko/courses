#include <stddef.h>
#include <stdbool.h>

typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} SortedStreamBuffer;

/**
 * @brief Вставляє новий елемент у вже відсортований буфер зі збереженням порядку.
 * 
 * @param buf Вказівник на дескриптор буфера.
 * @param val Значення, що додається.
 * @return true при успішній вставці, false якщо буфер заповнений.
 */
bool stream_buffer_insert(SortedStreamBuffer *buf, int val) {
    if (buf == NULL || buf->data == NULL || buf->size >= buf->capacity) {
        return false;
    }

    size_t j = buf->size;
    while (j > 0 && buf->data[j - 1] > val) {
        buf->data[j] = buf->data[j - 1];
        --j;
    }

    buf->data[j] = val;
    buf->size++;
    return true;
}
