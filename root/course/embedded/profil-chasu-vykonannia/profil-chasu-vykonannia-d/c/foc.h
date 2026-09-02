/* Контур струму векторного керування: Кларк -> Парк -> два ПІ -> зворотні
 * перетворення -> шпаруватості. Увесь критичний шлях живе в SRAM.
 */
#ifndef FOC_H
#define FOC_H

#include <stdint.h>
#include "ramfunc.h"

/* Три шпаруватості, 0..1. Однорідний агрегат із трьох float повертається
   у регістрах s0-s2 (VFP HFA) — на критичному шляху немає стека. */
typedef struct {
    float a;
    float b;
    float c;
} duty3_t;

typedef struct {
    float kp;
    float ki;
    float out_max;
    float integ;
} pi_t;

/* Будує таблицю синусів у SRAM. Викликається один раз до пуску ШІМ:
   sinf() з libm на критичному шляху неприпустимий — час його виконання
   залежить від аргументу, а це чистий джитер. */
void foc_init(void);

void foc_set_targets(float id_ref, float iq_ref);
void foc_reset(void);

/* Кут — фаза Q32: перенесення через 2*pi це звичайне переповнення лічильника,
   тож у критичному коді немає ні fmodf, ні гілки нормалізації. */
RAM_FUNC duty3_t foc_step(float ia, float ib, uint32_t theta_q32, float vdc);

#endif /* FOC_H */
