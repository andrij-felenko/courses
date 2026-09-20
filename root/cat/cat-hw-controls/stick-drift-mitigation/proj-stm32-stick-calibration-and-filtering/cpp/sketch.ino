#include "JoystickCalibration.h"

// Приклади аналогових пінів АЦП
const int PIN_JOYSTICK_X = A0;
const int PIN_JOYSTICK_Y = A1;
const int PIN_CALIB_BTN  = 2;

JoystickCalibration joystick;
JoystickConfig configProfile;

unsigned long lastLogTime = 0;

void setup() {
    Serial.begin(115200);
    pinMode(PIN_CALIB_BTN, INPUT_PULLUP);

    Serial.println(F("--- Запуск драйвера обробки джойстика з калібруванням ---"));

    // Базова конфігурація за замовчуванням (12-бітний АЦП 0..4095)
    configProfile.center_x = 2048;
    configProfile.center_y = 2048;
    configProfile.min_x = 100;
    configProfile.max_x = 4000;
    configProfile.min_y = 100;
    configProfile.max_y = 4000;
    configProfile.deadzone_radial = 0.10f; // 10% Scaled Radial Deadzone
    configProfile.deadzone_type = static_cast<uint8_t>(DeadzoneType::ScaledRadial);

    joystick.updateConfigCRC(configProfile);

    // Ініціалізація модуля
    JoystickError err = joystick.begin(configProfile);
    if (err != JoystickError::OK) {
        Serial.println(F("ПОМИЛКА: Некоректний профіль конфігурації NVM!"));
    } else {
        Serial.println(F("УСПІХ: Конфігураційний профіль CRC16 перевірено й застосовано."));
    }
}

void loop() {
    // Зчитування сирих відліків АЦП
    int16_t raw_x = analogRead(PIN_JOYSTICK_X);
    int16_t raw_y = analogRead(PIN_JOYSTICK_Y);

    // Обробка джойстика (компенсація нуля, нормалізація [-1.0 .. +1.0], мертва зона)
    NormalizedPoint point = joystick.process(raw_x, raw_y);

    // Перевірка натискання кнопки калібрування (неблокуюче утримання)
    static bool prevBtnState = HIGH;
    bool currBtnState = digitalRead(PIN_CALIB_BTN);

    if (prevBtnState == HIGH && currBtnState == LOW) {
        if (!joystick.isCalibrating()) {
            Serial.println(F("Старт автокалібрування нейтралі (зачекайте 2 секунди)..."));
            joystick.startNeutralCalibration();
        }
    }
    prevBtnState = currBtnState;

    // Автоматичне завершення калібрування нейтралі після збору відліків
    static unsigned long calibStartTime = 0;
    if (joystick.isCalibrating()) {
        if (calibStartTime == 0) calibStartTime = millis();
        if (millis() - calibStartTime > 2000) {
            joystick.finishNeutralCalibration();
            calibStartTime = 0;
            Serial.println(F("Автокалібрування нейтралі успішно завершено!"));
            Serial.print(F("Новий центр X: "));
            Serial.print(joystick.getConfig().center_x);
            Serial.print(F(" | Y: "));
            Serial.println(joystick.getConfig().center_y);
        }
    }

    // Вивід результатів у послідовний порт раз на 200 мс
    if (millis() - lastLogTime > 200) {
        lastLogTime = millis();

        float magnitude = sqrt(point.x * point.x + point.y * point.y);

        Serial.print(F("Raw: ["));
        Serial.print(raw_x);
        Serial.print(F(", "));
        Serial.print(raw_y);
        Serial.print(F("] -> Norm: ["));
        Serial.print(point.x, 3);
        Serial.print(F(", "));
        Serial.print(point.y, 3);
        Serial.print(F("] | Mag: "));
        Serial.println(magnitude, 3);
    }
}
