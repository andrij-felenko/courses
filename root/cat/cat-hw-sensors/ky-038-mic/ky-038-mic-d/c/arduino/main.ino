const uint8_t SOUND = 2;      // вивід DO давача
const uint8_t LED   = 13;     // вбудований світлодіод
unsigned long lastEvt = 0;    // час останньої зарахованої події
unsigned long count   = 0;    // лічильник гучних подій

void setup() {
    pinMode(SOUND, INPUT);    // DO має підтяжку на платі; лишаємо звичайний вхід
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    int loud = digitalRead(SOUND);   // на більшості плат: HIGH = звук понад поріг
    digitalWrite(LED, loud);         // світимо, поки чуємо гучне

    // рахуємо подію, але не частіше ніж раз на 300 мс — один оплеск не десяток
    if (loud == HIGH && millis() - lastEvt > 300) {
        lastEvt = millis();
        Serial.print("гучно #");
        Serial.println(++count);
    }
    delay(2);   // щільний цикл, щоб не проґавити короткий сплеск звуку
}
