/**
 * @file pendant_driver.hpp
 * @brief Оголошення класу PendantDriver для управління промисловим підвісним пультом.
 */

#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <functional>

namespace IndustrialPendant {

/**
 * @brief Перелік можливих станів кнопок та входів пульта.
 */
enum class ButtonState : uint8_t {
    Released = 0,
    Pressed = 1
};

/**
 * @brief Системні стани пульта та захисного контуру.
 */
enum class SystemStatus : uint8_t {
    Normal = 0,
    EstopTriggered = 1, // Аварійна зупинка (розмикання NC ланцюга або обрив)
    Fault = 2
};

/**
 * @brief Структура для зберігання поточного стану всіх органів керування пульта.
 */
struct PendantState {
    ButtonState up{ButtonState::Released};
    ButtonState down{ButtonState::Released};
    ButtonState left{ButtonState::Released};
    ButtonState right{ButtonState::Released};
    ButtonState start{ButtonState::Released};
    ButtonState estop{ButtonState::Released}; // NC контакт: Pressed = замкнено (безпечно), Released/Open = аварія
    SystemStatus status{SystemStatus::Normal};
};

/**
 * @brief Клас драйвера підвісного пульта з антибрязканням та моніторингом E-Stop.
 */
class PendantDriver {
public:
    using DebounceTime = std::chrono::milliseconds;

    explicit PendantDriver(DebounceTime debounceInterval = DebounceTime(20));
    ~PendantDriver() = default;

    // Заборона копіювання для уникнення дублювання апаратного доступу
    PendantDriver(const PendantDriver&) = delete;
    PendantDriver& operator=(const PendantDriver&) = delete;
    PendantDriver(PendantDriver&&) noexcept = default;
    PendantDriver& operator=(PendantDriver&&) noexcept = default;

    /**
     * @brief Оновлює стан пульта за сирими вхідними сигналами з урахуванням антибрязкання та перевірки E-Stop.
     * @param rawUp Сирий стан кнопки "Вгору"
     * @param rawDown Сирий стан кнопки "Вниз"
     * @param rawLeft Сирий стан кнопки "Вліво"
     * @param rawRight Сирий стан кнопки "Вправо"
     * @param rawStart Сирий стан кнопки "Пуск"
     * @param rawEstop Сирий стан лінії аварійної зупинки (NC: true - замкнено/норма, false - розімкнено/обрив)
     */
    void update(bool rawUp, bool rawDown, bool rawLeft, bool rawRight, bool rawStart, bool rawEstop);

    /**
     * @brief Повертає поточний фільтрований стан пульта.
     */
    [[nodiscard]] PendantState getState() const noexcept;

    /**
     * @brief Пакує поточний стан телеметрії у фрейм RS-485 з розрахунком CRC-16.
     * @param buffer Буфер для вихідного кадру
     * @return Кількість записаних байтів у фрейм
     */
    [[nodiscard]] size_t serializeFrame(std::array<uint8_t, 16>& buffer) const noexcept;

    /**
     * @brief Перевіряє, чи перебуває система в аварійному стані (E-Stop).
     */
    [[nodiscard]] bool isEstopActive() const noexcept;

private:
    DebounceTime debounce_interval_;
    PendantState current_state_;

    // Структура для відстеження часу зміни сирого стану для антибрязкання
    struct DebounceEntry {
        bool stable_state{false};
        bool last_raw_state{false};
        std::chrono::steady_clock::time_point last_change_time{std::chrono::steady_clock::now()};
    };

    DebounceEntry db_up_;
    DebounceEntry db_down_;
    DebounceEntry db_left_;
    DebounceEntry db_right_;
    DebounceEntry db_start_;
    DebounceEntry db_estop_;

    bool filterButton(DebounceEntry& entry, bool rawInput, std::chrono::steady_clock::time_point now);
    [[nodiscard]] static uint16_t calculateCRC16(const uint8_t* data, size_t length) noexcept;
};

} // namespace IndustrialPendant
