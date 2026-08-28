/* dot.c — скалярний добуток трьома способами
   gcc -O3 -march=native -fopenmp-simd dot.c -o dot                */

#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

/* 0. Еталон: та сама сума, але акумулятор подвійної точності.
      Не для швидкості — щоб було з чим порівнювати.               */
double dot_ref(const float *a, const float *b, size_t n)
{
    double s = 0.0;
    for (size_t i = 0; i < n; i++)
        s += (double)a[i] * (double)b[i];
    return s;
}

/* 1. Наївно: один акумулятор, порядок доданків зафіксовано мовою.  */
float dot_naive(const float *a, const float *b, size_t n)
{
    float s = 0.0f;
    for (size_t i = 0; i < n; i++)
        s += a[i] * b[i];
    return s;
}

/* 2. Той самий цикл плюс явний дозвіл переставляти доданки.        */
float dot_omp(const float *a, const float *b, size_t n)
{
    float s = 0.0f;
    #pragma omp simd reduction(+:s)
    for (size_t i = 0; i < n; i++)
        s += a[i] * b[i];
    return s;
}
