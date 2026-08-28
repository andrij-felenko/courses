#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура результатів обчислення стану вологого повітря */
typedef struct {
    float temperature_c;       /* Температура повітря, °C */
    float relative_humidity;   /* Компенсована відносна вологість, % */
    float vapor_pressure_pa;   /* Парціальний тиск водяної пари, Па */
    float sat_pressure_pa;     /* Тиск насиченої пари, Па */
    float dew_point_c;         /* Температура точки роси, °C */
    float absolute_humidity_g; /* Абсолютна вологість, г/м³ */
    float enthalpy_kj;         /* Ентальпія вологого повітря, кДж/кг */
    bool  is_valid;            /* Прапорець коректності обчислень */
} humidity_result_t;

/* Параметри компенсації датчика (задаються у паспорті елемента) */
typedef struct {
    float temp_coeff;          /* Температурний коефіцієнт (% RH / °C) */
    float cal_temp_c;          /* Температура калібрування (зазвичай 25°C) */
} humidity_sensor_cal_t;

/* Рівняння Магнуса для тиску насиченої пари */
static float calc_saturation_pressure(float temp_c) {
    float a, b, c;
    if (temp_c >= 0.0f) {
        a = 611.21f;
        b = 17.502f;
        c = 240.97f;
    } else {
        a = 611.15f;
        b = 22.452f;
        c = 272.55f;
    }
    return a * expf((b * temp_c) / (c + temp_c));
}

/* Обчислення точки роси за виразом Магнуса */
static float calc_dew_point(float temp_c, float rh_percent) {
    if (rh_percent <= 0.01f) {
        rh_percent = 0.01f;
    } else if (rh_percent > 100.0f) {
        rh_percent = 100.0f;
    }
    
    float b = (temp_c >= 0.0f) ? 17.502f : 22.452f;
    float c = (temp_c >= 0.0f) ? 240.97f : 272.55f;
    
    float gamma = (b * temp_c) / (c + temp_c) + logf(rh_percent / 100.0f);
    return (c * gamma) / (b - gamma);
}

/* Головна функція обробки даних датчика */
bool process_humidity_measurement(
    float temp_c, 
    float rh_raw, 
    const humidity_sensor_cal_t *cal, 
    humidity_result_t *out_res
) {
    if (!out_res) {
        return false;
    }
    
    /* Перевірка виходу за фізичні межі */
    if (temp_c < -50.0f || temp_c > 100.0f || rh_raw < -10.0f || rh_raw > 110.0f) {
        out_res->is_valid = false;
        return false;
    }

    /* 1. Температурна компенсація сирого значення вологості */
    float cal_temp = cal ? cal->cal_temp_c : 25.0f;
    float temp_coeff = cal ? cal->temp_coeff : 0.15f;
    
    float rh_comp = rh_raw - (temp_c - cal_temp) * temp_coeff;
    if (rh_comp < 0.0f) rh_comp = 0.0f;
    if (rh_comp > 100.0f) rh_comp = 100.0f;

    /* 2. Обчислення термодинамічних параметрів */
    float p_sat = calc_saturation_pressure(temp_c);
    float p_v = (rh_comp / 100.0f) * p_sat;
    float dew_point = calc_dew_point(temp_c, rh_comp);
    
    /* Абсолютна вологість: ρ_v = 2.1667 * P_v / (T + 273.15) */
    float abs_hum = 2.1667f * (p_v / (temp_c + 273.15f));
    
    /* Влаговміст w (г/кг): при P_atm = 101325 Па */
    float p_atm = 101325.0f;
    float w_g_kg = 621.98f * (p_v / (p_atm - p_v));
    
    /* Ентальпія h (кДж/кг) */
    float enthalpy = 1.006f * temp_c + (w_g_kg / 1000.0f) * (2501.0f + 1.86f * temp_c);

    /* Заповнення результату */
    out_res->temperature_c = temp_c;
    out_res->relative_humidity = rh_comp;
    out_res->sat_pressure_pa = p_sat;
    out_res->vapor_pressure_pa = p_v;
    out_res->dew_point_c = dew_point;
    out_res->absolute_humidity_g = abs_hum;
    out_res->enthalpy_kj = enthalpy;
    out_res->is_valid = true;

    return true;
}

int main(void) {
    humidity_sensor_cal_t cal = { .temp_coeff = 0.15f, .cal_temp_c = 25.0f };
    humidity_result_t res;

    float t_in = 30.0f;
    float rh_in = 50.0f;

    if (process_humidity_measurement(t_in, rh_in, &cal, &res)) {
        printf("--- Термодинамічний стан вологого повітря ---\n");
        printf("Температура:          %.2f °C\n", res.temperature_c);
        printf("Відносна вологість:   %.2f %%\n", res.relative_humidity);
        printf("Тиск насичення:       %.2f Па\n", res.sat_pressure_pa);
        printf("Парціальний тиск:     %.2f Па\n", res.vapor_pressure_pa);
        printf("Точка роси:           %.2f °C\n", res.dew_point_c);
        printf("Абсолютна вологість:  %.2f г/м³\n", res.absolute_humidity_g);
        printf("Ентальпія повітря:    %.2f кДж/кг\n", res.enthalpy_kj);
    }
    return 0;
}
