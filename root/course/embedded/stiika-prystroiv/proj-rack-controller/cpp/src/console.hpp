// Налагоджувальна консоль слота: сирий термінал, стрім наживо, очікування рядка.
#pragma once

#include <chrono>
#include <cstddef>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>

#include "posix.hpp"

struct ConsoleTimeout : std::runtime_error {
    using std::runtime_error::runtime_error;
};

class Console {
public:
    // Відкриває порт, ставить 8N1 raw і чистить чергу. Кидає, якщо не вийшло.
    Console(int slotId, int mirrorFd);

    // Чекає на pattern; повертає лог від місця збігу. Кидає ConsoleTimeout.
    std::string_view expect(std::string_view pattern, std::chrono::milliseconds timeout);

    // Просто вичитує потік задану тривалість (стрім у дзеркало триває).
    void drain(std::chrono::milliseconds duration);

    void flushInput() noexcept;

    [[nodiscard]] std::string_view log() const noexcept { return log_; }
    [[nodiscard]] bool trimmed() const noexcept { return trimmed_; }

private:
    // Скільки логу тримаємо: у прогоні на години цікавий свіжий хвіст.
    static constexpr std::size_t kLogCap = 256 * 1024;
    static constexpr int kEmptyReadsLimit = 8;

    std::size_t pump(std::chrono::milliseconds slice);
    void configureRaw(int slotId);
    void appendToLog(std::span<const char> data);
    void mirror(std::span<const char> data) noexcept;

    UniqueFd fd_;
    int mirrorFd_;
    std::string log_;
    std::size_t searchFrom_{0};
    int emptyReads_{0};
    bool trimmed_{false};
};
