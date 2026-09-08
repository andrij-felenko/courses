#pragma once
#include <cstdint>

namespace boost {

template <typename EnPin, typename LoadGate, typename AdcReader, typename Logger>
class BoostSupervisor {
public:
    struct Config {
        uint32_t maxInductorCurrentMa{1800};
        uint32_t maxOutputVoltageMv{28500}; // Поріг OVP
        float    dividerRatio{11.0f};
        float    efficiency{0.88f};
    };

    explicit BoostSupervisor(EnPin en, LoadGate gate, AdcReader adc, Logger log, Config cfg = {})
        : m_en(en), m_gate(gate), m_adc(adc), m_log(log), m_cfg(cfg) {
        m_gate.disable();
        m_en.disable();
    }

    void powerOn() {
        m_en.enable();
        // Пауза виходу на режим ШІМ
        m_gate.enable();
        m_enabled = true;
        m_log.log("MT3608: Підвищувач запущено, навантаження підключено");
    }

    void powerOff() {
        m_gate.disable();
        m_en.disable();
        m_enabled = false;
        m_log.log("MT3608: Навантаження відключено (0 В), перетворювач у сні");
    }

    void update(uint32_t vinMv, uint32_t iLoadMa) {
        if (!m_enabled) return;

        uint32_t voutMv = static_cast<uint32_t>(m_adc.readPinMv() * m_cfg.dividerRatio);

        // Захист OVP
        if (voutMv > m_cfg.maxOutputVoltageMv) {
            powerOff();
            m_log.error("MT3608: Аварія OVP! Перенапруга на виході!");
            return;
        }

        // Оцінка струму дроселя
        if (voutMv > vinMv && vinMv > 0) {
            float d = 1.0f - (static_cast<float>(vinMv) / static_cast<float>(voutMv));
            float iInEst = static_cast<float>(iLoadMa) / ((1.0f - d) * m_cfg.efficiency);

            if (iInEst > m_cfg.maxInductorCurrentMa) {
                m_log.warn("MT3608: Струм індуктивності перевищує безпечну межу 1.8 А!");
            }
        }
    }

private:
    EnPin     m_en;
    LoadGate  m_gate;
    AdcReader m_adc;
    Logger    m_log;
    Config    m_cfg;
    bool      m_enabled{false};
};

} // namespace boost
