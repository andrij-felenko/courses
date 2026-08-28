#include <stdlib.h>

// Один крок: рахує градієнт dL/dz на логітах учня z_s[n].
//   z_s   — логіти учня (з прямого ходу мережі учня)
//   z_t   — логіти вчителя (порахувати РАЗ і закешувати; учитель не вчиться)
//   y     — індекс правильного класу (тверда мітка)
//   T     — температура (та сама для вчителя й учня!)
//   alpha — вага дистиляційної частини (0…1), (1−alpha) — вага якоря
//   grad  — вихід: dL/dz[n], його віддамо у зворотне поширення учня
static void distill_grad(const float *z_s, const float *z_t, int y,
                         float T, float alpha, float *grad, int n) {
    float ps_soft[16], q[16];      // розподіли за T (учень і вчитель)
    float ps_hard[16];             // розподіл учня за T=1 (для якоря)

    softmax_T(z_s, ps_soft, n, T);     // м'який вихід учня  (за T)
    softmax_T(z_t, q,       n, T);     // м'яка мітка вчителя (за T)
    softmax_T(z_s, ps_hard, n, 1.0f);  // гострий вихід учня  (за T=1)

    for (int i = 0; i < n; ++i) {
        // дистиляційна частина: (1/T)(ps_soft−q), домножена на T²  →  T·(ps_soft−q)
        float g_soft = T * (ps_soft[i] - q[i]);
        // якірна частина: звичайна CE поверх softmax за T=1  →  ps_hard − onehot(y)
        float target = (i == y) ? 1.0f : 0.0f;
        float g_hard = ps_hard[i] - target;
        // зважена сума двох сигналів
        grad[i] = alpha * g_soft + (1.0f - alpha) * g_hard;
    }
}
