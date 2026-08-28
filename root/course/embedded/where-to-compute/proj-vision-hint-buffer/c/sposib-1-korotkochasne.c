#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float    target_angle;   // кут на ціль від зору
    uint32_t stamp_ms;       // коли прийшов (мс від старту)
    bool     valid;          // чи взагалі щось приходило
} vision_hint_t;

// Спільна змінна: пише перерва UART, читає контур.
static volatile vision_hint_t g_hint = { 0.0f, 0, false };

// ── писар: у перерві приймача, коли розібрано пакет MAVLink ──
void on_vision_msg(float angle, uint32_t now_ms) {
    g_hint.target_angle = angle;   // перерва не переривається контуром,
    g_hint.stamp_ms     = now_ms;  // тож тут окремий захист не потрібен
    g_hint.valid        = true;
}

// ── читач: у витку контуру. Бере ЦІЛІСНИЙ знімок ──
vision_hint_t hint_read_critical(void) {
    vision_hint_t snap;

    __disable_irq();          // заборонили перерви (CMSIS; або своя обгортка)
    snap = g_hint;            // копіюємо цілком — перерва вклинитись не може
    __enable_irq();           // одразу повернули перерви

    return snap;              // далі працюємо з копією скільки завгодно
}
