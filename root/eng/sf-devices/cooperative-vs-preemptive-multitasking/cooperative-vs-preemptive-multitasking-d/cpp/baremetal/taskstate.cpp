#include <cstdint>
#include <cstddef>

namespace Kernel {

// Стан задачі в системі
enum class TaskState : uint8_t {
    Ready = 0,
    Running,
    Blocked,
    Suspended
};

// Абстрактний базовий клас для кооперативних та витісняльних задач
class ITask {
public:
    virtual void execute() = 0;
    virtual ~ITask() = default;
};

// Контрольний блок задачі у стилі C++
struct TaskControlBlock {
    uint32_t* stackPointer{nullptr};
    uint8_t priority{0};
    TaskState state{TaskState::Ready};
    uint32_t delayTicks{0};
    uint32_t* stackBase{nullptr};
    uint32_t stackSizeWords{0};
    ITask* taskInstance{nullptr};
};

class PreemptiveScheduler {
public:
    static constexpr size_t MaxTasks = 8;
    static constexpr size_t StackWords = 256;

    static bool addTask(ITask* instance, uint8_t priority) {
        if (m_taskCount >= MaxTasks) return false;

        TaskControlBlock& tcb = m_tcbs[m_taskCount];
        uint32_t* stack = m_stacks[m_taskCount];
        uint32_t* sp = &stack[StackWords];

        // Формування початкового кадру контексту ARM Cortex-M
        *(--sp) = 0x01000000; // xPSR
        *(--sp) = reinterpret_cast<uint32_t>(&taskTrampoline); // PC
        *(--sp) = 0xFFFFFFFD; // LR
        *(--sp) = 0; // R12
        *(--sp) = 0; // R3
        *(--sp) = 0; // R2
        *(--sp) = 0; // R1
        *(--sp) = reinterpret_cast<uint32_t>(instance); // R0 (аргумент this / instance)

        for (int i = 0; i < 8; ++i) {
            *(--sp) = 0; // R4-R11
        }

        tcb.stackPointer = sp;
        tcb.priority = priority;
        tcb.state = TaskState::Ready;
        tcb.stackBase = stack;
        tcb.stackSizeWords = StackWords;
        tcb.taskInstance = instance;

        m_readyBitmap |= (1U << priority);
        m_taskCount++;
        return true;
    }

    static void onSysTick() {
        for (size_t i = 0; i < m_taskCount; ++i) {
            if (m_tcbs[i].state == TaskState::Blocked) {
                if (--m_tcbs[i].delayTicks == 0) {
                    m_tcbs[i].state = TaskState::Ready;
                    m_readyBitmap |= (1U << m_tcbs[i].priority);
                }
            }
        }

        if (m_readyBitmap != 0) {
            uint8_t topPriority = 31 - __builtin_clz(m_readyBitmap);
            for (size_t i = 0; i < m_taskCount; ++i) {
                if (m_tcbs[i].priority == topPriority && m_tcbs[i].state == TaskState::Ready) {
                    m_nextTcb = &m_tcbs[i];
                    break;
                }
            }
        }

        if (m_nextTcb != m_currentTcb) {
            triggerPendSV();
        }
    }

private:
    static void taskTrampoline(ITask* task) {
        if (task) {
            task->execute();
        }
        while (true) {
            // Задача завершилася, призупиняємо стан
        }
    }

    static inline void triggerPendSV() {
        *(volatile uint32_t*)0xE000ED04 = (1U << 28);
    }

    static inline TaskControlBlock m_tcbs[MaxTasks];
    static inline uint32_t m_stacks[MaxTasks][StackWords];
    static inline size_t m_taskCount{0};
    static inline uint32_t m_readyBitmap{0};
    static inline TaskControlBlock* m_currentTcb{nullptr};
    static inline TaskControlBlock* m_nextTcb{nullptr};
};

} // namespace Kernel
