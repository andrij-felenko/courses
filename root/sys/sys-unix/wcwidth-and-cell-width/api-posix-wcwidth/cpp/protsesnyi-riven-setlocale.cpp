#include <iostream>
#include <clocale>
#include <cwchar>

int main() {
    // Ініціалізація локалі процесу
    const char* current_locale = std::setlocale(LC_CTYPE, "");
    if (!current_locale) {
        std::cerr << "Попередження: не вдалося завантажити системну локаль\n";
    }

    wchar_t cjk_char = L'語';
    std::cout << "Ширина символу: " << wcwidth(cjk_char) << " комірки\n";

    return 0;
}
