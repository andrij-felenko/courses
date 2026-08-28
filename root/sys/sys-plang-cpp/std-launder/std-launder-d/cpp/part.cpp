#include <new>
#include <iostream>

struct Config {
    const int timeout_ms;
};

void run() {
    auto* cfg = new Config{100};
    std::cout << cfg->timeout_ms << '\n'; // друкує 100

    cfg->~Config();                       // явне завершення часу життя
    new (cfg) Config{500};                // створення нового об'єкта в тому самому сховищі

    std::cout << cfg->timeout_ms << '\n'; // що надрукує оптимізована програма?
    delete cfg;
}
