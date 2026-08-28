#include <cxxabi.h>
#include <stdio.h>
#include <stdlib.h>

void print_symbol_info(const char* mangled) {
    int status = 0;
    char* demangled = abi::__cxa_demangle(mangled, NULL, NULL, &status);
    
    if (status == 0 && demangled != NULL) {
        printf("Оригінальний символ:  %s\n", mangled);
        printf("Декодований вигляд:   %s\n", demangled);
        free(demangled);
    } else {
        printf("Не вдалося декодувати символ %s (код помилки: %d)\n", mangled, status);
    }
}
