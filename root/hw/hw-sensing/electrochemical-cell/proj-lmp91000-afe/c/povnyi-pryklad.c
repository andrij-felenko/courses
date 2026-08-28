#include <stdio.h>
#include <unistd.h>

extern bool platform_i2c_write(uint8_t reg, uint8_t val);
extern bool platform_i2c_read(uint8_t reg, uint8_t *val);
extern float platform_adc_read_voltage(void);
extern void platform_delay_ms(uint32_t ms);
extern void platform_enter_sleep_mode(uint32_t seconds);

void run_gas_detector_task(void) {
    lmp91000_config_t co_config = {
        .gain = LMP91000_TIA_GAIN_120K,
        .rload = LMP91000_RLOAD_10OHM,
        .int_zero = LMP91000_INT_ZERO_20PCT,
        .bias_sign = LMP91000_BIAS_SIGN_NEG,
        .bias_mag = LMP91000_BIAS_0PCT,
        .vref_volts = 3.30f,
        .sensitivity_na_per_ppm = 70.0f,
        .baseline_current_na = 2.5f
    };

    lmp91000_t co_sensor;
    if (!lmp91000_init(&co_sensor, &co_config, platform_i2c_write, platform_i2c_read)) {
        return;
    }

    while (1) {
        lmp91000_set_mode(&co_sensor, LMP91000_OP_MODE_TEMP_TIAON, false);
        platform_delay_ms(20);
        float v_temp = platform_adc_read_voltage();
        float current_temp_c = lmp91000_raw_voltage_to_temperature(v_temp);

        lmp91000_set_mode(&co_sensor, LMP91000_OP_MODE_3LEAD_AMP, false);
        platform_delay_ms(50);
        float v_gas = platform_adc_read_voltage();

        float co_ppm = lmp91000_calculate_ppm(&co_sensor, v_gas, current_temp_c);

        if (co_ppm > 35.0f) {
            /* Поріг тривоги перевищено */
        }

        lmp91000_set_mode(&co_sensor, LMP91000_OP_MODE_DEEP_SLEEP, true);
        platform_enter_sleep_mode(5);
    }
}
