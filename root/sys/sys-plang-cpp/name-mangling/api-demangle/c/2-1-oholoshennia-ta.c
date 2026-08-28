#include <windows.h>
#include <dbghelp.h>
#include <stdio.h>

void win32_print_symbol(const char* decorated) {
    char buffer[1024];
    DWORD len = UnDecorateSymbolName(
        decorated,
        buffer,
        sizeof(buffer),
        UNDNAME_COMPLETE
    );
    
    if (len > 0) {
        printf("Windows декодовано: %s\n", buffer);
    } else {
        printf("Помилка декодування, код: %lu\n", GetLastError());
    }
}
