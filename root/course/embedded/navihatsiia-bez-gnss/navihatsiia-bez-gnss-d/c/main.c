#include <stdbool.h>
#include <math.h>

#define STATE_DIM 9
#define GRAVITY   9.81f

typedef struct {
    float x[STATE_DIM];            /* px, py, pz, vx, vy, vz, bax, bay, baz */
    float P[STATE_DIM];            /* дисперсії стану (діагональ коваріації) */
    float q_pos, q_vel, q_bias;    /* шуми процесу */
} ekf_nav_t;

/* Крок передбачення (Predict) за даними IMU на високій частоті */
void ekf_nav_predict(ekf_nav_t *ekf, const float a_body[3], const float R_wb[3][3], float dt)
{
    float a_unbiased[3];
    for (int i = 0; i < 3; i++) {
        a_unbiased[i] = a_body[i] - ekf->x[6 + i];
    }

    /* Обертання у світову систему NED: a_world = R_wb * a_unbiased */
    float a_world[3] = {0.0f, 0.0f, 0.0f};
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            a_world[i] += R_wb[i][j] * a_unbiased[j];
        }
    }
    a_world[2] += GRAVITY; /* додаємо вектор тяжіння вниз (+Z) */

    /* Інтегрування кінематики */
    float dt2 = 0.5f * dt * dt;
    for (int i = 0; i < 3; i++) {
        ekf->x[i]     += ekf->x[3 + i] * dt + a_world[i] * dt2;
        ekf->x[3 + i] += a_world[i] * dt;
    }

    /* Екстраполяція невизначеності */
    for (int i = 0; i < 3; i++) {
        ekf->P[i]     += (2.0f * ekf->P[3 + i] * dt + ekf->q_pos) * dt;
        ekf->P[3 + i] += ekf->q_vel * dt;
        ekf->P[6 + i] += ekf->q_bias * dt;
    }
}

/* Крок корекції швидкості за оптичним потоком (Update) */
bool ekf_nav_update_flow(ekf_nav_t *ekf, float vx_m, float vy_m, float r_flow, float gate_limit)
{
    float z[2] = {vx_m, vy_m};

    for (int axis = 0; axis < 2; axis++) {
        int v_idx = 3 + axis;
        float y = z[axis] - ekf->x[v_idx];         /* інновація */
        float S = ekf->P[v_idx] + r_flow;          /* дисперсія інновації */

        /* Gate-тест Махаланобіса на відкидання викидів */
        if ((y * y) / S > gate_limit) {
            return false;
        }

        float K = ekf->P[v_idx] / S;                /* підсилення Калмана */
        ekf->x[v_idx] += K * y;                     /* оновлення швидкості */

        /* Непряма корекція зсуву акселерометра */
        int b_idx = 6 + axis;
        ekf->x[b_idx] -= (ekf->P[b_idx] / S) * (y * 0.1f);

        ekf->P[v_idx] *= (1.0f - K);                /* зменшення дисперсії */
    }
    return true;
}
