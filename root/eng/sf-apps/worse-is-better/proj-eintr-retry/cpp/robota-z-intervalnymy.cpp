#include <chrono>
#include <ctime>
#include <cerrno>
#include <expected>
#include <system_error>

// Надійна затримка з використанням типів std::chrono
std::expected<void, std::error_code> sleep_exact(std::chrono::nanoseconds duration) {
    auto sec = std::chrono::duration_cast<std::chrono::seconds>(duration);
    auto nsec = duration - sec;

    struct timespec req{
        .tv_sec = static_cast<time_t>(sec.count()),
        .tv_nsec = static_cast<long>(nsec.count())
    };
    struct timespec rem{0, 0};

    while (::nanosleep(&req, &rem) == -1) {
        if (errno == EINTR) {
            req = rem; // Досипаємо залишок
            continue;
        }
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
