/* safe_logger_c.c - реалізація на мові C */
#include "safe_logger_c.h"

static SafeCLogger g_c_logger_inst;
static pthread_once_t g_c_logger_once = PTHREAD_ONCE_INIT;

static void init_c_logger_internal(void) {
    g_c_logger_inst.prefix = "SAFE_C_LOG";
    printf("[C LOG INIT] %s активовано\n", g_c_logger_inst.prefix);
}

SafeCLogger* get_safe_c_logger(void) {
    pthread_once(&g_c_logger_once, init_c_logger_internal);
    return &g_c_logger_inst;
}

void safe_c_logger_log(const char* msg) {
    SafeCLogger* logger = get_safe_c_logger();
    printf("[%s] %s\n", logger->prefix, msg);
}
