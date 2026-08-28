#include <stdio.h>
#include <math.h>

// Закон Шоклі для JFET у насиченні.
// idss — струм при Vgs=0 (А); vp — напруга відсічки (В, для n-каналу ВІД'ЄМНА);
// vgs — напруга затвор-витік робочої точки (В, від'ємна, між vp і 0).
typedef struct { float id; float gm_volt; float gm_root; } jfet_op;

jfet_op jfet_point(float idss, float vp, float vgs) {
    jfet_op r;
    float k = 1.0f - vgs / vp;          // (1 − Vgs/Vp), від 1 при Vgs=0 до 0 при Vgs=Vp
    r.id      = idss * k * k;           // квадрат Шоклі
    r.gm_volt = -(2.0f * idss / vp) * k;            // gm через напругу
    r.gm_root = (2.0f / fabsf(vp)) * sqrtf(idss * r.id); // gm через корінь зі струму
    return r;
}

int main(void) {
    float idss = 10.0e-3f;   // 10 мА
    float vp   = -4.0f;      // −4 В
    float vgs  = -1.0f;      // робоча точка

    jfet_op op = jfet_point(idss, vp, vgs);
    printf("ID      = %.3f мА\n", op.id * 1e3f);
    printf("gm (V)  = %.3f мА/В\n", op.gm_volt * 1e3f);  // через напругу
    printf("gm (√I) = %.3f мА/В\n", op.gm_root * 1e3f);  // через корінь зі струму
    // максимальна крутість приладу (при Vgs=0)
    printf("gm(max) = %.3f мА/В\n", (2.0f * idss / fabsf(vp)) * 1e3f);
    return 0;
}
