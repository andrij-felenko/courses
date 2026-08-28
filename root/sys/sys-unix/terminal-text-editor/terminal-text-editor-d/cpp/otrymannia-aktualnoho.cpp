#include <sys/ioctl.h>
#include <unistd.h>
#include <optional>

struct WindowDimensions {
    int rows{0};
    int cols{0};
};

std::optional<WindowDimensions> get_window_size() noexcept {
    struct winsize ws{};
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == -1 || ws.ws_col == 0) {
        return std::nullopt;
    }
    return WindowDimensions{.rows = ws.ws_row, .cols = ws.ws_col};
}
