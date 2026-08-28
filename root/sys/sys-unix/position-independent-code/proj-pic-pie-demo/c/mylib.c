/* mylib.c — C-версія розділюваної бібліотеки */
#include <stdio.h>

int global_counter = 42;

void internal_func(void) {
    global_counter++;
}

void exported_func(const char* msg) {
    internal_func();
    printf("[mylib] %s (лічильник: %d)\n", msg, global_counter);
}
