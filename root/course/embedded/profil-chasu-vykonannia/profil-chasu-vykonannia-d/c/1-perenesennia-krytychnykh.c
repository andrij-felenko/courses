/* Розміщення критичної математичної функції в SRAM на C */
#include <stdint.h>

#define RAM_FUNCTION __attribute__((section(".ramfunc"), noinline))

/* Ця функція компілюється для виконання в SRAM: 0 Flash Wait States */
RAM_FUNCTION void fast_foc_current_pid_step(float i_err_d, float i_err_q, 
                                            float *v_out_d, float *v_out_q) {
    static float i_integrator_d = 0.0f;
    static float i_integrator_q = 0.0f;
    const float Kp = 2.5f;
    const float Ki = 0.08f;

    i_integrator_d += Ki * i_err_d;
    i_integrator_q += Ki * i_err_q;

    *v_out_d = (Kp * i_err_d) + i_integrator_d;
    *v_out_q = (Kp * i_err_q) + i_integrator_q;
}
