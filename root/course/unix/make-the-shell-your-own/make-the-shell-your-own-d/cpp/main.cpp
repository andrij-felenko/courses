#include <iostream>
#include <string_view>
#include <unistd.h>

int main(int argc, char *argv[]) {
    // 1. Перевірка наявності дефіса на початку argv[0]
    const bool is_login = (argc > 0 && argv[0] != nullptr && argv[0][0] == '-');

    // 2. Перевірка підключення стандартного потоку вводу до TTY
    const bool is_interactive = (isatty(STDIN_FILENO) == 1);

    const std::string_view arg0 = (argc > 0 && argv[0] != nullptr) ? argv[0] : "(null)";

    std::cout << "Ідентифікація оболонки:\n";
    std::cout << "  argv[0]         = " << arg0 << "\n";
    std::cout << "  Login Shell     = " << (is_login ? "ТАК (ініціалізація сеансу)" : "НІ (вторинний процес)") << "\n";
    std::cout << "  Interactive     = " << (is_interactive ? "ТАК (підключено до термінала)" : "НІ (виконання скрипта)") << "\n";

    return 0;
}
