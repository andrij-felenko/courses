#include <iostream>
#include <string_view>
#include <termios.h>
#include <unistd.h>
#include <cstdio>

// Визначення фізичної ширини символу на склі термінала в стилі C++
int probe_actual_terminal_width(std::string_view utf8_char) {
    termios old_term{}, raw_term{};
    tcgetattr(STDIN_FILENO, &old_term);
    raw_term = old_term;
    raw_term.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &raw_term);

    // 1. Запит початкового стану
    std::cout << "\033[6n" << std::flush;
    int r1 = 0, c1 = 0;
    std::scanf("\033[%d;%dR", &r1, &c1);

    // 2. Вивід символу
    std::cout << utf8_char << std::flush;

    // 3. Запит фінального стану
    std::cout << "\033[6n" << std::flush;
    int r2 = 0, c2 = 0;
    std::scanf("\033[%d;%dR", &r2, &c2);

    tcsetattr(STDIN_FILENO, TCSANOW, &old_term);

    // Очищення тестового виводу
    std::cout << "\r\033[K" << std::flush;

    return c2 - c1;
}
