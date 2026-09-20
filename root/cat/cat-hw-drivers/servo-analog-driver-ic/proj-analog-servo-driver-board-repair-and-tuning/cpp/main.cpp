#include "ServoController.hpp"
#include <iostream>
#include <iomanip>
#include <vector>

void printHeader(const std::string& title) {
    std::cout << "\n==================================================\n";
    std::cout << "  " << title << "\n";
    std::cout << "==================================================\n";
}

int main() {
    using namespace servo;

    printHeader("Ініціалізація та налаштування драйвера AA5188");

    // Створення об'єкта контролера для аналогового підсилювача AA5188
    ServoController aa5188Controller(ServoChipType::AA5188);

    // Конфігурація стандартних часових параметрів імпульсу для RC-серво (1000–2000 мкс, 50 Гц)
    PulseConfig pulseConfig{
        .minPulseUs = 1000,
        .maxPulseUs = 2000,
        .centerPulseUs = 1500,
        .framePeriodUs = 20000
    };

    // Зона нечутливості 4 мкс для AA5188
    DeadbandConfig deadbandConfig{
        .deadbandUs = 4,
        .enabled = true
    };

    if (aa5188Controller.configure(pulseConfig, deadbandConfig)) {
        std::cout << "[ОК] Конфігурація AA5188 успішно застосована.\n";
    } else {
        std::cerr << "[ПОМИЛКА] Помилка налаштування параметрів імпульсів.\n";
        return 1;
    }

    // Частота тактування ШІМ-таймера мікроконтролера (наприклад, 1 МГц -> 1 тік = 1 мкс)
    constexpr uint32_t timerClockHz = 1000000;

    printHeader("Покрокове позиціонування (0° -> 180°)");
    const std::vector<float> testAngles = {0.0f, 45.0f, 90.0f, 135.0f, 180.0f};

    std::cout << std::fixed << std::setprecision(2);
    for (float angle : testAngles) {
        uint16_t pulseUs = aa5188Controller.setTargetAngle(angle);
        TimerTiming timing = aa5188Controller.calculateTimerTiming(timerClockHz);

        std::cout << "Цільовий кут: " << std::setw(6) << angle << "° | "
                  << "Тривалість: " << std::setw(4) << pulseUs << " мкс | "
                  << "Заповнення: " << std::setw(5) << timing.dutyCyclePercent << "% | "
                  << "Тіки таймера: " << timing.timerTicks << "\n";
    }

    printHeader("Тестування фільтрації зони нечутливості (Deadband Filter)");
    std::cout << "Встановлюємо початкову позицію 90.0° (1500 мкс)...\n";
    aa5188Controller.setTargetAngle(90.0f);

    std::cout << "Поточний вихідний імпульс: " << aa5188Controller.getCurrentPulseUs() << " мкс\n\n";

    // Симуляція дрібних шумових флуктуацій сигналу керування або потенціометра зворотного зв'язку
    const std::vector<uint16_t> noiseSequence = {
        1501, // +1 мкс (в межах deadband 4 мкс)
        1503, // +3 мкс (в межах deadband від початкового 1500 мкс)
        1502, // +2 мкс (в межах deadband)
        1508, // +8 мкс (ПЕРЕВИЩУЄ deadband, має оновити позицію!)
        1509, // +1 мкс від 1508 (в межах deadband, має відфільтруватися)
        1506  // -2 мкс від 1508 (в межах deadband, має відфільтруватися)
    };

    for (uint16_t targetUs : noiseSequence) {
        uint16_t outputUs = aa5188Controller.setTargetPulseUs(targetUs);
        bool filtered = aa5188Controller.wasFilteredByDeadband();

        std::cout << "Запит: " << targetUs << " мкс | "
                  << "Вихід: " << outputUs << " мкс | "
                  << "Стан: " << (filtered ? "[ВІДФІЛЬТРОВАНО Deadband]" : "[ОНОВЛЕНО ПОЗИЦІЮ]") << "\n";
    }

    printHeader("Порівняльне налаштування для мікросхеми KC0032");

    ServoController kc0032Controller(ServoChipType::KC0032);
    std::cout << "Типова зона нечутливості KC0032: "
              << kc0032Controller.getDeadbandConfig().deadbandUs << " мкс\n";

    // Демонстрація реагування KC0032 на дрібніший крок (2 мкс)
    kc0032Controller.setTargetPulseUs(1500);
    uint16_t kcOutput1 = kc0032Controller.setTargetPulseUs(1503); // +3 мкс > deadband 2 мкс
    std::cout << "KC0032 крок +3 мкс: Вихід = " << kcOutput1 << " мкс, Відфільтровано = "
              << (kc0032Controller.wasFilteredByDeadband() ? "Так" : "Ні") << "\n";

    printHeader("Підсумок впливу Deadband на стійкість системи");
    std::cout << "1. Відсікання флуктуацій менше порогу deadband блокує непотрібні перемикання H-моста.\n";
    std::cout << "2. Запобігає високочастотним осциляціям ротора та шуму сервоприводу.\n";
    std::cout << "3. Зменшує статичний струм споживання та захищає силові ключі AA5188/KC0032 від перегріву.\n";

    return 0;
}
