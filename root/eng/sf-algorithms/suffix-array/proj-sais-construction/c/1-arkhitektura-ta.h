#ifndef SUFFIX_INDEX_H
#define SUFFIX_INDEX_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Результат пошуку зразка в суфіксному масиві */
typedef struct {
    int left;   /* Початковий індекс у SA */
    int right;  /* Кінцевий індекс у SA */
    int count;  /* Кількість знайдених входжень (right - left + 1) */
} SearchResult;

/* Структура повного суфіксного індексу */
typedef struct {
    char *text;         /* Копія вихідного тексту з термінатором */
    int n;              /* Довжина тексту */
    int *sa;            /* Суфіксний масив: sa[k] = початковий індекс суфікса */
    int *rank;          /* Обернений масив: rank[i] = позиція суфікса S[i] у SA */
    int *lcp;           /* Масив LCP: lcp[k] = спільний префікс sa[k] та sa[k-1] */
    int **st;           /* Розріджена таблиця (Sparse Table) для RMQ на LCP */
    int max_log;        /* Кількість рівнів розрідженої таблиці */
} SuffixIndex;

/* Створення та знищення індексу */
SuffixIndex* suffix_index_create(const char *src);
void suffix_index_destroy(SuffixIndex *idx);

/* Базові пошукові операції */
SearchResult suffix_index_search(const SuffixIndex *idx, const char *pattern);
int suffix_index_query_lcp(const SuffixIndex *idx, int sa_idx_a, int sa_idx_b);

/* Аналітичні запити */
int suffix_index_longest_repeated(const SuffixIndex *idx, int *out_pos);
long long suffix_index_distinct_substrings(const SuffixIndex *idx);

#endif /* SUFFIX_INDEX_H */
