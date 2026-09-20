/**
 * @file EnablingPedal.hpp
 * @brief Клас інтерфейсу для 3-позиційної педалі дозволу («мертвої руки») відповідно до ISO 12100.
 */

#ifndef ENABLING_PEDAL_HPP
#define ENABLING_PEDAL_HPP

#include <cstdint>
#include <functional>
#include <string_view>

enum class SafetyState {
    Released,   ///< Положення 1: Вимкнено (відпущено)
    Enabled,    ///< Положення 2: Дозвіл роботи (робоче затискання)
    Panic,      ///< Положення 3: Панічна зупинка (перетиснуто до упору)
    Fault       ///< Аварія: розсинхронізація каналів, КЗ або заклинювання
};

enum class LedIndicator {
    Off,        ///< Індикація вимкнена (стан спокою)
    Green,      ///< Зелений: Дозвіл роботи активний
    RedBlinking,///< Червоний миготливий: Паніка або Аварія
    Yellow      ///< Жовтий: Очікування скидання (Reset)
};

struct PedalConfig {
    std::uint32_t debounceMs{20};           ///< Таймаут фільтрації брязкоту (мс)
    std::uint32_t discrepancyTimeoutMs{100};///< Максимальний часовий розсув осей (мс)
    std::uint32_t maxStuckTimeMs{30000};    ///< Граничний час безперервного затискання педалі (мс)
};

class EnablingPedal {
public:
    using StateCallback = std::function<void(SafetyState)>;
    using FaultCallback = std::function<void(std::string_view)>;

    explicit EnablingPedal(const PedalConfig& config = {});

    void update(bool channelA, bool channelB, std::uint32_t currentTimeMs);

    void reset();

    void setOnStateChanged(StateCallback callback);
    void setOnFault(FaultCallback callback);

    [[nodiscard]] SafetyState getState() const noexcept { return m_state; }
    [[nodiscard]] LedIndicator getLedStatus() const noexcept { return m_ledStatus; }
    [[nodiscard]] static std::string_view stateToString(SafetyState state) noexcept;

private:
    void debounce(bool rawA, bool rawB, std::uint32_t currentTimeMs);
    void updateFsm(std::uint32_t currentTimeMs);
    void setLed(LedIndicator led) noexcept;
    void triggerFault(std::string_view reason);

    PedalConfig m_config;
    SafetyState m_state{SafetyState::Released};
    LedIndicator m_ledStatus{LedIndicator::Off};

    bool m_debouncedA{false};
    bool m_debouncedB{false};
    bool m_rawLastA{false};
    bool m_rawLastB{false};

    std::uint32_t m_lastChangeMsA{0};
    std::uint32_t m_lastChangeMsB{0};

    std::uint32_t m_discrepancyStartMs{0};
    bool m_discrepancyActive{false};

    std::uint32_t m_enabledStartMs{0};
    bool m_requiresReset{false};

    StateCallback m_onStateChanged;
    FaultCallback m_onFault;
};

#endif // ENABLING_PEDAL_HPP
