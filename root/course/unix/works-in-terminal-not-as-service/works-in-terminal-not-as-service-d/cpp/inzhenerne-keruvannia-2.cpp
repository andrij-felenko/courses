#include <iostream>
#include <cstdio>
#include <unistd.h>

void setup_service_stdio() {
    // Вимикаємо синхронізацію C++ iostream зі стандартними C-буферами для швидкості
    std::ios_base::sync_with_stdio(false);

    if (!isatty(fileno(stdout))) {
        // Вмикаємо рядковий режим буферизації для потоку C
        setvbuf(stdout, nullptr, _IOLBF, 0);
    }
    
    setvbuf(stderr, nullptr, _IONBF, 0);

    if (!isatty(fileno(stdin))) {
        std::freopen("/dev/null", "r", stdin);
    }
}
