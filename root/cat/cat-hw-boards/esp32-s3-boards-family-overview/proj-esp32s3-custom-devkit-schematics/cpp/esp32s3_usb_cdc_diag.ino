#include <Arduino.h>
#include <esp_system.h>

// Перевірка конфігурації нативного USB CDC у середовищі Arduino IDE
#if !ARDUINO_USB_CDC_ON_BOOT
  #warning "Для роботи нативного USB CDC рекомендується увімкнути 'USB CDC On Boot: Enabled' у меню Tools"
#endif

// Клас для зчитування та детального форматування причини скидання контролера ESP32-S3
class ResetDiagnostics {
public:
    // Повертає текстовий опис причини останнього перезавантаження SoC
    static const char* getReasonString(esp_reset_reason_t reason) {
        switch (reason) {
            case ESP_RST_POWERON:   return "POWER_ON (Звичайне включення живлення)";
            case ESP_RST_EXT:       return "EXTERNAL_PIN (Скидання зовнішньою кнопкою RESET/EN)";
            case ESP_RST_SW:        return "SOFTWARE_RESET (Програмне скидання через esp_restart())";
            case ESP_RST_PANIC:     return "PANIC (Критична помилка виконання / Exception Panic)";
            case ESP_RST_INT_WDT:   return "INT_WDT (Переривання таймера сторожового собаки / Interrupt Watchdog)";
            case ESP_RST_TASK_WDT:  return "TASK_WDT (Сторожовий собака задач / Task Watchdog)";
            case ESP_RST_WDT:       return "OTHER_WDT (Інший сторонній сторожовий таймер)";
            case ESP_RST_DEEPSLEEP: return "DEEP_SLEEP (Вихід із режиму глибокого сну)";
            case ESP_RST_BROWNOUT:  return "BROWNOUT (Падіння напруги живлення / Brownout Reset)";
            case ESP_RST_SDIO:      return "SDIO (Скидання через SDIO-інтерфейс)";
            default:                return "UNKNOWN (Невідома причина скидання)";
        }
    }

    // Зчитує системну причину та виводить повну відлагоджувальну інформацію в CDC-порт
    static void printDiagnosticSummary(Stream& stream) {
        esp_reset_reason_t reason = esp_reset_reason();
        stream.println(F("\n=================================================="));
        stream.println(F("    ESP32-S3 NATIVE USB CDC DIAGNOSTICS LOG       "));
        stream.println(F("=================================================="));
        stream.print(F("Причина перезавантаження SoC : "));
        stream.println(getReasonString(reason));
        stream.print(F("Частота CPU                 : "));
        stream.print(getCpuFrequencyMhz());
        stream.println(F(" MHz"));
        stream.print(F("Вільні ресурси RAM (Heap)   : "));
        stream.print(ESP.getFreeHeap() / 1024);
        stream.println(F(" KB"));
        stream.println(F("--------------------------------------------------"));
        stream.println(F("Введіть 'help' для перегляду доступних команд."));
        stream.println(F("==================================================\n"));
    }
};

// Буфер для зчитування вхідного рядка з USB CDC
String inputBuffer = "";

void setup() {
    // Ініціалізація нативного USB CDC (віртуальний ком-порт)
    Serial.begin(115200);

    // Очікування встановлення віртуального з'єднання з хостом (до 5 секунд)
    uint32_t startTime = millis();
    while (!Serial && (millis() - startTime < 5000)) {
        delay(10);
    }

    // Затримка для стабілізації буфера термінала на боці ПК
    delay(500);

    // Виведення діагностичної інформації про запуск та причину скидання
    ResetDiagnostics::printDiagnosticSummary(Serial);
}

void loop() {
    // Перевірка наявності вхідних даних від USB CDC термінала
    while (Serial.available() > 0) {
        char ch = static_cast<char>(Serial.read());

        // Обробка завершення введення рядка
        if (ch == '\n' || ch == '\r') {
            inputBuffer.trim();
            if (inputBuffer.length() > 0) {
                if (inputBuffer.equalsIgnoreCase("help")) {
                    Serial.println(F("Доступні команди:"));
                    Serial.println(F("  ping   - перевірка зв'язку (повертає pong)"));
                    Serial.println(F("  status - вивести поточний стан RAM і uptime"));
                    Serial.println(F("  reboot - виконати програмне перезавантаження SoC"));
                    Serial.println(F("  help   - показати цю довідку"));
                } else if (inputBuffer.equalsIgnoreCase("ping")) {
                    Serial.println(F("PONG (USB CDC активний і відповідає)"));
                } else if (inputBuffer.equalsIgnoreCase("status")) {
                    Serial.print(F("Uptime: "));
                    Serial.print(millis() / 1000);
                    Serial.println(F(" сек."));
                    Serial.print(F("Free Heap: "));
                    Serial.print(ESP.getFreeHeap());
                    Serial.println(F(" байтів"));
                } else if (inputBuffer.equalsIgnoreCase("reboot")) {
                    Serial.println(F("Ініціалізація програмного перезавантаження ESP32-S3..."));
                    Serial.flush();
                    delay(200);
                    esp_restart();
                } else {
                    Serial.print(F("Невідома команда: '"));
                    Serial.print(inputBuffer);
                    Serial.println(F("'. Введіть 'help'."));
                }
                inputBuffer = "";
            }
        } else {
            // Накопичення символів у буфер
            inputBuffer += ch;
        }
    }
}
