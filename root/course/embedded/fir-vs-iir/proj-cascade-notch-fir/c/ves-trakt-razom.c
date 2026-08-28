#include <stdint.h>
#include <stddef.h>

typedef struct {
    med3_t       med;         // 1) нелінійна медіана проти викидів
    sos_chain_t  notch;       // 2) БІХ-notch 50 Гц (каскад біквадів, DF1, Q31)
    // 3) КІХ-згладжування (Q31) — коефіцієнти й кільцевий буфер
    const int32_t *fir_b;     // коефіцієнти КІХ у Q31
    int32_t       *fir_x;     // кільцевий буфер минулих входів
    size_t         fir_len;
    size_t         fir_pos;
} pipeline_t;

// один крок КІХ у Q31: MAC у 64-бітному акумуляторі, зсув, насичення
static int32_t fir_q31_step(pipeline_t *p, int32_t x) {
    p->fir_x[p->fir_pos] = x;
    int64_t acc = 0;
    size_t idx = p->fir_pos;
    for (size_t k = 0; k < p->fir_len; ++k) {
        acc += (int64_t)p->fir_b[k] * p->fir_x[idx];   // Q31×Q31 → Q62
        idx = (idx == 0) ? p->fir_len - 1 : idx - 1;   // йдемо назад по буферу
    }
    p->fir_pos = (p->fir_pos + 1) % p->fir_len;
    acc = (acc + (1LL << 30)) >> 31;                   // Q62 → Q31 з округленням
    return sat32(acc);
}

// повний тракт: сирий відлік АЦП (Q31) → чистий відлік (Q31)
int32_t pipeline_step(pipeline_t *p, int32_t raw) {
    int32_t s = med3_step(&p->med, raw);      // 1) прибрати викиди (нелінійно)
    s = headroom_in(s);                       //    2 біти запасу перед БІХ
    s = sos_step(&p->notch, s);               // 2) гострий notch 50 Гц (БІХ)
    s = headroom_out(s);                      //    відновити масштаб
    s = fir_q31_step(p, s);                   // 3) м'яке згладжування (КІХ)
    return s;
}
