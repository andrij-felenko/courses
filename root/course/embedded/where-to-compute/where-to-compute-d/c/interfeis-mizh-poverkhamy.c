// Бортовий комп'ютер надсилає по UART повідомлення MAVLink із кутом на ціль.
// Контур керування НЕ чекає на нього — читає останнє відоме значення й летить.
typedef struct {
    float   target_angle;   // останній кут на ціль від зору
    uint32_t stamp_ms;      // коли прийшов (мс від старту)
    bool    valid;          // чи взагалі щось приходило
} vision_hint_t;

static volatile vision_hint_t g_hint = { 0.0f, 0, false };

// Викликається у перерві приймача UART, коли розібрано пакет MAVLink:
void on_vision_msg(float angle, uint32_t now_ms) {
    g_hint.target_angle = angle;
    g_hint.stamp_ms     = now_ms;
    g_hint.valid        = true;
}

// Викликається в кожному витку контуру (1–8 кГц). Ніколи не блокується:
void control_step(uint32_t now_ms) {
    vision_hint_t h = g_hint;                 // копія-знімок
    bool fresh = h.valid && (now_ms - h.stamp_ms) < 200;  // не старше 200 мс
    if (fresh) {
        steer_towards(h.target_angle);        // веди на ціль
    } else {
        hold_or_search();                     // підказка застаріла — тримай курс / шукай
    }
}
