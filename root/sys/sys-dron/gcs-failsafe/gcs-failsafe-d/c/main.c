#include <stdint.h>
#include <stdbool.h>

#define JOYSTICK_TIMEOUT_MS 1000u

typedef struct {
    int16_t pitch;    // -1000 .. +1000
    int16_t roll;     // -1000 .. +1000
    int16_t throttle; // 0 .. 1000
    int16_t yaw;      // -1000 .. +1000
} manual_axes_t;

typedef struct {
    manual_axes_t target_axes;
    uint32_t last_manual_packet_ms;
    bool is_joystick_active;
    bool failsafe_engaged;
} joystick_failsafe_t;

void joystick_failsafe_init(joystick_failsafe_t *fs) {
    fs->target_axes = (manual_axes_t){0, 0, 0, 0};
    fs->last_manual_packet_ms = 0;
    fs->is_joystick_active = false;
    fs->failsafe_engaged = false;
}

// Викликається при отриманні MAVLink повідомлення MANUAL_CONTROL (#69)
void joystick_failsafe_on_packet(joystick_failsafe_t *fs, int16_t p, int16_t r, int16_t t, int16_t y, uint32_t now_ms) {
    fs->target_axes.pitch = p;
    fs->target_axes.roll = r;
    fs->target_axes.throttle = t;
    fs->target_axes.yaw = y;
    fs->last_manual_packet_ms = now_ms;
    fs->is_joystick_active = true;
    fs->failsafe_engaged = false;
}

// Викликається у високочастотному циклі регулятора (наприклад, 100 Гц)
void joystick_failsafe_update(joystick_failsafe_t *fs, uint32_t now_ms) {
    if (!fs->is_joystick_active) {
        return;
    }

    uint32_t elapsed = now_ms - fs->last_manual_packet_ms;
    if (elapsed >= JOYSTICK_TIMEOUT_MS) {
        // Таймаут перевищено: скидаємо стики в безпечну нейтраль
        fs->target_axes.pitch = 0;
        fs->target_axes.roll = 0;
        fs->target_axes.yaw = 0;
        // Газ утримується на рівні зависання (Hover Throttle) або передається регулятору висоти
        fs->target_axes.throttle = 500;
        fs->failsafe_engaged = true;
    }
}
