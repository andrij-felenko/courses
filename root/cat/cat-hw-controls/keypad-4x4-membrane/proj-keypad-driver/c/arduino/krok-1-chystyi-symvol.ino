#include <Keypad.h>

const byte ROWS = 4, COLS = 4;

// що НАДРУКОВАНО на клавіатурі, [рядок][стовпець]:
char keys[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};

byte rowPins[ROWS] = {9, 8, 7, 6};   // R1..R4
byte colPins[COLS] = {5, 4, 3, 2};   // C1..C4

// makeKeymap перетворює двовимірний масив на те, що очікує конструктор:
Keypad kpd = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
    Serial.begin(9600);
    kpd.setDebounceTime(20);   // скільки мс тримати рівень, щоб повірити (типово 10)
}

void loop() {
    char k = kpd.getKey();     // символ у МИТЬ натиску, інакше NO_KEY (0)
    if (k != NO_KEY) {
        Serial.print("клавіша: ");
        Serial.println(k);
    }
    // тут-таки роби будь-що інше — getKey() не блокує, вертається миттєво
}
