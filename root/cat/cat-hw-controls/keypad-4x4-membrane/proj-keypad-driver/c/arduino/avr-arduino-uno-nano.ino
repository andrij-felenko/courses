#include <Keypad.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>

const byte ROWS = 4, COLS = 4;
char keys[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};
byte rowPins[ROWS] = {4, 5, 6, 7};      // усі в PORTD → один вектор PCINT2
byte colPins[COLS] = {8, 9, 10, 11};

Keypad kpd = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

volatile bool woke = false;             // ISR лише піднімає прапорець

ISR(PCINT2_vect) {                      // спрацьовує на будь-яку зміну на D0..D7
    woke = true;                        // усе — жодного Serial/скану тут
}

// Перевести сітку в АРМ-стан: усі стовпці ведені у «0», рядки — входи з підтяжкою.
void armForWake() {
    for (byte c = 0; c < COLS; c++) {
        pinMode(colPins[c], OUTPUT);
        digitalWrite(colPins[c], LOW);  // усі стовпці РАЗОМ у «0»
    }
    for (byte r = 0; r < ROWS; r++)
        pinMode(rowPins[r], INPUT_PULLUP);   // рядки у спокої «1», натиск їх завалить

    // Увімкнути PCINT на рядкових ногах D4..D7 (PCINT20..23 у PORTD):
    PCICR  |= (1 << PCIE2);             // дозволити групу PORTD
    PCMSK2  = (1 << PCINT20) | (1 << PCINT21) | (1 << PCINT22) | (1 << PCINT23);
    PCIFR  |= (1 << PCIF2);             // скинути можливий залишковий прапорець
}

void sleepNow() {
    armForWake();
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);   // найглибший сон AVR
    cli();
    sleep_enable();
    woke = false;
    sei();                             // переривання дозволені перед самим сном
    sleep_cpu();                       // ← процесор засинає рівно тут
    // --- прокинулися: виконання йде далі ---
    sleep_disable();
    PCICR &= ~(1 << PCIE2);            // вимкнути вартове переривання на час роботи
}

void setup() {
    Serial.begin(9600);
    kpd.setDebounceTime(20);
}

void loop() {
    Serial.println("Засинаю. Розбудить натиск.");
    Serial.flush();                    // дописати порт ДО сну, інакше обірветься
    sleepNow();                        // спимо, поки клавіатуру не притиснуть

    // Прокинулися від натиску. Дамо бібліотеці визначити, ЯКА клавіша:
    // (бібліотека сама поверне сітку у звичайний режим сканування)
    char k = NO_KEY;
    for (byte tries = 0; tries < 40 && k == NO_KEY; tries++) {
        k = kpd.getKey();              // кілька спроб: клавіша ще може деренчати
        delay(2);
    }
    if (k != NO_KEY) {
        Serial.print("клавіша: ");
        Serial.println(k);
        // тут: обробити, надіслати, показати — і назад у сон
    }
}
