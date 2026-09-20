// Інтеграція неблокуючого опитування перемикача у головний цикл програми мовою C++
#include "ThumbwheelDriver.hpp"

static ThumbwheelDriver thumbwheel({
    .dataPins = {4, 5, 6, 7},
    .digitCount = 4,
    .debounceMs = 50
});

void setup() {
    thumbwheel.begin();
}

void loop() {
    static uint32_t lastValue = 0;

    // Регулярний неблокуючий виклик у циклі loop()
    thumbwheel.update();

    if (thumbwheel.isValid()) {
        uint32_t currentValue = thumbwheel.getValue();
        if (currentValue != lastValue) {
            lastValue = currentValue;
            // Використання нової підтвердженої уставки
        }
    }

    delay(10);
}
