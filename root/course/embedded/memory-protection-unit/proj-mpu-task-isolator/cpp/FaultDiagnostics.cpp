#include "FaultDiagnostics.hpp"

namespace embedded::mpu {

RecoveryAction FaultDiagnostics::evaluate_policy(const FaultReport& report) noexcept {
    /* Якщо збій стався у непривілейованому режимі задачі (PSP) */
    if (report.occurred_in_unprivileged_thread) {
        /*
         * Якщо відбулося порушення вибірки (IACCVIOL) або даних (DACCVIOL),
         * ізолюємо та перезапускаємо винну задачу.
         */
        if (report.mmfsr_flags & (1U << 1)) {
            return RecoveryAction::RestartTask;
        }
        return RecoveryAction::TerminateTask;
    }

    /* Збій у привілейованому режимі ядра (MSP) є фатальною подією */
    return RecoveryAction::SystemReset;
}

void FaultDiagnostics::log_report_to_console(const FaultReport& report) noexcept {
    (void)report;
    /*
     * Реалізація виводу через UART / ITM / RTT діагностичного каналу
     * у промисловому вбудованому застосунку.
     */
}

} // namespace embedded::mpu
