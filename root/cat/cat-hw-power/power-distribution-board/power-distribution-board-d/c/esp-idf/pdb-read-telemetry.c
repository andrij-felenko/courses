#include <stdint.h>
#include <stdbool.h>

// Структура конфігурації вимірювального тракту PDB
typedef struct {
    float v_divider_ratio;    // Коефіцієнт дільника напруги (наприклад, 11.0 для 10k / 1k)
    float shunt_resistor_ohm; // Опір шунта в омах (0.0005 Ом)
    float amp_gain;           // Коефіцієнт підсилення диференціального підсилювача (50.0)
    float adc_vref;           // Опорна напруга АЦП (3.3 В)
    uint32_t adc_resolution;  // Градація АЦП (4096 для 12-біт)
} pdb_telemetry_config_t;

// Структура поточних виміряних значень телеметрії
typedef struct {
    float voltage_v;          // Напруга акумулятора (В)
    float current_a;          // Поточний струм споживання (А)
    float consumed_mah;       // Накопичена спожита ємність (мА·год)
} pdb_telemetry_data_t;

// Обчислення фізичних величин живлення за відліками АЦП
void pdb_read_telemetry(const pdb_telemetry_config_t *config, 
                        uint16_t raw_adc_voltage, 
                        uint16_t raw_adc_current, 
                        float dt_seconds, 
                        pdb_telemetry_data_t *output) {
    // 1. Перетворення сирих відліків АЦП у напругу на вхідних ніжках
    float v_adc_sense = ((float)raw_adc_voltage / (float)config->adc_resolution) * config->adc_vref;
    float i_adc_sense = ((float)raw_adc_current / (float)config->adc_resolution) * config->adc_vref;

    // 2. Реконструкція реальної напруги акумуляторної батареї
    output->voltage_v = v_adc_sense * config->v_divider_ratio;

    // 3. Реконструкція струму: V_shunt = V_adc / G, I = V_shunt / R_shunt
    float v_shunt = i_adc_sense / config->amp_gain;
    output->current_a = v_shunt / config->shunt_resistor_ohm;

    // 4. Дискретне інтегрування струму в часі для обчислення спожитої ємності
    output->consumed_mah += (output->current_a * 1000.0f) * (dt_seconds / 3600.0f);
}
