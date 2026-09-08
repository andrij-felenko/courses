#pragma once
#include <cstdint>
#include <string_view>

/**
 * Ідіоматичний C++ супервізор ізольованого домену живлення на B0505S.
 */
namespace isolated {

enum class Status {
    PoweredDown,
    Starting,
    Healthy,
    FaultNoHeartbeat
};

template <typename PowerSwitch, typename DummyLoad, typename PulseSource, typename Logger>
class IsolatedPowerDomain {
public:
    struct Config {
        uint32_t heartbeatTimeoutMs{60}; // Таймаут імпульсів оптопари
        uint32_t startupDelayMs{25};     // Час виходу генератора Ройєра на режим
    };

    explicit IsolatedPowerDomain(PowerSwitch pwr, DummyLoad dummy, PulseSource pulse, Logger log, Config cfg = {})
        : m_pwr(pwr), m_dummy(dummy), m_pulse(pulse), m_log(log), m_cfg(cfg) {
        m_pwr.disable();
        m_dummy.enable(); // Завжди тримаємо баласт увімкненим перед подачею живлення
    }

    void powerOn() {
        m_dummy.enable();
        m_pwr.enable();
        m_status = Status::Starting;
        m_log.log("B0505S: Первинне живлення подано, баласт 220 Ом активний");
    }

    void powerOff() {
        m_pwr.disable();
        m_dummy.enable();
        m_status = Status::PoweredDown;
        m_log.log("B0505S: Домен знеструмлено");
    }

    void update(uint32_t currentMs) {
        if (m_status == Status::PoweredDown) return;

        if (m_pulse.hasRecentPulse(m_cfg.heartbeatTimeoutMs)) {
            m_status = Status::Healthy;
        } else {
            m_status = Status::FaultNoHeartbeat;
            m_dummy.enable(); // Страховка від перенапруги
            m_log.warn("B0505S: Втрачено пульс вторинного домену!");
        }
    }

    void onPeripheralStateChange(bool peripheralIsActive) {
        if (m_status != Status::Healthy) {
            m_dummy.enable();
            return;
        }

        if (peripheralIsActive) {
            m_dummy.disable(); // Економія струму, коли працює трансивер
        } else {
            m_dummy.enable();  // Захист від закидання 7 В при холостому ході
        }
    }

    [[nodiscard]] bool isHealthy() const noexcept {
        return m_status == Status::Healthy;
    }

    [[nodiscard]] Status status() const noexcept {
        return m_status;
    }

private:
    PowerSwitch m_pwr;
    DummyLoad   m_dummy;
    PulseSource m_pulse;
    Logger      m_log;
    Config      m_cfg;
    Status      m_status{Status::PoweredDown};
};

} // namespace isolated
