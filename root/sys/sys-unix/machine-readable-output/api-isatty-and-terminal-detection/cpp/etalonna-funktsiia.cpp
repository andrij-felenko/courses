#include <cstdlib>
#include <cstring>
#include <string_view>
#include <unistd.h>

[[nodiscard]] bool should_enable_color(int fd) noexcept {
    // 1. Стандарт NO_COLOR: найвищий пріоритет
    if (const char *no_color = std::getenv("NO_COLOR"); no_color != nullptr && no_color[0] != '\0') {
        return false;
    }

    // 2. Примусове увімкнення кольорів для CI/CD логів
    if (const char *force = std::getenv("CLICOLOR_FORCE"); force != nullptr && std::string_view(force) != "0") {
        return true;
    }

    // 3. Перевірка примітивного термінала dumb
    if (const char *term = std::getenv("TERM"); term != nullptr && std::string_view(term) == "dumb") {
        return false;
    }

    // 4. Заборона через CLICOLOR=0
    if (const char *clicolor = std::getenv("CLICOLOR"); clicolor != nullptr && std::string_view(clicolor) == "0") {
        return false;
    }

    // 5. Автоматичне визначення TTY
    return isatty(fd) == 1;
}
