#include "Xpt8871Player.hpp"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

// -----------------------------------------------------------------------------
// Імітація апаратного рівня мікроконтролера (HAL для тестування та демонстрації)
// -----------------------------------------------------------------------------

namespace hal_sim {
    static uint32_t simulatedMillis = 0;
    static uint32_t dmaBusyUntilMillis = 0;
    static bool shutdownPinState = false;

    void log(const char* module, const std::string& message) {
        std::cout << "[" << std::setw(5) << std::setfill('0') << simulatedMillis << " мс] "
                  << "[" << module << "] " << message << "\n";
    }

    void setShutdownPin(bool enable) {
        shutdownPinState = enable;
        if (enable) {
            log("ХАРДВЕР", "Лінія SHDN -> HIGH: увімкнення підсилювача XPT8871");
        } else {
            log("ХАРДВЕР", "Лінія SHDN -> LOW: вимкнення підсилювача (сон, струм < 1 мкА)");
        }
    }

    void transmitDma(std::span<const int16_t> buffer) {
        // При частоті 16 кГц буфер на 128 вибірок транслюється рівно 8 мілісекунд
        constexpr uint32_t transferDurationMs = 8;
        dmaBusyUntilMillis = simulatedMillis + transferDurationMs;
        log("DMA", "Старт передачі блоку DMA (" + std::to_string(buffer.size()) +
                   " вибірок, тривалість " + std::to_string(transferDurationMs) + " мс)");
    }

    bool isDmaBusy() {
        return simulatedMillis < dmaBusyUntilMillis;
    }

    uint32_t getMillis() {
        return simulatedMillis;
    }
}

// Генерація короткого тестового сигналу (синусоїдальний тон)
std::vector<int16_t> generateTone(float frequencyHz, size_t sampleCount, float sampleRate = 16000.0f, int16_t amplitude = 12000) {
    std::vector<int16_t> pcm(sampleCount);
    const float step = 2.0f * 3.1415926535f * frequencyHz / sampleRate;
    for (size_t i = 0; i < sampleCount; ++i) {
        pcm[i] = static_cast<int16_t>(amplitude * std::sin(step * static_cast<float>(i)));
    }
    return pcm;
}

int main() {
    std::cout << "========================================================\n";
    std::cout << "  Демонстрація керування аудіопідсилювачем XPT8871 (C++)\n";
    std::cout << "========================================================\n\n";

    // Налаштування функцій зворотного виклику периферії
    Xpt8871Player::HardwareCallbacks callbacks{
        .setShutdownPin = hal_sim::setShutdownPin,
        .transmitDma = hal_sim::transmitDma,
        .isDmaBusy = hal_sim::isDmaBusy,
        .getMillis = hal_sim::getMillis
    };

    // Налаштування часових інтервалів XPT8871
    Xpt8871Player::Config config{
        .stabilizationDelayMs = 60, // 60 мс для заряду конденсатора BYP (anti-pop)
        .autoSleepDelayMs = 40      // 40 мс простою до автоматичного засинання (для швидкої демо)
    };

    // Створення програвача (RAII керує живленням підсилювача)
    Xpt8871Player player(callbacks, config);

    // Синтез двох звукових сповіщень:
    // 1. Короткий звуковий сигнал підтвердження (Beep, 1000 Гц, 160 вибірок = 10 мс)
    const auto soundBeep = generateTone(1000.0f, 160);
    // 2. Двотоновий сигнал застереження (Alert, 1800 Гц, 256 вибірок = 16 мс)
    const auto soundAlert = generateTone(1800.0f, 256);

    hal_sim::log("ГОЛОВНИЙ", "Постановка сповіщення №1 (Beep) у чергу...");
    player.enqueue(soundBeep, 101);

    // Імітація диспетчера головного циклу мікроконтролера
    // Крок симуляції — 2 мілісекунди на ітерацію
    while (hal_sim::simulatedMillis <= 180) {
        // Оновлення логіки програвача (неблокувальний виклик)
        player.update();

        // Імітація зовнішньої події: під час відтворення першого звуку надходить друге сповіщення
        if (hal_sim::simulatedMillis == 76) {
            hal_sim::log("ГОЛОВНИЙ", "Зовнішня подія: додаємо сповіщення №2 (Alert) у чергу!");
            player.enqueue(soundAlert, 102);
        }

        // Крок часу симуляції
        hal_sim::simulatedMillis += 2;
    }

    std::cout << "\n--- Тест повторного пробудження після сну ---\n";
    hal_sim::log("ГОЛОВНИЙ", "Постановка сповіщення №3 після того, як підсилювач заснув...");
    player.enqueue(soundBeep, 103);

    while (hal_sim::simulatedMillis <= 300) {
        player.update();
        hal_sim::simulatedMillis += 2;
    }

    hal_sim::log("ГОЛОВНИЙ", "Завершення роботи. Деструктор автоматично вимкне підсилювач (RAII).");
    return 0;
}
