#include <Arduino.h>

// Велика таблиця тонів — читається лише DMA-периферією за покажчиком,
// статичного посилання з коду нема → gc-sections може вирізати!
// Атрибут __attribute__((used)) каже лінкеру: «лишити навіть без посилань»
static const uint16_t TONE_TABLE[] __attribute__((used)) = {
    261, 294, 330, 349, 392, 440, 494, 523
};

// Цю функцію кличе loop() — статичне посилання видно лінкеру,
// gc-sections її не чіпає
static void play_tick(uint16_t freq) {
    // ... виводить частоту на таймер ...
    (void)freq;
}

// Обробник переривання: на нього посилається лише таблиця векторів,
// яку збирає лінкер-скрипт — статичного виклику з C-коду немає.
// Без __attribute__((used)) gc-sections може його вирізати!
void IRAM_ATTR TIMER0_IRQHandler() __attribute__((used));
void IRAM_ATTR TIMER0_IRQHandler() {
    // ... обслуговує переривання таймера ...
}

void setup() {}

void loop() {
    play_tick(TONE_TABLE[0]);  // ← статичне посилання: лінкер бачить, лишає
}
