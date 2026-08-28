/* C: Демонстрація нестійкості Quicksort та стійкості Merge Sort */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int grade;
    char name[32];
    int original_index;
} Student;

void print_students(const char *label, const Student *arr, size_t n) {
    printf("=== %s ===\n", label);
    for (size_t i = 0; i < n; i++) {
        printf("  [%zu] Оцінка: %d | Ім'я: %-12s (orig_idx: %d)\n",
               i, arr[i].grade, arr[i].name, arr[i].original_index);
    }
    printf("\n");
}

/* Компаратор для qsort (порівняння лише за оцінкою, за спаданням) */
int compare_by_grade_desc(const void *a, const void *b) {
    const Student *sa = (const Student *)a;
    const Student *sb = (const Student *)b;
    if (sb->grade != sa->grade) {
        return sb->grade - sa->grade;
    }
    return 0; /* Рівні оцінки — qsort не гарантує збереження порядку! */
}

/* Стійке сортування злиттям (Merge Sort) */
void merge_stable(Student *arr, Student *temp, size_t left, size_t mid, size_t right) {
    size_t i = left;
    size_t j = mid + 1;
    size_t k = left;

    while (i <= mid && j <= right) {
        /* ВАЖЛИВО: Оператор >= забезпечує стійкість.
           При рівних оцінках першим береться елемент із лівої частини (i). */
        if (arr[i].grade >= arr[j].grade) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
    }

    while (i <= mid) {
        temp[k++] = arr[i++];
    }
    while (j <= right) {
        temp[k++] = arr[j++];
    }

    for (i = left; i <= right; i++) {
        arr[i] = temp[i];
    }
}

void merge_sort_recursive(Student *arr, Student *temp, size_t left, size_t right) {
    if (left >= right) return;
    size_t mid = left + (right - left) / 2;
    merge_sort_recursive(arr, temp, left, mid);
    merge_sort_recursive(arr, temp, mid + 1, right);
    merge_stable(arr, temp, left, mid, right);
}

void merge_sort_students(Student *arr, size_t n) {
    Student *temp = (Student *)malloc(n * sizeof(Student));
    if (!temp) return;
    merge_sort_recursive(arr, temp, 0, n - 1);
    free(temp);
}

int main(void) {
    Student original[] = {
        {5, "Авраменко", 0},
        {4, "Бондаренко", 1},
        {5, "Василенко", 2},
        {4, "Грищенко", 3},
        {5, "Дмитренко", 4}
    };
    size_t n = sizeof(original) / sizeof(original[0]);

    Student arr_qsort[5];
    Student arr_merge[5];
    memcpy(arr_qsort, original, sizeof(original));
    memcpy(arr_merge, original, sizeof(original));

    print_students("Вихідний масив (відсортований за прізвищем)", original, n);

    /* Сортування через стандартний qsort (може бути нестійким) */
    qsort(arr_qsort, n, sizeof(Student), compare_by_grade_desc);
    print_students("Після C qsort() [Нестійке сортування]", arr_qsort, n);

    /* Сортування через наш стійкий Merge Sort */
    merge_sort_students(arr_merge, n);
    print_students("Після Merge Sort [Стійке сортування]", arr_merge, n);

    return 0;
}
