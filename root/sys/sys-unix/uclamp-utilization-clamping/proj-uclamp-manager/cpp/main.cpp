#include <iostream>
#include <system_error>
#include <expected>
#include <cstdint>
#include <cstring>
#include <cerrno>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

namespace sys {
    #ifndef SYS_sched_setattr
    #define SYS_sched_setattr 314
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP_MIN
    #define SCHED_FLAG_UTIL_CLAMP_MIN 0x20
    #endif

    #ifndef SCHED_FLAG_UTIL_CLAMP_MAX
    #define SCHED_FLAG_UTIL_CLAMP_MAX 0x40
    #endif
}

class UtilizationClamp {
public:
    enum class Profile {
        LatencyCritical,
        BackgroundEnergySaver,
        Default
    };

    static std::expected<void, std::error_code> apply(pid_t tid, Profile profile) noexcept {
        struct sched_attr attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_OTHER;

        switch (profile) {
            case Profile::LatencyCritical:
                attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
                attr.sched_util_min = 600;  // Підтягуємо мінімум до ~58%
                attr.sched_util_max = 1024; // Не обмежуємо максимум
                break;
            case Profile::BackgroundEnergySaver:
                attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
                attr.sched_util_min = 0;
                attr.sched_util_max = 256;  // Затискаємо максимум до ~25%
                break;
            case Profile::Default:
                attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
                attr.sched_util_min = 0;
                attr.sched_util_max = 1024;
                break;
        }

        long res = ::syscall(SYS_sched_setattr, tid, &attr, 0);
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

int main() {
    pid_t tid = ::gettid();
    std::cout << "[C++] Налаштування uclamp для потоку TID=" << tid << "...\n";

    auto res = UtilizationClamp::apply(tid, UtilizationClamp::Profile::LatencyCritical);
    if (!res) {
        std::cerr << "Помилка застосування профілю: " << res.error().message() << '\n';
        return 1;
    }
    std::cout << "[C++] Успішно встановлено профіль LatencyCritical (uclamp_min=600)\n";

    ::usleep(100000);

    res = UtilizationClamp::apply(tid, UtilizationClamp::Profile::BackgroundEnergySaver);
    if (!res) {
        std::cerr << "Помилка застосування профілю: " << res.error().message() << '\n';
        return 1;
    }
    std::cout << "[C++] Успішно встановлено профіль BackgroundEnergySaver (uclamp_max=256)\n";

    return 0;
}
