#include <cmath>

/* Базові скалярні інтерфейси C++11/C++20/C++23 у просторі std:: */
namespace std {
    double      fma(double x, double y, double z);
    float       fma(float x, float y, float z);
    long double fma(long double x, long double y, long double z);

    float       fmaf(float x, float y, float z);
    long double fmal(long double x, long double y, long double z);
}
