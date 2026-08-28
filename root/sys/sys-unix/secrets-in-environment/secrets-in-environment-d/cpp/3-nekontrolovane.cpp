// Концептуальне представлення неконтрольованої передачі оточення
#include <unistd.h>
#include <span>
#include <string_view>

extern char **environ;

namespace posix_wrapper {
    int execute_utility(std::string_view file, char *const argv[]) noexcept {
        // execve неявно отримує глобальний environ батьківського процесу
        return ::execve(file.data(), argv, environ);
    }
}
