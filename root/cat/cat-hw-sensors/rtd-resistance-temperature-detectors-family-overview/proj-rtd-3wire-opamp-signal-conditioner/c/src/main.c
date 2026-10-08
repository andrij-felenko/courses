#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>
#include "rtd_sensor.h"
#include "rtd_lut.h"

/**
 * @brief Структура цифрового експоненційного фільтра (EMA) для зменшення шуму АЦП.
 */
typedef struct {
    float alpha;         /**< Коефіцієнт згладжування (0.0 < alpha <= 1.0) */
    float filtered_val;  /**< Поточне відфільтроване значення */
    bool is_initialized; /**< Прапорець первинного заповнення */
} ema_filter_t;

/**
 * @brief Оновлення вибірки у цифровому фільтрі ЕМА.
 */
static float ema_filter_update(ema_filter_t *filter, float sample) {
    if (!filter->is_initialized) {
        filter->filtered_val = sample;
        filter->is_initialized = true;
        return sample;
    }
    filter->filtered_val = (filter->alpha * sample) + ((1.0f - filter->alpha) * filter->filtered_val);
    return filter->filtered_val;
}

/**
 * @brief Симуляція оцифрування АЦП для заданого опору з додаванням провідникового опору та шуму.
 */
static uint32_t simulate_adc_read(float target_r_sensor, const rtd_config_t *config, float noise_amplitude_ohms) {
    /* Опір сенсора з урахуванням вимірювальних провідників */
    float total_resistance = target_r_sensor + config->r_lead_ohms;
    
    /* Шум вимірювального тракту (псевдовипадкова складова) */
    float noise = (((float)(rand() % 200) - 100.0f) / 100.0f) * noise_amplitude_ohms;
    total_resistance += noise;

    /* Вхідна напруга на сенсорі: V_in = I_ex * R */
    float v_in = config->excitation_current_a * total_resistance;

    /* Вихідна напруга підсилювача ОП: V_out = V_in * Gain */
    float v_out = v_in * config->gain;

    /* Обмеження напруги діапазоном опорної напруги АЦП */
    if (v_out > config->vref_v) {
        v_out = config->vref_v;
    }
    if (v_out < 0.0f) {
        v_out = 0.0f;
    }

    /* Конверсія у сирий код АЦП */
    return (uint32_t)((v_out / config->vref_v) * (float)config->adc_max_code + 0.5f);
}

/**
 * @brief Отримання рядкового текстового опису для статусу діагностики.
 */
static const char* get_status_string(rtd_status_t status) {
    switch (status) {
        case RTD_STATUS_OK:                return "OK";
        case RTD_STATUS_ERR_OPEN_CIRCUIT:  return "ОБРИВ КОЛА (OPEN)";
        case RTD_STATUS_ERR_SHORT_CIRCUIT: return "КОРОТКЕ ЗАМИКАННЯ (SHORT)";
        case RTD_STATUS_ERR_OUT_OF_RANGE:  return "ВИХІД ЗА МЕЖІ (OUT OF RANGE)";
        case RTD_STATUS_ERR_PARAM:         return "ПОМИЛКА ПАРАМЕТРІВ (PARAM ERR)";
        default:                           return "НЕВІДОМО";
    }
}

int main(void) {
    printf("====================================================================\n");
    printf("  Драйвер 3-провідного резистивного перетворювача Pt100 / Pt1000   \n");
    printf("====================================================================\n\n");

    /* 1. Конфігурація аналогового тракту ембеддед-системи */
    rtd_config_t rtd_config = {
        .vref_v = 3.3f,                  /* Опорна напруга АЦП = 3.3 В */
        .gain = 10.0f,                   /* Коефіцієнт підсилення ОП = 10 */
        .excitation_current_a = 0.001f,  /* Струм збудження 1 мА (0.001 А) */
        .adc_max_code = 4095,            /* 12-бітовий АЦП (2^12 - 1) */
        .r_lead_ohms = 1.25f,            /* Опір 1 провідника лінії = 1.25 Ом */
        .r0_ohms = RTD_PT100_R0,         /* Датчик Pt100 (R0 = 100.0 Ом) */
        .type = RTD_TYPE_PT100
    };

    /* 2. Інтеграція коефіцієнтів двоточкового калібрування з магазину опорів */
    rtd_calib_t rtd_calib = {
        .offset_ohms = 0.15f,            /* Системний зсув нуля = +0.15 Ом */
        .gain_scale = 1.0012f            /* Коефіцієнт масштабу нуля та шкали */
    };

    /* 3. Ініціалізація цифрового фільтра шуму АЦП (EMA alpha = 0.25) */
    ema_filter_t adc_filter = {
        .alpha = 0.25f,
        .filtered_val = 0.0f,
        .is_initialized = false
    };

    /* Тестові сценарії вимірювання */
    struct {
        const char *description;
        float target_r_sensor;
    } test_scenarios[] = {
        { "Кімнатна температура (+25.0 °C)",   109.73f },
        { "Кріогенний режим (-50.0 °C)",        80.31f  },
        { "Високотемпературний печі (+300.0 °C)", 212.05f },
        { "Діагностика: Обрив лінії датчика",  600.00f },
        { "Діагностика: Коротке замикання",     5.00f   }
    };

    size_t num_tests = sizeof(test_scenarios) / sizeof(test_scenarios[0]);

    for (size_t i = 0; i < num_tests; i++) {
        printf("--- Тест %zu: %s ---\n", i + 1, test_scenarios[i].description);
        adc_filter.is_initialized = false; /* Скидання фільтра перед новим тестом */

        /* Імітація серії з 10 вибірок АЦП з фільтрацією шуму */
        uint32_t raw_adc_code = 0;
        float filtered_adc_code = 0.0f;

        for (int sample = 0; sample < 10; sample++) {
            raw_adc_code = simulate_adc_read(test_scenarios[i].target_r_sensor, &rtd_config, 0.08f);
            filtered_adc_code = ema_filter_update(&adc_filter, (float)raw_adc_code);
        }

        uint32_t adc_code_to_process = (uint32_t)(filtered_adc_code + 0.5f);

        /* Використання драйвера обробки сигналів */
        float measured_r = 0.0f;
        float temp_cvd = 0.0f;
        float temp_lut = 0.0f;

        /* Аналітичний розрахунок за формулою Каллендара — Ван Дюзена */
        rtd_status_t status_cvd = rtd_process_adc_sample(adc_code_to_process, 
                                                         &rtd_config, 
                                                         &rtd_calib, 
                                                         &measured_r, 
                                                         &temp_cvd);

        /* Табличний розрахунок за допомогою методів LUT та лінійної інтерполяції */
        rtd_status_t status_lut = rtd_lut_resistance_to_temp_float(measured_r, rtd_config.r0_ohms, &temp_lut);

        /* Розрахунок у фіксованій крапці для МК без FPU */
        int32_t temp_mC_fixed = 0;
        rtd_status_t status_fixed = rtd_lut_resistance_to_temp_fixed((uint32_t)(measured_r * 1000.0f), 
                                                                    (uint32_t)(rtd_config.r0_ohms * 1000.0f), 
                                                                    &temp_mC_fixed);

        /* Розрахунок проміжних величин для детального виводу */
        float measured_v_adc = rtd_adc_to_voltage(adc_code_to_process, &rtd_config);

        printf("  Сирий код АЦП: %u | Відфільтрований: %.1f\n", raw_adc_code, filtered_adc_code);
        printf("  Напруга АЦП: %.4f В | Відновлений опір RTD: %.3f Ом\n", measured_v_adc, measured_r);
        printf("  Статус діагностики: [%s]\n", get_status_string(status_cvd));
        
        if (status_cvd == RTD_STATUS_OK || status_cvd == RTD_STATUS_ERR_OUT_OF_RANGE) {
            printf("  Температура (CVD аналітична): %.3f °C\n", temp_cvd);
            printf("  Температура (LUT float):      %.3f °C (Похибка LUT: %.3f °C)\n", 
                   temp_lut, temp_lut - temp_cvd);
            printf("  Температура (LUT fixed-point): %.3f °C\n", (float)temp_mC_fixed / 1000.0f);
        }
        printf("\n");
    }

    printf("====================================================================\n");
    printf("  Обробка вимірювань успішно завершена.\n");
    printf("====================================================================\n");

    return 0;
}
