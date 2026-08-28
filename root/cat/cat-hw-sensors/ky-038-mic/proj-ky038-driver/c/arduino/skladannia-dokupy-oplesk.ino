const uint8_t PIN_DO = 2;
const uint8_t PIN_OUT = 13;             // те, чим керуємо (світлодіод/реле)
uint8_t idleLevel;
bool wasSound = false, outputOn = false;
unsigned long lastClap = 0, lastToggle = 0;
uint8_t clapCount = 0;
const unsigned long CLAP_WINDOW = 300;  // придушення торохтіння одного оплеску
const unsigned long DOUBLE_GAP  = 600;  // максимум між двома оплесками пари

void loop() {
    bool isSound = (digitalRead(PIN_DO) != idleLevel);
    unsigned long now = millis();

    if (isSound && !wasSound && now - lastClap > CLAP_WINDOW) {
        // зарахований новий оплеск
        if (now - lastClap < DOUBLE_GAP) clapCount++;   // близько до попереднього — пара
        else                             clapCount = 1; // задалеко — починаємо лічбу спершу
        lastClap = now;

        if (clapCount >= 2) {           // два оплески поспіль — перемикаємось
            outputOn = !outputOn;
            digitalWrite(PIN_OUT, outputOn);
            clapCount = 0;              // скидаємо, щоб потрійний не рахувався ще раз
            Serial.println(outputOn ? "УВІМК" : "ВИМК");
        }
    }
    wasSound = isSound;
}
