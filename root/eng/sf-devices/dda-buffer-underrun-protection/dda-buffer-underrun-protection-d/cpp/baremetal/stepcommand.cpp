#include <cstdint>
#include <cstddef>
#include <atomic>
#include <array>

namespace MotionControl {

// Структура кванта руху
struct StepCommand {
    std::uint32_t stepTicks{0};
    std::uint8_t  dirMask{0};
    std::uint8_t  stepMask{0};
    std::uint16_t durationUs{0};
};

// Автомат станів захисту від опустошення буфера
enum class ProtectionState : std::uint8_t {
    Normal = 0,
    Warning,
    Decelerating,
    UnderrunStopped,
    Recovery
};

template <std::size_t Capacity = 128>
class DdaBufferProtection {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");

public:
    DdaBufferProtection(std::uint32_t warningUs, std::uint32_t decelUs)
        : m_warningThresholdUs(warningUs),
          m_decelThresholdUs(decelUs),
          m_state(ProtectionState::Normal) {}

    // Додавання нової команди планувальником (Thread Context)
    bool push(const StepCommand& cmd) noexcept {
        const auto h = m_head.load(std::memory_order_relaxed);
        const auto t = m_tail.load(std::memory_order_acquire);

        if (((h + 1) & BufferMask) == (t & BufferMask)) {
            return false; // Буфер переповнений
        }

        m_ringBuffer[h & BufferMask] = cmd;
        m_head.store((h + 1) & BufferMask, std::memory_order_release);
        m_totalTimeAvailUs.fetch_add(cmd.durationUs, std::memory_order_relaxed);
        return true;
    }

    // Викликається з ISR таймера DDA (Interrupt Context)
    void handleTimerIsr() noexcept {
        const auto t = m_tail.load(std::memory_order_relaxed);
        const auto h = m_head.load(std::memory_order_acquire);

        const std::size_t availableCount = (h - t) & BufferMask;
        const std::uint32_t currentAvailUs = m_totalTimeAvailUs.load(std::memory_order_relaxed);

        auto currentState = m_state.load(std::memory_order_relaxed);

        // Перевірка порогових значень захисту
        if (currentState != ProtectionState::Decelerating && currentState != ProtectionState::UnderrunStopped) {
            if (currentAvailUs <= m_decelThresholdUs || availableCount <= 1) {
                m_state.store(ProtectionState::Decelerating, std::memory_order_relaxed);
                m_decelStepCount = 1;
                currentState = ProtectionState::Decelerating;
            } else if (currentAvailUs <= m_warningThresholdUs) {
                m_state.store(ProtectionState::Warning, std::memory_order_relaxed);
            } else {
                m_state.store(ProtectionState::Normal, std::memory_order_relaxed);
            }
        }

        // Режим автономного гальмування при спустошенні
        if (currentState == ProtectionState::Decelerating) {
            executeAutonomousDeceleration();
            return;
        }

        if (currentState == ProtectionState::UnderrunStopped) {
            return;
        }

        // Нормальне виконання елемента з буфера
        if (availableCount > 0) {
            const auto& cmd = m_ringBuffer[t & BufferMask];
            
            // Фізичне виведення на периферію
            m_lastStepTicks = cmd.stepTicks;

            if (currentAvailUs >= cmd.durationUs) {
                m_totalTimeAvailUs.fetch_sub(cmd.durationUs, std::memory_order_relaxed);
            } else {
                m_totalTimeAvailUs.store(0, std::memory_order_relaxed);
            }

            m_tail.store((t + 1) & BufferMask, std::memory_order_release);
        }
    }

    [[nodiscard]] ProtectionState getState() const noexcept {
        return m_state.load(std::memory_order_relaxed);
    }

private:
    void executeAutonomousDeceleration() noexcept {
        const std::uint32_t n = m_decelStepCount;
        const std::uint32_t cPrev = (m_lastStepTicks == 0) ? 1000U : m_lastStepTicks;

        const std::uint32_t cNext = cPrev + (2U * cPrev) / (4U * n + 1U);
        m_lastStepTicks = cNext;
        m_decelStepCount++;

        if (m_decelStepCount >= MaxDecelSteps || cNext > 50000U) {
            m_state.store(ProtectionState::UnderrunStopped, std::memory_order_relaxed);
        }
    }

    static constexpr std::size_t BufferMask = Capacity - 1;
    static constexpr std::uint32_t MaxDecelSteps = 100;

    alignas(64) std::array<StepCommand, Capacity> m_ringBuffer{};
    alignas(64) std::atomic<std::size_t> m_head{0};
    alignas(64) std::atomic<std::size_t> m_tail{0};
    std::atomic<std::uint32_t> m_totalTimeAvailUs{0};

    std::uint32_t m_warningThresholdUs{0};
    std::uint32_t m_decelThresholdUs{0};
    std::uint32_t m_lastStepTicks{1000};
    std::uint32_t m_decelStepCount{0};

    std::atomic<ProtectionState> m_state{ProtectionState::Normal};
};

} // namespace MotionControl
