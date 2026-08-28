#include <iostream>
#include <cstdio>

#define DBG_PRINT(tag, fmt, ...) \
    std::printf("[" tag "] " fmt "\n" __VA_OPT__(,) __VA_ARGS__)

int main() {
    DBG_PRINT("NET", "З'єднання встановлено");
    DBG_PRINT("CPU", "Завантаження: %d%%, Температура: %d C", 45, 62);
    return 0;
}
