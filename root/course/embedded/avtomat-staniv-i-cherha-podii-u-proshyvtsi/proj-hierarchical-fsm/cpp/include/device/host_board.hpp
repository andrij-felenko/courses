// host_board.hpp — хостова плата: кожна дія називає себе, тож порядок
// викликів Entry/Exit під час переходу видно очима. На справжньому приладі
// на її місці стоїть клас із регістрами дисплея, Flash і АЦП — концепт
// Board однаковий для обох.
#pragma once

#include "device/board.hpp"

#include <array>
#include <cstdint>
#include <iostream>
#include <string_view>

namespace device {

class HostBoard {
public:
    void setBacklight(std::uint8_t percent) {
        if (percent == 0) {
            std::cout << "  [LCD ] підсвітку вимкнено\n";
        } else {
            std::cout << "  [LCD ] підсвітка " << +percent << "%\n";
        }
    }

    void drawMenu(std::uint8_t item) {
        const std::string_view name = (item < kMenuNames.size()) ? kMenuNames[item] : "?";
        std::cout << "  [LCD ] головне меню, виділено «" << name << "»\n";
    }

    void drawSettings(std::uint8_t brightness, std::int16_t offset, bool calibrated) {
        std::cout << "  [LCD ] налаштування: яскравість " << +brightness
                  << "%, зміщення " << offset << " ("
                  << (calibrated ? "калібровано" : "заводське") << ")\n";
    }

    void showMeasurement(std::int16_t offset) {
        std::cout << "  [LCD ] вимірювання, поправка нуля " << offset << "\n";
    }

    void showAbout() { std::cout << "  [LCD ] калібратор, прошивка 1.4.0\n"; }

    void showFault(std::uint8_t errorCount) {
        std::cout << "  [LCD ] АВАРІЯ давача, відмов поспіль: " << +errorCount << "\n";
    }

    void saveSettings(std::uint8_t brightness, std::int16_t offset) {
        std::cout << "  [FLASH] збережено: яскравість " << +brightness << "%, зміщення "
                  << offset << "\n";
    }

    void startCalibration() {
        calibRunning_ = true;
        std::cout << "  [ADC ] калібрувальний генератор увімкнено\n";
    }

    std::int16_t stopCalibration() {
        if (!calibRunning_) {
            // Подвійна зупинка означала б, що Exit прийшов двічі — це вада
            // рушія, а не заліза, і мовчати про неї не можна.
            std::cout << "  [ADC ] ПОМИЛКА: зупинка незапущеного генератора\n";
            return 0;
        }
        calibRunning_ = false;
        const std::int16_t measured = calibRaw_;
        std::cout << "  [ADC ] генератор вимкнено, виміряне зміщення " << measured << "\n";
        calibRaw_ = static_cast<std::int16_t>(calibRaw_ + 5); // наступний замір інший
        return measured;
    }

    void enterLowPower() { std::cout << "  [PWR ] режим мікроспоживання\n"; }
    void exitLowPower() { std::cout << "  [PWR ] повне тактування ядра\n"; }

    void trace(const char* msg) { std::cout << "  [    ] " << msg << "\n"; }

private:
    static constexpr std::array<std::string_view, 3> kMenuNames{
        "Вимірювання", "Налаштування", "Про прилад"};

    bool calibRunning_{false};
    std::int16_t calibRaw_{-37};
};

static_assert(Board<HostBoard>, "хостова плата мусить задовольняти концепт Board");

} // namespace device
