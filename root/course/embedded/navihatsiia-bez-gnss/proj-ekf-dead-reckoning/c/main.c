#include <math.h>
#include <stdbool.h>
#include <string.h>

#define STATE_DIM 9
#define GRAVITY_MSS 9.81f

/* Структура фільтра EKF Dead Reckoning */
typedef struct {
    float x[STATE_DIM];                  /* вектор стану: px, py, pz, vx, vy, vz, bax, bay, baz */
    float P[STATE_DIM][STATE_DIM];       /* матриця коваріації похибок 9x9 */
    float Q_pos;                         /* дисперсія процесу для координати */
    float Q_vel;                         /* дисперсія процесу для швидкості */
    float Q_bias;                        /* дисперсія випадкового блукання зсуву IMU */
} ekf_dr_t;

/* Ініціалізація початкового стану та коваріацій */
void ekf_dr_init(ekf_dr_t *ekf)
{
    memset(ekf->x, 0, sizeof(ekf->x));
    memset(ekf->P, 0, sizeof(ekf->P));

    /* Початкова невизначеність: координати ±1м, швидкості ±0.1м/с, зсув ±0.05м/с² */
    for (int i = 0; i < 3; i++) ekf->P[i][i] = 1.0f;
    for (int i = 3; i < 6; i++) ekf->P[i][i] = 0.01f;
    for (int i = 6; i < 9; i++) ekf->P[i][i] = 0.0025f;

    ekf->Q_pos = 0.001f;
    ekf->Q_vel = 0.05f;
    ekf->Q_bias = 0.00001f;
}

/* Крок ПЕРЕДБАЧЕННЯ (Predict) за даними IMU (200-500 Гц)
   a_body: виміряне акселерометром прискорення [ax, ay, az] (м/с²)
   R_wb: матриця обертання 3x3 з системи тіла у світ NED
   dt: інтервал інтегрування (с) */
void ekf_dr_predict(ekf_dr_t *ekf, const float a_body[3], const float R_wb[3][3], float dt)
{
    /* 1. Компенсація оціненого зсуву нуля акселерометра */
    float a_unbiased[3];
    for (int i = 0; i < 3; i++) {
        a_unbiased[i] = a_body[i] - ekf->x[6 + i];
    }

    /* 2. Обертання прискорення у світову систему NED: a_world = R_wb * a_unbiased */
    float a_world[3] = {0};
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            a_world[i] += R_wb[i][j] * a_unbiased[j];
        }
    }
    /* Додаємо гравітацію (вісь Z спрямована вниз, прискорення вільного падіння +g) */
    a_world[2] += GRAVITY_MSS;

    /* 3. Кінематична інтеграція координат та швидкостей */
    float dt2 = 0.5f * dt * dt;
    for (int i = 0; i < 3; i++) {
        ekf->x[i]     += ekf->x[3 + i] * dt + a_world[i] * dt2;   /* p = p + v*dt + 0.5*a*dt² */
        ekf->x[3 + i] += a_world[i] * dt;                         /* v = v + a*dt */
    }

    /* 4. Екстраполяція коваріації: аналітичне розгортання для продуктивності на MCU */
    for (int i = 0; i < 3; i++) {
        ekf->P[i][i]         += (2.0f * ekf->P[3 + i][3 + i] * dt + ekf->Q_pos) * dt;
        ekf->P[3 + i][3 + i] += ekf->Q_vel * dt;
        ekf->P[6 + i][6 + i] += ekf->Q_bias * dt;
    }
}

/* Крок КОРЕКЦІЇ за даними ОПТИЧНОГО ПОТОКУ (вимірювання швидкості Vx, Vy)
   vx_meas, vy_meas: лінійна швидкість у системі світу (після деротації та масштабування висотою)
   r_cov: дисперсія шуму оптичного потоку (м²/с²)
   gate_limit: поріг відкидання викидів Махаланобіса */
bool ekf_dr_update_velocity2d(ekf_dr_t *ekf, float vx_meas, float vy_meas, float r_cov, float gate_limit)
{
    float z[2] = {vx_meas, vy_meas};

    for (int axis = 0; axis < 2; axis++) {
        int v_idx = 3 + axis;
        float y = z[axis] - ekf->x[v_idx];              /* інновація (нев'язка) */
        float S = ekf->P[v_idx][v_idx] + r_cov;          /* коваріація інновації */

        /* Тест Махаланобіса на відкидання викидів */
        if ((y * y) / S > gate_limit) {
            return false; /* викид сенсора або змаз кадру — пропускаємо */
        }

        float K = ekf->P[v_idx][v_idx] / S;             /* коефіцієнт Калмана */

        /* Корекція вектора стану */
        ekf->x[v_idx] += K * y;

        /* Непряма корекція зсуву акселерометра */
        int b_idx = 6 + axis;
        float K_bias = ekf->P[b_idx][b_idx] / S;
        ekf->x[b_idx] -= K_bias * (y * 0.1f);

        /* Оновлення коваріації */
        ekf->P[v_idx][v_idx] *= (1.0f - K);
    }
    return true;
}

/* Крок КОРЕКЦІЇ ВИСОТИ за далекоміром ToF або барометром */
void ekf_dr_update_altitude(ekf_dr_t *ekf, float z_meas, float r_cov)
{
    float y = z_meas - ekf->x[2];                        /* нев'язка по осі Z */
    float S = ekf->P[2][2] + r_cov;
    float K = ekf->P[2][2] / S;

    ekf->x[2] += K * y;                                  /* коригуємо висоту */
    ekf->x[5] += (K * 0.5f) * y;                         /* частково підтягуємо вертикальну швидкість */
    ekf->P[2][2] *= (1.0f - K);
}

/* Крок ZUPT (Zero Velocity Update) при повній зупинці апарата */
void ekf_dr_update_zupt(ekf_dr_t *ekf, float r_zupt)
{
    for (int i = 3; i < 6; i++) {
        float y = 0.0f - ekf->x[i];                      /* швидкість у спокої дорівнює нулю */
        float S = ekf->P[i][i] + r_zupt;
        float K = ekf->P[i][i] / S;

        ekf->x[i] += K * y;
        ekf->P[i][i] *= (1.0f - K);

        /* Скидання зсуву акселерометра під час нерухомості */
        int b_idx = 6 + (i - 3);
        ekf->x[b_idx] += (ekf->P[b_idx][b_idx] / S) * y;
    }
}
