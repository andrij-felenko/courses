#include <stdio.h>

void process_data(int flag) {
    int uninitialized_value;
    if (flag) {
        uninitialized_value = 100;
    }
    /* Якщо flag == 0, V-біти змінної uninitialized_value дорівнюють нулю */
    if (uninitialized_value > 50) {
        printf("Condition met\n");
    }
}
