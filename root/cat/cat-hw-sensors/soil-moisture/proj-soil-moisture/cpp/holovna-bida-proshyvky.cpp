const uint8_t POWER = 7;          // VCC давача живимо з цифрового виводу, не з шини
const uint8_t SOIL  = A0;

void setup() {
    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, LOW);     // у спокої щуп ЗНЕСТРУМЛЕНИЙ
    Serial.begin(9600);
}

int measure() {
    digitalWrite(POWER, HIGH);    // подали живлення на щуп
    delay(10);                     // даємо напрузі усталитися (подільник + ємність)
    int v = median9();             // швидко зняли згладжене число
    digitalWrite(POWER, LOW);     // ОДРАЗУ знеструмили — щуп «відпочиває»
    return v;
}

void loop() {
    int v = measure();
    Serial.println(v);
    delay(60000);                  // міряємо раз на хвилину, а не безперервно
}
