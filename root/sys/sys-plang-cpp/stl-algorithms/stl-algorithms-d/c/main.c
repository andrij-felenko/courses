#include <stdlib.h>

int cmp_int(const void* a, const void* b) {
    int arg1 = *(const int*)a;
    int arg2 = *(const int*)b;
    return (arg1 > arg2) - (arg1 < arg2);
}

void sort_c(int* arr, size_t n) {
    // Кожне порівняння викликає cmp_int через вказівник на функцію
    qsort(arr, n, sizeof(int), cmp_int);
}
