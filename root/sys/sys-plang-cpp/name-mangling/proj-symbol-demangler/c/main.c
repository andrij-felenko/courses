#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#include <dbghelp.h>
#pragma comment(lib, "dbghelp.lib")
#else
#include <cxxabi.h>
#endif

// C-версія: ручне керування покажчиком на буфер та його ємністю
char* demangle_symbol_c(const char* mangled, char* buffer, size_t* capacity) {
    if (!mangled || mangled[0] == '\0') {
        return NULL;
    }

#if defined(_WIN32)
    char win_buf[1024];
    DWORD flags = UNDNAME_NO_MS_KEYWORDS | UNDNAME_NO_ACCESS_SPECIFIERS;
    DWORD res = UnDecorateSymbolName(mangled, win_buf, sizeof(win_buf), flags);
    
    if (res > 0) {
        if (!buffer || *capacity < res + 1) {
            buffer = (char*)realloc(buffer, res + 1);
            *capacity = res + 1;
        }
        memcpy(buffer, win_buf, res + 1);
        return buffer;
    }
#else
    const char* target = mangled;
    // Обробка специфіки Mach-O на macOS: видалення зайвого початкового підкреслення
    if (target[0] == '_' && target[1] == '_') {
        target++;
    }

    int status = 0;
    char* demangled = abi::__cxa_demangle(target, buffer, capacity, &status);
    if (status == 0 && demangled != NULL) {
        return demangled; // Покажчик міг змінитися в результаті роботи realloc
    }
#endif

    // Якщо деманґлінг не дав результату, повертаємо незмінений вхідний рядок
    size_t len = strlen(mangled);
    if (!buffer || *capacity < len + 1) {
        buffer = (char*)realloc(buffer, len + 1);
        *capacity = len + 1;
    }
    memcpy(buffer, mangled, len + 1);
    return buffer;
}
