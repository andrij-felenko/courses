# Один крок: рахує градієнт dL/dz на логітах учня z_s.
#   z_s   — логіти учня (з прямого ходу мережі учня)
#   z_t   — логіти вчителя (порахувати РАЗ і закешувати; учитель не вчиться)
#   y     — індекс правильного класу (тверда мітка)
#   T     — температура (та сама для вчителя й учня!)
#   alpha — вага дистиляційної частини (0…1), (1−alpha) — вага якоря
#   повертає dL/dz — його віддамо у зворотне поширення учня
def distill_grad(z_s, z_t, y, T, alpha):
    ps_soft = softmax_T(z_s, T)      # м'який вихід учня  (за T)
    q       = softmax_T(z_t, T)      # м'яка мітка вчителя (за T)
    ps_hard = softmax_T(z_s, 1.0)    # гострий вихід учня  (за T=1)

    grad = []
    for i in range(len(z_s)):
        # дистиляційна частина: (1/T)(ps_soft−q), домножена на T²  →  T·(ps_soft−q)
        g_soft = T * (ps_soft[i] - q[i])
        # якірна частина: звичайна CE поверх softmax за T=1  →  ps_hard − onehot(y)
        target = 1.0 if i == y else 0.0
        g_hard = ps_hard[i] - target
        # зважена сума двох сигналів
        grad.append(alpha * g_soft + (1.0 - alpha) * g_hard)
    return grad
