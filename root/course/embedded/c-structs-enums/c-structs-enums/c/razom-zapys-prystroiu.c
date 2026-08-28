#include <stdint.h>
#include <stdio.h>

enum sensor_mode {
    S_IDLE,        // 0 — чекає
    S_READING,     // 1 — саме міряє
    S_FAULT        // 2 — несправність
};

typedef struct {
    uint8_t          id;       // номер давача на шині
    float            last;     // останнє показання, °C
    enum sensor_mode mode;     // у якому стані давач зараз
} Sensor;

// один крок обробки давача: залежно від стану — своя дія
void step(Sensor *s, float reading) {
    switch (s->mode) {
        case S_IDLE:
            s->mode = S_READING;          // прокидаємося міряти
            break;
        case S_READING:
            if (reading < -50 || reading > 150) {
                s->mode = S_FAULT;        // безглузде число — несправність
            } else {
                s->last = reading;        // приймаємо вимір
                s->mode = S_IDLE;         // і знову чекаємо
            }
            break;
        case S_FAULT:
            // лишаємося в помилці, доки не скинуть ззовні
            break;
    }
}

int main(void) {
    Sensor t = { .id = 1, .last = 0.0f, .mode = S_IDLE };

    step(&t, 0.0f);      // S_IDLE  → S_READING
    step(&t, 23.5f);     // S_READING → приймає 23.5, → S_IDLE
    step(&t, 0.0f);      // S_IDLE  → S_READING
    step(&t, 999.0f);    // безглуздий вимір → S_FAULT

    printf("давач %u: останнє %.1f°C, режим %d\n",
           t.id, t.last, t.mode);
    return 0;
}
