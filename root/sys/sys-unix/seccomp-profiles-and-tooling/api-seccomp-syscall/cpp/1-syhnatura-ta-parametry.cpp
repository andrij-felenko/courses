#include <unistd.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <system_error>
#include <expected>

namespace sys {

// Ідіоматична C++23 обгортка для системного виклику seccomp
inline std::expected<void, std::error_code> seccomp_call(
    unsigned int operation, 
    unsigned int flags, 
    void* args) noexcept 
{
    long rc = ::syscall(SYS_seccomp, operation, flags, args);
    if (rc < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace sys
