#include <math.h>
#include <stdint.h>
#include <stdbool.h>

// Розрахунок часу перебування пакета SX1262 в ефірі (Time-on-Air) у мілісекундах
double calculate_sx1262_toa_ms(uint8_t sf, double bw_hz, uint8_t cr, 
                               uint8_t payload_len, uint16_t preamble_len, 
                               bool explicit_header, bool crc_on) 
{
    // Тривалість одного символу в секундах
    double t_s = (double)(1 << sf) / bw_hz;
    
    // Перевірка умови активації LowDataRateOptimize
    bool low_dr_opt = (t_s > 0.016);
    
    // Кількість символів преамбули з урахуванням апаратного заголовка SX1262
    double n_preamble = (double)preamble_len + 4.25;
    double t_preamble = n_preamble * t_s;
    
    // Параметри кадру
    int h = explicit_header ? 0 : 1;
    int crc = crc_on ? 1 : 0;
    int de = low_dr_opt ? 1 : 0;
    
    // Обчислення кількості символів корисного навантаження
    double num = 8.0 * payload_len - 4.0 * sf + 28.0 + 16.0 * crc - 20.0 * h;
    double den = 4.0 * (sf - 2.0 * de);
    
    double ceil_val = ceil(num / den);
    if (ceil_val < 0.0) {
        ceil_val = 0.0;
    }
    
    double n_payload = 8.0 + ceil_val * (cr + 4.0);
    double t_payload = n_payload * t_s;
    
    // Повернення підсумкового часу в мілісекундах
    return (t_preamble + t_payload) * 1000.0;
}
