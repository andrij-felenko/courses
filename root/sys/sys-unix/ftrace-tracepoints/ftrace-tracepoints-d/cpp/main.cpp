#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <csignal>
#include <atomic>
#include <system_error>
#include <unistd.h>

namespace fs = std::filesystem;

class ScopedTracepoint {
public:
    ScopedTracepoint(std::string_view subsystem, std::string_view eventName)
        : basePath_("/sys/kernel/tracing/events/" + std::string(subsystem) + "/" + std::string(eventName)) {
        disable();
        clearFilter();
    }

    ~ScopedTracepoint() {
        try {
            disable();
            clearFilter();
        } catch (...) {
            // Запобігаємо виходу винятків з деструктора
        }
    }

    ScopedTracepoint(const ScopedTracepoint&) = delete;
    ScopedTracepoint& operator=(const ScopedTracepoint&) = delete;

    void setFilter(std::string_view filterExpr) const {
        writeControlFile(basePath_ / "filter", filterExpr);
    }

    void enable() const {
        writeControlFile(basePath_ / "enable", "1");
    }

    void disable() const noexcept {
        std::error_code ec;
        writeControlFileNoExcept(basePath_ / "enable", "0", ec);
    }

    void clearFilter() const noexcept {
        std::error_code ec;
        writeControlFileNoExcept(basePath_ / "filter", "0", ec);
    }

private:
    fs::path basePath_;

    static void writeControlFile(const fs::path& path, std::string_view content) {
        std::ofstream stream(path);
        if (!stream.is_open()) {
            throw std::runtime_error("Не вдалося відкрити для запису: " + path.string());
        }
        stream << content;
        if (!stream.good()) {
            throw std::runtime_error("Помилка запису у файл: " + path.string());
        }
    }

    static void writeControlFileNoExcept(const fs::path& path, std::string_view content, std::error_code& ec) noexcept {
        std::ofstream stream(path);
        if (stream.is_open()) {
            stream << content;
        }
    }
};

static std::atomic<bool> g_terminated{false};

void signalHandler(int) {
    g_terminated = true;
}

int main() {
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    try {
        std::cout << "Ініціалізація C++ RAII трасера точки syscalls:sys_enter_openat...\n";
        ScopedTracepoint tp("syscalls", "sys_enter_openat");

        std::string filter = "common_pid != " + std::to_string(getpid());
        tp.setFilter(filter);
        tp.enable();

        std::ifstream pipeStream("/sys/kernel/tracing/trace_pipe");
        if (!pipeStream.is_open()) {
            std::cerr << "Помилка відкриття /sys/kernel/tracing/trace_pipe (потрібен root).\n";
            return 1;
        }

        std::cout << "Слухання подій у реальному часі (Ctrl+C для виходу)...\n";
        std::string line;

        while (!g_terminated && std::getline(pipeStream, line)) {
            std::cout << line << '\n';
        }

        std::cout << "\nЗавершення роботи. Автоматичне скидання налаштувань tracefs...\n";
    } catch (const std::exception& ex) {
        std::cerr << "Виникла виняткова ситуація: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
