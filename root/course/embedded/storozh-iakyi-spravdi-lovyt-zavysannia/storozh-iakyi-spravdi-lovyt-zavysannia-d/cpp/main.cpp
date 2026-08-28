#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>

namespace embedded::safety {

enum class FaultReason : uint32_t {
    None = 0,
    Timeout = 1,
    BadCheckpoint = 2
};

struct CrashReport {
    uint32_t magic;
    uint32_t faultTaskId;
    uint32_t faultTick;
    FaultReason reason;
};

// Секція оперативної пам'яті, що не ініціалізується при старті
#if defined(__GNUC__)
[[gnu::section(".noinit")]]
#endif
static volatile CrashReport g_sharedCrashDump;

template <size_t MaxTasks = 8>
class TaskWatchdogSupervisor {
public:
    static constexpr uint32_t MagicValid = 0x5A5AA5A5U;
    static constexpr uint32_t CheckpointFinal = 0x3C69A55AU;

    struct TaskConfig {
        uint32_t taskId{0};
        uint32_t timeoutMs{1000};
        uint32_t lastCheckinTick{0};
        uint32_t expectedCheckpoint{CheckpointFinal};
        uint32_t currentCheckpoint{CheckpointFinal};
        bool isRegistered{false};
        bool isActive{false};
    };

    constexpr TaskWatchdogSupervisor() = default;

    std::optional<size_t> registerTask(uint32_t taskId, uint32_t timeoutMs, uint32_t currentTick) noexcept {
        for (size_t i = 0; i < taskCount_; ++i) {
            if (tasks_[i].taskId == taskId) {
                return i;
            }
        }
        if (taskCount_ >= MaxTasks) {
            return std::nullopt;
        }

        size_t handle = taskCount_++;
        tasks_[handle] = TaskConfig{
            .taskId = taskId,
            .timeoutMs = timeoutMs,
            .lastCheckinTick = currentTick,
            .expectedCheckpoint = CheckpointFinal,
            .currentCheckpoint = CheckpointFinal,
            .isRegistered = true,
            .isActive = true
        };
        return handle;
    }

    void checkpoint(size_t handle, uint32_t phaseStep) noexcept {
        if (handle < taskCount_ && tasks_[handle].isActive) {
            uint32_t cp = tasks_[handle].currentCheckpoint;
            tasks_[handle].currentCheckpoint = (cp << 3) ^ (cp >> 29) ^ phaseStep;
        }
    }

    void checkin(size_t handle, uint32_t currentTick) noexcept {
        if (handle < taskCount_ && tasks_[handle].isActive) {
            tasks_[handle].lastCheckinTick = currentTick;
            tasks_[handle].currentCheckpoint = CheckpointFinal;
        }
    }

    bool evaluateAndReload(uint32_t currentTick) noexcept {
        for (size_t i = 0; i < taskCount_; ++i) {
            if (!tasks_[i].isActive) {
                continue;
            }

            const uint32_t elapsed = currentTick - tasks_[i].lastCheckinTick;
            if (elapsed > tasks_[i].timeoutMs) {
                recordCrash(tasks_[i].taskId, currentTick, FaultReason::Timeout);
                return false;
            }

            if (tasks_[i].currentCheckpoint != tasks_[i].expectedCheckpoint) {
                recordCrash(tasks_[i].taskId, currentTick, FaultReason::BadCheckpoint);
                return false;
            }
        }

        reloadHardware();
        return true;
    }

    static std::optional<CrashReport> extractCrashReport() noexcept {
        if (g_sharedCrashDump.magic == MagicValid) {
            CrashReport report = const_cast<const CrashReport&>(g_sharedCrashDump);
            g_sharedCrashDump.magic = 0;
            return report;
        }
        return std::nullopt;
    }

private:
    std::array<TaskConfig, MaxTasks> tasks_{};
    size_t taskCount_{0};

    static void reloadHardware() noexcept {
        volatile auto* iwdgKr = reinterpret_cast<volatile uint32_t*>(0x40003000U);
        *iwdgKr = 0xAAAAU;
    }

    static void recordCrash(uint32_t taskId, uint32_t tick, FaultReason reason) noexcept {
        g_sharedCrashDump.magic = MagicValid;
        g_sharedCrashDump.faultTaskId = taskId;
        g_sharedCrashDump.faultTick = tick;
        g_sharedCrashDump.reason = reason;
    }
};

} // namespace embedded::safety
