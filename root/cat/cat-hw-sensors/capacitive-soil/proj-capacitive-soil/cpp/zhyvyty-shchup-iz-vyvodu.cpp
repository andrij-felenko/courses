const uint8_t POWER = 7;          // VCC щупа живимо з цифрового виводу
const uint8_t SOIL  = A0;         // AOUT

void setup() {
    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, LOW);     // у спокої щуп ЗНЕСТРУМЛЕНИЙ (генератор мовчить)
}

int measure() {
    digitalWrite(POWER, HIGH);    // подали живлення — генератор запустився
    delay(50);                     // ЧЕКАЄМО, поки все усталиться (див. нижче)
    int v = readAvg(SOIL);         // тепер знімаємо
    digitalWrite(POWER, LOW);     // знеструмили — щуп «відпочиває»
    return v;
}
