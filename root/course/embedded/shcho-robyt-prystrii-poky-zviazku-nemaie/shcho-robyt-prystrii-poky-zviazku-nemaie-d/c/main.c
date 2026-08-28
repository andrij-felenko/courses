#include <stdint.h>
#include <stdbool.h>

#define TIMEOUT_PHASE1_MS    5000U
#define TIMEOUT_PHASE2_MS   60000U
#define DEADMAN_INTERVAL_MS   250U

typedef enum {
    STATE_ONLINE = 0,
    STATE_HOLD_PHASE1,
    STATE_AUTONOMOUS_PHASE2,
    STATE_SAFE_STATE_PHASE3,
    STATE_RECONNECTING
} fallback_state_t;

typedef struct {
    float throttle_cmd;      // уставка газу [-1.0 .. +1.0]
    float steering_cmd;      // уставка керма [-1.0 .. +1.0]
    uint32_t seq_id;         // номер пакета
} control_packet_t;

typedef struct {
    fallback_state_t state;
    uint32_t last_packet_time_ms;
    uint32_t state_entry_time_ms;
    control_packet_t cached_cmd;
    float current_throttle;
    float current_steering;
    bool hardware_enabled;
} fallback_controller_t;

// Апаратні прототипи взаємодії з силовою частиною та пам'яттю
void hw_set_actuators(float throttle, float steering);
void hw_set_power_enable(bool enable);
void hw_flash_log_event(uint8_t event_id, uint32_t timestamp);
uint32_t platform_get_ms(void);

void fallback_init(fallback_controller_t *fsm) {
    fsm->state = STATE_ONLINE;
    fsm->last_packet_time_ms = platform_get_ms();
    fsm->state_entry_time_ms = fsm->last_packet_time_ms;
    fsm->cached_cmd = (control_packet_t){0.0f, 0.0f, 0};
    fsm->current_throttle = 0.0f;
    fsm->current_steering = 0.0f;
    fsm->hardware_enabled = true;
    hw_set_power_enable(true);
}

// Викликається при отриманні валідного авторизованого пакета
void fallback_on_packet_received(fallback_controller_t *fsm, const control_packet_t *pkt) {
    uint32_t now = platform_get_ms();
    fsm->last_packet_time_ms = now;

    if (fsm->state == STATE_HOLD_PHASE1) {
        fsm->state = STATE_ONLINE;
        fsm->cached_cmd = *pkt;
    } else if (fsm->state == STATE_AUTONOMOUS_PHASE2 || fsm->state == STATE_SAFE_STATE_PHASE3) {
        fsm->state = STATE_RECONNECTING;
        fsm->state_entry_time_ms = now;
        fsm->cached_cmd = *pkt;
        hw_flash_log_event(0xA1 /* RECONNECT_START */, now);
    } else if (fsm->state == STATE_ONLINE) {
        fsm->cached_cmd = *pkt;
    }
}

// Періодичний такт автомата (наприклад, кожні 10 мс у головному циклі)
void fallback_update_tick(fallback_controller_t *fsm) {
    uint32_t now = platform_get_ms();
    uint32_t silence_duration = now - fsm->last_packet_time_ms;

    switch (fsm->state) {
        case STATE_ONLINE:
            if (silence_duration > DEADMAN_INTERVAL_MS) {
                fsm->state = STATE_HOLD_PHASE1;
                fsm->state_entry_time_ms = now;
                hw_flash_log_event(0x01 /* ENTER_PHASE1 */, now);
            } else {
                fsm->current_throttle = fsm->cached_cmd.throttle_cmd;
                fsm->current_steering = fsm->cached_cmd.steering_cmd;
                hw_set_actuators(fsm->current_throttle, fsm->current_steering);
            }
            break;

        case STATE_HOLD_PHASE1:
            if (silence_duration > TIMEOUT_PHASE1_MS) {
                fsm->state = STATE_AUTONOMOUS_PHASE2;
                fsm->state_entry_time_ms = now;
                hw_flash_log_event(0x02 /* ENTER_PHASE2 */, now);
            } else {
                // Утримання уставки з поступовим безпечним згасанням тяги на 20%
                fsm->current_throttle = fsm->cached_cmd.throttle_cmd * 0.8f;
                hw_set_actuators(fsm->current_throttle, fsm->cached_cmd.steering_cmd);
            }
            break;

        case STATE_AUTONOMOUS_PHASE2:
            if (silence_duration > TIMEOUT_PHASE2_MS) {
                fsm->state = STATE_SAFE_STATE_PHASE3;
                fsm->state_entry_time_ms = now;
                fsm->hardware_enabled = false;
                hw_set_power_enable(false); // Апаратне знеструмлення силових ключів
                hw_set_actuators(0.0f, 0.0f);
                hw_flash_log_event(0x03 /* ENTER_PHASE3_FAILSAFE */, now);
            } else {
                // Локальна евристика: плавна зупинка й повернення коліс у нуль
                if (fsm->current_throttle > 0.05f) {
                    fsm->current_throttle -= 0.02f; // Плавне гальмування
                } else {
                    fsm->current_throttle = 0.0f;
                }
                fsm->current_steering = 0.0f;
                hw_set_actuators(fsm->current_throttle, fsm->current_steering);
            }
            break;

        case STATE_SAFE_STATE_PHASE3:
            // Повний Fail-Safe: приводи знеструмлені, усе в нулі
            hw_set_actuators(0.0f, 0.0f);
            break;

        case STATE_RECONNECTING:
            // Плавне підтягування (Ramp-up) від поточної позиції до нової команди
            if (!fsm->hardware_enabled) {
                fsm->hardware_enabled = true;
                hw_set_power_enable(true);
            }
            // Зрівнюємо газ не більше ніж на 0.05 за ітерацію (усунення ривка)
            float diff = fsm->cached_cmd.throttle_cmd - fsm->current_throttle;
            if (diff > 0.05f) fsm->current_throttle += 0.05f;
            else if (diff < -0.05f) fsm->current_throttle -= 0.05f;
            else fsm->current_throttle = fsm->cached_cmd.throttle_cmd;

            fsm->current_steering = fsm->cached_cmd.steering_cmd;
            hw_set_actuators(fsm->current_throttle, fsm->current_steering);

            if ((now - fsm->state_entry_time_ms) > 1000U) { // 1 с на плавний перехід
                fsm->state = STATE_ONLINE;
                hw_flash_log_event(0xA2 /* RECONNECT_COMPLETE */, now);
            }
            break;
    }
}
