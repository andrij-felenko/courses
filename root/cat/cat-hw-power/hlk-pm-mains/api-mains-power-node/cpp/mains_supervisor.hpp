#pragma once
#include <cstdint>
#include <string_view>

/**
 * Ідіоматичний C++ супервізор мережевого джерела живлення HLK-PM.
 * Контролює імпульси оптопари переходу через нуль (Zero-Cross),
 * реалізує протокол «Dying Gasp» (аварійне скидання навантаження та запис стану)
 * у межах 20..30 мс вікна розряду вихідних конденсаторів модуля.
 */
namespace mains {

enum class PowerState {
    Normal,
    OutageDetected,
    DyingGaspCompleted,
    Brownout
};

template <typename RelayDriver, typename RadioDriver, typename StorageDriver, typename Logger>
class MainsSupervisor {
public:
    struct Config {
        uint32_t zeroCrossTimeoutUs{15000};  // Поріг фіксації зникнення 220 В (15 мс)
        uint32_t relayPullInLagUs{6000};     // Механічний час спрацьовування реле (6 мс)
        uint32_t halfCycleUs{10000};         // Напівперіод 50 Гц (10 мс)
    };

    explicit MainsSupervisor(RelayDriver relay, RadioDriver radio, StorageDriver storage, Logger logger, Config cfg = {})
        : m_relay(relay), m_radio(radio), m_storage(storage), m_log(logger), m_cfg(cfg) {}

    // Викликається з обробника переривання оптопари нульової фази
    void onZeroCrossInterrupt(uint32_t timestampUs) noexcept {
        m_lastPulseUs = timestampUs;
        m_acDetected = true;

        if (m_switchScheduled) {
            m_relay.setDelayMicroseconds(m_cfg.halfCycleUs - m_cfg.relayPullInLagUs);
            m_relay.setLevel(m_targetRelayState);
            m_switchScheduled = false;
        }
    }

    // Регулярний цикл опитування (наприклад, у головному таску кожні 1..5 мс)
    void poll(uint32_t currentUs) {
        if (m_state == PowerState::DyingGaspCompleted || m_state == PowerState::Brownout) {
            return;
        }

        if (m_acDetected && (currentUs - m_lastPulseUs) > m_cfg.zeroCrossTimeoutUs) {
            // Мережа 220 В зникла! Починаємо Dying Gasp
            m_state = PowerState::OutageDetected;
            m_log.warn("HLK-PM: Мережу 220 В втрачено! Запуск аварійного протоколу Dying Gasp.");

            executeDyingGasp();
        }
    }

    void requestRelayState(bool turnOn) noexcept {
        m_targetRelayState = turnOn;
        m_switchScheduled = true;
    }

    [[nodiscard]] PowerState state() const noexcept {
        return m_state;
    }

    [[nodiscard]] bool isMainsGood() const noexcept {
        return m_state == PowerState::Normal;
    }

private:
    void executeDyingGasp() {
        // Крок 1: Негайний розрив котушки реле (зняття струму 60..80 мА)
        m_relay.setLevel(false);

        // Крок 2: Зупинка радіо (струм падає на 150+ мА, утримуючи напругу на виході HLK-PM)
        m_radio.powerOff();

        // Крок 3: Аварійний запис критичних лічильників у Flash/EEPROM/NVS
        m_storage.emergencyCommit();

        m_state = PowerState::DyingGaspCompleted;
        m_log.info("HLK-PM: Дані збережено за залишковий час holdup time. Очікування знеструмлення.");
    }

    RelayDriver   m_relay;
    RadioDriver   m_radio;
    StorageDriver m_storage;
    Logger        m_log;
    Config        m_cfg;

    volatile uint32_t m_lastPulseUs{0};
    volatile bool     m_acDetected{false};
    volatile bool     m_switchScheduled{false};
    volatile bool     m_targetRelayState{false};
    PowerState        m_state{PowerState::Normal};
};

} // namespace mains
