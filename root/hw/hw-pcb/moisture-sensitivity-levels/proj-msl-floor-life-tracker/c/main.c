#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAX_NAME_LEN 64

typedef enum {
    MSL_1 = 0,
    MSL_2,
    MSL_2A,
    MSL_3,
    MSL_4,
    MSL_5,
    MSL_5A,
    MSL_6
} msl_class_t;

typedef enum {
    STATE_SEALED = 0,
    STATE_EXPOSED,
    STATE_PAUSED_DRY_10RH,
    STATE_RECOVERING_5RH,
    STATE_EXPIRED_NEEDS_BAKE,
    STATE_BAKING,
    STATE_CONSUMED
} tracker_state_t;

typedef enum {
    PKG_THICKNESS_LE_1_4MM = 0,
    PKG_THICKNESS_LE_2_0MM,
    PKG_THICKNESS_LE_4_5MM
} pkg_thickness_t;

typedef struct {
    msl_class_t msl;
    const char* label;
    double nominal_floor_life_hours;
    double max_short_exposure_hours;
} msl_metadata_t;

static const msl_metadata_t MSL_TABLE[] = {
    { MSL_1,  "MSL 1",  1e9,    1e9  },
    { MSL_2,  "MSL 2",  8760.0, 12.0 },
    { MSL_2A, "MSL 2a", 672.0,  12.0 },
    { MSL_3,  "MSL 3",  168.0,  12.0 },
    { MSL_4,  "MSL 4",  72.0,   8.0  },
    { MSL_5,  "MSL 5",  48.0,   8.0  },
    { MSL_5A, "MSL 5a", 24.0,   8.0  },
    { MSL_6,  "MSL 6",  6.0,    0.0  }
};

static const double BAKE_HOURS_125C[8][3] = {
    { 0,  0,   0  },
    { 5,  7,   9  },
    { 7,  8,   10 },
    { 9,  18,  48 },
    { 11, 21,  48 },
    { 15, 24,  48 },
    { 20, 28,  48 },
    { 24, 32,  48 }
};

typedef struct {
    char part_number[MAX_NAME_LEN];
    char lot_id[MAX_NAME_LEN];
    msl_class_t msl;
    pkg_thickness_t thickness;
    tracker_state_t state;
    
    double floor_life_remaining_hours;
    double current_exposure_run_hours;
    double recovery_credit_hours;
    
    double cumulative_bake_125c_hours;
    double current_bake_remaining_hours;
    
    bool hic_ok_on_open;
    bool is_active;
} component_reel_t;

static double calc_saturation_vapor_pressure(double temp_c) {
    return 0.61078 * exp((17.27 * temp_c) / (temp_c + 237.3));
}

static double calc_environmental_derating(double temp_c, double rh_percent) {
    double p_sat_curr = calc_saturation_vapor_pressure(temp_c);
    double p_actual = (rh_percent / 100.0) * p_sat_curr;
    
    double p_sat_nom = calc_saturation_vapor_pressure(30.0);
    double p_nom = 0.60 * p_sat_nom;
    
    double k = p_actual / p_nom;
    return (k < 0.1) ? 0.1 : k;
}

void reel_init(component_reel_t* reel, const char* part_num, const char* lot,
               msl_class_t msl, pkg_thickness_t th) {
    memset(reel, 0, sizeof(component_reel_t));
    strncpy(reel->part_number, part_num, MAX_NAME_LEN - 1);
    strncpy(reel->lot_id, lot, MAX_NAME_LEN - 1);
    reel->msl = msl;
    reel->thickness = th;
    reel->state = STATE_SEALED;
    reel->floor_life_remaining_hours = MSL_TABLE[msl].nominal_floor_life_hours;
    reel->is_active = true;
}

bool reel_event_unpack(component_reel_t* reel, bool hic_10_percent_blue) {
    if (reel->state != STATE_SEALED) {
        printf("[ПОМИЛКА] Котушка %s вже розпакована!\n", reel->part_number);
        return false;
    }
    reel->hic_ok_on_open = hic_10_percent_blue;
    if (!hic_10_percent_blue) {
        reel->state = STATE_EXPIRED_NEEDS_BAKE;
        reel->floor_life_remaining_hours = 0.0;
        printf("[УВАГА] HIC індикатор вологий! Котушка %s переведена на обов'язковий Bake.\n", reel->part_number);
        return false;
    }
    reel->state = STATE_EXPOSED;
    reel->current_exposure_run_hours = 0.0;
    printf("[OK] Котушка %s розпакована. MSL: %s, Запас Floor Life: %.1f год.\n",
           reel->part_number, MSL_TABLE[reel->msl].label, reel->floor_life_remaining_hours);
    return true;
}

bool reel_event_store_in_dry_cabinet(component_reel_t* reel, double cabinet_rh) {
    if (reel->state != STATE_EXPOSED) {
        printf("[ПОМИЛКА] Перемістити в суху шафу можна лише відкриту котушку.\n");
        return false;
    }
    if (cabinet_rh <= 5.0) {
        reel->state = STATE_RECOVERING_5RH;
        reel->recovery_credit_hours = 0.0;
        printf("[FSM] Котушка %s -> Суха шафа RH < 5%% (Режим відновлення 5x).\n", reel->part_number);
    } else if (cabinet_rh <= 10.0) {
        reel->state = STATE_PAUSED_DRY_10RH;
        printf("[FSM] Котушка %s -> Суха шафа RH < 10%% (Режим паузи).\n", reel->part_number);
    } else {
        printf("[ПОМИЛКА] Вологість шафи %.1f%% занадто висока (>10%%)!\n", cabinet_rh);
        return false;
    }
    return true;
}

bool reel_event_start_baking(component_reel_t* reel, double bake_temp_c) {
    if (reel->state != STATE_EXPIRED_NEEDS_BAKE && reel->state != STATE_EXPOSED) {
        printf("[ПОМИЛКА] Некоректний стан для старту сушіння.\n");
        return false;
    }
    double required_hours = 0.0;
    if (fabs(bake_temp_c - 125.0) < 5.0) {
        required_hours = BAKE_HOURS_125C[reel->msl][reel->thickness];
        if (reel->cumulative_bake_125c_hours + required_hours > 96.0) {
            printf("[КРИТИЧНО] Ліміт сумарного сушіння 96 год при 125 °C буде перевищено!\n");
            return false;
        }
    } else if (fabs(bake_temp_c - 40.0) < 5.0) {
        required_hours = BAKE_HOURS_125C[reel->msl][reel->thickness] * 18.0;
    } else {
        printf("[ПОМИЛКА] Непідтримувана температура сушіння: %.1f °C\n", bake_temp_c);
        return false;
    }
    reel->state = STATE_BAKING;
    reel->current_bake_remaining_hours = required_hours;
    printf("[BAKE] Котушка %s -> Піч %.0f °C. Потрібно: %.1f годин.\n",
           reel->part_number, bake_temp_c, required_hours);
    return true;
}

void reel_tick_time(component_reel_t* reel, double delta_hours, double ambient_t, double ambient_rh) {
    if (!reel->is_active) return;
    switch (reel->state) {
        case STATE_EXPOSED: {
            double derating = calc_environmental_derating(ambient_t, ambient_rh);
            double effective_spent = delta_hours * derating;
            reel->current_exposure_run_hours += delta_hours;
            reel->floor_life_remaining_hours -= effective_spent;
            if (reel->floor_life_remaining_hours <= 0.0) {
                reel->floor_life_remaining_hours = 0.0;
                reel->state = STATE_EXPIRED_NEEDS_BAKE;
                printf("[АВАРІЯ] Котушка %s: Floor Life ВИЧЕРПАНО! Пайку заблоковано.\n", reel->part_number);
            }
            break;
        }
        case STATE_RECOVERING_5RH: {
            reel->recovery_credit_hours += delta_hours;
            double max_short = MSL_TABLE[reel->msl].max_short_exposure_hours;
            double required_recovery = 5.0 * reel->current_exposure_run_hours;
            if (reel->current_exposure_run_hours <= max_short &&
                reel->recovery_credit_hours >= required_recovery) {
                reel->floor_life_remaining_hours = MSL_TABLE[reel->msl].nominal_floor_life_hours;
                reel->current_exposure_run_hours = 0.0;
                reel->recovery_credit_hours = 0.0;
                printf("[ВІДНОВЛЕНО] Котушка %s: Floor Life повністю відновлено до 100%% за правилом 5x!\n",
                       reel->part_number);
            }
            break;
        }
        case STATE_BAKING: {
            reel->current_bake_remaining_hours -= delta_hours;
            reel->cumulative_bake_125c_hours += delta_hours;
            if (reel->current_bake_remaining_hours <= 0.0) {
                reel->current_bake_remaining_hours = 0.0;
                reel->floor_life_remaining_hours = MSL_TABLE[reel->msl].nominal_floor_life_hours;
                reel->current_exposure_run_hours = 0.0;
                reel->state = STATE_PAUSED_DRY_10RH;
                printf("[СУШІННЯ ЗАВЕРШЕНО] Котушка %s повністю зневоднена та готова до монтажу.\n",
                       reel->part_number);
            }
            break;
        }
        default:
            break;
    }
}

void reel_print_status(const component_reel_t* reel) {
    const char* state_names[] = {
        "SEALED_IN_MBB", "EXPOSED_ON_LINE", "PAUSED_DRY_10RH",
        "RECOVERING_5RH", "EXPIRED_NEEDS_BAKE", "BAKING_IN_OVEN", "CONSUMED_REFLOW"
    };
    printf("┌─────────────────────────────────────────────────────────────┐\n");
    printf("│ ДЕТАЛЬ: %-20s ЛОТ: %-15s MSL: %-6s │\n",
           reel->part_number, reel->lot_id, MSL_TABLE[reel->msl].label);
    printf("│ СТАН:   %-20s ЗАЛИШОК LIFE: %6.1f год       │\n",
           state_names[reel->state], reel->floor_life_remaining_hours);
    printf("│ ЕКСПОЗИЦІЯ СЕСІЇ: %5.1f год    СУМАРНИЙ BAKE 125°C: %4.1f год │\n",
           reel->current_exposure_run_hours, reel->cumulative_bake_125c_hours);
    printf("└─────────────────────────────────────────────────────────────┘\n");
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ РОБОТИ MSL FLOOR LIFE TRACKER (C99) ===\n\n");
    component_reel_t qfn_chip;
    reel_init(&qfn_chip, "STM32H743IIT6", "LOT-2026-A89", MSL_3, PKG_THICKNESS_LE_1_4MM);
    reel_event_unpack(&qfn_chip, true);
    reel_print_status(&qfn_chip);
    
    printf("\n>>> Робота на SMT лінії протягом 8 годин при 30 °C / 75%% RH...\n");
    for (int i = 0; i < 8; ++i) {
        reel_tick_time(&qfn_chip, 1.0, 30.0, 75.0);
    }
    reel_print_status(&qfn_chip);
    
    printf("\n>>> Зняття залишку котушки в суху шафу RH < 5%% на відновлення...\n");
    reel_event_store_in_dry_cabinet(&qfn_chip, 3.0);
    
    for (int i = 0; i < 40; ++i) {
        reel_tick_time(&qfn_chip, 1.0, 22.0, 3.0);
    }
    reel_print_status(&qfn_chip);
    return 0;
}
