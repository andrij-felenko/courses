#include <cstdint>
#include <cstddef>
#include <array>

namespace Diagnostics {

// -----------------------------------------------------------------------------
// 1. СТАТИЧНИЙ МОНІТОР ПЕРЕПОВНЕННЯ СТЕКА
// -----------------------------------------------------------------------------

template <size_t StackWords>
class StackMonitor {
public:
    static constexpr uint32_t WatermarkSignature = 0xA5A5A5A5UL;

    constexpr StackMonitor() = default;

    void paint() noexcept {
        m_stackBuffer.fill(WatermarkSignature);
    }

    [[nodiscard]] size_t getUnusedWords() const noexcept {
        size_t freeWords = 0;
        for (const auto word : m_stackBuffer) {
            if (word != WatermarkSignature) {
                break;
            }
            ++freeWords;
        }
        return freeWords;
    }

    [[nodiscard]] size_t getPeakUsageBytes() const noexcept {
        return (StackWords - getUnusedWords()) * sizeof(uint32_t);
    }

    [[nodiscard]] uint32_t* getBuffer() noexcept { return m_stackBuffer.data(); }
    [[nodiscard]] constexpr size_t getSizeWords() const noexcept { return StackWords; }

private:
    std::array<uint32_t, StackWords> m_stackBuffer{};
};

// -----------------------------------------------------------------------------
// 2. АПАРАТНИЙ ПРОФІЛЮВАЛЬНИК ТАКТІВ DWT З RAII ІНТЕРФЕЙСОМ
// -----------------------------------------------------------------------------

class CycleProfiler {
public:
    static void initializeHardware() noexcept {
        *reinterpret_cast<volatile uint32_t*>(0xE000EDFC) |= (1UL << 24); // DEMCR.TRCENA
        *reinterpret_cast<volatile uint32_t*>(0xE0001004) = 0;            // DWT.CYCCNT
        *reinterpret_cast<volatile uint32_t*>(0xE0001000) |= 1UL;          // DWT.CTRL.CYCCNTENA
    }

    CycleProfiler() noexcept : m_startCycles(getCurrentCycles()) {}

    [[nodiscard]] uint32_t elapsedCycles() const noexcept {
        return getCurrentCycles() - m_startCycles;
    }

    static uint32_t getCurrentCycles() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0xE0001004);
    }

private:
    uint32_t m_startCycles;
};

// -----------------------------------------------------------------------------
// 3. ГІБРИДНИЙ ВИКОНАВЕЦЬ ЧЕРГИ ВІДКЛАДЕНИХ РОБІТ
// -----------------------------------------------------------------------------

class CooperativeEventDispatcher {
public:
    using Delegate = void (*)(void*);

    struct WorkItem {
        Delegate callback{nullptr};
        void* context{nullptr};
    };

    static constexpr size_t QueueSize = 16;

    bool post(Delegate callback, void* context) noexcept {
        const size_t nextHead = (m_head + 1) % QueueSize;
        if (nextHead == m_tail) {
            return false;
        }
        m_queue[m_head] = WorkItem{callback, context};
        m_head = nextHead;
        return true;
    }

    void processPending() noexcept {
        while (m_tail != m_head) {
            WorkItem item = m_queue[m_tail];
            m_tail = (m_tail + 1) % QueueSize;
            if (item.callback) {
                item.callback(item.context);
            }
        }
    }

private:
    std::array<WorkItem, QueueSize> m_queue{};
    volatile size_t m_head{0};
    volatile size_t m_tail{0};
};

} // namespace Diagnostics
