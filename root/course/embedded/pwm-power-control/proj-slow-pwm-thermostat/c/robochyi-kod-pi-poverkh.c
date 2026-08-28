#include <stdint.h>

// ПІ-регулятор температури з умовним інтегруванням (anti-windup через clamping).
// Викликати повільно й РІВНОМІРНО (фіксований крок dt), напр. раз на секунду.
typedef struct {
    float setpoint;   // бажана температура, °C
    float kp;         // пропорційний коефіцієнт (частка/°C)
    float ki;         // інтегральний коефіцієнт (частка/(°C·с))
    float integ;      // накопичений інтеграл (у одиницях частки потужності)
    float dt;         // крок дискретизації, с (має збігатися з реальним темпом виклику)
} pi_t;

void pi_init(pi_t *c, float setpoint, float kp, float ki, float dt) {
    c->setpoint = setpoint;
    c->kp = kp;
    c->ki = ki;
    c->integ = 0.0f;
    c->dt = dt;
}

// Повертає бажану частку потужності 0..1.
float pi_update(pi_t *c, float temp) {
    float err = c->setpoint - temp;           // додатна = холодно, треба гріти

    // Кандидат інтеграла, ЯКБИ ми проінтегрували цей крок.
    float integ_next = c->integ + err * c->dt;

    // Сирий (ненасичений) вихід із кандидатом інтеграла.
    float raw = c->kp * err + c->ki * integ_next;

    // Насичуємо вихід до фізичних меж 0..1.
    float out = raw;
    if (out > 1.0f) out = 1.0f;
    if (out < 0.0f) out = 0.0f;

    // УМОВНЕ ІНТЕГРУВАННЯ: приймаємо новий інтеграл ЛИШЕ якщо вихід НЕ насичений,
    // або якщо похибка штовхає нас ГЕТЬ від межі (тобто інтеграл почне спадати).
    bool saturated_high = (raw > 1.0f) && (err > 0.0f);
    bool saturated_low  = (raw < 0.0f) && (err < 0.0f);
    if (!saturated_high && !saturated_low) {
        c->integ = integ_next;   // інтегруємо
    }
    // інакше — заморожуємо інтеграл на місці (не роздуваємо)

    return out;
}
