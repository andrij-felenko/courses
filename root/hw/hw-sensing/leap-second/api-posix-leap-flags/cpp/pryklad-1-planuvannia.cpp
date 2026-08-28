#include <iostream>
#include <expected>
#include <string_view>
#include <cstring>
#include <cerrno>
#include <sys/timex.h>

namespace time_control {

enum class KernelState {
    Ok = TIME_OK,
    InsertPending = TIME_INS,
    DeletePending = TIME_DEL,
    LeapActive = TIME_OOP,
    WaitClear = TIME_WAIT,
    Error = TIME_ERROR
};

[[nodiscard]] std::expected<KernelState, std::string_view> schedule_leap_second_insertion() noexcept {
    struct timex tx{};

    // Отримуємо поточний стан
    if (::adjtimex(&tx) < 0) {
        return std::unexpected("Не вдалося отримати поточний стан підсистеми часу");
    }

    tx.modes = ADJ_STATUS;
    tx.status |= STA_INS;
    tx.status &= ~STA_DEL;

    const int state = ::adjtimex(&tx);
    if (state < 0) {
        if (errno == EPERM) {
            return std::unexpected("Відмовлено в доступі: потрібні права CAP_SYS_TIME");
        }
        return std::unexpected("Системний виклик adjtimex завершився з помилкою");
    }

    return static_cast<KernelState>(state);
}

} // namespace time_control
