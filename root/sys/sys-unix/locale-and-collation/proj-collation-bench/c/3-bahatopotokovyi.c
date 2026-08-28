/* C11 + POSIX.1-2008: Багатопотокове сортування з uselocale */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#include <pthread.h>

typedef struct {
    char **data;
    size_t count;
    const char *loc_name;
} ThreadWorkerArg;

void *thread_sort_worker(void *arg) {
    ThreadWorkerArg *targ = (ThreadWorkerArg *)arg;

    // Створення локального об'єкта локалі для потоку
    locale_t loc = newlocale(LC_ALL_MASK, targ->loc_name, NULL);
    if (!loc) {
        loc = newlocale(LC_ALL_MASK, "C", NULL);
    }

    // Встановлення локалі суто для цього потоку
    locale_t old_loc = uselocale(loc);

    // Виконання сортування шматка даних через strcoll_l
    for (size_t i = 0; i < targ->count - 1; ++i) {
        for (size_t j = i + 1; j < targ->count; ++j) {
            if (strcoll_l(targ->data[i], targ->data[j], loc) > 0) {
                char *tmp = targ->data[i];
                targ->data[i] = targ->data[j];
                targ->data[j] = tmp;
            }
        }
    }

    uselocale(old_loc);
    freelocale(loc);
    return NULL;
}
