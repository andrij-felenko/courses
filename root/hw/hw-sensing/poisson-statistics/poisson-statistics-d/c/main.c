#include <math.h>

/* Оцінка відносної похибки виміру лічбою за Пуассоном.
   counts — скільки імпульсів (подій) назбирано за час виміру; counts > 0.
   Повертає відносну похибку (частку): 1/√N. */
float poisson_rel_error(long counts)
{
    float n = (float)counts;
    float sigma = sqrtf(n);     /* абсолютний розкид ≈ √N */
    return sigma / n;           /* = 1/√N — відносна похибка */
}

/* Скільки імпульсів треба назбирати для заданої відносної точності.
   target — бажана відносна похибка (напр. 0.01 для 1 %).
   З 1/√N = target випливає N = 1/target². */
long counts_needed(float target)
{
    return (long)(1.0f / (target * target));   /* квадратична ціна точності */
}
