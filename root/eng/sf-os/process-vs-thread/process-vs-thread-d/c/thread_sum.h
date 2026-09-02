#ifndef THREAD_SUM_H
#define THREAD_SUM_H

#include <stddef.h>

/* Рахує суму data[0..n) силами workers потоків ОДНОГО процесу.
   Потокам передається лише покажчик: масив нікуди не копіюється.
   Повертає 0 і кладе результат у *out, інакше — код помилки (як errno). */
int thread_sum(const int *data, size_t n, size_t workers, long long *out);

#endif /* THREAD_SUM_H */
