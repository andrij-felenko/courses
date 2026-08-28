// Звуковий давач на LM393 → Arduino Uno.
// DO давача на D2 (переривання), вбудований світлодіод на D13.
// Спокій = 1, звук = короткий 0. Дебаунс неблокуючий, у перериванні.

const uint8_t SOUND = 2;                  // DO на ногу переривання D2
const uint8_t LED   = 13;                 // вбудований світлодіод плати
const unsigned long WINDOW = 150;         // вікно дебаунсу, мс

volatile unsigned long lastHit = 0;
volatile unsigned long count   = 0;
volatile bool ready = false;

void onSound() {                          // ISR: коротка, лише відсів і позначка
    unsigned long t = millis();
    if (t - lastHit > WINDOW) {           // ігноруємо торохтіння того ж плеску
        lastHit = t;
        count++;
        ready = true;
    }
}

void setup() {
    pinMode(SOUND, INPUT);                // підтяжка на платі → спокій = 1
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    attachInterrupt(digitalPinToInterrupt(SOUND), onSound, FALLING);
    Serial.println("готово. плесніть у долоні.");
}

void loop() {
    if (ready) {                          // головний цикл збирає врожай
        ready = false;
        digitalWrite(LED, HIGH);
        Serial.print("плеск #");
        Serial.println(count);
        delay(30);                        // коротке блимання — тут delay доречний
        digitalWrite(LED, LOW);
    }
    // сюди можна вставити будь-яку іншу роботу — переривання не проґавить звук
}
