#include <math.h>
// Q = 0.5*sqrt(C1/C2). Шукаємо C1/C2 для заданого Q.
// => sqrt(C1/C2) = 2Q  =>  C1/C2 = (2Q)^2
float Q     = 0.70710678f;          // Баттерворт, 1/sqrt(2)
float ratio = (2.0f * Q) * (2.0f * Q);   // = 2.0 рівно

// Отже C1 має бути вдвічі більшим за C2.
// Якщо взяти C2 = 10 нФ:
float C2 = 10e-9f;
float C1 = ratio * C2;              // = 20 нФ
