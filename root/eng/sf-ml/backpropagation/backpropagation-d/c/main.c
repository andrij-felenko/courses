#include <math.h>
#include <stdio.h>

int main(void) {
    /* ── дано ── */
    float x = 1.0f, w1 = 0.8f, w2 = 1.5f, target = 2.0f;

    /* ── ПРОХІД УПЕРЕД (дорогою запам'ятовуємо проміжні числа) ── */
    float z = w1 * x;              /* вхід прихованого нейрона     */
    float h = tanhf(z);            /* його вихід після активації   */
    float out = w2 * h;            /* вихід мережі                 */
    float err = out - target;      /* «сира» різниця               */
    float E = 0.5f * err * err;    /* похибка (1/2 — щоб похідна була чистою) */

    /* ── ПРОХІД НАЗАД (кожен крок = помножити те, що прийшло, на локальне) ── */
    float dE_dout = err;           /* ∂E/∂out : похідна 1/2·err² по out = err */
    float dE_dw2  = dE_dout * h;   /* out = w2·h ⇒ локальне ∂out/∂w2 = h      */

    float dE_dh   = dE_dout * w2;  /* несемо провину в прихований шар: ∂out/∂h = w2 */
    float dtanh   = 1.0f - h * h;  /* локальна похідна tanh: 1 − tanh²(z)     */
    float dE_dz   = dE_dh * dtanh; /* дельта прихованого нейрона              */
    float dE_dw1  = dE_dz * x;     /* z = w1·x ⇒ локальне ∂z/∂w1 = x          */

    printf("out=%.4f  E=%.4f\n", out, E);       /* out=0.9961  E=0.5040 */
    printf("dE/dw2=%.4f\n", dE_dw2);            /* -0.6667 */
    printf("dE/dw1=%.4f\n", dE_dw1);            /* -0.8419 */
    return 0;
}
