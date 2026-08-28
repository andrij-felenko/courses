#include <stdint.h>
#include <stdbool.h>

// Прочитати ОДИН пін кілька разів і повернути значення-переможця (0 або 1).
// Захищає від поодинокого наведення на момент зчитування.
static uint8_t read_pin_debounced(GPIO_TypeDef *port, uint16_t pin) {
    const int N = 5;                 // непарне — щоб більшість завжди існувала
    int ones = 0;
    for (int i = 0; i < N; i++) {
        if (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_SET) ones++;
        for (volatile int d = 0; d < 200; d++) { }   // коротка пауза між відліками
    }
    return (ones > N / 2) ? 1 : 0;   // більшість «одиниць» → 1, інакше 0
}
