#include <unistd.h>
#include <fcntl.h>
#include <string_view>
#include <span>

namespace sys {
inline int exec_at(int dirfd, std::string_view path,
                   std::span<char* const> argv,
                   std::span<char* const> envp,
                   int flags = 0) noexcept {
    return ::execveat(dirfd, path.data(), argv.data(), envp.data(), flags);
}
}
