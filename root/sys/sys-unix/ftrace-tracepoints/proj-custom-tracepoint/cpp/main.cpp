#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <csignal>
#include <atomic>
#include <chrono>
#include <thread>
#include <system_error>

namespace fs = std::filesystem;

class TracepointController {
public:
    explicit TracepointController(std::string_view subsys, std::string_view event)
        : basePath_("/sys/kernel/tracing/events/" + std::string(subsys) + "/" + std::string(event)) {
        disable();
        clearFilter();
    }

    ~TracepointController() {
        try {
            disable();
            clearFilter();
        } catch (...) {
            // Запобігаємо виходу винятків з деструктора
        }
    }

    TracepointController(const TracepointController&) = delete;
    TracepointController& operator=(const TracepointController&) = delete;

    bool setFilter(std::string_view filterExpression) const {
        return writeToFile(basePath_ / "filter", filterExpression);
    }

    bool enable() const {
        return writeToFile(basePath_ / "enable", "1");
    }

    bool disable() const noexcept {
        std::error_code ec;
        return writeToFileNoExcept(basePath_ / "enable", "0", ec);
    }

    bool clearFilter() const noexcept {
        std::error_code ec;
        return writeToFileNoExcept(basePath_ / "filter", "0", ec);
    }

private:
    fs::path basePath_;

    static bool writeToFile(const fs::path& path, std::string_view content) {
        std::ofstream file(path);
        if (!file.is_open()) {
            std::cerr << "Не вдалося записати у файл: " << path << '\n';
            return false;
        }
        file << content;
        return file.good();
    }

    static bool writeToFileNoExcept(const fs::path& path, std::string_view content, std::error_code& ec) noexcept {
        std::ofstream file(path);
        if (!file.is_open()) {
            return false;
        }
        file << content;
        return file.good();
    }
};

static std::atomic<bool> g_running{true};

void sigHandler(int) {
    g_running = false;
}

int main() {
    std::signal(SIGINT, sigHandler);
    std::signal(SIGTERM, sigHandler);

    TracepointController controller("sample_subsys", "sample_sensor_read");

    std::cout << "Налаштування ftrace (C++ RAII Controller)...\n";
    if (!controller.setFilter("raw_value > 40")) {
        std::cerr << "Переконайтеся, що модуль ядра tp_sample_mod завантажено.\n";
        return 1;
    }

    if (!controller.enable()) {
        std::cerr << "Не вдалося активувати подію.\n";
        return 1;
    }

    std::cout << "Читання /sys/kernel/tracing/trace_pipe (Ctrl+C для виходу)...\n";
    std::ifstream pipe("/sys/kernel/tracing/trace_pipe");
    if (!pipe.is_open()) {
        std::cerr << "Помилка відкриття trace_pipe (потрібні права root).\n";
        return 1;
    }

    std::string line;
    while (g_running && std::getline(pipe, line)) {
        std::cout << line << '\n';
    }

    std::cout << "\nЗавершення роботи. Автоматичне скидання налаштувань контролера.\n";
    return 0;
}
