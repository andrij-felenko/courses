#ifndef ADMITTANCE_H
#define ADMITTANCE_H

#include <stdbool.h>
#include <stdint.h>

#define ADM_DOF          6      /* Fx Fy Fz Tx Ty Tz — декартова шістка */
#define ADM_DT_SEC       0.001f /* крок контуру жорсткого реального часу, 1 кГц */
#define ADM_TARE_SAMPLES 500    /* 0.5 с усереднення нуля давача */

/* Скінченний автомат безпеки. Перехід IDLE → TARING робить виклик
   admittance_start_tare(), TARING → ACTIVE автомат робить сам,
   ACTIVE → FORCE_EXCEEDED → RETRACT — перевищення сили,
   RETRACT → ACTIVE — квитування оператором (admittance_acknowledge). */
typedef enum {
    ADMITTANCE_MODE_IDLE = 0,
    ADMITTANCE_MODE_TARING,
    ADMITTANCE_MODE_ACTIVE,
    ADMITTANCE_MODE_FORCE_EXCEEDED,
    ADMITTANCE_MODE_RETRACT,
    ADMITTANCE_MODE_FAULT
} admittance_mode_t;

typedef struct {
    float m_d[ADM_DOF];        /* віртуальна маса (кг, кг·м²) */
    float d_d[ADM_DOF];        /* віртуальне демпфування (Н·с/м, Н·м·с/рад) */
    float k_d[ADM_DOF];        /* віртуальна жорсткість (Н/м, Н·м/рад) */
    float filter_alpha;        /* коефіцієнт ФНЧ першого порядку, 0 < alpha <= 1 */
    float deadband[ADM_DOF];   /* зона нечутливості (Н, Н·м) */
    float max_force[ADM_DOF];  /* аварійний ліміт сили (Н, Н·м) */
    float max_disp[ADM_DOF];   /* межа ходу податливості (м, рад) */
    float max_vel[ADM_DOF];    /* межа швидкості податливості (м/с, рад/с) */
    float retract_speed;       /* швидкість аварійного відходу (м/с) */
} admittance_config_t;

typedef struct {
    float f_raw_offset[ADM_DOF];     /* зсув нуля, знятий таруванням */
    float f_filt[ADM_DOF];           /* відфільтрована сила (після зняття нуля) */
    float disp[ADM_DOF];             /* поточне зміщення податливості */
    float vel[ADM_DOF];              /* поточна швидкість зміщення */
    float retract_dir[ADM_DOF];      /* одиничний напрямок відходу (нормаль контакту) */
    float tare_accumulator[ADM_DOF]; /* сума вибірок під час тарування */
    uint32_t tare_counter;
    admittance_mode_t mode;
} admittance_context_t;

/* alpha для ФНЧ першого порядку із заданою частотою зрізу на кроці ADM_DT_SEC. */
float admittance_alpha_for_cutoff(float cutoff_hz);

/* D_d = 2·sqrt(M_d·K_d): zeta = 1, зрив контакту без перерегулювання. */
void admittance_set_critical_damping(admittance_config_t *cfg);

bool admittance_config_valid(const admittance_config_t *cfg);

void admittance_init(admittance_context_t *ctx);
void admittance_start_tare(admittance_context_t *ctx);

/* Квитування аварії: RETRACT → ACTIVE. Накопичене зміщення лишається —
   до номіналу його поверне сама віртуальна пружина. */
void admittance_acknowledge(admittance_context_t *ctx);

/* Один такт контуру.
   f_ext     — сила РЕАКЦІЇ (з якою інструмент тисне на середовище) у системі
               давача, вже без ваги інструмента, але ще зі зсувом нуля;
   x_nominal — номінальна траєкторія в тій самій системі;
   x_cmd     — траєкторія, зміщена податливістю; v_cmd — відповідна швидкість.
   Повертає новий стан автомата; вихідні масиви заповнюються ЗАВЖДИ,
   у тому числі в аварійних станах. */
admittance_mode_t admittance_step(const admittance_config_t *cfg,
                                  admittance_context_t *ctx,
                                  const float f_ext[ADM_DOF],
                                  const float x_nominal[ADM_DOF],
                                  const float v_nominal[ADM_DOF],
                                  float x_cmd[ADM_DOF],
                                  float v_cmd[ADM_DOF]);

#endif /* ADMITTANCE_H */
