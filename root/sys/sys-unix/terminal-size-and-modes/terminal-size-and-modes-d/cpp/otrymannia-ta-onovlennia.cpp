#include <iostream>
#include <system_error>
#include <sys/ioctl.h>
#include <unistd.h>

int main() {
    struct winsize ws{};
    if (::ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == -1) {
        std::error_code ec(errno, std::generic_category());
        std::cerr << "Помилка ioctl: " << ec.message() << '\n';
        return 1;
    }
    std::cout << "Розмір термінала: " << ws.ws_row << " рядків × "
              << ws.ws_col << " стовпців (" << ws.ws_xpixel << "×"
              << ws.ws_ypixel << " px)\n";
    return 0;
}
