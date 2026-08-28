/* safe_logger_c.c - C-еквівалент із ледачою ініціалізацією */
#include <stdio.h>
#include <stdbool.h>

typedef struct {
    const char* filename;
    bool is_open;
} CLogger;

static CLogger s_c_logger_instance;
static bool s_is_initialized = false;

CLogger* get_logger_instance(void) {
    if (!s_is_initialized) {
        s_c_logger_instance.filename = "application.log";
        s_c_logger_instance.is_open = true;
        s_is_initialized = true;
        printf("[CLogger] Ініціалізовано: %s\n", s_c_logger_instance.filename);
    }
    return &s_c_logger_instance;
}
