// test_kobject_stress.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <array>

namespace {
    constexpr const char* SYSFS_PATH = "/sys/kernel/sample_device/baud_rate";
    constexpr int READER_THREADS = 7;
    std::atomic<bool> g_running{true};

    void reader_worker(int id) {
        std::string line;
        while (g_running.load(std::memory_order_relaxed)) {
            std::ifstream file(SYSFS_PATH);
            if (file.is_open()) {
                if (std::getline(file, line)) {
                    // Успішне зчитування атрибута kernfs
                }
            } else {
                // Модуль вивантажується або файл видалено
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
            std::this_thread::sleep_for(std::chrono::microseconds(500));
        }
    }

    void writer_worker() {
        const std::array<std::string, 6> values = {"9600", "19200", "38400", "57600", "115200", "230400"};
        size_t idx = 0;

        while (g_running.load(std::memory_order_relaxed)) {
            std::ofstream file(SYSFS_PATH);
            if (file.is_open()) {
                file << values[idx % values.size()] << std::endl;
                idx++;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }
}

int main() {
    std::cout << "[STRESS-CPP] Запуск потоків тестування sysfs: " << SYSFS_PATH << std::endl;

    std::vector<std::thread> workers;
    workers.reserve(READER_THREADS + 1);

    for (int i = 0; i < READER_THREADS; ++i) {
        workers.emplace_back(reader_worker, i);
    }
    workers.emplace_back(writer_worker);

    std::cout << "[STRESS-CPP] Потоки активні. Спробуйте вивантажити модуль ядра (rmmod).\n";
    std::this_thread::sleep_for(std::chrono::seconds(10));

    g_running.store(false, std::memory_order_relaxed);
    for (auto& t : workers) {
        if (t.joinable()) {
            t.join();
        }
    }

    std::cout << "[STRESS-CPP] Тестування завершено коректно.\n";
    return 0;
}
