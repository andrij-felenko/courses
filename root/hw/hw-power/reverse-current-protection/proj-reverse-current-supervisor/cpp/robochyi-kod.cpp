#include <stdint.h>

// ── Калібрування ланцюга давача (рахується раз, під конкретну плату) ─────────
// АЦП 12-біт, опора 3.300 В  → 3300 мВ / 4096 = 0.8057 мВ на відлік
// Чутливість S = G·Rs = 50 · 0.010 Ом = 0.5 В/А   →   1 мВ = 2 мА
//   один відлік = 0.8057 мВ · 2 мА/мВ = 1.611 мА ≈ 1611 мкА
static const int32_t UA_PER_COUNT = 1611;   // мкА на один відлік АЦП
static const int16_t BIAS_COUNT   = 2048;   // 1.650 В — точка нульового струму

// Сирий відлік → ЗНАКОВИЙ струм у мкА (плюс — уперед, мінус — назад):
static inline int32_t counts_to_uA(uint16_t raw) {
    return (int32_t)((int16_t)raw - BIAS_COUNT) * UA_PER_COUNT;
}

void gate_write(bool on);   // прив'язка до заліза — нижче

// ── Наглядач зворотного струму ──────────────────────────────────────────────
class ReverseGuard {
public:
    struct Config {
        int32_t trip_uA;    // модуль реверсу, що вважаємо аварією (300000 = 300 мА)
        int32_t rearm_uA;   // прямий струм для повернення на варту (гістерезис)
        uint8_t deglitch;   // скільки вибірок поспіль умова має протриматися
        bool    latching;   // true — лишатися вимкненим до явного reset()
    };

    explicit ReverseGuard(const Config& c) : cfg(c) {}

    // Виклик із РІВНОМІРНОГО такту (обробник переривання таймера).
    void tick(int32_t i_uA) {
        last_uA = i_uA;
        if (state == ARMED) {
            // реверс від'ємний; аварія — коли струм глибше за −trip
            if (i_uA <= -cfg.trip_uA) {
                if (++rev_run >= cfg.deglitch) trip();
            } else {
                rev_run = 0;              // будь-яка здорова вибірка скидає лічильник
            }
        } else {                          // TRIPPED
            if (cfg.latching) return;     // засувка: вихід лише через reset()
            if (i_uA >= cfg.rearm_uA) {
                if (++fwd_run >= cfg.deglitch) rearm();
            } else {
                fwd_run = 0;
            }
        }
    }

    bool    faulted() const { return fault; }    // липкий прапорець для системи
    int32_t current() const { return last_uA; }
    void    reset()         { fault = false; rearm(); }  // ручне скидання засувки

private:
    enum State { ARMED, TRIPPED };

    void trip() {
        gate_write(false);   // ПЕРШЕ — розімкнути ключ (дія в залізі)
        state = TRIPPED;
        fault = true;        // ПОТІМ — підняти прапорець для системи
        rev_run = 0;
    }
    void rearm() {
        gate_write(true);
        state = ARMED;
        fwd_run = 0;
    }

    Config  cfg;
    State   state   = ARMED;
    uint8_t rev_run = 0, fwd_run = 0;
    bool    fault   = false;
    int32_t last_uA = 0;
};
