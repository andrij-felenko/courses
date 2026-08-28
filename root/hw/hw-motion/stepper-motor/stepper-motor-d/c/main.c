#include <stdint.h>

// чотири виходи MCU на входи драйвера/ключів котушок A, B, A', B'
static const uint8_t COIL[4] = { PIN_A, PIN_B, PIN_NA, PIN_NB };

// одна активна фаза за раз; рядок таблиці = яку котушку живимо
static const uint8_t PHASE[4][4] = {
    {1, 0, 0, 0},   // живиться A
    {0, 1, 0, 0},   // живиться B
    {0, 0, 1, 0},   // живиться A'
    {0, 0, 0, 1},   // живиться B'
};

// один крок: виставити фазу за індексом
static void apply_phase(uint8_t idx) {
    for (uint8_t c = 0; c < 4; c++)
        gpio_write(COIL[c], PHASE[idx][c]);
}

// провернути на steps кроків; dir = +1 (вперед) або -1 (назад)
void stepper_move(uint32_t steps, int8_t dir, uint32_t delay_us) {
    static uint8_t phase = 0;                 // пам'ятаємо, де ми у послідовності
    for (uint32_t i = 0; i < steps; i++) {
        phase = (phase + (dir > 0 ? 1 : 3)) & 3;   // +1 уперед, +3 (=−1 mod 4) назад
        apply_phase(phase);
        delay_microseconds(delay_us);          // пауза задає швидкість
    }
}

// провернути вал на 90° для мотора з кроком 1.8° (200 кроків/оберт)
void quarter_turn(void) {
    stepper_move(50, +1, 2000);                // 50 кроків уперед, 2 мс між кроками
}
