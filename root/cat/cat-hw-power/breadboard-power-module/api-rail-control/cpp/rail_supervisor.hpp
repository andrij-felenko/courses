#pragma once
#include <cstdint>

/**
 * Ідіоматичний C++ супервізор шини живлення MB102.
 * 
 * Використовує шаблон проектування RAII для гарантованого переведення
 * ключа навантаження у безпечний стан при ініціалізації або аварії.
 */
namespace power {

enum class State {
    Normal,
    BrownoutWarning,
    CriticalFault
};

template <typename AdcReader, typename LoadSwitch, typename Logger>
class RailSupervisor {
public:
    struct Config {
        uint16_t tripThresholdMv{4650};     // Поріг тривоги (4.65 В)
        uint16_t recoveryThresholdMv{4800}; // Поріг повернення до норми (4.80 В)
        float    dividerRatio{3.0f};        // Коефіцієнт резистивного дільника
        float    emaAlpha{0.25f};           // Вага нового заміру
    };

    explicit RailSupervisor(AdcReader adc, LoadSwitch loadSwitch, Logger logger, Config cfg = {})
        : m_adc(adc), m_loadSwitch(loadSwitch), m_logger(logger), m_cfg(cfg) {
        m_loadSwitch.disable(); // Безпечний початковий стан
    }

    void begin() {
        m_smoothedVoltageMv = readRawMv();
        m_loadSwitch.enable();
        m_logger.log("RailSupervisor: шина активна, навантаження підключено");
    }

    void update() {
        uint16_t currentMv = readRawMv();
        m_smoothedVoltageMv = (m_cfg.emaAlpha * currentMv) + ((1.0f - m_cfg.emaAlpha) * m_smoothedVoltageMv);
        uint16_t v = static_cast<uint16_t>(m_smoothedVoltageMv);

        switch (m_state) {
            case State::Normal:
                if (v < m_cfg.tripThresholdMv) {
                    m_state = State::BrownoutWarning;
                    m_loadSwitch.disable();
                    m_logger.warn("Brown-out! Навантаження аварійно відключено");
                }
                break;

            case State::BrownoutWarning:
                if (v >= m_cfg.recoveryThresholdMv) {
                    m_state = State::Normal;
                    m_loadSwitch.enable();
                    m_logger.log("Напруга шини відновилася, навантаження знову підключено");
                }
                break;

            default:
                break;
        }
    }

    [[nodiscard]] uint16_t voltageMv() const noexcept {
        return static_cast<uint16_t>(m_smoothedVoltageMv);
    }

    [[nodiscard]] State state() const noexcept {
        return m_state;
    }

    [[nodiscard]] bool isStable() const noexcept {
        return m_state == State::Normal;
    }

private:
    uint16_t readRawMv() {
        float pinMv = m_adc.readPinMv();
        return static_cast<uint16_t>(pinMv * m_cfg.dividerRatio);
    }

    AdcReader   m_adc;
    LoadSwitch  m_loadSwitch;
    Logger      m_logger;
    Config      m_cfg;
    State       m_state{State::Normal};
    float       m_smoothedVoltageMv{5000.0f};
};

} // namespace power
