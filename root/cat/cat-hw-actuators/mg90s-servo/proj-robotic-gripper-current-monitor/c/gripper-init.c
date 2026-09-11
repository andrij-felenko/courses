#include <stdint.h>
#include <stdbool.h>

#define ADC_SAMPLE_PERIOD_MS    2
#define FSM_UPDATE_PERIOD_MS    10
#define CURRENT_STALL_LIMIT_MA  750
#define BLANKING_TIME_MS        30
#define SQUEEZE_TIMEOUT_MS      350
#define DERIV_THRESHOLD_MA_MS   30

typedef enum {
    STATE_OPEN,
    STATE_APPROACH,
    STATE_CONTACT_DETECT,
    STATE_SQUEEZE,
    STATE_HOLD,
    STATE_STALL_ERROR
} GripperState;

typedef struct {
    GripperState state;
    float current_angle_deg;
    float target_force_n;
    uint32_t state_timer_ms;
    uint32_t blanking_timer_ms;
    int32_t filtered_current_q8;
    uint16_t current_history[4];
    uint8_t history_idx;
} GripperDriver;

// Зовнішні апаратні функції платформи
extern uint16_t bsp_adc_read_current_ma(void);
extern void bsp_servo_set_angle(float angle_deg);
extern void bsp_servo_power_off(void);
extern uint32_t bsp_get_time_ms(void);

void gripper_init(GripperDriver *dev) {
    dev->state = STATE_OPEN;
    dev->current_angle_deg = 10.0f;
    dev->target_force_n = 3.0f;
    dev->state_timer_ms = 0;
    dev->blanking_timer_ms = 0;
    dev->filtered_current_q8 = 0;
    dev->history_idx = 0;
    for (int i = 0; i < 4; i++) dev->current_history[i] = 0;
    bsp_servo_set_angle(dev->current_angle_deg);
}

// Крок швидкої фільтрації струму (викликається кожні 2 мс)
void gripper_process_adc_tick(GripperDriver *dev) {
    uint16_t raw_ma = bsp_adc_read_current_ma();

    // Експоненційний фільтр EMA (alpha = 0.10, Q8)
    int32_t raw_q8 = (int32_t)raw_ma << 8;
    dev->filtered_current_q8 = (26 * raw_q8 + 230 * dev->filtered_current_q8) >> 8;
    uint16_t current_ma = (uint16_t)(dev->filtered_current_q8 >> 8);

    // Збереження в кільцевий буфер
    dev->current_history[dev->history_idx] = current_ma;
    dev->history_idx = (dev->history_idx + 1) & 0x03;

    // Сторожовий контроль заклинювання (Stall Watchdog)
    if (dev->state != STATE_OPEN && dev->state != STATE_STALL_ERROR) {
        if (current_ma >= CURRENT_STALL_LIMIT_MA) {
            dev->state = STATE_STALL_ERROR;
            dev->current_angle_deg -= 5.0f;
            bsp_servo_set_angle(dev->current_angle_deg);
            bsp_servo_power_off();
        }
    }
}

// Крок автомата керування (викликається кожні 10 мс)
void gripper_process_fsm_tick(GripperDriver *dev) {
    dev->state_timer_ms += FSM_UPDATE_PERIOD_MS;
    if (dev->blanking_timer_ms > 0) {
        dev->blanking_timer_ms = (dev->blanking_timer_ms >= FSM_UPDATE_PERIOD_MS) ?
                                 (dev->blanking_timer_ms - FSM_UPDATE_PERIOD_MS) : 0;
    }

    uint16_t current_ma = (uint16_t)(dev->filtered_current_q8 >> 8);
    uint8_t oldest_idx = dev->history_idx; // Наступний за поточним — найстаріший
    int16_t di_dt = ((int16_t)current_ma - (int16_t)dev->current_history[oldest_idx]) / 8;

    switch (dev->state) {
        case STATE_OPEN:
            break;

        case STATE_APPROACH:
            dev->current_angle_deg += 2.0f;
            bsp_servo_set_angle(dev->current_angle_deg);
            if (dev->blanking_timer_ms == 0) {
                dev->state = STATE_CONTACT_DETECT;
            }
            break;

        case STATE_CONTACT_DETECT:
            dev->current_angle_deg += 1.0f;
            bsp_servo_set_angle(dev->current_angle_deg);
            if (di_dt >= DERIV_THRESHOLD_MA_MS) {
                dev->state = STATE_SQUEEZE;
                dev->state_timer_ms = 0;
            }
            break;

        case STATE_SQUEEZE: {
            dev->current_angle_deg += 0.5f;
            bsp_servo_set_angle(dev->current_angle_deg);
            // Приблизна лінійна оцінка сили: (I - 165 мА) * 0.013 Н/мА
            float force_n = (current_ma > 165) ? (float)(current_ma - 165) * 0.013f : 0.0f;
            if (force_n >= dev->target_force_n) {
                dev->state = STATE_HOLD;
                dev->current_angle_deg -= 0.8f; // Безпечний відкат
                bsp_servo_set_angle(dev->current_angle_deg);
            } else if (dev->state_timer_ms >= SQUEEZE_TIMEOUT_MS) {
                dev->state = STATE_STALL_ERROR;
                bsp_servo_power_off();
            }
            break;
        }

        case STATE_HOLD:
        case STATE_STALL_ERROR:
            break;
    }
}
