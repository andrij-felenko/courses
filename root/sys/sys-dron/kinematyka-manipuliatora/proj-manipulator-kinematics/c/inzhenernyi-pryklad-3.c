int main(void) {
    manipulator_chain_t arm = {
        .num_joints = 3,
        .joints = {
            {.theta = 0.0f, .d = 0.0f, .a = 0.35f, .alpha = 0.0f, .is_revolute = true, .q_min = -3.14f, .q_max = 3.14f},
            {.theta = 0.0f, .d = 0.0f, .a = 0.30f, .alpha = 0.0f, .is_revolute = true, .q_min = -2.50f, .q_max = 2.50f},
            {.theta = 0.0f, .d = 0.0f, .a = 0.15f, .alpha = 0.0f, .is_revolute = true, .q_min = -2.50f, .q_max = 2.50f}
        }
    };

    vec3_t target = {0.45f, 0.25f, 0.0f};
    float q_init[3] = {0.1f, 0.1f, 0.1f};
    float q_sol[3] = {0};

    if (ik_solve_dls_position(&arm, target, q_init, q_sol, 100, 1e-4f, 0.05f)) {
        mat4_t t_verify;
        fk_solve(&arm, q_sol, NULL, &t_verify);
        printf("IK зійшлася: q = [%.3f, %.3f, %.3f] рад\n", q_sol[0], q_sol[1], q_sol[2]);
        printf("Кінцева позиція: [%.4f, %.4f, %.4f] м\n",
               t_verify.data[0][3], t_verify.data[1][3], t_verify.data[2][3]);
    } else {
        printf("IK не зійшлася (поза межами або сингулярність)\n");
    }
    return 0;
}
