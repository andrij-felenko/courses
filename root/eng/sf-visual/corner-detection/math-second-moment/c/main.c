#include <math.h>
#include <stdio.h>

typedef struct { float Sxx, Syy, Sxy; } M2;

static void classify(const char* name, M2 m) {
    float det   = m.Sxx * m.Syy - m.Sxy * m.Sxy;   // λ1·λ2
    float trace = m.Sxx + m.Syy;                    // λ1+λ2
    float harris = det - 0.05f * trace * trace;     // відгук Гарріса
    // менше власне число = min(λ1, λ2):
    float disc  = sqrtf(trace * trace * 0.25f - det);
    float lmin  = trace * 0.5f - disc;              // Ші–Томасі
    printf("%-8s det=%8.1f trace=%7.1f  Harris=%9.1f  min(lam)=%6.1f\n",
           name, det, trace, harris, lmin);
}

int main(void) {
    classify("рівне", (M2){   5.f,    4.f,   1.f });  // обидва градієнти кволі
    classify("край",  (M2){ 900.f,    6.f,  70.f });  // сильний лише по x
    classify("кут",   (M2){ 800.f,  650.f,  90.f });  // сильний по обох осях
    return 0;
}
