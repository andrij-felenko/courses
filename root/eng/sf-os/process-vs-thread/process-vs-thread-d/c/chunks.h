#ifndef CHUNKS_H
#define CHUNKS_H

#include <stddef.h>

/* Півінтервал [start, end) індексів масиву — частка одного робітника. */
typedef struct {
    size_t start;
    size_t end;
} chunk_t;

/* Ріже [0, n) на parts майже рівних часток; залишок роздає першим із них.
   Масив out мусить мати щонайменше parts елементів. */
void chunk_split(size_t n, size_t parts, chunk_t *out);

/* Сума елементів у межах частки. Однакова і для потоку, і для процесу:
   різниця між ними не в арифметиці, а в тому, чия це пам'ять. */
long long sum_range(const int *data, chunk_t part);

#endif /* CHUNKS_H */
