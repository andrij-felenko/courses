#include <stdio.h>

/* Класичний C-підхід: вимагає макросу для фіксації __FILE__ та __LINE__ */
#define LOG_EVENT(msg) log_internal(msg, __FILE__, __LINE__, __func__)

static void log_internal(const char* msg, const char* file, int line, const char* func) {
    printf("[%s:%d in %s()] %s\n", file, line, func, msg);
}

int main(void) {
    LOG_EVENT("Ініціалізація підсистеми C");
    return 0;
}
