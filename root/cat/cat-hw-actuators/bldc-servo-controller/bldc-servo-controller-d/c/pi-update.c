#include <math.h>

// Структура ПІ-регулятора струму
typedef struct {
    float kp;
    float ki;
    float integrator;
    float i_max;
    float out_max;
} PiController;

// Структура стану контуру FOC
typedef struct {
    float i_a;
    float i_b;
    float theta_e;
    float i_d_target;
    float i_q_target;
    PiController pi_d;
    PiController pi_q;
    float u_alpha;
    float u_beta;
} FocCurrentLoop;

static float pi_update(PiController *pi, float error, float dt) {
    pi->integrator += error * pi->ki * dt;
    if (pi->integrator > pi->i_max) {
        pi->integrator = pi->i_max;
    } else if (pi->integrator < -pi->i_max) {
        pi->integrator = -pi->i_max;
    }
    float output = error * pi->kp + pi->integrator;
    if (output > pi->out_max) {
        output = pi->out_max;
    } else if (output < -pi->out_max) {
        output = -pi->out_max;
    }
    return output;
}

// Виконання одного кроку розрахунку FOC-контуру струму
void foc_process_current_loop(FocCurrentLoop *foc, float dt) {
    // 1. Пряме перетворення Кларк (з abc в αβ)
    float i_alpha = foc->i_a;
    float i_beta = (foc->i_a + 2.0f * foc->i_b) * 0.57735026919f; // 1/√3

    // 2. Пряме перетворення Парка (з αβ у dq)
    float sin_th = sinf(foc->theta_e);
    float cos_th = cosf(foc->theta_e);

    float i_d = i_alpha * cos_th + i_beta * sin_th;
    float i_q = -i_alpha * sin_th + i_beta * cos_th;

    // 3. Обчислення ПІ-регуляторів струмів d та q
    float err_d = foc->i_d_target - i_d;
    float err_q = foc->i_q_target - i_q;

    float u_d = pi_update(&foc->pi_d, err_d, dt);
    float u_q = pi_update(&foc->pi_q, err_q, dt);

    // 4. Зворотне перетворення Парка (з dq в αβ для модулятора SVPWM)
    foc->u_alpha = u_d * cos_th - u_q * sin_th;
    foc->u_beta  = u_d * sin_th + u_q * cos_th;
}
