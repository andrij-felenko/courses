#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

/* Допоміжна функція для обміну двох елементів у пам'яті */
static void swap_bytes(void *a, void *b, size_t elem_size) {
    unsigned char *p1 = (unsigned char *)a;
    unsigned char *p2 = (unsigned char *)b;
    for (size_t i = 0; i < elem_size; ++i) {
        unsigned char tmp = p1[i];
        p1[i] = p2[i];
        p2[i] = tmp;
    }
}

/* 
 * Ітеративний Quickselect мовою C з тристороннім розбиттям (Dutch National Flag).
 * - base: вказівник на початок масиву
 * - num_elems: кількість елементів у масиві
 * - elem_size: розмір одного елемента в байтах
 * - k: індекс шуканого елемента (0-based: 0 <= k < num_elems)
 * - cmp: функція порівняння двох елементів (повертає <0, 0, >0)
 */
bool quickselect_c(void *base, size_t num_elems, size_t elem_size, size_t k,
                   int (*cmp)(const void *, const void *)) {
    if (!base || num_elems == 0 || k >= num_elems) {
        return false;
    }

    char *arr = (char *)base;
    size_t left = 0;
    size_t right = num_elems - 1;

    while (left < right) {
        /* Вибір випадкового півота для запобігання деградації */
        size_t pivot_idx = left + (size_t)rand() % (right - left + 1);
        
        /* Переміщуємо pivot на початок поточного діапазону */
        swap_bytes(arr + left * elem_size, arr + pivot_idx * elem_size, elem_size);

        /* Тристороннє розбиття (3-way partition):
         * [left..lt-1]  — елементи < pivot
         * [lt..gt]      — елементи == pivot
         * [gt+1..right] — елементи > pivot
         */
        size_t lt = left;
        size_t i = left + 1;
        size_t gt = right;

        void *pivot_val = arr + left * elem_size;

        while (i <= gt) {
            int res = cmp(arr + i * elem_size, pivot_val);
            if (res < 0) {
                swap_bytes(arr + lt * elem_size, arr + i * elem_size, elem_size);
                lt++;
                i++;
            } else if (res > 0) {
                swap_bytes(arr + i * elem_size, arr + gt * elem_size, elem_size);
                if (gt == 0) break;
                gt--;
            } else {
                i++;
            }
        }

        /* Анатомія вибору гілки за індексом k:
         * Якщо k в межах [lt..gt], елемент з рангом k вже стоїть на своєму місці!
         */
        if (k < lt) {
            if (lt == 0) break;
            right = lt - 1;
        } else if (k > gt) {
            left = gt + 1;
        } else {
            /* k знаходиться в зоні однакових елементів == pivot */
            return true;
        }
    }

    return true;
}

/* Компаратор для типів int */
static int cmp_int(const void *a, const void *b) {
    int arg1 = *(const int *)a;
    int arg2 = *(const int *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

int main(void) {
    srand((unsigned int)time(NULL));
    int data[] = {7, 2, 1, 6, 8, 5, 3, 4, 5, 2, 8, 5};
    size_t n = sizeof(data) / sizeof(data[0]);
    size_t k = 5; /* Пошук 6-го найменшого елемента (індекс 5) */

    if (quickselect_c(data, n, sizeof(int), k, cmp_int)) {
        printf("Знайдено k-й (%zu) елемент: %d\n", k, data[k]);
    }

    return 0;
}
