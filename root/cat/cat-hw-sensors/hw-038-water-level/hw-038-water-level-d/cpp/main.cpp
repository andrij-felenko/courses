#define WATER_POWER_PIN  7    // цифрова ніжка живить давач (+ HW-038)
#define WATER_SIGNAL_PIN A0   // аналоговий вхід ← S (OUT) давача

void setup() {
    Serial.begin(9600);
    pinMode(WATER_POWER_PIN, OUTPUT);
    digitalWrite(WATER_POWER_PIN, LOW);   // за замовчуванням давач знеструмлений
}

int readWaterLevel() {
    digitalWrite(WATER_POWER_PIN, HIGH);  // подали живлення на гребінку
    delay(10);                            // ~10 мс, щоб сигнал усталився
    int value = analogRead(WATER_SIGNAL_PIN);  // 0..1023 на 10-бітному АЦП
    digitalWrite(WATER_POWER_PIN, LOW);   // одразу знеструмили — менше корозії
    return value;
}

void loop() {
    int level = readWaterLevel();

    // Пороги ПІД СВОЮ воду — визнач їх дослідом, не бери чужі!
    if (level < 50)        Serial.println("сухо");
    else if (level < 400)  Serial.println("трохи води");
    else                   Serial.println("багато води");

    delay(1000);   // раз на секунду досить; давач і так не живимо постійно
}
