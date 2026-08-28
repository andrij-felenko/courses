const uint8_t POWER = 7;         // VCC давача живимо з цифрового виводу
const uint8_t SOIL  = A0;

void setup() {
    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, LOW);    // у спокої давач знеструмлений
    Serial.begin(9600);
}

int measure() {
    digitalWrite(POWER, HIGH);   // подали живлення на щуп
    delay(10);                   // даємо напрузі усталитися
    int v = analogRead(SOIL);    // швидко зняли
    digitalWrite(POWER, LOW);    // одразу знеструмили — щуп «відпочиває»
    return v;
}

void loop() {
    Serial.println(measure());
    delay(60000);                // міряємо раз на хвилину, а не безперервно
}
