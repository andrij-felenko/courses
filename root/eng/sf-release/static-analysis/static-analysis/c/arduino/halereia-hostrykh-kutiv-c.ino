#include <Wire.h>

// (а) = замість ==
int flag = 0;
if (flag = digitalRead(2)) {           // пастка: присвоєння, не порівняння
    Serial.println("triggered");       // виконується завжди, коли рівень != 0
}

// (б) звуження типу — маска нульова
uint8_t mask = 1 << 9;                 // 1<<9 = 512 = 0x200; uint8_t → 0
Wire.beginTransmission(0x20);
Wire.write(mask);                      // у розширювач іде 0 — жоден вихід не встає
Wire.endTransmission();
