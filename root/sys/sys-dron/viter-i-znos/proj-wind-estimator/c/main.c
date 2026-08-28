#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define PI_F 3.14159265358979323846f
#define TWO_PI_F (2.0f * PI_F)

/* Нормалізація кута в діапазон [-pi, +pi] */
static float wrap_pi(float angle) {
    while (angle > PI_F) {
        angle -= TWO_PI_F;
    }
    while (angle < -PI_F) {
        angle += TWO_PI_F;
    }
    return angle;
}

/* Обмеження величини в діапазон [min, max] */
static float constrain_f(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/* Структура стану фільтра вітру EKF */
typedef struct {
    float state[3];      /* [0]: W_N (м/с), [1]: W_E (м/с), [2]: k_scale (коеф. піто) */
    float P[3][3];       /* Коваріаційна матриця оцінки */
    float Q_wind;        /* Дисперсія процесу для вітру (м/с)^2 / с */
    float Q_scale;       /* Дисперсія процесу для коефіцієнта трубки Піто */
    float R_tas;         /* Дисперсія вимірювання повітряної швидкості (м/с)^2 */
    bool  initialized;
} WindEkf;

/* Структура розв'язку навігаційного трикутника */
typedef struct {
    float heading_cmd_rad;    /* Заданий курс орієнтації носа psi (рад) */
    float crab_angle_rad;     /* Кут крабування alpha_c (рад) */
    float ground_speed_exp;   /* Очікувана шляхова швидкість V_g (м/с) */
    bool  is_solvable;        /* Чи вистачає швидкості подолати вітер */
} CrabAngleSolution;

/* Ініціалізація EKF оцінювача вітру */
void wind_ekf_init(WindEkf *ekf) {
    ekf->state[0] = 0.0f; /* Початковий вітер Північ = 0 */
    ekf->state[1] = 0.0f; /* Початковий вітер Схід = 0 */
    ekf->state[2] = 1.0f; /* Номінальний масштаб трубки Піто = 1.0 */

    memset(ekf->P, 0, sizeof(ekf->P));
    ekf->P[0][0] = 25.0f;   /* Початкова дисперсія W_N: (5 м/с)^2 */
    ekf->P[1][1] = 25.0f;   /* Початкова дисперсія W_E: (5 м/с)^2 */
    ekf->P[2][2] = 0.04f;   /* Початкова дисперсія k_scale: (0.2)^2 */

    ekf->Q_wind  = 0.1f;    /* Шум випадкового блукання вітру */
    ekf->Q_scale = 0.00001f;/* Повільний дрейф масштабу датчика */
    ekf->R_tas   = 1.5f;    /* Шум вимірювання датчика тиску */
    ekf->initialized = true;
}

/* Крок прогнозу фільтра Калмана (часова екстраполяція) */
void wind_ekf_predict(WindEkf *ekf, float dt) {
    if (!ekf->initialized || dt <= 0.0f) return;

    /* Стан не змінюється (W_dot = 0, k_scale_dot = 0) */
    /* Зростання коваріації за рахунок процесного шуму */
    ekf->P[0][0] += ekf->Q_wind * dt;
    ekf->P[1][1] += ekf->Q_wind * dt;
    ekf->P[2][2] += ekf->Q_scale * dt;
}

/* Крок корекції за даними трубки Піто, GNSS швидкості та орієнтації */
bool wind_ekf_fuse_airspeed(WindEkf *ekf,
                            float tas_measured,
                            float vg_n,
                            float vg_e,
                            float heading_rad,
                            float pitch_rad) {
    if (!ekf->initialized || tas_measured <= 1.0f) return false;

    float cos_hdg = cosf(heading_rad);
    float sin_hdg = sinf(heading_rad);
    float cos_pit = cosf(pitch_rad);

    /* Проєкція повітряної швидкості в горизонтальну площину NED */
    float dir_n = cos_hdg * cos_pit;
    float dir_e = sin_hdg * cos_pit;

    float k_scale = ekf->state[2];
    float tas_scaled = k_scale * tas_measured;

    /* Очікувана швидкість по землі: v_g_pred = v_a + W */
    float pred_vg_n = dir_n * tas_scaled + ekf->state[0];
    float pred_vg_e = dir_e * tas_scaled + ekf->state[1];

    /* Очікуваний модуль повітряної швидкості за різницею швидкостей: */
    /* v_a_vec = V_g - W */
    float diff_n = vg_n - ekf->state[0];
    float diff_e = vg_e - ekf->state[1];
    float pred_tas = sqrtf(diff_n * diff_n + diff_e * diff_e);

    if (pred_tas < 0.1f) return false;

    /* Інновація (нев'язка вимірювання): y = tas_scaled - pred_tas */
    float innov = tas_scaled - pred_tas;

    /* Матриця спостереження H (Якобіан відносно [W_N, W_E, k_scale]): */
    float H[3];
    H[0] = -diff_n / pred_tas;
    H[1] = -diff_e / pred_tas;
    H[2] = tas_measured;

    /* P * H^T */
    float PHt[3];
    PHt[0] = ekf->P[0][0] * H[0] + ekf->P[0][1] * H[1] + ekf->P[0][2] * H[2];
    PHt[1] = ekf->P[1][0] * H[0] + ekf->P[1][1] * H[1] + ekf->P[1][2] * H[2];
    PHt[2] = ekf->P[2][0] * H[0] + ekf->P[2][1] * H[1] + ekf->P[2][2] * H[2];

    /* Інноваційна коваріація: S = H * P * H^T + R */
    float S = H[0] * PHt[0] + H[1] * PHt[1] + H[2] * PHt[2] + ekf->R_tas;
    if (S <= 0.0001f) return false;

    /* Коефіцієнт підсилення Калмана: K = PHt / S */
    float K[3];
    K[0] = PHt[0] / S;
    K[1] = PHt[1] / S;
    K[2] = PHt[2] / S;

    /* Оновлення стану: x = x + K * innov */
    ekf->state[0] += K[0] * innov;
    ekf->state[1] += K[1] * innov;
    ekf->state[2] += K[2] * innov;

    /* Обмеження масштабу трубки Піто у розумних межах [0.7, 1.3] */
    ekf->state[2] = constrain_f(ekf->state[2], 0.7f, 1.3f);

    /* Оновлення коваріаційної матриці: P = (I - K*H) * P */
    float I_KH[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            float kh = K[i] * H[j];
            I_KH[i][j] = (i == j ? 1.0f : 0.0f) - kh;
        }
    }

    float P_new[3][3];
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            P_new[i][j] = 0.0f;
            for (int k = 0; k < 3; k++) {
                P_new[i][j] += I_KH[i][k] * ekf->P[k][j];
            }
        }
    }
    memcpy(ekf->P, P_new, sizeof(ekf->P));
    return true;
}

/* Отримання поточної оцінки вітру */
void wind_ekf_get_wind(const WindEkf *ekf, float *wind_n, float *wind_e, float *wind_speed, float *wind_dir_rad) {
    *wind_n = ekf->state[0];
    *wind_e = ekf->state[1];
    *wind_speed = sqrtf((*wind_n) * (*wind_n) + (*wind_e) * (*wind_e));
    *wind_dir_rad = wrap_pi(atan2f(*wind_e, *wind_n));
}

/* Розрахунок навігаційного кута крабування та уставки курсу */
CrabAngleSolution solve_crab_angle(float track_cmd_rad,
                                  float tas,
                                  float wind_n,
                                  float wind_e) {
    CrabAngleSolution sol;
    memset(&sol, 0, sizeof(sol));

    if (tas < 1.0f) {
        sol.heading_cmd_rad = track_cmd_rad;
        sol.is_solvable = false;
        return sol;
    }

    /* Проєкція вітру на нормаль до лінії шляху: W_cross (з правого борту > 0) */
    float w_cross = wind_n * sinf(track_cmd_rad) - wind_e * cosf(track_cmd_rad);
    /* Проєкція вітру вздовж лінії шляху: W_along (попутний > 0, зустрічний < 0) */
    float w_along = wind_n * cosf(track_cmd_rad) + wind_e * sinf(track_cmd_rad);

    float sin_crab_arg = w_cross / tas;

    if (fabsf(sin_crab_arg) >= 1.0f) {
        /* Критичний вітер: боковий вітер перевищує повітряну швидкість */
        sol.is_solvable = false;
        sol.crab_angle_rad = (sin_crab_arg > 0.0f) ? (PI_F * 0.5f) : (-PI_F * 0.5f);
        sol.heading_cmd_rad = wrap_pi(track_cmd_rad - sol.crab_angle_rad);
        sol.ground_speed_exp = 0.0f;
        return sol;
    }

    /* Стандартний розрахунок кута крабування */
    sol.crab_angle_rad = asinf(sin_crab_arg);
    sol.heading_cmd_rad = wrap_pi(track_cmd_rad - sol.crab_angle_rad);
    sol.ground_speed_exp = tas * cosf(sol.crab_angle_rad) + w_along;
    sol.is_solvable = (sol.ground_speed_exp > 0.0f);

    return sol;
}
