#include <cstdint>
#include <cstddef>

// -----------------------------------------------------------------------------
// 1. АПАРАТНИЙ ТА ПРОГРАМНИЙ КАДРИ СТЕКА В ООП-МОДЕЛІ C++
// -----------------------------------------------------------------------------

namespace Hal {

struct alignas(8) HardwareContext {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
};

struct SoftwareContext {
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t r8;
    uint32_t r9;
    uint32_t r10;
    uint32_t r11;
};

struct alignas(8) FullStackFrame {
    SoftwareContext software;
    HardwareContext hardware;
};

// RAII обгортка критичної секції на базі регістра BASEPRI
class CriticalSection {
public:
    explicit CriticalSection(uint8_t priorityThreshold = 0x50) noexcept {
        asm volatile (
            "mrs     %0, basepri             \n"
            "msr     basepri, %1             \n"
            "isb                             \n"
            : "=r" (m_previousBasepri)
            : "r" (static_cast<uint32_t>(priorityThreshold))
            : "memory"
        );
    }

    ~CriticalSection() {
        asm volatile (
            "msr     basepri, %0             \n"
            "isb                             \n"
            :
            : "r" (m_previousBasepri)
            : "memory"
        );
    }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;

private:
    uint32_t m_previousBasepri{0};
};

} // namespace Hal

namespace Os {

class TaskControlBlock {
public:
    using TaskFunction = void (*)(void*);

    TaskControlBlock() = default;

    void initializeStack(TaskFunction function, void* argument, uint32_t* stackBuffer, size_t sizeWords) {
        m_stackBase = stackBuffer;
        m_stackSizeWords = sizeWords;

        // Вирівнювання верхньої межі стека по межі 8 байтів
        auto topAddress = reinterpret_cast<uintptr_t>(stackBuffer + sizeWords) & ~uintptr_t{0x07};
        auto* frame = reinterpret_cast<Hal::FullStackFrame*>(topAddress - sizeof(Hal::FullStackFrame));

        // Налаштування апаратного кадру
        frame->hardware.xpsr = 0x01000000UL; // Thumb bit
        frame->hardware.pc   = reinterpret_cast<uint32_t>(function);
        frame->hardware.lr   = reinterpret_cast<uint32_t>(&defaultTaskExitTrap);
        frame->hardware.r0   = reinterpret_cast<uint32_t>(argument);
        frame->hardware.r1   = 0;
        frame->hardware.r2   = 0;
        frame->hardware.r3   = 0;
        frame->hardware.r12  = 0;

        // Діагностичні шаблони програмного кадру
        frame->software.r4   = 0x44444444UL;
        frame->software.r5   = 0x55555555UL;
        frame->software.r6   = 0x66666666UL;
        frame->software.r7   = 0x77777777UL;
        frame->software.r8   = 0x88888888UL;
        frame->software.r9   = 0x99999999UL;
        frame->software.r10  = 0xAAAAAAAAUL;
        frame->software.r11  = 0xBBBBBBBBUL;

        m_stackPointer = reinterpret_cast<uint32_t*>(frame);
    }

    [[nodiscard]] uint32_t* getStackPointer() const noexcept { return m_stackPointer; }
    void setStackPointer(uint32_t* sp) noexcept { m_stackPointer = sp; }

    static void yield() noexcept {
        *reinterpret_cast<volatile uint32_t*>(0xE000ED04) = (1UL << 28);
        asm volatile ("dsb \n isb");
    }

private:
    static void defaultTaskExitTrap() {
        while (true) {
            asm volatile ("wfi");
        }
    }

    uint32_t* m_stackPointer{nullptr};
    uint32_t* m_stackBase{nullptr};
    size_t    m_stackSizeWords{0};
};

} // namespace Os
