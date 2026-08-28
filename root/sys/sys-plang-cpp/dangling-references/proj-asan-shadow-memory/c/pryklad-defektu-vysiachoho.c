#include <stdio.h>

const int* get_multiplier(void) {
    int factor = 10;
    return &factor; // Повертає адресу локальної змінної стека
}

void overwrite_stack(void) {
    volatile double array[32];
    for (int i = 0; i < 32; ++i) array[i] = 3.14159;
}

int main(void) {
    const int* p = get_multiplier();
    
    overwrite_stack(); // Перезаписує звільнений кадр
    
    // Невизначена поведінка: читання з розкрученого стека
    printf("Значення коефіцієнта: %d\n", *p);
    return 0;
}
