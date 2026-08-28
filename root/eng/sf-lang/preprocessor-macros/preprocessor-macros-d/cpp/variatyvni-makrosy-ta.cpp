#include <iostream>
#include <cstdio>

#define LOG_MSG(fmt, ...) std::printf(fmt __VA_OPT__(,) __VA_ARGS__)

int main() {
    LOG_MSG("Повідомлення без аргументів\n");
    LOG_MSG("Координати: x=%d, y=%d\n", 10, 20);
    return 0;
}
