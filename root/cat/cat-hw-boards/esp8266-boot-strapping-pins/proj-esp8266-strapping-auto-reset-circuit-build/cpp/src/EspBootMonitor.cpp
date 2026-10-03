#include "EspBootMonitor.hpp"

void EspBootMonitor::begin() {
    // Налаштування внутрішніх підтягувальних резисторів:
    // GPIO0: підтяжка до VCC (PULLUP). Для старту з SPI Flash має бути HIGH.
    pinMode(PIN_GPIO0, INPUT_PULLUP);

    // GPIO2: підтяжка до VCC (PULLUP). Під час завантаження має бути HIGH.
    pinMode(PIN_GPIO2, INPUT_PULLUP);

    // GPIO15: має бути LOW (PULLDOWN). ESP8266 не має внутрішньої підтяжки PULLDOWN
    // на GPIO15, тому використовуємо INPUT та покладаємося на зовнішній резистор 10 кОм до GND.
    pinMode(PIN_GPIO15, INPUT);

    // Фіксація початкового стану strapping-виводів одразу при старті програми
    initialReport.gpio0State  = (digitalRead(PIN_GPIO0) == HIGH);
    initialReport.gpio2State  = (digitalRead(PIN_GPIO2) == HIGH);
    initialReport.gpio15State = (digitalRead(PIN_GPIO15) == HIGH);

    // Зчитування апаратної причини перезавантаження
    initialReport.resetReasonStr = fetchResetReason(initialReport.resetReasonRaw);

    // Обчислення відповідного режиму завантаження
    initialReport.mode = evaluateBootMode(
        initialReport.gpio0State,
        initialReport.gpio2State,
        initialReport.gpio15State
    );

    isInitialized = true;
}

BootStatusReport EspBootMonitor::getInitialBootReport() const {
    return initialReport;
}

BootStatusReport EspBootMonitor::sampleCurrentState() const {
    BootStatusReport report;
    report.gpio0State  = (digitalRead(PIN_GPIO0) == HIGH);
    report.gpio2State  = (digitalRead(PIN_GPIO2) == HIGH);
    report.gpio15State = (digitalRead(PIN_GPIO15) == HIGH);
    report.resetReasonRaw = initialReport.resetReasonRaw;
    report.resetReasonStr = initialReport.resetReasonStr;
    report.mode = evaluateBootMode(report.gpio0State, report.gpio2State, report.gpio15State);
    return report;
}

BootMode EspBootMonitor::evaluateBootMode(bool g0, bool g2, bool g15) {
    // Критерії вибору режиму завантаження ESP8266:
    // 1. Якщо GPIO15 = HIGH (1), чип намагається завантажитися з SD-карти (SDIO).
    if (g15) {
        return BootMode::SdCard;
    }

    // 2. Якщо GPIO2 = LOW (0), комбінація є неприпустимою для штатного запуску.
    if (!g2) {
        return BootMode::Invalid;
    }

    // 3. Якщо GPIO15 = LOW і GPIO2 = HIGH, режим визначається рівнем на GPIO0:
    //    - GPIO0 = HIGH (1) -> SPI Flash (запуск робочої програми)
    //    - GPIO0 = LOW (0)  -> UART Downloader (режим прошивки)
    if (g0) {
        return BootMode::SpiFlash;
    } else {
        return BootMode::UartDownload;
    }
}

const char* EspBootMonitor::bootModeToString(BootMode mode) {
    switch (mode) {
        case BootMode::SpiFlash:
            return "SPI Flash Boot (Штатний запуск програми)";
        case BootMode::UartDownload:
            return "UART Downloader (Режим завантаження прошивки)";
        case BootMode::SdCard:
            return "SD-Card Boot (Режим завантаження з SDIO)";
        case BootMode::Invalid:
        default:
            return "Invalid Config (Некоректний стан виводів)";
    }
}

String EspBootMonitor::fetchResetReason(uint32_t& rawCode) const {
    rst_info* resetInfo = ESP.getResetInfoPtr();
    if (resetInfo != nullptr) {
        rawCode = static_cast<uint32_t>(resetInfo->reason);
        switch (resetInfo->reason) {
            case REASON_DEFAULT_RST:
                return "Power-on (Подача живлення)";
            case REASON_WDT_RST:
                return "Hardware Watchdog Reset (Апаратний WDT)";
            case REASON_EXCEPTION_RST:
                return "Fatal Exception (Фатальний виняток)";
            case REASON_SOFT_WDT_RST:
                return "Software Watchdog Reset (Програмний WDT)";
            case REASON_SOFT_RESTART:
                return "Software Restart (Програмний перезапуск)";
            case REASON_DEEP_SLEEP_AWAKE:
                return "Deep-Sleep Wakeup (Вихід із глибокого сну)";
            case REASON_EXT_SYS_RST:
                return "External System Reset (Апаратна кнопка або DTR/RTS схема)";
            default:
                return ESP.getResetReason();
        }
    }
    rawCode = 0;
    return "Невідома причина (Unknown)";
}

String BootStatusReport::toString() const {
    String output;
    output.reserve(512);

    output += "========== ЗВІТ СТАНУ ЗАВАНТАЖЕННЯ ESP8266 ==========\n";
    output += "Конфігураційні виводи (Strapping Pins):\n";
    output += "  - GPIO0  (Boot Mode Selection) : " + String(gpio0State ? "HIGH (1) [Pull-Up]" : "LOW (0) [GND]") + "\n";
    output += "  - GPIO2  (UART TXD1 / Debug)  : " + String(gpio2State ? "HIGH (1) [Pull-Up]" : "LOW (0) [GND]") + "\n";
    output += "  - GPIO15 (MTDO / SDIO Select)  : " + String(gpio15State ? "HIGH (1) [VCC]" : "LOW (0) [Pull-Down]") + "\n";
    output += "-----------------------------------------------------\n";
    output += "Визначений режим завантаження: " + String(EspBootMonitor::bootModeToString(mode)) + "\n";
    output += "Причина скидання (Reset Reason): " + resetReasonStr + " (код: " + String(resetReasonRaw) + ")\n";
    output += "Аналіз авто-скидання (DTR/RTS транзисторний ланцюг):\n";
    if (mode == BootMode::UartDownload) {
        output += "  -> Виявлено режим прошивки (GPIO0=LOW). Сигнал DTR притягнув GPIO0 до GND,\n";
        output += "     а сигнал RTS сформував імпульс скидання на лінії RST.\n";
    } else if (mode == BootMode::SpiFlash) {
        output += "  -> Виявлено штатний запуск (GPIO0=HIGH, GPIO15=LOW). Транзистори DTR/RTS\n";
        output += "     відкриті або перебувають у стані спокою (DTR=0, RTS=0).\n";
    } else {
        output += "  -> Нестандартна конфігурація. Перевірте зовнішні підтягувальні резистори.\n";
    }
    output += "=====================================================\n";

    return output;
}
