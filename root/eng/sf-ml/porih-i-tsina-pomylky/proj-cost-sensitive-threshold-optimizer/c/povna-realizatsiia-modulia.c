#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define CLAMP_F(x, low, high) (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))

/* ── Константи та структури даних ─────────────────────────────────────────── */

#define CALIBRATION_TABLE_MAX_SIZE 16
#define BLACKBOX_BUFFER_SIZE 256

/* Режими калібрування */
typedef enum {
    CALIB_MODE_PLATT = 0,
    CALIB_MODE_TEMPERATURE = 1,
    CALIB_MODE_ISOTONIC_TABLE = 2
} c_calib_mode_t;

/* Вузол ізотонічної калібрувальної таблиці */
typedef struct {
    float raw_score;      /* Вхідний скор моделі */
    float calibrated_prob;/* Відповідна емпірична ймовірність */
} c_calib_point_t;

/* Об'єднана конфігурація калібратора */
typedef struct {
    c_calib_mode_t mode;
    float platt_a;
    float platt_b;
    float temperature;
    
    c_calib_point_t table[CALIBRATION_TABLE_MAX_SIZE];
    uint8_t table_size;
} c_calibrator_config_t;

/* Матриця вартостей рішень */
typedef struct {
    float cost_tp;  /* Штраф за True Positive */
    float cost_fp;  /* Штраф за False Positive */
    float cost_tn;  /* Штраф за True Negative */
    float cost_fn;  /* Штраф за False Negative */
} c_cost_matrix_t;

/* Вектор зовнішнього контексту */
typedef struct {
    float battery_ratio; /* Заряд батареї від 0.0 до 1.0 */
    float speed_mps;     /* Швидкість платформи, м/с */
    float queue_ratio;   /* Заповнення черги оператора від 0.0 до 1.0 */
    float sensor_noise;  /* Дисперсія шуму сенсора */
} c_adaptive_context_t;

/* Запис чорної скриньки */
typedef struct {
    uint32_t timestamp_us;
    float raw_score;
    float calibrated_prob;
    float active_threshold;
    float battery_ratio;
    float speed_mps;
    bool decision;
} c_blackbox_entry_t;

/* Коефіцієнти адаптера */
typedef struct {
    float beta_battery;   /* Чутливість до батареї */
    float crit_battery;   /* Критичний рівень батареї */
    float beta_speed;     /* Чутливість до швидкості */
    float max_speed_mps;  /* Максимальна швидкість */
    float beta_queue;     /* Чутливість до черги */
    float ema_alpha;      /* Коефіцієнт EMA */
    float base_hyst_width;/* Базова ширина гістерезису */
    float noise_hyst_gain;/* Коефіцієнт розширення гістерезису від шуму */
} c_adapter_config_t;

/* Стан вбудованого оптимізатора */
typedef struct {
    c_cost_matrix_t base_costs;
    c_cost_matrix_t current_costs;
    c_calibrator_config_t calibrator;
    c_adapter_config_t config;
    
    float prior_positive;
    float current_threshold;
    float current_hyst_width;
    bool previous_decision;
    bool is_initialized;
    
    c_blackbox_entry_t blackbox[BLACKBOX_BUFFER_SIZE];
    uint16_t blackbox_head;
} c_threshold_optimizer_t;

/* Результат класифікації */
typedef struct {
    bool decision;             /* Фінальне рішення (1 = тривога) */
    float calibrated_prob;     /* Оцінка p(x) */
    float active_threshold;    /* Поточний поріг T* */
    float expected_risk;       /* Очікувані втрати */
    float confidence_margin;   /* Дистанція до порогу */
} c_decision_result_t;

/* ── Реалізація функцій ──────────────────────────────────────────────────── */

static inline float safe_sigmoid(float logit) {
    float clamped = CLAMP_F(logit, -85.0f, 85.0f);
    return 1.0f / (1.0f + expf(-clamped));
}

/* Ініціалізація оптимізатора */
bool c_optimizer_init(
    c_threshold_optimizer_t *opt,
    c_cost_matrix_t base_costs,
    c_calibrator_config_t calibrator,
    c_adapter_config_t config,
    float prior_pos
) {
    if (!opt || prior_pos <= 0.0f || prior_pos >= 1.0f) {
        return false;
    }
    
    if (base_costs.cost_fn <= base_costs.cost_tp || base_costs.cost_fp <= base_costs.cost_tn) {
        return false;
    }
    
    if (config.ema_alpha <= 0.0f || config.ema_alpha > 1.0f || config.max_speed_mps <= 0.0f) {
        return false;
    }
    
    opt->base_costs = base_costs;
    opt->current_costs = base_costs;
    opt->calibrator = calibrator;
    opt->config = config;
    opt->prior_positive = prior_pos;
    
    float num = base_costs.cost_fp - base_costs.cost_tn;
    float den = (base_costs.cost_fp - base_costs.cost_tn) + (base_costs.cost_fn - base_costs.cost_tp);
    opt->current_threshold = num / den;
    opt->current_hyst_width = config.base_hyst_width;
    
    opt->previous_decision = false;
    opt->blackbox_head = 0;
    opt->is_initialized = true;
    return true;
}

/* Калібрування сирого скору */
static float calibrate_score(const c_calibrator_config_t *cal, float raw_score) {
    if (cal->mode == CALIB_MODE_TEMPERATURE) {
        float temp = (cal->temperature > 1e-4f) ? cal->temperature : 1.0f;
        return safe_sigmoid(raw_score / temp);
    }
    
    if (cal->mode == CALIB_MODE_PLATT) {
        float z = -(cal->platt_a * raw_score + cal->platt_b);
        return safe_sigmoid(z);
    }
    
    if (cal->mode == CALIB_MODE_ISOTONIC_TABLE && cal->table_size >= 2) {
        if (raw_score <= cal->table[0].raw_score) {
            return cal->table[0].calibrated_prob;
        }
        if (raw_score >= cal->table[cal->table_size - 1].raw_score) {
            return cal->table[cal->table_size - 1].calibrated_prob;
        }
        
        uint8_t low = 0;
        uint8_t high = cal->table_size - 1;
        
        while (high - low > 1) {
            uint8_t mid = (low + high) >> 1;
            if (cal->table[mid].raw_score <= raw_score) {
                low = mid;
            } else {
                high = mid;
            }
        }
        
        float z0 = cal->table[low].raw_score;
        float z1 = cal->table[high].raw_score;
        float p0 = cal->table[low].calibrated_prob;
        float p1 = cal->table[high].calibrated_prob;
        
        float dz = z1 - z0;
        if (fabsf(dz) < 1e-6f) return p0;
        
        float t = (raw_score - z0) / dz;
        return p0 + t * (p1 - p0);
    }
    
    return safe_sigmoid(raw_score);
}

/* Оновлення контексту середовища та розрахунок порогу */
void c_optimizer_update_context(
    c_threshold_optimizer_t *opt,
    c_adaptive_context_t ctx
) {
    if (!opt || !opt->is_initialized) return;
    
    float batt_deficit = 0.0f;
    if (ctx.battery_ratio < opt->config.crit_battery) {
        batt_deficit = (opt->config.crit_battery - ctx.battery_ratio) / opt->config.crit_battery;
    }
    float k_batt = 1.0f + opt->config.beta_battery * batt_deficit;
    
    float speed_ratio = ctx.speed_mps / opt->config.max_speed_mps;
    speed_ratio = CLAMP_F(speed_ratio, 0.0f, 2.0f);
    float k_speed = 1.0f + opt->config.beta_speed * (speed_ratio * speed_ratio);
    
    float q_ratio = CLAMP_F(ctx.queue_ratio, 0.0f, 1.0f);
    float k_queue = 1.0f + opt->config.beta_queue * (q_ratio * q_ratio);
    
    opt->current_costs.cost_fp = opt->base_costs.cost_fp * k_batt * k_queue;
    opt->current_costs.cost_fn = opt->base_costs.cost_fn * k_speed;
    opt->current_costs.cost_tp = opt->base_costs.cost_tp;
    opt->current_costs.cost_tn = opt->base_costs.cost_tn;
    
    float num = opt->current_costs.cost_fp - opt->current_costs.cost_tn;
    float den = (opt->current_costs.cost_fp - opt->current_costs.cost_tn) + 
                (opt->current_costs.cost_fn - opt->current_costs.cost_tp);
    
    float raw_target = CLAMP_F(num / den, 0.001f, 0.999f);
    
    opt->current_threshold = opt->config.ema_alpha * raw_target + 
                             (1.0f - opt->config.ema_alpha) * opt->current_threshold;
    
    opt->current_hyst_width = opt->config.base_hyst_width + 
                             opt->config.noise_hyst_gain * ctx.sensor_noise;
}

/* Обробка одного інференс-зрізу */
c_decision_result_t c_optimizer_process_sample(
    c_threshold_optimizer_t *opt,
    float raw_score
) {
    c_decision_result_t res;
    if (!opt || !opt->is_initialized) {
        res.decision = false;
        res.calibrated_prob = 0.0f;
        res.active_threshold = 0.5f;
        res.expected_risk = 0.0f;
        res.confidence_margin = 0.0f;
        return res;
    }
    
    float prob = calibrate_score(&opt->calibrator, raw_score);
    float prob_neg = 1.0f - prob;
    
    float half_hyst = opt->current_hyst_width * 0.5f;
    float switch_thresh;
    
    if (opt->previous_decision) {
        switch_thresh = opt->current_threshold - half_hyst;
    } else {
        switch_thresh = opt->current_threshold + half_hyst;
    }
    
    bool decision = (prob >= switch_thresh);
    opt->previous_decision = decision;
    
    float risk_pos = prob * opt->current_costs.cost_tp + prob_neg * opt->current_costs.cost_fp;
    float risk_neg = prob * opt->current_costs.cost_fn + prob_neg * opt->current_costs.cost_tn;
    
    res.decision = decision;
    res.calibrated_prob = prob;
    res.active_threshold = opt->current_threshold;
    res.expected_risk = decision ? risk_pos : risk_neg;
    res.confidence_margin = fabsf(prob - opt->current_threshold);
    
    /* Запис у чорну скриньку */
    uint16_t idx = opt->blackbox_head;
    opt->blackbox[idx].timestamp_us = 0; /* Отримується з системного таймера DWT/SysTick */
    opt->blackbox[idx].raw_score = raw_score;
    opt->blackbox[idx].calibrated_prob = prob;
    opt->blackbox[idx].active_threshold = opt->current_threshold;
    opt->blackbox[idx].decision = decision;
    opt->blackbox_head = (idx + 1) % BLACKBOX_BUFFER_SIZE;
    
    return res;
}
