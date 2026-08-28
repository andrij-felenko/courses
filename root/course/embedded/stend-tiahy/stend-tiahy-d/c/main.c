#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define FILTER_WINDOW_SIZE 16

typedef struct {
    float scale_counts_per_gram;
    float tare_offset_raw;
    float temp_coeff_zero;      // г/°C (дрейф нуля від температури)
    float base_temp_c;          // базова температура калібрування
    float shunt_resistor_ohms;  // опір вимірювального шунта
    float arm_ratio;            // L2 / L1 (редукція плеча важеля)
} thrust_calibration_t;

typedef struct {
    float raw_thrust_counts;
    float bus_voltage_v;
    float shunt_voltage_mv;
    float rotor_rpm;
    float sensor_temp_c;
    uint32_t timestamp_ms;
} raw_sensor_frame_t;

typedef struct {
    float thrust_grams;
    float thrust_newtons;
    float bus_voltage_v;
    float current_amperes;
    float electrical_power_w;
    float rotor_rpm;
    float efficiency_gpw;       // грами на ват
    float mechanical_torque_nm; // розрахунковий момент на валу
    bool data_valid;
} processed_thrust_point_t;

typedef struct {
    thrust_calibration_t cal;
    float thrust_ring_buf[FILTER_WINDOW_SIZE];
    uint8_t ring_idx;
    uint8_t samples_filled;
} thrust_processor_t;

void thrust_processor_init(thrust_processor_t *proc, const thrust_calibration_t *cal) {
    proc->cal = *cal;
    proc->ring_idx = 0;
    proc->samples_filled = 0;
    for (uint8_t i = 0; i < FILTER_WINDOW_SIZE; i++) {
        proc->thrust_ring_buf[i] = 0.0f;
    }
}

void thrust_processor_set_tare(thrust_processor_t *proc, float tare_raw, float current_temp_c) {
    proc->cal.tare_offset_raw = tare_raw;
    proc->cal.base_temp_c = current_temp_c;
}

static float filter_moving_average(thrust_processor_t *proc, float new_val) {
    proc->thrust_ring_buf[proc->ring_idx] = new_val;
    proc->ring_idx = (proc->ring_idx + 1) % FILTER_WINDOW_SIZE;
    if (proc->samples_filled < FILTER_WINDOW_SIZE) {
        proc->samples_filled++;
    }
    
    float sum = 0.0f;
    for (uint8_t i = 0; i < proc->samples_filled; i++) {
        sum += proc->thrust_ring_buf[i];
    }
    return sum / (float)proc->samples_filled;
}

processed_thrust_point_t thrust_processor_update(thrust_processor_t *proc, const raw_sensor_frame_t *raw) {
    processed_thrust_point_t out;
    out.data_valid = false;
    
    if (proc->cal.scale_counts_per_gram < 1e-6f || proc->cal.shunt_resistor_ohms < 1e-6f) {
        return out;
    }
    
    // 1. Обчислення сирої сили з урахуванням тари
    float counts_diff = raw->raw_thrust_counts - proc->cal.tare_offset_raw;
    float uncompensated_grams = counts_diff / proc->cal.scale_counts_per_gram;
    
    // 2. Температурна компенсація зміщення нуля
    float delta_temp = raw->sensor_temp_c - proc->cal.base_temp_c;
    float temp_offset_g = delta_temp * proc->cal.temp_coeff_zero;
    float compensated_grams = uncompensated_grams - temp_offset_g;
    
    // 3. Врахування коефіцієнта плеча важеля L2 / L1
    float lever_corrected_grams = compensated_grams * proc->cal.arm_ratio;
    
    // 4. Цифрова фільтрація ковзним середнім
    out.thrust_grams = filter_moving_average(proc, lever_corrected_grams);
    out.thrust_newtons = out.thrust_grams * 0.00980665f;
    
    // 5. Електричні параметри
    out.bus_voltage_v = raw->bus_voltage_v;
    out.current_amperes = (raw->shunt_voltage_mv * 0.001f) / proc->cal.shunt_resistor_ohms;
    if (out.current_amperes < 0.0f) out.current_amperes = 0.0f;
    
    out.electrical_power_w = out.bus_voltage_v * out.current_amperes;
    out.rotor_rpm = raw->rotor_rpm;
    
    // 6. Розрахунок питомої тяги (грами на ват)
    if (out.electrical_power_w > 0.05f) {
        out.efficiency_gpw = out.thrust_grams / out.electrical_power_w;
    } else {
        out.efficiency_gpw = 0.0f;
    }
    
    // 7. Оцінка механічного моменту на валу tau = P_mech / omega
    // Припускаємо типовий електричний ККД мотора 80% для першого наближення
    float omega_rad_s = out.rotor_rpm * (2.0f * 3.14159265f / 60.0f);
    if (omega_rad_s > 10.0f) {
        float p_mech_est = out.electrical_power_w * 0.80f;
        out.mechanical_torque_nm = p_mech_est / omega_rad_s;
    } else {
        out.mechanical_torque_nm = 0.0f;
    }
    
    out.data_valid = true;
    return out;
}
