#include <iostream>
#include <cwchar>
#include <clocale>
#include <vector>
#include <iomanip>

int main() {
    // Увімкнення системної локалі для коректної класифікації Unicode
    std::setlocale(LC_CTYPE, "");

    const std::vector<wchar_t> chars = { L'A', L'ф', L'語', 0x0301, L'🚀' };

    for (wchar_t wc : chars) {
        int w = wcwidth(wc);
        std::cout << "Символ U+" << std::hex << std::uppercase << std::setw(4) 
                  << std::setfill('0') << static_cast<unsigned int>(wc) 
                  << " -> ширина: " << std::dec << std::setw(2) << std::setfill(' ') 
                  << w << " комірки\n";
    }
    return 0;
}
