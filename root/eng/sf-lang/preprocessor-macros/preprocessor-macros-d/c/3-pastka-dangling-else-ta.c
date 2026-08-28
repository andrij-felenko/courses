#include <stdio.h>
#include <stdlib.h>

#define SAFE_CLEANUP(ptr) \
    do { \
        free(ptr); \
        printf("Ресурс звільнено\n"); \
    } while (0)

int main(void) {
    int* data = (int*)malloc(sizeof(int));
    int ok = 1;

    if (ok)
        SAFE_CLEANUP(data);
    else
        printf("Помилка\n");

    return 0;
}
