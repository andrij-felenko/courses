#ifndef PROC_SUM_H
#define PROC_SUM_H

#include <stddef.h>

/* Рахує суму data[0..n) силами workers ОКРЕМИХ процесів.
   Кожна дитина дістає масив копією-при-записі й віддає свою часткову суму
   назад через канал. Повертає 0 і результат у *out, інакше — код errno. */
int proc_sum(const int *data, size_t n, size_t workers, long long *out);

#endif /* PROC_SUM_H */
