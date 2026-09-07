#include <stdio.h>
#include "adc_calib.h"

int main(void) {
    printf("=== Демонстрація модуля фонового самокалібрування АЦП ===\n\n");
    
    adc_calib_t calib;
    /* 12-бітний АЦП: 4095 відліків, VREF = 3300 мВ, T0 = 25 °C, ТК зміщення 0.015 мВ/°C, альфа = 0.1 */
    adc_calib_init(&calib, 4095, 3300.0f, 25.0f, 0.0f, 0.015f, 0.0002f, 0.1f);
    
    /* Імітація прогріву приладу від 25 °C до 75 °C */
    float actual_input_mv = 1650.0f; /* Точно середина шкали: 1.65 В */
    
    printf("Вхідна напруга: %.2f мВ\n", actual_input_mv);
    printf("------------------------------------------------------------------------------------\n");
    printf("Темп (°C) | Сирий код | Некориг. (мВ) | AGND код | VREF код | Скориговано (мВ) | Похибка (мВ)\n");
    printf("------------------------------------------------------------------------------------\n");
    
    for (float temp = 25.0f; temp <= 75.0f; temp += 10.0f) {
        /* Оновлюємо температуру кристала */
        for (int i = 0; i < 5; ++i) {
            adc_calib_update_temperature(&calib, temp);
        }
        
        /* Моделюємо дрейф зміщення нуля (+0.4 LSB/°C) та дрейф VREF (-30 ppm/°C) */
        float dt = temp - 25.0f;
        int32_t sim_zero = (int32_t)(15.0f + 0.4f * dt);
        float sim_vref_mv = 3300.0f * (1.0f - 30e-6f * dt);
        int32_t sim_vref_code = (int32_t)((sim_vref_mv / 3300.0f) * 4095.0f);
        
        /* Фонове вимірювання еталонів у мікроконтролері */
        adc_calib_update_references(&calib, sim_zero, sim_vref_code);
        
        /* Моделюємо сирий відлік сигналу з урахуванням зміщення нуля та дрейфу VREF */
        int32_t raw_code = sim_zero + (int32_t)((actual_input_mv / sim_vref_mv) * (sim_vref_code - sim_zero));
        
        /* Некоригований розрахунок за наївною формулою */
        float uncalibrated_mv = ((float)raw_code / 4095.0f) * 3300.0f;
        
        /* Розрахунок за модулем калібрування */
        float calibrated_mv = adc_calib_process_sample(&calib, raw_code);
        float error_mv = calibrated_mv - actual_input_mv;
        
        printf("%8.1f  | %9d | %13.2f | %8d | %8d | %16.2f | %12.3f\n",
               temp, raw_code, uncalibrated_mv, sim_zero, sim_vref_code, calibrated_mv, error_mv);
    }
    
    printf("------------------------------------------------------------------------------------\n");
    printf("Калібрування успішно усунуло дрейф зсуву та масштабу до часток мілівольта.\n");
    return 0;
}
