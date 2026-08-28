#include <fstream>
#include <string>

struct LogEntry {
    std::string timestamp;
    std::string level;
    std::string message;
};

// Лінивий генератор рядків із файлу
std::generator<std::string> read_lines(std::string path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        co_return;
    }
    std::string line;
    while (std::getline(file, line)) {
        co_yield line; // Зупинка та передача рядка викликачу
    }
}

// Перетворювач рядків у LogEntry
std::generator<LogEntry> parse_logs(std::string path) {
    for (std::string line : read_lines(std::move(path))) {
        if (line.empty() || line.starts_with('#')) {
            continue; // Пропускаємо коментарі та порожні рядки
        }
        
        // Парсинг тексту формату: "TIMESTAMP [LEVEL] MESSAGE"
        auto first_space = line.find(' ');
        auto open_bracket = line.find('[');
        auto close_bracket = line.find(']');

        if (first_space != std::string::npos && 
            open_bracket != std::string::npos && 
            close_bracket != std::string::npos) {
            
            LogEntry entry{
                .timestamp = line.substr(0, first_space),
                .level = line.substr(open_bracket + 1, close_bracket - open_bracket - 1),
                .message = line.substr(close_bracket + 2)
            };
            co_yield entry; // Передача структурованого запису
        }
    }
}
