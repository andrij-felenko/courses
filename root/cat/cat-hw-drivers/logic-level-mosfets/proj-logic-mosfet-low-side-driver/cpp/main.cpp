#include "MosfetSwitch.hpp"
#include <iostream>
#include <iomanip>

void printSwitchStatus(const std::string& title, const hardware::MosfetSwitch& sw) {
    auto metrics = sw.getMetrics();
    auto specs = sw.getSpecs();

    std::cout << "--- " << title << " ---\n";
    std::cout << "  Модель MOSFET: " << hardware::mosfetModelToString(sw.getModel()) << "\n";
    std::cout << "  Режим керування: " << hardware::controlModeToString(metrics.mode) << "\n";
    std::cout << "  Стан ключа: " << (metrics.isEnabled ? "ВІДКРИТИЙ (ON)" : "ЗАКРИТИЙ (OFF)") << "\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "  Робочий цикл (Duty Cycle): " << metrics.currentDutyCyclePercent << " %\n";
    std::cout << "  Струм навантаження: " << metrics.estimatedCurrentAmpere << " А\n";
    std::cout << "  Теплові втрати на ключі: " << metrics.estimatedPowerLossWatts << " Вт (Макс: " << specs.maxPowerDissipationW << " Вт)\n";
    std::cout << "  Лічильник комутацій: " << metrics.switchCounter << "\n";
    std::cout << "  Статус аварій: " << hardware::switchFaultToString(metrics.lastFault) << "\n";
    std::cout << "--------------------------------------------------------\n\n";
}

int main() {
    std::cout << "========================================================\n";
    std::cout << "  Керування MOSFET логічного рівня (IRLZ44N / FDD8447L)  \n";
    std::cout << "========================================================\n\n";

    // 1. Налаштування параметрів виводу МК та ШІМ для силового ключа IRLZ44N
    hardware::PinConfig pinCfg;
    pinCfg.gpioPin = 5;
    pinCfg.pwmChannel = 1;
    pinCfg.isPwmSupported = true;
    pinCfg.gateResistorOhms = 100; // Резистор затвора R_G = 100 Ом для захисту GPIO МК від струмових сплесків перезаряду C_iss

    hardware::PwmConfig pwmCfg;
    pwmCfg.frequencyHz = 10000;       // Частота ШІМ 10 кГц (для плавного керування мотором або нагрівачем)
    pwmCfg.minDutyPercent = 0.0f;
    pwmCfg.maxDutyPercent = 100.0f;
    pwmCfg.maxSafeDutyPercent = 90.0f; // Захисне обмеження максимального робочого циклу (90%)
    pwmCfg.rampStepPercent = 5.0f;     // Крок зміни робочого циклу 5%

    // 2. Створення екземпляра силового ключа
    hardware::MosfetSwitch gateSwitch(hardware::MosfetModel::IRLZ44N, pinCfg, pwmCfg);

    // 3. Безпечна ініціалізація периферії (притиснення затвора pull-down до GND)
    std::cout << "1. Виконання безпечної ініціалізації периферії МК...\n";
    if (!gateSwitch.initialize()) {
        std::cerr << "Помилка ініціалізації ключа MOSFET!\n";
        return 1;
    }
    printSwitchStatus("Початковий стан після ініціалізації (Pull-Down)", gateSwitch);

    // 4. Демонстрація дискретного керування GPIO (Turn ON / Turn OFF)
    std::cout << "2. Демонстрація дискретного керування силовим навантаженням (GPIO)...\n";
    if (gateSwitch.turnOn()) {
        gateSwitch.updateLoadEstimates(10.0f, 3.3f); // Струм навантаження 10A при V_GS = 3.3V
        printSwitchStatus("Дискретне ввімкнення (100% Duty / HIGH)", gateSwitch);
    }

    std::cout << "Вимкнення силового ключа...\n";
    gateSwitch.turnOff();
    printSwitchStatus("Дискретне вимкнення (LOW / GND)", gateSwitch);

    // 5. Демонстрація плавної регуляції потужності через ШІМ (Smooth Ramp)
    std::cout << "3. Плавна регуляція потужності навантаження через апаратний ШІМ (Ramp Up)...\n";
    if (gateSwitch.smoothRampTo(75.0f, 10)) {
        gateSwitch.updateLoadEstimates(12.0f, 3.3f);
        printSwitchStatus("Плавне наростання потужності до 75% Duty", gateSwitch);
    }

    // 6. Перевірка роботи захисного обмеження робочого циклу (maxSafeDutyPercent)
    std::cout << "4. Тестування спроби встановлення робочого циклу вище безпечного ліміту (95% > 90%)...\n";
    gateSwitch.setDutyCycle(95.0f); // Налаштовано обмеження maxSafeDutyPercent = 90.0%
    gateSwitch.updateLoadEstimates(15.0f, 3.3f);
    printSwitchStatus("Результат обмеження Duty Cycle до безпечних 90%", gateSwitch);

    // 7. Моніторинг теплового навантаження та симуляція перевищення допустимої потужності
    std::cout << "5. Симуляція перевищення струму навантаження та розрахункового перегріву ключа...\n";
    gateSwitch.updateLoadEstimates(25.0f, 3.3f); // Струм 25А викликає P_loss = I^2 * Rds(on) > maxPowerDissipationW
    printSwitchStatus("Автоматичне аварійне відключення при перегріві", gateSwitch);

    // 8. Відновлення після аварії та робота з іншою моделлю MOSFET (FDD8447L)
    std::cout << "6. Скидання аварійного стану та ініціалізація SMD-ключеві FDD8447L...\n";
    gateSwitch.clearFault();

    hardware::MosfetSwitch smdSwitch(hardware::MosfetModel::FDD8447L, pinCfg, pwmCfg);
    smdSwitch.initialize();
    smdSwitch.setDutyCycle(50.0f);
    smdSwitch.updateLoadEstimates(8.0f, 5.0f); // V_GS = 5.0В від мікроконтролера з 5V логікою
    printSwitchStatus("Штатний режим роботи транзистора FDD8447L (50% Duty, Vgs=5V)", smdSwitch);

    // 9. Ручне аварійне відключення (Emergency Stop)
    std::cout << "7. Тестування кнопкового екстреного аварійного відключення (Emergency Shutdown)...\n";
    smdSwitch.emergencyShutdown(hardware::SwitchFault::EmergencyStopTriggered);
    printSwitchStatus("Екстрене зупинення за зовнішньою командою", smdSwitch);

    std::cout << "Демонстрацію роботи силових MOSFET-ключів логічного рівня завершено успішно.\n";
    return 0;
}
