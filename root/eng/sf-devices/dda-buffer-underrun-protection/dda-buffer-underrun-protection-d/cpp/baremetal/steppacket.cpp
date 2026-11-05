#include <cstdint>
#include <array>
#include <atomic>

namespace MotionHardware {

struct StepPacket {
    std::uint32_t stepIntervalTicks{2000};
    std::uint32_t durationUs{50};
    std::uint8_t  dirMask{0};
    bool          isTerminal{false};
};

enum class State : std::uint8_t {
    Idle = 0,
    Normal,
    Warning,
    Decelerating,
    UnderrunStopped
};

template <typename TimerPeripheral, std::size_t Capacity = 64>
class DdaHardwareController {
    static_assert((Capacity & (Capacity - 1)) == 0, "Місткість буфера має бути степенем 2");

public:
    explicit DdaHardwareController(TimerPeripheral& timer) noexcept : m_timer(timer) {}

    void start(std::uint32_t prescaler) noexcept {
        m_timer.CR1 &= ~0x01U;
        m_timer.PSC = prescaler;
        m_timer.ARR = 2000;
        m_timer.CCR1 = 50;
        m_timer.CR1 |= (1U << 7); // ARPE: увімкнення тіньового регістра ARR
        m_timer.DIER |= 0x01U;
        m_timer.EGR |= 0x01U;
        m_state.store(State::Idle, std::memory_order_relaxed);
    }

    void handleTimerInterrupt() noexcept {
        m_timer.SR &= ~0x01U;
        State currentState = m_state.load(std::memory_order_relaxed);

        if (currentState == State::UnderrunStopped || currentState == State::Idle) {
            m_timer.CR1 &= ~0x01U;
            return;
        }

        if (currentState == State::Decelerating) {
            processDecelerationStep();
            return;
        }

        const std::size_t tail = m_tail.load(std::memory_order_relaxed);
        const std::size_t head = m_head.load(std::memory_order_acquire);

        if (head != tail) {
            const StepPacket& pkt = m_buffer[tail];
            m_tail.store((tail + 1) & (Capacity - 1), std::memory_order_release);

            const std::uint32_t avail = m_totalTimeAvailUs.load(std::memory_order_relaxed);
            const std::uint32_t nextAvail = (avail >= pkt.durationUs) ? (avail - pkt.durationUs) : 0;
            m_totalTimeAvailUs.store(nextAvail, std::memory_order_relaxed);

            m_lastPeriodTicks = pkt.stepIntervalTicks;
            m_timer.ARR = pkt.stepIntervalTicks;

            if (nextAvail <= m_decelThresholdUs) {
                m_state.store(State::Decelerating, std::memory_order_relaxed);
                m_decelStep = 0;
            } else if (nextAvail <= m_warningThresholdUs) {
                m_state.store(State::Warning, std::memory_order_relaxed);
            } else {
                m_state.store(State::Normal, std::memory_order_relaxed);
            }
        } else {
            m_state.store(State::Decelerating, std::memory_order_relaxed);
            m_decelStep = 0;
            processDecelerationStep();
        }
    }

private:
    void processDecelerationStep() noexcept {
        if (m_decelStep < TaylorSteps) {
            const std::uint32_t k = TaylorTable[m_decelStep++];
            const std::uint32_t delta = (m_lastPeriodTicks * k) >> 16;
            m_lastPeriodTicks += delta;
            m_timer.ARR = m_lastPeriodTicks;
        } else {
            m_state.store(State::UnderrunStopped, std::memory_order_relaxed);
            m_timer.CR1 &= ~0x01U;
        }
    }

    static constexpr std::size_t TaylorSteps = 16;
    static constexpr std::array<std::uint16_t, 16> TaylorTable = {
        26214, 14564, 10082, 7710, 6242, 5243, 4520, 3972,
        3542,  3197,  2913,  2675, 2473, 2300, 2149, 2017
    };

    TimerPeripheral& m_timer;
    alignas(64) std::array<StepPacket, Capacity> m_buffer{};
    alignas(64) std::atomic<std::size_t> m_head{0};
    alignas(64) std::atomic<std::size_t> m_tail{0};
    std::atomic<std::uint32_t> m_totalTimeAvailUs{0};
    std::atomic<State> m_state{State::Idle};

    std::uint32_t m_warningThresholdUs{8000};
    std::uint32_t m_decelThresholdUs{3000};
    std::uint32_t m_lastPeriodTicks{2000};
    std::uint32_t m_decelStep{0};
};

} // namespace MotionHardware
