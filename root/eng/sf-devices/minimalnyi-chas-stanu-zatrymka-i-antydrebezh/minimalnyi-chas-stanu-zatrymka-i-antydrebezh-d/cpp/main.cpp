#include <cstdint>
#include <chrono>
#include <algorithm>

namespace embedded {

using namespace std::chrono_literals;

/* --- 1. Типобезпечний клас несиметричної кваліфікації сигналу --- */
template <typename Duration = std::chrono::milliseconds>
class TimeQualifier {
public:
    constexpr TimeQualifier(Duration tripTime, Duration recoverTime, bool initialValue = false) noexcept
        : m_tripTime(tripTime)
        , m_recoverTime(recoverTime)
        , m_lastSample(initialValue)
        , m_debouncedState(initialValue)
        , m_lastChangeTime(Duration::zero()) {}

    bool update(bool rawInput, Duration now) noexcept {
        if (rawInput != m_lastSample) {
            m_lastSample = rawInput;
            m_lastChangeTime = now;
        }

        if (rawInput != m_debouncedState) {
            const Duration requiredHold = rawInput ? m_tripTime : m_recoverTime;
            if ((now - m_lastChangeTime) >= requiredHold) {
                m_debouncedState = rawInput;
            }
        }

        return m_debouncedState;
    }

    [[nodiscard]] constexpr bool get() const noexcept { return m_debouncedState; }

private:
    Duration m_tripTime;
    Duration m_recoverTime;
    bool m_lastSample;
    bool m_debouncedState;
    Duration m_lastChangeTime;
};

/* --- 2. Вартовий інваріанту Minimum Dwell Time --- */
template <typename Duration = std::chrono::milliseconds>
class DwellGuard {
public:
    constexpr explicit DwellGuard(Duration initialDwell, Duration now = Duration::zero()) noexcept
        : m_entryTime(now)
        , m_minDuration(initialDwell) {}

    void reset(Duration duration, Duration now) noexcept {
        m_entryTime = now;
        m_minDuration = duration;
    }

    [[nodiscard]] bool isExpired(Duration now) const noexcept {
        return (now - m_entryTime) >= m_minDuration;
    }

    [[nodiscard]] Duration elapsed(Duration now) const noexcept {
        return now - m_entryTime;
    }

private:
    Duration m_entryTime;
    Duration m_minDuration;
};

/* --- 3. Скінченний автомат компресора --- */
enum class CompressorState : uint8_t {
    Off,
    Run,
    Fault
};

class CompressorController {
public:
    using Milliseconds = std::chrono::milliseconds;

    static constexpr auto MinRunTime       = 60s;
    static constexpr auto MinOffTime       = 180s;
    static constexpr auto TempOnDebounce   = 2000ms;
    static constexpr auto TempOffDebounce  = 4000ms;
    static constexpr auto OilFaultTripTime = 400ms;
    static constexpr auto OilFaultRecovery = 10s;

    explicit CompressorController(Milliseconds now) noexcept
        : m_state(CompressorState::Off)
        , m_dwell(MinOffTime, now)
        , m_tempDemandQual(TempOnDebounce, TempOffDebounce, false)
        , m_oilFaultQual(OilFaultTripTime, OilFaultRecovery, false)
        , m_relayActive(false) {}

    void step(bool rawTempDemand, bool rawOilPressureFault, bool emergencyStop, Milliseconds now) noexcept {
        const bool coolingNeeded = m_tempDemandQual.update(rawTempDemand, now);
        const bool oilFault      = m_oilFaultQual.update(rawOilPressureFault, now);

        switch (m_state) {
        case CompressorState::Off:
            m_relayActive = false;
            if (emergencyStop || oilFault) {
                transitionTo(CompressorState::Fault, MinOffTime, now);
            } else if (coolingNeeded && m_dwell.isExpired(now)) {
                transitionTo(CompressorState::Run, MinRunTime, now);
            }
            break;

        case CompressorState::Run:
            m_relayActive = true;
            if (emergencyStop || oilFault) {
                // Аварійний обхід миттєво розмикає реле
                transitionTo(CompressorState::Fault, MinOffTime, now);
            } else if (!coolingNeeded && m_dwell.isExpired(now)) {
                transitionTo(CompressorState::Off, MinOffTime, now);
            }
            break;

        case CompressorState::Fault:
            m_relayActive = false;
            if (!emergencyStop && !oilFault && m_dwell.isExpired(now)) {
                transitionTo(CompressorState::Off, MinOffTime, now);
            }
            break;
        }
    }

    [[nodiscard]] constexpr CompressorState state() const noexcept { return m_state; }
    [[nodiscard]] constexpr bool relayCommand() const noexcept { return m_relayActive; }

private:
    void transitionTo(CompressorState nextState, Milliseconds dwellTime, Milliseconds now) noexcept {
        m_state = nextState;
        m_dwell.reset(dwellTime, now);
    }

    CompressorState m_state;
    DwellGuard<Milliseconds> m_dwell;
    TimeQualifier<Milliseconds> m_tempDemandQual;
    TimeQualifier<Milliseconds> m_oilFaultQual;
    bool m_relayActive;
};

} // namespace embedded
