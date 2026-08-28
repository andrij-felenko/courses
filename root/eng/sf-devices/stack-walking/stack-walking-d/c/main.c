#include <stdio.h>
#include <stdlib.h>
#include <execinfo.h>
#include <unistd.h>

void capture_backtrace(void) {
    void* callstack[32];
    int frames = backtrace(callstack, 32);
    char** symbols = backtrace_symbols(callstack, frames);

    if (symbols != NULL) {
        for (int i = 0; i < frames; ++i) {
            printf("  [%02d] %s\n", i, symbols[i]);
        }
        free(symbols);
    }
}
