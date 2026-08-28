#include <stdio.h>

// Сумісний C-макрос із розширенням GNU/Clang
#if defined(__GNUC__) || defined(__clang__)
#define LOG_MSG(fmt, ...) printf("[LOG] " fmt "\n", ##__VA_ARGS__)
#elif defined(_MSC_VER)
#define LOG_MSG(fmt, ...) printf("[LOG] " fmt "\n", __VA_ARGS__)
#endif

void run_c_demo(void) {
    LOG_MSG("System initialized");
    LOG_MSG("Values: %d, %d", 10, 20);
}
