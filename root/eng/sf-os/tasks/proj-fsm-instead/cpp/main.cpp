#include <Arduino.h>

enum class State { Idle, Purge, Running, Cooldown };

static State     state = State::Idle;
static uint32_t  t0    = 0;        // мітка входу в поточний стан (millis)

constexpr uint32_t PURGE_MS    = 2000;   // 2 с продувки
constexpr uint32_t COOLDOWN_MS = 3000;   // 3 с охолодження

constexpr uint8_t PIN_VALVE = 5;
constexpr uint8_t PIN_PUMP  = 6;

// Вхід у новий стан: зберегти + перезапустити таймер
static void enter(State s) {
    state = s;
    t0    = millis();
}

// Детектор натискання — фронт з антибрязкотом (§4.4.5 / ⚙️ §4.4.5a)
static bool buttonPressed() {
    // реалізацію детектора фронту взято з §4.4.5a
    return false; // заглушка
}

// Головна функція автомата — зветься щооберту, НЕ блокує
void fsmStep() {
    const uint32_t now = millis();

    switch (state) {
        case State::Idle:
            if (buttonPressed())            enter(State::Purge);      // подія
            break;

        case State::Purge:
            digitalWrite(PIN_VALVE, LOW);                              // дія стану
            if (now - t0 >= PURGE_MS)       enter(State::Running);    // час
            break;

        case State::Running:
            digitalWrite(PIN_PUMP, HIGH);
            if (buttonPressed())            enter(State::Cooldown);   // подія
            break;

        case State::Cooldown:
            digitalWrite(PIN_PUMP, LOW);
            if (now - t0 >= COOLDOWN_MS)    enter(State::Idle);       // час → коло
            break;
    }
}

void setup() {
    pinMode(PIN_VALVE, OUTPUT);
    pinMode(PIN_PUMP,  OUTPUT);
}

void loop() {
    fsmStep();   // весь автомат — один виклик
}
