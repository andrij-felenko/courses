// board.hpp — контракт заліза портативного калібратора у вигляді концепту.
//
// Автомат станів параметризується платою, а не успадковується від
// абстрактного інтерфейсу: віртуальних викликів у гарячому шляху немає,
// а невідповідність контракту ловиться компілятором на місці підстановки,
// а не компоновником наприкінці збирання.
#pragma once

#include <concepts>
#include <cstdint>

namespace device {

template <class T>
concept Board = requires(T& b, std::uint8_t percent, std::uint8_t item,
                         std::int16_t offset, bool flag, const char* msg) {
    // Дисплей
    { b.setBacklight(percent) } -> std::same_as<void>;
    { b.drawMenu(item) } -> std::same_as<void>;
    { b.drawSettings(percent, offset, flag) } -> std::same_as<void>;
    { b.showMeasurement(offset) } -> std::same_as<void>;
    { b.showAbout() } -> std::same_as<void>;
    { b.showFault(percent) } -> std::same_as<void>;

    // Енергонезалежна пам'ять
    { b.saveSettings(percent, offset) } -> std::same_as<void>;

    // АЦП і калібрувальний генератор
    { b.startCalibration() } -> std::same_as<void>;
    { b.stopCalibration() } -> std::same_as<std::int16_t>; // виміряне зміщення нуля

    // Живлення
    { b.enterLowPower() } -> std::same_as<void>;
    { b.exitLowPower() } -> std::same_as<void>;

    // Службовий друк для спостереження за порядком дій
    { b.trace(msg) } -> std::same_as<void>;
};

} // namespace device
