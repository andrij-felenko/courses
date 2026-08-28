#include <sys/ioctl.h>
#include <cstdint>

// У C++ структура struct winsize доступна через заголовок <sys/ioctl.h>
// Її двійкове представлення повністю відповідає стандарту POSIX та Linux ABI
struct TerminalWindowSize {
    std::uint16_t ws_row{0};
    std::uint16_t ws_col{0};
    std::uint16_t ws_xpixel{0};
    std::uint16_t ws_ypixel{0};
};
