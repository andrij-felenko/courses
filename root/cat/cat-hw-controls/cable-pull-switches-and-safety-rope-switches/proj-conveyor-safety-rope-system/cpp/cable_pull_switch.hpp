#ifndef CABLE_PULL_SWITCH_HPP
#define CABLE_PULL_SWITCH_HPP

#include <cstdint>

/**
 * @brief Драйвер двоканального тросового вимикача аварійного зупинення (IEC 60947-5-5).
 * Реалізує дебаунсинг, розсинхрон каналів, FSM станів та ручне скидання.
 */
class CablePullSwitch {
public:
    enum class State {
        Normal,            ///< Нормальний робочий стан (обидва NC-контакти замкнені)
        EmergencyStop,     ///< Аварійне зупинення (обидва NC-контакти розімкнені)
        DiscrepancyFault,  ///< Апаратна аварія (розсинхрон спрацьовування каналів понад таймаут)
        WaitForReset       ///< Очікування підтвердженого ручного скидання після усунення аварії
    };

    struct Config {
        uint32_t debounce_ms{10};          ///< Час фільтрації дребезгу контактів (мс)
        uint32_t max_discrepancy_ms{40};   ///< Максимально допустимий розсинхрон каналів (мс)
    };

    explicit CablePullSwitch(const Config& config = Config{});

    /**
     * @brief Оновлення стану драйвера в циклі опитування.
     * @param now_ms Поточний системний час у мілісекундах.
     * @param raw_nc1 Сирий фізичний рівень лінії NC1 (true = контакт замкнений / 24V).
     * @param raw_nc2 Сирий фізичний рівень лінії NC2 (true = контакт замкнений / 24V).
     */
    void update(uint32_t now_ms, bool raw_nc1, bool raw_nc2);

    /**
     * @brief Спроба ручного скидання засува аварії після відновлення замикання контактів.
     * @return true якщо скидання успішне й FSM повернувся в State::Normal.
     */
    bool reset();

    [[nodiscard]] State getState() const noexcept { return m_state; }
    [[nodiscard]] bool isSafeToOperate() const noexcept { return m_state == State::Normal; }
    [[nodiscard]] bool isEmergencyActive() const noexcept { return m_state == State::EmergencyStop; }
    [[nodiscard]] bool isFaultActive() const noexcept { return m_state == State::DiscrepancyFault; }

private:
    struct ChannelDebounce {
        bool raw_state{true};
        bool stable_state{true};
        uint32_t last_change_ms{0};
    };

    void updateChannelDebounce(ChannelDebounce& channel, bool raw_input, uint32_t now_ms);

    Config m_config;
    State m_state{State::Normal};

    ChannelDebounce m_ch1;
    ChannelDebounce m_ch2;

    bool m_discrepancy_timer_active{false};
    uint32_t m_discrepancy_start_ms{0};
};

#endif // CABLE_PULL_SWITCH_HPP
