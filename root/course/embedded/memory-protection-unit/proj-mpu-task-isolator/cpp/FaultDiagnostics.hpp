#ifndef FAULT_DIAGNOSTICS_HPP
#define FAULT_DIAGNOSTICS_HPP

#include "MpuTypes.hpp"
#include <string_view>

namespace embedded::mpu {

enum class RecoveryAction {
    TerminateTask,
    RestartTask,
    SystemReset,
    IgnoreAndResume
};

class FaultDiagnostics {
public:
    [[nodiscard]] static RecoveryAction evaluate_policy(const FaultReport& report) noexcept;
    static void log_report_to_console(const FaultReport& report) noexcept;
};

} // namespace embedded::mpu

#endif // FAULT_DIAGNOSTICS_HPP
