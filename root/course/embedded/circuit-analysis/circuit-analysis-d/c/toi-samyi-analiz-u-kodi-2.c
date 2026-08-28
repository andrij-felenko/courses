#include <stdio.h>

typedef struct { float v_th, r_th; } Thevenin;

/* Дві точки (навантаження, виміряна напруга) → пряма V = V_th − I·R_th.
   Струм у кожній точці: I = V/R_load. Дві точки дають нахил R_th і зсув V_th. */
static Thevenin thevenin_from_two_loads(float ra, float va, float rb, float vb) {
    Thevenin t;
    float ia = va / ra;                 /* струм у першій точці */
    float ib = vb / rb;                 /* струм у другій точці */
    t.r_th = (vb - va) / (ia - ib);     /* нахил прямої V(I): −ΔV/ΔI */
    t.v_th = va + ia * t.r_th;          /* екстраполяція до I=0 (розімкнене) */
    return t;
}

int main(void) {
    /* Батарея: під 100 Ω дала 6.15 В, під 47 Ω — 6.02 В */
    Thevenin t = thevenin_from_two_loads(100.0f, 6.15f, 47.0f, 6.02f);
    printf("V_th = %.2f В\n", t.v_th);  /* 6.27 В — «істинна» ЕРС без навантаження */
    printf("R_th = %.2f Ω\n", t.r_th);  /* 1.95 Ω — внутрішній опір */
    return 0;
}
