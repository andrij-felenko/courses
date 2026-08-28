// runner.cpp — C++20 ідіоматичний інструмент аудіювання Kmemleak
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <thread>
#include <chrono>
#include <cstdlib>
#include <filesystem>

namespace fs = std::filesystem;
using namespace std::chrono_literals;

class KmemleakController {
    fs::path debugfs_path_;

public:
    explicit KmemleakController(fs::path path = "/sys/kernel/debug/kmemleak")
        : debugfs_path_(std::move(path)) {}

    bool send_command(std::string_view cmd) const {
        std::ofstream ofs(debugfs_path_);
        if (!ofs.is_open()) return false;
        ofs << cmd << std::endl;
        return ofs.good();
    }

    [[nodiscard]] std::string read_reports() const {
        std::ifstream ifs(debugfs_path_);
        if (!ifs.is_open()) return {};
        return std::string((std::istreambuf_iterator<char>(ifs)),
                            std::istreambuf_iterator<char>());
    }
};

int main() {
    KmemleakController controller;

    std::cout << "[+] Очищення стану Kmemleak...\n";
    if (!controller.send_command("clear")) {
        std::cerr << "[-] Помилка доступу до debugfs. Перевірте root-права.\n";
        return EXIT_FAILURE;
    }

    std::cout << "[+] Запуск циклу тестування драйвера...\n";
    std::system("insmod ./dummy_leak_driver.ko && rmmod dummy_leak_driver");

    std::this_thread::sleep_for(500ms);

    std::cout << "[+] Запуск сканування пам'яті ядра...\n";
    if (!controller.send_command("scan")) {
        std::cerr << "[-] Не вдалося відправити команду scan.\n";
        return EXIT_FAILURE;
    }

    const auto report = controller.read_reports();
    if (report.empty()) {
        std::cout << "[SUCCESS] Пам'ять ядра чиста. Витоків немає.\n";
        return EXIT_SUCCESS;
    }

    std::cout << "[DEFECT] Виявлено витік пам'яті у драйвері!\n";
    std::cout << report << std::endl;
    return EXIT_FAILURE;
}
