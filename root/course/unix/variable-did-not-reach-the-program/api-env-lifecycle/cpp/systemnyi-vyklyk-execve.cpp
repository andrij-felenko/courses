#include <unistd.h>
#include <string_view>
#include <span>
#include <vector>

namespace sys {
// C++23 типізована обгортка для прямого виклику execve
inline int exec_raw(std::string_view path,
                    std::span<char* const> argv,
                    std::span<char* const> envp) noexcept {
    return ::execve(path.data(), argv.data(), envp.data());
}
}
