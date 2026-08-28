#include <Keypad.h>

const byte ROWS = 4;
const byte COLS = 4;

// Розкладка — та сама таблиця символів, що й у голому драйвері.
char keys[ROWS][COLS] = {
    { '1', '2', '3', 'A' },
    { '4', '5', '6', 'B' },
    { '7', '8', '9', 'C' },
    { '*', '0', '#', 'D' },
};

byte rowPins[ROWS] = { 2, 3, 4, 5 };   // ніжки рядків
byte colPins[COLS] = { 6, 7, 8, 9 };   // ніжки стовпців

// makeKeymap(keys) віддає бібліотеці таблицю; далі — ніжки й розміри.
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
    Serial.begin(115200);
}

void loop() {
    char key = keypad.getKey();     // 0 (NO_KEY), якщо нічого свіжого нема
    if (key) {
        Serial.print("натиснуто: ");
        Serial.println(key);
    }
}
