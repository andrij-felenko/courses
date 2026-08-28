#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Ідіоматичний еквівалент обробки помилок у C через статус-структури
typedef struct {
    int code;
    const char* category;
    char message[256];
    char file[128];
    int line;
} c_error_context;

// Потік-локальний стек помилок (Thread-Local Error Context)
static __thread c_error_context g_last_error = {0};

void set_last_error(int code, const char* cat, const char* msg, const char* file, int line) {
    g_last_error.code = code;
    g_last_error.category = cat;
    g_last_error.line = line;
    snprintf(g_last_error.message, sizeof(g_last_error.message), "%s", msg);
    snprintf(g_last_error.file, sizeof(g_last_error.file), "%s", file);
}

const c_error_context* get_last_error(void) {
    return &g_last_error;
}

// Функція з C-моделлю повернення статусу
int low_level_network_read_c(const char* host) {
    if (strcmp(host, "invalid") == 0) {
        set_last_error(104, "POSIX", "Connection reset by peer", __FILE__, __LINE__);
        return -1; // Сигнал помилки
    }
    return 0; // Успіх
}

int main(void) {
    if (low_level_network_read_c("invalid") != 0) {
        const c_error_context* err = get_last_error();
        printf("=== C-STYLE ERROR CONTEXT ===\n");
        printf("Код: %s:%d\n", err->category, err->code);
        printf("Опис: %s\n", err->message);
        printf("Локація: %s:%d\n", err->file, err->line);
    }
    return 0;
}
