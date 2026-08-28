#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_CHANNELS          6
#define EMA_ALPHA             0.20
#define GRADIENT_WINDOW       5
#define GAS_CONSTANT_R        8.314462
#define IMC_ACTIVATION_ENERGY 72500.0   /* Дж/моль */
#define IMC_PRE_EXP_FACTOR    1.2e-4    /* м^2/с */

/* Перелік стадій термопрофілю за стандартом J-STD-020 */
typedef enum {
    STAGE_STANDBY = 0,
    STAGE_PREHEAT,
    STAGE_SOAK,
    STAGE_REFLOW,
    STAGE_COOLING,
    STAGE_FINISHED,
    STAGE_ERROR_ABORT
} ProfileStage;

/* Ознаки апаратних помилок вимірювання термопари */
typedef enum {
    FAULT_NONE          = 0x00,
    FAULT_OPEN_CIRCUIT  = 0x01,
    FAULT_OVER_VOLTAGE  = 0x02,
    FAULT_UNDER_VOLTAGE = 0x04,
    FAULT_CJC_OUT_RANGE = 0x08,
    FAULT_SENSOR_DROPOUT= 0x10
} SensorFaultFlags;

/* Технологічні межі для безсвинцевого сплаву SAC305 */
typedef struct {
    double liquidus_temp;      /* 217.0 C */
    double target_peak_temp;   /* 245.0 C */
    double min_peak_temp;      /* 238.0 C */
    double max_peak_temp;      /* 252.0 C */
    double target_tal_sec;     /* 65.0 s */
    double min_tal_sec;        /* 45.0 s */
    double max_tal_sec;        /* 90.0 s */
    double target_soak_sec;    /* 90.0 s */
    double min_soak_sec;       /* 60.0 s */
    double max_soak_sec;       /* 120.0 s */
    double max_preheat_ramp;   /* +3.0 C/s */
    double max_cooling_ramp;   /* -4.0 C/s */
    double max_delta_t_reflow; /* 8.0 C */
} ProcessLimits;

/* Структура стану окремого термопарного каналу */
typedef struct {
    char channel_name[32];
    double raw_temp;
    double filtered_temp;
    double temp_history[GRADIENT_WINDOW];
    uint8_t history_idx;
    double ramp_rate;
    double peak_temperature;
    double time_above_liquidus;
    double soak_start_time;
    double soak_duration;
    double imc_thickness_um;
    double pwi_peak;
    double pwi_tal;
    double pwi_soak;
    double pwi_ramp_up;
    double pwi_ramp_down;
    double max_pwi_channel;
    uint8_t fault_flags;
    bool is_enabled;
} ChannelState;

/* Головна структура реєстратора-аналізатора */
typedef struct {
    ProcessLimits limits;
    ChannelState channels[MAX_CHANNELS];
    uint8_t active_channels;
    ProfileStage stage;
    double session_time_sec;
    double stage_start_time;
    double delta_t_current;
    double delta_t_max_reflow;
    double delta_t_max_soak;
    double overall_pwi;
    uint32_t total_samples;
    bool violation_flag;
    double conveyor_speed_m_min;
    double total_oven_length_m;
} ReflowProfiler;

/* Ініціалізація специфікації процесу */
void profiler_limits_init_sac305(ProcessLimits *lim) {
    lim->liquidus_temp = 217.0;
    lim->target_peak_temp = 245.0;
    lim->min_peak_temp = 238.0;
    lim->max_peak_temp = 252.0;
    lim->target_tal_sec = 65.0;
    lim->min_tal_sec = 45.0;
    lim->max_tal_sec = 90.0;
    lim->target_soak_sec = 90.0;
    lim->min_soak_sec = 60.0;
    lim->max_soak_sec = 120.0;
    lim->max_preheat_ramp = 3.0;
    lim->max_cooling_ramp = -4.0;
    lim->max_delta_t_reflow = 8.0;
}

/* Текстовий опис поточної стадії */
const char* profiler_stage_to_string(ProfileStage stage) {
    switch (stage) {
        case STAGE_STANDBY:     return "STANDBY";
        case STAGE_PREHEAT:     return "PREHEAT";
        case STAGE_SOAK:        return "SOAK";
        case STAGE_REFLOW:      return "REFLOW";
        case STAGE_COOLING:     return "COOLING";
        case STAGE_FINISHED:    return "FINISHED";
        case STAGE_ERROR_ABORT: return "ERROR_ABORT";
        default:                return "UNKNOWN";
    }
}

/* Ініціалізація реєстратора */
void profiler_init(ReflowProfiler *prof, const ProcessLimits *lim, uint8_t channel_count) {
    memset(prof, 0, sizeof(ReflowProfiler));
    prof->limits = *lim;
    prof->active_channels = (channel_count > MAX_CHANNELS) ? MAX_CHANNELS : channel_count;
    prof->stage = STAGE_STANDBY;
    prof->session_time_sec = 0.0;
    prof->conveyor_speed_m_min = 0.90; /* типова швидкість 0.9 м/хв */
    prof->total_oven_length_m = 3.60;
    
    for (uint8_t i = 0; i < prof->active_channels; i++) {
        snprintf(prof->channels[i].channel_name, sizeof(prof->channels[i].channel_name), "TC_%d", i + 1);
        prof->channels[i].filtered_temp = 25.0;
        prof->channels[i].peak_temperature = 25.0;
        prof->channels[i].imc_thickness_um = 0.5; /* базова товщина підкладки */
        prof->channels[i].is_enabled = true;
        prof->channels[i].fault_flags = FAULT_NONE;
        for (int k = 0; k < GRADIENT_WINDOW; k++) {
            prof->channels[i].temp_history[k] = 25.0;
        }
    }
}

/* Обчислення локального PWI для конкретного показника */
static double calculate_single_pwi(double val, double target, double low, double high) {
    double half_window = 0.5 * (high - low);
    if (half_window <= 0.0001) return 0.0;
    return (fabs(val - target) / half_window) * 100.0;
}

/* Оновлення стану каналу вимірювання */
static void update_channel_data(ChannelState *ch, double raw_val, double dt, double current_time, double t_liquidus) {
    if (!ch->is_enabled) return;
    
    /* Перевірка на обрив або аномальний стрибок (обрив термопари) */
    if (raw_val > 400.0 || raw_val < -20.0 || isnan(raw_val)) {
        ch->fault_flags |= FAULT_OPEN_CIRCUIT;
        ch->is_enabled = false;
        printf("[WARN] Канал %s відключено: виявлено обрив термопари (Raw = %.1f C)\n",
               ch->channel_name, raw_val);
        return;
    }
    
    ch->raw_temp = raw_val;
    
    /* Фільтрація EMA */
    ch->filtered_temp = EMA_ALPHA * raw_val + (1.0 - EMA_ALPHA) * ch->filtered_temp;
    
    /* Розрахунок термічного градієнта dT/dt */
    double oldest_val = ch->temp_history[ch->history_idx];
    ch->temp_history[ch->history_idx] = ch->filtered_temp;
    ch->history_idx = (ch->history_idx + 1) % GRADIENT_WINDOW;
    
    ch->ramp_rate = (ch->filtered_temp - oldest_val) / (GRADIENT_WINDOW * dt);
    
    /* Фіксація пікової температури */
    if (ch->filtered_temp > ch->peak_temperature) {
        ch->peak_temperature = ch->filtered_temp;
    }
    
    /* Акумуляція TAL */
    if (ch->filtered_temp >= t_liquidus) {
        ch->time_above_liquidus += dt;
        
        /* Чисельне моделювання росту інтерметаліду Cu6Sn5 за Арреніусом */
        double temp_k = ch->filtered_temp + 273.15;
        double k_rate = IMC_PRE_EXP_FACTOR * exp(-IMC_ACTIVATION_ENERGY / (GAS_CONSTANT_R * temp_k));
        ch->imc_thickness_um += (k_rate * dt * 1e6) / (2.0 * fmax(ch->imc_thickness_um, 0.1));
    }
}

/* Головний цикл обробки дискретного заміру */
void profiler_process_sample(ReflowProfiler *prof, const double raw_readings[], double dt) {
    if (dt <= 0.0) return;
    prof->session_time_sec += dt;
    prof->total_samples++;
    
    double max_t = -1000.0;
    double min_t = 10000.0;
    double avg_t = 0.0;
    uint8_t valid_channels = 0;
    
    /* Оновлення всіх каналів */
    for (uint8_t i = 0; i < prof->active_channels; i++) {
        update_channel_data(&prof->channels[i], raw_readings[i], dt, prof->session_time_sec, prof->limits.liquidus_temp);
        
        if (prof->channels[i].is_enabled) {
            double t = prof->channels[i].filtered_temp;
            if (t > max_t) max_t = t;
            if (t < min_t) min_t = t;
            avg_t += t;
            valid_channels++;
        }
    }
    
    if (valid_channels == 0) {
        prof->stage = STAGE_ERROR_ABORT;
        printf("[ERROR] Усі термопарні канали відмовили! Аварійна зупинка сесії.\n");
        return;
    }
    
    avg_t /= valid_channels;
    prof->delta_t_current = max_t - min_t;
    
    /* Фіксація розкиду в зоні витримки Soak */
    if (prof->stage == STAGE_SOAK) {
        if (prof->delta_t_current > prof->delta_t_max_soak) {
            prof->delta_t_max_soak = prof->delta_t_current;
        }
    }
    
    /* Фіксація Delta T у зоні Reflow */
    if (avg_t >= prof->limits.liquidus_temp) {
        if (prof->delta_t_current > prof->delta_t_max_reflow) {
            prof->delta_t_max_reflow = prof->delta_t_current;
        }
    }
    
    /* Автомат перемикання стадій профілю */
    switch (prof->stage) {
        case STAGE_STANDBY:
            if (avg_t >= 35.0) {
                prof->stage = STAGE_PREHEAT;
                prof->stage_start_time = prof->session_time_sec;
                printf("[LOG] Вхід у зону PREHEAT при t = %.1f c (T_avg = %.1f C)\n",
                       prof->session_time_sec, avg_t);
            }
            break;
            
        case STAGE_PREHEAT:
            if (avg_t >= 150.0) {
                prof->stage = STAGE_SOAK;
                prof->stage_start_time = prof->session_time_sec;
                for (uint8_t i = 0; i < prof->active_channels; i++) {
                    if (prof->channels[i].is_enabled) {
                        prof->channels[i].soak_start_time = prof->session_time_sec;
                    }
                }
                printf("[LOG] Вхід у зону SOAK при t = %.1f c (dT/dt = %.2f C/s)\n",
                       prof->session_time_sec, prof->channels[0].ramp_rate);
            }
            break;
            
        case STAGE_SOAK:
            if (avg_t >= 200.0) {
                prof->stage = STAGE_REFLOW;
                prof->stage_start_time = prof->session_time_sec;
                for (uint8_t i = 0; i < prof->active_channels; i++) {
                    if (prof->channels[i].is_enabled) {
                        prof->channels[i].soak_duration = prof->session_time_sec - prof->channels[i].soak_start_time;
                    }
                }
                printf("[LOG] Вхід у зону REFLOW при t = %.1f c (Delta T = %.1f C)\n",
                       prof->session_time_sec, prof->delta_t_current);
            }
            break;
            
        case STAGE_REFLOW:
            if (avg_t < prof->limits.liquidus_temp && max_t > prof->limits.liquidus_temp) {
                prof->stage = STAGE_COOLING;
                prof->stage_start_time = prof->session_time_sec;
                printf("[LOG] Вхід у зону COOLING при t = %.1f c (Max Peak = %.1f C)\n",
                       prof->session_time_sec, max_t);
            }
            break;
            
        case STAGE_COOLING:
            if (max_t <= 45.0) {
                prof->stage = STAGE_FINISHED;
                printf("[LOG] Термопрофіль успішно ЗАВЕРШЕНО при t = %.1f c\n", prof->session_time_sec);
            }
            break;
            
        case STAGE_FINISHED:
        case STAGE_ERROR_ABORT:
            break;
    }
    
    /* Розрахунок PWI для всіх активних каналів */
    double worst_pwi = 0.0;
    for (uint8_t i = 0; i < prof->active_channels; i++) {
        ChannelState *ch = &prof->channels[i];
        if (!ch->is_enabled) continue;
        
        ch->pwi_peak = calculate_single_pwi(ch->peak_temperature, prof->limits.target_peak_temp,
                                            prof->limits.min_peak_temp, prof->limits.max_peak_temp);
        ch->pwi_tal = calculate_single_pwi(ch->time_above_liquidus, prof->limits.target_tal_sec,
                                           prof->limits.min_tal_sec, prof->limits.max_tal_sec);
        ch->pwi_soak = calculate_single_pwi(ch->soak_duration, prof->limits.target_soak_sec,
                                            prof->limits.min_soak_sec, prof->limits.max_soak_sec);
        
        ch->max_pwi_channel = fmax(ch->pwi_peak, fmax(ch->pwi_tal, ch->pwi_soak));
        if (ch->max_pwi_channel > worst_pwi) {
            worst_pwi = ch->max_pwi_channel;
        }
    }
    prof->overall_pwi = worst_pwi;
    if (prof->overall_pwi >= 100.0) {
        prof->violation_flag = true;
    }
}

/* Друк фінального інженерного звіту верифікації */
void profiler_print_verification_report(const ReflowProfiler *prof) {
    printf("\n====================================================================\n");
    printf("        ЗВІТ ВЕРИФІКАЦІЇ ТЕРМОПРОФІЛЮ ОПЛАВЛЕННЯ (J-STD-020)        \n");
    printf("====================================================================\n");
    printf("Загальний час сесії:      %.1f с\n", prof->session_time_sec);
    printf("Активних каналів:         %d із %d\n", prof->active_channels, MAX_CHANNELS);
    printf("Макс. Delta T у Reflow:   %.2f °C (Ліміт: %.1f °C) -> %s\n",
           prof->delta_t_max_reflow, prof->limits.max_delta_t_reflow,
           (prof->delta_t_max_reflow <= prof->limits.max_delta_t_reflow) ? "PASS" : "FAIL");
    printf("Підсумковий індекс PWI:   %.1f%% -> %s\n",
           prof->overall_pwi,
           (prof->overall_pwi < 50.0) ? "EXCELLENT (<50%)" :
           (prof->overall_pwi < 100.0) ? "PASS (<100%)" : "REJECTED (>=100%)");
    printf("--------------------------------------------------------------------\n");
    printf("%-8s | %-8s | %-8s | %-8s | %-8s | %-8s\n",
           "Канал", "T_peak", "TAL(с)", "Soak(с)", "IMC(мкм)", "PWI(%)");
    printf("--------------------------------------------------------------------\n");
    
    for (uint8_t i = 0; i < prof->active_channels; i++) {
        const ChannelState *ch = &prof->channels[i];
        if (ch->is_enabled) {
            printf("%-8s | %6.1f °C | %6.1f с | %6.1f с | %6.2f   | %6.1f%%\n",
                   ch->channel_name, ch->peak_temperature, ch->time_above_liquidus,
                   ch->soak_duration, ch->imc_thickness_um, ch->max_pwi_channel);
        } else {
            printf("%-8s | %s\n", ch->channel_name, "FAULT / DISCONNECTED");
        }
    }
    printf("====================================================================\n\n");
}
