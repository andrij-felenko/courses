// два взаємозамінні «правила» — дві окремі стратегії
int by_asc(const void *a, const void *b) {
    return *(const int*)a - *(const int*)b;      // за зростанням
}
int by_desc(const void *a, const void *b) {
    return *(const int*)b - *(const int*)a;      // за спаданням
}

int nums[] = {5, 2, 9, 1};
qsort(nums, 4, sizeof(int), by_asc);             // підставили одну
qsort(nums, 4, sizeof(int), by_desc);            // підставили іншу
