#include <iostream>
#include <cstdint>
#include <cstring>
#include <cerrno>
#include <expected>
#include <format>
#include <sys/prctl.h>
#include <unistd.h>

#ifndef PR_SCHED_CORE
#define PR_SCHED_CORE 62
#define PR_SCHED_CORE_GET 0
#define PR_SCHED_CORE_CREATE 1
#define PIDTYPE_PID 0
#define PIDTYPE_TGID 1
#endif

namespace core_sched {

enum class SchedError {
    NoSmtSupport,
    PermissionDenied,
    KernelNotSupported,
    UnknownError
};

std::expected<uint64_t, SchedError> create_trust_domain() {
    int res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_CREATE, 0, PIDTYPE_TGID, 0);
    if (res < 0) {
        if (errno == ENODEV) {
            return std::unexpected(SchedError::NoSmtSupport);
        }
        if (errno == EPERM) {
            return std::unexpected(SchedError::PermissionDenied);
        }
        if (errno == EINVAL) {
            return std::unexpected(SchedError::KernelNotSupported);
        }
        return std::unexpected(SchedError::UnknownError);
    }

    uint64_t cookie{0};
    res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_GET, 0, PIDTYPE_PID, reinterpret_cast<unsigned long>(&cookie));
    if (res < 0) {
        return std::unexpected(SchedError::UnknownError);
    }

    return cookie;
}

} // namespace core_sched

int main() {
    auto result = core_sched::create_trust_domain();
    if (result.has_value()) {
        std::cout << "Core Scheduling активовано успішно. Cookie: 0x"
                  << std::hex << result.value() << std::dec << '\n';
        return 0;
    }

    switch (result.error()) {
        case core_sched::SchedError::NoSmtSupport:
            std::cerr << "SMT не підтримується процесором або вимкнено в BIOS/sysfs\n";
            break;
        case core_sched::SchedError::PermissionDenied:
            std::cerr << "Брак прав для зміни параметрів планування\n";
            break;
        case core_sched::SchedError::KernelNotSupported:
            std::cerr << "Ядро Linux зібрано без CONFIG_SCHED_CORE\n";
            break;
        case core_sched::SchedError::UnknownError:
            std::cerr << "Невідома системна помилка при виклику prctl\n";
            break;
    }
    return 1;
}
