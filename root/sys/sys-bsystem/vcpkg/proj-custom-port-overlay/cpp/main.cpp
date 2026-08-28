// src/main.cpp
#include "telemetry_consumer.hpp"
#include <fmt/core.h>
#include <vector>
#include <chrono>

int main() {
    std::vector<telemetry::Record> batch{
        {1700000000000ULL, 101, 23.85},
        {1700000001000ULL, 102, 101.32}
    };

    fmt::print("Ініціалізація відправлення {} записів телеметрії...\n", batch.size());
    
    if (telemetry::dispatch_records(batch)) {
        fmt::print("Телеметрію успішно передано до агрегатора fast-telemetry.\n");
        return 0;
    }

    fmt::print(stderr, "Помилка передавання кадру телеметрії!\n");
    return 1;
}
