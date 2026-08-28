#include <stdio.h>
#include <stdlib.h>

void heap_overflow_demo(void) {
    int *array = (int *)malloc(5 * sizeof(int)); // Виділено 20 байтів
    // Допустимі індекси: 0, 1, 2, 3, 4
    array[5] = 100; // ASan зловить Heap Buffer Overflow (вихід на 4 байти вправо)
    free(array);
}

void use_after_free_demo(void) {
    char *buffer = (char *)malloc(64);
    free(buffer);
    buffer[0] = 'A'; // ASan зловить Heap Use-After-Free
}
