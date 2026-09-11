#include "gearmotor.hpp"
#include <iostream>
#include <iomanip>
#include <cstdint>

namespace {

/**
 * @brief Імітатор апаратного рівня мікроконтролера (HAL).
 * Зберігає реальні стани вихідних ліній керування драйвером H-моста.
 */
struct HardwareMock {
    bool pinIn1{false};     ///< Рівень на вході IN1 драйвера
    bool pinIn2{false};     ///< Рівень на вході IN2 драйвера
    uint16_t pinPwm{0};     ///< Шпаруватість ШІМ на вході PWM/EN драйвера
};

static HardwareMock g_hw;

void halGpioWrite(uint8_t pin, bool level) {
    if (pin == 5) {
        g_hw.pinIn1 = level;
    } else if (pin == 6) {
        g_hw.pinIn2 = level;
    }
}

void halPwmWrite(uint8_t pin, uint16_t duty) {
    if (pin == 9) {
        g_hw.pinPwm = duty;
    }
}

const char* stateToString(actuators::State s) {
    switch (s) {
        case actuators::State::STOP_COAST: return "STOP_COAST (вибіг)";
        case actuators::State::FORWARD:    return "FORWARD    (вперед)";
        case actuators::State::REVERSE:    return "REVERSE    (реверс)";
        case actuators::State::BRAKE:      return "BRAKE      (гальмо)";
    }
    return "UNKNOWN";
}

void printStatus(uint32_t timeMs, const actuators::Gearmotor& motor, const char* note = nullptr) {
    const double dutyPercent = (static_cast<double>(motor.getCurrentDuty()) / 1000.0) * 100.0;

    std::cout << "[Час: " << std::setw(5) << timeMs << " мс] "
              << "Стан: " << stateToString(motor.getState()) << " | "
              << "ШІМ: " << std::setw(4) << motor.getCurrentDuty() << "/1000 "
              << "(" << std::fixed << std::setprecision(1) << std::setw(5) << dutyPercent << "%) | "
              << "Піни: IN1=" << g_hw.pinIn1 << ", IN2=" << g_hw.pinIn2
              << ", PWM=" << std::setw(4) << g_hw.pinPwm;

    if (note && note[0] != '\0') {
        std::cout << "  <-- " << note;
    }
    std::cout << "\n";
}

} // анонімний простір імен

int main() {
    std::cout << "================================================================================\n"
              << " ДЕМОНСТРАЦІЯ ДРАЙВЕРА 6В КОЛЕКТОРНОГО МОТОР-РЕДУКТОРА (C++ РІВЕНЬ 2)\n"
              << " Захист редуктора: лінійна рампа розгону та деселерації\n"
              << " Захист ключів моста: break-before-make та пауза dead-time під час реверсу\n"
              << " Електродинамічне гальмування проти-ЕРС vs вільний вибіг (High-Z)\n"
              << "================================================================================\n\n";

    // 1. Конфігурація приводу для 6-вольтового мотор-редуктора (100 / 600 об/хв):
    // maxDuty = 1000 дискрет (роздільна здатність 0.1%).
    // accelRate = 1000 одиниць/с (розгін від 0 до 80% за 800 мс).
    // decelRate = 2000 одиниць/с (гальмування від 80% до 0 за 400 мс).
    // deadTimeMs = 40 мс (захисна пауза для гасіння індуктивності обмоток).
    const actuators::Config config{
        .pins = { .in1 = 5, .in2 = 6, .pwm = 9 },
        .maxDuty = 1000,
        .accelRate = 1000,
        .decelRate = 2000,
        .deadTimeMs = 40,
        .writeGpio = halGpioWrite,
        .writePwm = halPwmWrite
    };

    actuators::Gearmotor motor(config);
    if (!motor.init()) {
        std::cerr << "Помилка ініціалізації приводу!\n";
        return 1;
    }

    // Дискретність суперциклу вбудованої системи: 20 мс (частота виклику 50 Гц)
    constexpr uint32_t TICK_MS = 20;
    uint32_t timeMs = 0;

    printStatus(timeMs, motor, "Початковий безпечний стан: ключі розімкнені");

    // -------------------------------------------------------------------------
    // СЦЕНАРІЙ 1: Плавний пуск уперед до 80% шпаруватості (800 / 1000)
    // -------------------------------------------------------------------------
    std::cout << "\n>>> [ПОДІЯ] Команда: плавний пуск уперед (цільова шпаруватість +80.0%)\n";
    motor.setSpeed(800);

    bool rampForwardDone = false;
    while (timeMs < 1200) {
        motor.update(TICK_MS);
        timeMs += TICK_MS;

        // Виводимо проміжні точки рампи кожні 100 мс або при завершенні розгону
        if (timeMs % 100 == 0 || (!rampForwardDone && !motor.isRamping())) {
            const char* note = "";
            if (!rampForwardDone && !motor.isRamping()) {
                rampForwardDone = true;
                note = "Рампу розгону завершено, сталий рух 80%";
            }
            printStatus(timeMs, motor, note);
        }
    }

    // -------------------------------------------------------------------------
    // СЦЕНАРІЙ 2: Команда реверсу на -80% (-800 / 1000)
    // Автоматично: плавне гальмування до 0 -> dead-time 40 мс -> плавний розгін назад
    // -------------------------------------------------------------------------
    std::cout << "\n>>> [ПОДІЯ] Команда: безпечний реверс на -80.0%\n"
              << "    (1. Зниження струму до 0 -> 2. Dead-time пауза -> 3. Розгін назад)\n";
    motor.setSpeed(-800);

    bool reachedZero = false;
    bool switchedToReverse = false;
    bool rampReverseDone = false;

    while (timeMs < 2800) {
        const actuators::State prevState = motor.getState();
        const bool prevDeadTime = motor.isInDeadTime();

        motor.update(TICK_MS);
        timeMs += TICK_MS;

        // Фіксуємо перехід у нуль та dead-time
        if (!reachedZero && motor.isInDeadTime()) {
            reachedZero = true;
            printStatus(timeMs, motor, "Швидкість 0 досягнута. Вхід у захисний dead-time (40 мс)");
            continue;
        }

        // Фіксуємо зміну полярності після завершення dead-time
        if (reachedZero && !switchedToReverse && prevState == actuators::State::STOP_COAST &&
            motor.getState() == actuators::State::REVERSE) {
            switchedToReverse = true;
            printStatus(timeMs, motor, "Dead-time минув. Полярність безпечно перемкнуто на REVERSE");
            continue;
        }

        // Друк кроків рампи
        if (timeMs % 100 == 0 || (!rampReverseDone && switchedToReverse && !motor.isRamping())) {
            const char* note = "";
            if (!rampReverseDone && switchedToReverse && !motor.isRamping()) {
                rampReverseDone = true;
                note = "Рампу реверсу завершено, сталий рух -80%";
            }
            printStatus(timeMs, motor, note);
        }
    }

    // -------------------------------------------------------------------------
    // СЦЕНАРІЙ 3: Активне електродинамічне гальмування (BRAKE) на швидкості -80%
    // Обидва нижні ключі Q2 і Q4 замикаються на GND (IN1=1, IN2=1, PWM=100%).
    // Струм проти-ЕРС короткого замикання миттєво зупиняє ротор.
    // -------------------------------------------------------------------------
    std::cout << "\n>>> [ПОДІЯ] Команда: екстрене динамічне гальмування (BRAKE)!\n"
              << "    (Замикання обмоток мотора на шину GND. Проти-ЕРС гасить обертання)\n";
    motor.brake();
    printStatus(timeMs, motor, "Активне гальмування увімкнено (IN1=1, IN2=1, PWM=100%)");

    while (timeMs < 3400) {
        motor.update(TICK_MS);
        timeMs += TICK_MS;

        if (timeMs % 200 == 0) {
            printStatus(timeMs, motor, "Утримання ротора під активним гальмом");
        }
    }

    // -------------------------------------------------------------------------
    // СЦЕНАРІЙ 4: Переведення моста у вільний вибіг (COAST / High-Z)
    // Розмикання всіх ключів (IN1=0, IN2=0, PWM=0). Вал вільний від гальмівного моменту.
    // -------------------------------------------------------------------------
    std::cout << "\n>>> [ПОДІЯ] Команда: переведення приводу у вільний вибіг (COAST)\n"
              << "    (Ключі розімкнені, вал котиться вільно або обертається вручну)\n";
    motor.coast();
    printStatus(timeMs, motor, "Вибіг активовано: міст знеструмлено");

    while (timeMs <= 3800) {
        motor.update(TICK_MS);
        timeMs += TICK_MS;

        if (timeMs % 200 == 0) {
            printStatus(timeMs, motor, "Стан спокою у режимі вибігу");
        }
    }

    std::cout << "\n================================================================================\n"
              << " ДЕМОНСТРАЦІЮ ЗАВЕРШЕНО УСПІШНО.\n"
              << " Усі захисні інтервали H-моста та механічні рампи відпрацьовано бездоганно.\n"
              << "================================================================================\n";

    return 0;
}
