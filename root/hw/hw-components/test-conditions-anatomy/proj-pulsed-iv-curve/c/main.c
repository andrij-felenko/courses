#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PULSE_DURATION_US      300
#define ADC_TRIGGER_DELAY_US   250
#define COOLDOWN_DELAY_MS      20
#define SHUNT_RESISTANCE_OHM   0.010f   /* 10 мОм прецизійний шунт */
#define ADC_VREF_VOLTS         3.300f   /* Опорна напруга АЦП */
#define ADC_MAX_CODE           4095.0f  /* 12-бітний АЦП */
#define MIN_VALID_CURRENT_A    0.200f   /* Поріг відсікання шумів струму */
#define MAX_CURRENT_LIMIT_A    35.000f  /* Аварійний струмовий ліміт */

typedef struct {
    float v_ds_volts;
    float i_d_amperes;
    float r_ds_on_ohms;
    float energy_joules;
    bool  is_valid;
    bool  overcurrent_fault;
} pulse_measurement_t;

/* Оголошення апаратних функцій периферії MCU */
extern void hw_timer_init_one_pulse(uint32_t pulse_us, uint32_t trigger_us);
extern void hw_timer_trigger_pulse(void);
extern void hw_timer_wait_complete(void);
extern void hw_adc_read_simultaneous(uint16_t *vds_raw, uint16_t *shunt_raw);
extern void hw_gate_driver_set_voltage(float v_gs);
extern void hw_emergency_shutdown(void);
extern void hw_delay_ms(uint32_t ms);

/* Конвертація сирого коду АЦП у напругу */
static inline float convert_adc_to_volts(uint16_t raw_code) {
    return ((float)raw_code / ADC_MAX_CODE) * ADC_VREF_VOLTS;
}

/* Виконання одного імпульсного вимірювання за умов даташита */
pulse_measurement_t perform_pulsed_measurement(float target_v_gs) {
    pulse_measurement_t report = {0};
    uint16_t raw_vds_code = 0;
    uint16_t raw_shunt_code = 0;

    /* 1. Встановлення напруги керування затвором (наприклад 4.5 В або 10.0 В) */
    hw_gate_driver_set_voltage(target_v_gs);

    /* 2. Ініціалізація та запуск апаратного таймера синхронізації */
    hw_timer_init_one_pulse(PULSE_DURATION_US, ADC_TRIGGER_DELAY_US);
    hw_timer_trigger_pulse();

    /* 3. Очікування апаратного завершення імпульсу */
    hw_timer_wait_complete();

    /* 4. Зчитування результатів оцифрування, зафіксованих на 250-й мікросекунді */
    hw_adc_read_simultaneous(&raw_vds_code, &raw_shunt_code);

    /* 5. Перерахунок напруги на стоці та струму шунта */
    report.v_ds_volts = convert_adc_to_volts(raw_vds_code);
    float v_shunt_volts = convert_adc_to_volts(raw_shunt_code);
    report.i_d_amperes = v_shunt_volts / SHUNT_RESISTANCE_OHM;

    /* 6. Апаратний захист: перевірка на перевищення граничного струму */
    if (report.i_d_amperes > MAX_CURRENT_LIMIT_A) {
        hw_emergency_shutdown();
        report.overcurrent_fault = true;
        report.is_valid = false;
        return report;
    }

    /* 7. Розрахунок опору каналу за законом Ома */
    if (report.i_d_amperes >= MIN_VALID_CURRENT_A) {
        report.r_ds_on_ohms = report.v_ds_volts / report.i_d_amperes;
        report.energy_joules = report.v_ds_volts * report.i_d_amperes * (PULSE_DURATION_US * 1e-6f);
        report.is_valid = true;
    } else {
        report.r_ds_on_ohms = 0.0f;
        report.energy_joules = 0.0f;
        report.is_valid = false;
    }

    /* 8. Забезпечення обов'язкової паузи охолодження для виключення нагріву */
    hw_delay_ms(COOLDOWN_DELAY_MS);

    return report;
}
