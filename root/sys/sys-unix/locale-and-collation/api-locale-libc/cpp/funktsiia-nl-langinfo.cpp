// C++17 приклад витягування кодування через std::locale
#include <iostream>
#include <locale>
#include <clocale>
#include <langinfo.h>

void print_current_codeset_cpp() {
    std::setlocale(LC_ALL, "");
    const char *cs = nl_langinfo(CODESET);
    std::cout << "Активне кодування термінала (C++): " << cs << "\n";
}
