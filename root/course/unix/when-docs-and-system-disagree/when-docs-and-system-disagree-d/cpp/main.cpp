// Ідіоматична реалізація аудиту середовища на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <cstdlib>
#include <clocale>
#include <ranges>

namespace fs = std::filesystem;

void inspect_locale()
{
    const char* loc = std::setlocale(LC_ALL, "");
    std::cout << "[1] Системна локаль: " << (loc ? loc : "не визначено") << '\n';
    const char* collate = std::getenv("LC_COLLATE");
    std::cout << "    LC_COLLATE: " << (collate ? collate : "(за замовчуванням)") << '\n';
}

void resolve_command(std::string_view cmd_name)
{
    std::cout << "[2] Дослідження команди: " << cmd_name << '\n';

    // Якщо передано прямий шлях
    if (cmd_name.find('/') != std::string_view::npos) {
        std::error_code ec;
        fs::path p(cmd_name);
        fs::path canonical_path = fs::canonical(p, ec);
        if (!ec) {
            std::cout << "    Прямий шлях знайдено: " << canonical_path.string() << '\n';
        } else {
            std::cout << "    Шлях недоступний: " << ec.message() << '\n';
        }
        return;
    }

    const char* path_env = std::getenv("PATH");
    if (!path_env) {
        std::cerr << "    Змінна PATH відсутня в середовищі!\n";
        return;
    }

    std::string_view path_view(path_env);
    int found_count = 0;

    // Розбір PATH через ranges string_view (C++20)
    for (const auto dir_range : std::views::split(path_view, ':')) {
        std::string dir_str(dir_range.begin(), dir_range.end());
        if (dir_str.empty()) continue;

        fs::path candidate = fs::path(dir_str) / cmd_name;
        std::error_code ec;

        // Перевірка існування та прав на виконання
        auto status = fs::status(candidate, ec);
        if (!ec && fs::exists(status) && !fs::is_directory(status)) {
            auto perms = status.permissions();
            bool is_executable = (perms & (fs::perms::owner_exec | fs::perms::group_exec | fs::perms::others_exec)) != fs::perms::none;
            
            if (is_executable) {
                fs::path canonical_target = fs::canonical(candidate, ec);
                std::cout << "    Знайдено у PATH [" << ++found_count << "]: " 
                          << candidate.string() << " -> " 
                          << (ec ? candidate.string() : canonical_target.string()) << '\n';
            }
        }
    }

    if (found_count == 0) {
        std::cout << "    Команду '" << cmd_name << "' не знайдено у каталогах PATH.\n";
    }
}

int main(int argc, char* argv[])
{
    std::string_view target = (argc > 1) ? argv[1] : "grep";
    std::cout << "=== Системний аудит середовища виконання (C++20) ===\n";
    inspect_locale();
    resolve_command(target);
    return 0;
}
