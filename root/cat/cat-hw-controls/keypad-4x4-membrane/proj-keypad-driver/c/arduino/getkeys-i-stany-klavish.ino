#include <Keypad.h>

const byte ROWS = 4, COLS = 4;
char keys[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};
Keypad kpd = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
    Serial.begin(9600);
    kpd.setDebounceTime(20);
    kpd.setHoldTime(1000);     // "тримають" = утримання понад 1000 мс
}

void loop() {
    if (kpd.getKeys()) {                          // хоч одна клавіша активна
        for (byte i = 0; i < LIST_MAX; i++) {     // перебрати до 10 клавіш
            if (!kpd.key[i].stateChanged) continue;   // цікавить лише ЗМІНА стану
            char c = kpd.key[i].kchar;
            switch (kpd.key[i].kstate) {
                case PRESSED:
                    Serial.print("натиснуто: "); Serial.println(c);
                    break;
                case HOLD:
                    Serial.print("довге утримання: "); Serial.println(c);
                    break;
                case RELEASED:
                    Serial.print("відпущено: "); Serial.println(c);
                    break;
                case IDLE:
                    break;
            }
        }
    }
}
