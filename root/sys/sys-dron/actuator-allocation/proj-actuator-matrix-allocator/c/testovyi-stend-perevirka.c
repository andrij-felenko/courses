#include <stdio.h>
#include <assert.h>

void test_quad_x_allocation(void)
{
    allocator_config_t cfg = {
        .num_actuators = 4,
        .u_min = {0.0f, 0.0f, 0.0f, 0.0f},
        .u_max = {1.0f, 1.0f, 1.0f, 1.0f},
        .b_pseudo_inv = {
            /* F_z     Roll     Pitch     Yaw */
            { 0.25f,  0.25f,   0.25f,   0.25f }, /* Motor 1: Front-Right CCW */
            { 0.25f,  0.25f,  -0.25f,  -0.25f }, /* Motor 2: Rear-Right  CW  */
            { 0.25f, -0.25f,   0.25f,  -0.25f }, /* Motor 3: Front-Left   CW  */
            { 0.25f, -0.25f,  -0.25f,   0.25f }  /* Motor 4: Rear-Left   CCW */
        }
    };

    allocator_t alloc;
    allocator_init(&alloc, &cfg);

    /* Тест 1: Номінальне зависання (газ 50%, нульові моменти) */
    float tau1[4] = { 2.0f, 0.0f, 0.0f, 0.0f };
    float u1[4];
    allocator_update(&alloc, tau1, u1);

    for (int i = 0; i < 4; ++i) {
        /* Усі мотори мають отримати 0.5 */
        assert(u1[i] >= 0.499f && u1[i] <= 0.501f);
    }

    /* Тест 2: Насичення при високому газі (газ 90% + сильний крен 0.4) */
    float tau2[4] = { 3.6f, 0.4f, 0.0f, 0.0f };
    float u2[4];
    allocator_update(&alloc, tau2, u2);

    /* Мотори 1 та 2 мали б отримати 0.9 + 0.1 = 1.0; мотори 3 та 4: 0.9 - 0.1 = 0.8 */
    assert(alloc.saturated == false); /* Рівно на межі */

    /* Тест 3: Глибоке насичення (газ 95% + крен 0.8) */
    float tau3[4] = { 3.8f, 0.8f, 0.0f, 0.0f };
    float u3[4];
    allocator_update(&alloc, tau3, u3);

    assert(alloc.saturated == true);
    /* Завдяки десатурації максимальний мотор не перевищує 1.0, різниця збережена */
    assert(u3[0] <= 1.0001f);
    assert(u3[0] - u3[2] >= 0.199f);
}

int main(void)
{
    test_quad_x_allocation();
    return 0;
}
