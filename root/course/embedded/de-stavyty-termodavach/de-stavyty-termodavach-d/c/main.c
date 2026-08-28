/* Обчислення одного кроку компенсатора самонагріву */
float thermal_compensator_step(float t_raw, float p_heat, float dt,
                               float r_th1, float tau1, float *state1,
                               float r_th2, float tau2, float *state2) {
    /* Розрахунок коефіцієнтів згладжування */
    float a1 = expf(-dt / tau1);
    float a2 = expf(-dt / tau2);

    /* Інтегрування швидкої та повільної ланок */
    *state1 = (a1 * (*state1)) + ((1.0f - a1) * (r_th1 * p_heat));
    *state2 = (a2 * (*state2)) + ((1.0f - a2) * (r_th2 * p_heat));

    /* Віднімання змодельованого сумарного самонагріву */
    float delta_self = (*state1) + (*state2);
    return t_raw - delta_self;
}
