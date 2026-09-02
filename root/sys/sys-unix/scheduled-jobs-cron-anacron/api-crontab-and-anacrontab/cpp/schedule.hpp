// Розклад cron: розбір п'яти часових полів у бітові набори, зіставлення з
// часом, сон без дрейфу та стеження за змінами таблиць.
#pragma once

#include "day_match.hpp"
#include "posix.hpp"

#include <bitset>
#include <chrono>
#include <expected>
#include <filesystem>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace minicron {

struct ParseError {
    std::string field;    // "minute", "hour", …
    std::string detail;
    [[nodiscard]] std::string message() const;   // «bad minute: …»
};

class Schedule {
public:
    struct Parsed {
        Schedule schedule;
        std::string_view rest;   // усе після п'яти полів або макроса
    };

    // Помилку віддаємо значенням: хибний рядок таблиці — це не виняткова
    // ситуація, а звичайний результат розбору чужого файлу.
    static std::expected<Parsed, ParseError> parse(std::string_view line);

    [[nodiscard]] bool matches(const std::tm& now) const noexcept;
    [[nodiscard]] bool at_reboot() const noexcept { return reboot_; }
    [[nodiscard]] std::string_view day_rule() const noexcept { return days_.rule(); }

private:
    std::bitset<60> minutes_;
    std::bitset<24> hours_;
    std::bitset<13> months_;   // біти 1..12
    DayFields days_;
    bool reboot_ = false;
};

// Скільки лишилося до нульової секунди наступної хвилини.
std::chrono::seconds seconds_to_next_minute(std::chrono::system_clock::time_point now);

// inotify там, де він доступний, інакше — опитування часу модифікації.
class SourceWatch {
public:
    explicit SourceWatch(std::span<const std::filesystem::path> paths);

    [[nodiscard]] int fd() const noexcept { return inotify_.get(); }
    [[nodiscard]] bool polling() const noexcept { return !inotify_.valid(); }
    [[nodiscard]] bool changed();

private:
    bool stamps_changed();

    UniqueFd inotify_;
    std::vector<std::filesystem::path> paths_;
    std::vector<std::optional<std::filesystem::file_time_type>> stamps_;
};

}  // namespace minicron
