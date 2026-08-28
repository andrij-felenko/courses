// C++17: Нуль-алокаційний парсер на основі std::string_view
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>

struct LogEntry {
    std::string_view timestamp;
    std::string_view level;
    std::string_view module;
    std::string_view message;
};

class LogParser {
public:
    // Розбір одного рядка за O(1) додаткової пам'яті
    static std::optional<LogEntry> parse_line(std::string_view line) noexcept {
        LogEntry entry;

        // 1. Витяг timestamp: [2026-08-14...]
        auto open_bracket = line.find('[');
        auto close_bracket = line.find(']');
        if (open_bracket == std::string_view::npos || close_bracket == std::string_view::npos) {
            return std::nullopt;
        }
        entry.timestamp = line.substr(open_bracket + 1, close_bracket - open_bracket - 1);

        // Зсуваємо вікно за перший тег
        line.remove_prefix(close_bracket + 1);

        // 2. Витяг level: [ERROR]
        open_bracket = line.find('[');
        close_bracket = line.find(']');
        if (open_bracket == std::string_view::npos || close_bracket == std::string_view::npos) {
            return std::nullopt;
        }
        entry.level = line.substr(open_bracket + 1, close_bracket - open_bracket - 1);

        line.remove_prefix(close_bracket + 1);

        // 3. Витяг module: [NETWORKING]
        open_bracket = line.find('[');
        close_bracket = line.find(']');
        if (open_bracket == std::string_view::npos || close_bracket == std::string_view::npos) {
            return std::nullopt;
        }
        entry.module = line.substr(open_bracket + 1, close_bracket - open_bracket - 1);

        line.remove_prefix(close_bracket + 1);

        // 4. Залишок рядка — це повідомлення (видаляємо початкові пробіли)
        auto msg_start = line.find_first_not_of(" \t");
        if (msg_start != std::string_view::npos) {
            line.remove_prefix(msg_start);
        }
        entry.message = line;

        return entry;
    }
};

int main() {
    // Вхідний буфер вказано як строковий літерал (живе в сегменті read-only даних)
    std::string_view log_data = 
        "[2026-08-14T19:00:00.123] [ERROR] [NETWORKING] Socket connection reset by peer\n"
        "[2026-08-14T19:00:00.125] [INFO] [DATABASE] Query executed successfully";

    std::size_t line_start = 0;
    while (line_start < log_data.size()) {
        auto line_end = log_data.find('\n', line_start);
        if (line_end == std::string_view::npos) {
            line_end = log_data.size();
        }

        std::string_view line = log_data.substr(line_start, line_end - line_start);
        auto entry = LogParser::parse_line(line);

        if (entry) {
            std::cout << "Parsed Log Entry:\n"
                      << "  Time:    " << entry->timestamp << "\n"
                      << "  Level:   " << entry->level << "\n"
                      << "  Module:  " << entry->module << "\n"
                      << "  Message: " << entry->message << "\n\n";
        }

        line_start = line_end + 1;
    }
    return 0;
}
