#include <cxxabi.h>
#include <stdio.h>
#include <stdlib.h>

void process_symbol_batch(const char** list, size_t count) {
    size_t capacity = 512;
    char* buffer = (char*)malloc(capacity);
    int status = 0;

    for (size_t i = 0; i < count; ++i) {
        char* result = abi::__cxa_demangle(list[i], buffer, &capacity, &status);
        if (status == 0 && result != NULL) {
            buffer = result; // Покажчик міг змінитися після виклику realloc
            printf("[%zu] %s\n", i, buffer);
        } else {
            printf("[%zu] %s (без змін)\n", i, list[i]);
        }
    }
    free(buffer);
}
