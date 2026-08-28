// Ідіоматична реалізація на C++20 з використанням std::string_view, std::span та RAII
#include <iostream>
#include <string_view>
#include <span>
#include <vector>
#include <unistd.h>

struct ProgramOptions {
    bool verbose{false};
    std::string_view output_file{};
    std::vector<std::string_view> positional_files{};
};

int main(int argc, char* argv[])
{
    ProgramOptions opts;
    int opt = 0;

    // Скидаємо optind для передбачуваної поведінки
    optind = 1;
    opterr = 1;

    while ((opt = getopt(argc, argv, "vo:")) != -1) {
        switch (opt) {
        case 'v':
            opts.verbose = true;
            break;
        case 'o':
            opts.output_file = optarg;
            break;
        case '?':
        default:
            std::cerr << "Використання: " << argv[0] 
                      << " [-v] [-o output] file1 [file2 ...]\n";
            return 1;
        }
    }

    // Забираємо позиційні аргументи через безпечний діапазон std::span
    std::span<char*> raw_args(argv, argc);
    for (size_t i = static_cast<size_t>(optind); i < raw_args.size(); ++i) {
        opts.positional_files.emplace_back(raw_args[i]);
    }

    std::cout << "Прапорець verbose: " << (opts.verbose ? "увімкнено" : "вимкнено") << '\n';
    std::cout << "Файл виводу: " << (opts.output_file.empty() ? "(за замовчуванням)" : opts.output_file) << '\n';
    std::cout << "Позиційні аргументи (файли):\n";
    for (const auto& file : opts.positional_files) {
        std::cout << "  файл: " << file << '\n';
    }

    return 0;
}
