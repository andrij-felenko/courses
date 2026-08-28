#define LOG_LEVEL_TRACE 0
#define LOG_LEVEL_DEBUG 1
#define LOG_LEVEL_INFO  2
#define LOG_LEVEL_WARN  3
#define LOG_LEVEL_ERROR 4
#define LOG_LEVEL_FATAL 5

/* Компіляційний поріг для Release-збірки */
#ifndef LOG_COMPILE_LEVEL
#define LOG_COMPILE_LEVEL LOG_LEVEL_INFO
#endif

extern uint8_t g_runtime_log_level;

#define LOG_EMIT(level, mod_id, token_id, payload_ptr, payload_len) do { \
    if ((level) >= LOG_COMPILE_LEVEL && (level) >= g_runtime_log_level) { \
        log_backend_write((level), (mod_id), (token_id), (payload_ptr), (payload_len)); \
    } \
} while(0)
