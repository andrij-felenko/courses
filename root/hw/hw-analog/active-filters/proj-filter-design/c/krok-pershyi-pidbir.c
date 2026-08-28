#include <math.h>
#include <stdint.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Опис однієї ланки Саллена–Кі (ФНЧ, рівні резистори R1=R2=R).
typedef struct {
    float R;       // спільний резистор, Ом
    float C1;      // конденсатор додатного ЗЗ (верхній), Ф
    float C2;      // конденсатор на землю (нижній), Ф
    float f0;      // частота зрізу ланки, Гц
    float Q;       // добротність ланки
} sk_stage;

// Підібрати ідеальні C1, C2 для заданих R, f0, Q.
// Заповнює stage->C1, stage->C2; R, f0, Q беруться з полів структури.
static void sk_pick_caps(sk_stage *s) {
    float Cg = 1.0f / (2.0f * (float)M_PI * s->R * s->f0);  // √(C1·C2)
    float two_q = 2.0f * s->Q;                              // √(C1/C2)
    s->C1 = Cg * two_q;     // верхній — більший за Q>0.5
    s->C2 = Cg / two_q;     // нижній  — менший
}
