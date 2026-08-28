#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>

// Структура крокового курсора мовою C
typedef struct {
    const int* ptr;       // Поточна адреса елемента
    const int* end;       // Адреса за останнім елементом масиву
    size_t stride;        // Крок зсуву (наприклад, 2 або 3)
} stride_cursor_t;

// Ініціалізація курсора
stride_cursor_t stride_cursor_init(const int* array, size_t size, size_t stride) {
    stride_cursor_t cursor;
    cursor.ptr = array;
    cursor.end = array + size;
    cursor.stride = stride;
    return cursor;
}

// Перевірка, чи не досягнуто кінця
bool stride_cursor_has_next(const stride_cursor_t* cursor) {
    return cursor->ptr < cursor->end;
}

// Перехід до наступного елемента з кроком
void stride_cursor_next(stride_cursor_t* cursor) {
    if (cursor->ptr < cursor->end) {
        cursor->ptr += cursor->stride;
    }
}

// Отримання поточного значення
int stride_cursor_get(const stride_cursor_t* cursor) {
    return *(cursor->ptr);
}

int main(void) {
    int data[] = {10, 20, 30, 40, 50, 60, 70, 80, 90};
    size_t count = sizeof(data) / sizeof(data[0]);

    // Обхід кожного 2-го елемента мовою C
    stride_cursor_t cursor = stride_cursor_init(data, count, 2);
    printf("C-style stride traversal: ");
    while (stride_cursor_has_next(&cursor)) {
        printf("%d ", stride_cursor_get(&cursor));
        stride_cursor_next(&cursor);
    }
    printf("\n");
    return 0;
}
