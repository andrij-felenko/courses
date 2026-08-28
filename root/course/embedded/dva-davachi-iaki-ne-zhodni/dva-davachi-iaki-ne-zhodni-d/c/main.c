#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define VOTER_MAX_SENSORS 3

typedef enum {
    BIAS_FAILSAFE_DEFAULT = 0, /* Скидання у фіксований безпечний стан (напр. 0) */
    BIAS_PESSIMISTIC_MAX  = 1, /* Вибір максимуму (температура, тиск, струм) */
    BIAS_PESSIMISTIC_MIN  = 2  /* Вибір мінімуму (висота, дистанція, заряд) */
} VoterBiasPolicy;

typedef enum {
    VOTER_STATE_HEALTHY_CONSENSUS   = 0, /* Усі канали узгоджені */
    VOTER_STATE_DEGRADED_TMR        = 1, /* Відкинуто 1 канал у схемі 2oo3 */
    VOTER_STATE_DEGRADED_ANALYTICAL = 2, /* 1oo2 розв'язано фізичною моделлю */
    VOTER_STATE_BIASED_FAILSAFE     = 3, /* 1oo2 розв'язано через Safe Bias */
    VOTER_STATE_CRITICAL_FAULT      = 4  /* Повна втрата достовірності */
} VoterState;

typedef struct {
    float tolerance;            /* Максимальна допустима різниця між каналами */
    float model_tolerance;      /* Допуск між давачем і моделлю */
    uint16_t trip_debounce;     /* Кількість циклів незгоди для входу в аварію */
    uint16_t heal_debounce;     /* Кількість циклів згоди для виходу з аварії */
    VoterBiasPolicy bias_policy;/* Політика захисного зміщення при 1oo2 */
    float failsafe_default;     /* Значення за замовчуванням при аварії */
} VoterConfig;

typedef struct {
    VoterConfig cfg;
    VoterState state;
    uint16_t fault_counter;
    uint16_t heal_counter;
    uint8_t healthy_mask;       /* Бітова маска справних каналів (біт 0..2) */
    float last_valid_output;
} SensorVoter;

void voter_init(SensorVoter *voter, const VoterConfig *config) {
    voter->cfg = *config;
    voter->state = VOTER_STATE_HEALTHY_CONSENSUS;
    voter->fault_counter = 0;
    voter->heal_counter = 0;
    voter->healthy_mask = 0x07;
    voter->last_valid_output = config->failsafe_default;
}

static float apply_bias(float v0, float v1, VoterBiasPolicy policy, float def_val) {
    switch (policy) {
        case BIAS_PESSIMISTIC_MAX: return (v0 > v1) ? v0 : v1;
        case BIAS_PESSIMISTIC_MIN: return (v0 < v1) ? v0 : v1;
        case BIAS_FAILSAFE_DEFAULT:
        default:
            return def_val;
    }
}

bool voter_process(SensorVoter *voter, 
                   const float *readings, 
                   uint8_t count, 
                   const float *opt_model_val, 
                   float *out_val) 
{
    if (count < 2 || count > VOTER_MAX_SENSORS || !readings || !out_val) {
        if (out_val) *out_val = voter->cfg.failsafe_default;
        voter->state = VOTER_STATE_CRITICAL_FAULT;
        return false;
    }

    /* ── ОБРОБКА ДВОХ ДАВАЧІВ (1oo2 / Дублювання) ── */
    if (count == 2) {
        float diff = fabsf(readings[0] - readings[1]);
        
        if (diff <= voter->cfg.tolerance) {
            /* Канали узгоджені */
            if (voter->fault_counter > 0) voter->fault_counter--;
            if (voter->heal_counter < voter->cfg.heal_debounce) voter->heal_counter++;
            
            if (voter->heal_counter >= voter->cfg.heal_debounce) {
                voter->state = VOTER_STATE_HEALTHY_CONSENSUS;
                voter->healthy_mask = 0x03;
            }
            
            *out_val = (readings[0] + readings[1]) * 0.5f;
            voter->last_valid_output = *out_val;
            return true;
        }

        /* Розбіжність перевищила допуск */
        voter->heal_counter = 0;
        if (voter->fault_counter < voter->cfg.trip_debounce) {
            voter->fault_counter++;
            /* Поки дебаунс не накопичився — віддаємо останнє валідне значення */
            *out_val = voter->last_valid_output;
            return true;
        }

        /* Аварія підтверджена часом: спроба арбітражу моделлю */
        if (opt_model_val != NULL) {
            float err0 = fabsf(readings[0] - *opt_model_val);
            float err1 = fabsf(readings[1] - *opt_model_val);

            if (err0 <= voter->cfg.model_tolerance && err1 > voter->cfg.model_tolerance) {
                voter->state = VOTER_STATE_DEGRADED_ANALYTICAL;
                voter->healthy_mask = 0x01; /* Канал 0 справний */
                *out_val = readings[0];
                voter->last_valid_output = *out_val;
                return true;
            } else if (err1 <= voter->cfg.model_tolerance && err0 > voter->cfg.model_tolerance) {
                voter->state = VOTER_STATE_DEGRADED_ANALYTICAL;
                voter->healthy_mask = 0x02; /* Канал 1 справний */
                *out_val = readings[1];
                voter->last_valid_output = *out_val;
                return true;
            }
        }

        /* Моделі немає або обидва канали розійшлися з моделлю: Safe Bias */
        voter->state = VOTER_STATE_BIASED_FAILSAFE;
        voter->healthy_mask = 0x00;
        *out_val = apply_bias(readings[0], readings[1], voter->cfg.bias_policy, voter->cfg.failsafe_default);
        voter->last_valid_output = *out_val;
        return (voter->cfg.bias_policy != BIAS_FAILSAFE_DEFAULT);
    }

    /* ── ОБРОБКА ТРЬОХ ДАВАЧІВ (2oo3 / TMR) ── */
    float d01 = fabsf(readings[0] - readings[1]);
    float d12 = fabsf(readings[1] - readings[2]);
    float d20 = fabsf(readings[2] - readings[0]);

    bool pair01 = (d01 <= voter->cfg.tolerance);
    bool pair12 = (d12 <= voter->cfg.tolerance);
    bool pair20 = (d20 <= voter->cfg.tolerance);

    if (pair01 && pair12 && pair20) {
        /* Усі три канали в консенсусі */
        voter->state = VOTER_STATE_HEALTHY_CONSENSUS;
        voter->healthy_mask = 0x07;
        voter->fault_counter = 0;
        *out_val = (readings[0] + readings[1] + readings[2]) / 3.0f;
        voter->last_valid_output = *out_val;
        return true;
    }

    if (pair01) {
        /* Канали 0 і 1 згодні, канал 2 — викид */
        voter->state = VOTER_STATE_DEGRADED_TMR;
        voter->healthy_mask = 0x03;
        *out_val = (readings[0] + readings[1]) * 0.5f;
    } else if (pair12) {
        /* Канали 1 і 2 згодні, канал 0 — викид */
        voter->state = VOTER_STATE_DEGRADED_TMR;
        voter->healthy_mask = 0x06;
        *out_val = (readings[1] + readings[2]) * 0.5f;
    } else if (pair20) {
        /* Канали 2 і 0 згодні, канал 1 — викид */
        voter->state = VOTER_STATE_DEGRADED_TMR;
        voter->healthy_mask = 0x05;
        *out_val = (readings[2] + readings[0]) * 0.5f;
    } else {
        /* Повна втрата кворуму в TMR: жодна пара не збіглася */
        voter->state = VOTER_STATE_CRITICAL_FAULT;
        voter->healthy_mask = 0x00;
        *out_val = voter->cfg.failsafe_default;
        return false;
    }

    voter->last_valid_output = *out_val;
    return true;
}
