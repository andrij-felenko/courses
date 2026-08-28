#include <Arduino.h>

const uint8_t PAD = A0;       // вивід сенсорної площадки
const uint16_t TIMEOUT = 2000;// стеля циклів, щоб не зависнути

// Один замір: розрядити площадку, тоді порахувати цикли до порога "1".
uint16_t measure_pad(void) {
    // 1) розряд: вивід — вихід, рівень 0
    pinMode(PAD, OUTPUT);
    digitalWrite(PAD, LOW);
    delayMicroseconds(50);    // дати ємності повністю стектись

    // 2) відпускаємо: вивід — вхід без підтяжки; рахуємо, доки не стане "1"
    uint16_t n = 0;
    pinMode(PAD, INPUT);
    while (digitalRead(PAD) == LOW && n < TIMEOUT)
        n++;                  // кожен цикл — фіксований квант часу
    return n;                 // більша ємність → більше n
}
