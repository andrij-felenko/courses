/* C: Симулятор сортування таблиці за 2 колонками */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char country[32];
    char city[32];
    int population;
} CityRecord;

void print_table(const char *title, const CityRecord *records, size_t n) {
    printf("--- %s ---\n", title);
    for (size_t i = 0; i < n; i++) {
        printf("  %-12s | %-12s | Населення: %d\n",
               records[i].country, records[i].city, records[i].population);
    }
    printf("\n");
}

/* Стійка процедура сортування масиву за довільним компаратором (Merge Sort) */
void merge_sort_generic(void *base, size_t num, size_t size,
                        int (*compar)(const void *, const void *)) {
    if (num < 2) return;
    size_t mid = num / 2;
    void *left = base;
    void *right = (char *)base + mid * size;

    merge_sort_generic(left, mid, size, compar);
    merge_sort_generic(right, num - mid, size, compar);

    /* Злиття */
    char *temp = (char *)malloc(num * size);
    size_t i = 0, j = 0, k = 0;

    while (i < mid && j < (num - mid)) {
        const void *p1 = (char *)left + i * size;
        const void *p2 = (char *)right + j * size;
        if (compar(p1, p2) <= 0) { /* <= забезпечує стійкість */
            memcpy(temp + k * size, p1, size);
            i++;
        } else {
            memcpy(temp + k * size, p2, size);
            j++;
        }
        k++;
    }

    while (i < mid) {
        memcpy(temp + k * size, (char *)left + i * size, size);
        i++; k++;
    }
    while (j < (num - mid)) {
        memcpy(temp + k * size, (char *)right + j * size, size);
        j++; k++;
    }

    memcpy(base, temp, num * size);
    free(temp);
}

int cmp_city(const void *a, const void *b) {
    return strcmp(((const CityRecord *)a)->city, ((const CityRecord *)b)->city);
}

int cmp_country(const void *a, const void *b) {
    return strcmp(((const CityRecord *)a)->country, ((const CityRecord *)b)->country);
}

int main(void) {
    CityRecord data[] = {
        {"Україна", "Львів",  720000},
        {"Польща",  "Краків", 780000},
        {"Україна", "Київ",   2950000},
        {"Польща",  "Варшава",1790000},
        {"Україна", "Одеса",  1010000}
    };
    size_t n = sizeof(data) / sizeof(data[0]);

    print_table("Вхідна таблиця", data, n);

    /* Крок 1: Сортуємо за Містом */
    merge_sort_generic(data, n, sizeof(CityRecord), cmp_city);
    print_table("Крок 1: Після стійкого сортування за Містом", data, n);

    /* Крок 2: Сортуємо за Країною */
    merge_sort_generic(data, n, sizeof(CityRecord), cmp_country);
    print_table("Крок 2: Після стійкого сортування за Країною (Міста впорядковані!)", data, n);

    return 0;
}
