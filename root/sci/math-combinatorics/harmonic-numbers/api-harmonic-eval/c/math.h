#include <math.h>

/* Пряма гамма-функція Euler Gamma: Γ(x) */
double      tgamma(double x);
float       tgammaf(float x);
long double tgammal(long double x);

/* Логарифм абсолютного значення гамма-функції: ln|Γ(x)| */
double      lgamma(double x);
float       lgammaf(float x);
long double lgammal(long double x);

/* POSIX реентерабельні версії зі збереженням знака Γ(x) */
double      lgamma_r(double x, int *signgamp);
float       lgammafr(float x, int *signgamp);
long double lgammal_r(long double x, int *signgamp);
