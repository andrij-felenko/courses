#include <sys/ioctl.h>
#include <cstdint>

// У C++ структура struct winsize доступна через <sys/ioctl.h>
struct TerminalWindowSize {
    std::uint16_t ws_row{0};
    std::uint16_t ws_col{0};
    std::uint16_t ws_xpixel{0};
    std::uint16_t ws_ypixel{0};
};
