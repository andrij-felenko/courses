#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <regex>
#include <filesystem>

namespace fs = std::filesystem;

struct EventField {
    std::string declaration;
    int offset{0};
    int size{0};
    bool is_signed{false};
};

void parse_event_format(const fs::path& format_path) {
    std::ifstream file(format_path);
    if (!file.is_open()) {
        std::cerr << "Не вдалося відкрити: " << format_path << '\n';
        return;
    }

    std::cout << "Розбір структури події: " << format_path.string() << '\n';
    
    // field:char next_comm[16];\toffset:40;\tsize:16;\tsigned:0;
    std::regex field_regex(R"(field:([^;]+);\s+offset:(\d+);\s+size:(\d+);\s+signed:(\d+);)");
    std::string line;

    while (std::getline(file, line)) {
        if (line.find("common_") != std::string::npos) {
            continue; // Пропускаємо загальні службові поля заголовка
        }

        std::smatch match;
        if (std::regex_search(line, match, field_regex)) {
            EventField field{
                .declaration = match[1].str(),
                .offset = std::stoi(match[2].str()),
                .size = std::stoi(match[3].str()),
                .is_signed = (match[4].str() == "1")
            };

            std::cout << "  Поле: " << field.declaration
                      << " | Зміщення: " << field.offset
                      << " | Розмір: " << field.size << " байт"
                      << " | Знак: " << (field.is_signed ? "signed" : "unsigned") << '\n';
        }
    }
}

int main() {
    parse_event_format("/sys/kernel/tracing/events/sched/sched_switch/format");
    return 0;
}
