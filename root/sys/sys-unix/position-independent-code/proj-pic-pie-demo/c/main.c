/* main.c — C-версія головного виконуваного файлу */
#include <stdio.h>

extern int global_counter;
extern void exported_func(const char* msg);

int main(void) {
    printf("[main] Початкове значення лічильника: %d\n", global_counter);
    exported_func("Виклик з main");
    printf("[main] Кінцеве значення лічильника: %d\n", global_counter);
    return 0;
}
