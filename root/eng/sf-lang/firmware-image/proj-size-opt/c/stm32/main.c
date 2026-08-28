#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim3;

// Велика таблиця тонів — читає лише DMA за адресою,
// статичного посилання з коду нема → gc-sections може вирізати!
// Атрибут __attribute__((used)) каже лінкеру: «лишити навіть без посилань»
static const uint16_t TONE_TABLE[] __attribute__((used)) = {
    261, 294, 330, 349, 392, 440, 494, 523
};

// Цю функцію кличе main() — статичне посилання видно лінкеру,
// gc-sections її не чіпає
static void play_tick(uint16_t freq) {
    // ... виводить частоту на таймер ...
    (void)freq;
}

// Обробник переривання: на нього посилається лише таблиця векторів
// зі startup-файлу. Тут утримує не атрибут, а скрипт компонувальника:
// KEEP(*(.isr_vector)) — інакше --gc-sections викине секцію цілком.
void TIM3_IRQHandler(void) {
    HAL_TIM_IRQHandler(&htim3);  // ... обслуговує переривання таймера ...
}

int main(void) {
    HAL_Init();
    play_tick(TONE_TABLE[0]);    // ← статичне посилання: лінкер бачить, лишає
    while (1) { HAL_Delay(10); }
}
