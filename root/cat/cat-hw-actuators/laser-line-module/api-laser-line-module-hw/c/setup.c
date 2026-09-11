// Керування імпульсом лазерної лінії з урахуванням часу встановлення випромінювання
const uint8_t LASER_PIN = 5;

void setup() {
    pinMode(LASER_PIN, OUTPUT);
    digitalWrite(LASER_PIN, LOW); // Гарантоване закриття ключа під час старту
}

void strobeLaser(uint16_t exposureUs) {
    // Відкриваємо N-канальний MOSFET подачею високого логічного рівня
    digitalWrite(LASER_PIN, HIGH);

    // Очікуємо стабілізації струму драйвера та виходу на повну потужність (t[on])
    delayMicroseconds(50);

    // Корисний час стабільного підсвічування для експозиції сенсора камери
    delayMicroseconds(exposureUs);

    // Закриваємо транзисторний ключ
    digitalWrite(LASER_PIN, LOW);
}
