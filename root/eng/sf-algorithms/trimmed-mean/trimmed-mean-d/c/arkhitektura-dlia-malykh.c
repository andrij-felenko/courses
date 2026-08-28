#include <stddef.h>
#include <stdbool.h>

#define MAX_WINDOW_SIZE 32

typedef struct {
    double buffer[MAX_WINDOW_SIZE];      /* Хронологічний кільцевий буфер */
    double sorted[MAX_WINDOW_SIZE];      /* Відсортовані значення вікна */
    size_t window_size;                  /* Повна ширина вікна W */
    size_t trim_k;                       /* Кількість відкинутих з кожного краю k */
    size_t count;                        /* Поточна кількість накопичених елементів */
    size_t head;                         /* Індекс наступного запису в кільцевий буфер */
} SlidingTrimmedMean;

void sliding_trimmed_mean_init(SlidingTrimmedMean *filter, size_t w, size_t k) {
    if (w > MAX_WINDOW_SIZE) {
        w = MAX_WINDOW_SIZE;
    }
    filter->window_size = w;
    filter->trim_k = (2 * k < w) ? k : 0;
    filter->count = 0;
    filter->head = 0;
}

double sliding_trimmed_mean_update(SlidingTrimmedMean *filter, double new_val) {
    size_t w = filter->window_size;
    size_t k = filter->trim_k;

    if (filter->count < w) {
        /* Фаза первинного заповнення буфера */
        filter->buffer[filter->head] = new_val;
        filter->head = (filter->head + 1) % w;

        /* Вставка зі збереженням сортування */
        size_t pos = filter->count;
        while (pos > 0 && filter->sorted[pos - 1] > new_val) {
            filter->sorted[pos] = filter->sorted[pos - 1];
            pos--;
        }
        filter->sorted[pos] = new_val;
        filter->count++;
    } else {
        /* Фаза усталеного ковзного вікна */
        double old_val = filter->buffer[filter->head];
        filter->buffer[filter->head] = new_val;
        filter->head = (filter->head + 1) % w;

        /* 1. Пошук і видалення старого значення */
        size_t old_pos = 0;
        while (old_pos < w && filter->sorted[old_pos] != old_val) {
            old_pos++;
        }
        for (size_t i = old_pos; i + 1 < w; ++i) {
            filter->sorted[i] = filter->sorted[i + 1];
        }

        /* 2. Вставка нового значення на належне місце */
        size_t new_pos = w - 1;
        while (new_pos > 0 && filter->sorted[new_pos - 1] > new_val) {
            filter->sorted[new_pos] = filter->sorted[new_pos - 1];
            new_pos--;
        }
        filter->sorted[new_pos] = new_val;
    }

    /* Якщо накопичено замало даних для усічення, беремо просте середнє */
    if (filter->count <= 2 * k) {
        double sum = 0.0;
        for (size_t i = 0; i < filter->count; ++i) {
            sum += filter->sorted[i];
        }
        return sum / (double)filter->count;
    }

    /* Усереднення центрального ядра */
    size_t active_start = k;
    size_t active_end = filter->count - k;
    double sum = 0.0;
    for (size_t i = active_start; i < active_end; ++i) {
        sum += filter->sorted[i];
    }

    return sum / (double)(active_end - active_start);
}
