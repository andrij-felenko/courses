#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int capacity;
    int* data;
} DynamicArrayC;

DynamicArrayC array_create(int capacity) {
    DynamicArrayC arr;
    arr.capacity = capacity;
    arr.data = (int*)malloc(capacity * sizeof(int));
    return arr;
}

void print_array_c(const DynamicArrayC* arr) {
    printf("Array capacity: %d\n", arr->capacity);
}

int main(void) {
    // У мові C неявні перетворення структур неможливі: помилка фіксується на етапі компіляції
    DynamicArrayC arr = array_create(100);
    print_array_c(&arr);
    free(arr.data);
    return 0;
}
