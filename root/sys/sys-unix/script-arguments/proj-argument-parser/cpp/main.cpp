// Ідіоматична реалізація CLI-парсера мовою C++20 з використанням std::string_view
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <cstdlib>
#include <getopt.h>

struct ProgramConfig {
    std::string_view output_file;
    bool force{false};
    std::vector<std::string_view> positional_files;
};

static void print_usage(std::string_view progname) {
    std::cout << "Використання: " << progname << " [ОПЦІЇ] [ФАЙЛ ...]\n"
              << "  -h, --help            Показати довідку\n"
              << "  -v, --version         Показати версію\n"
              << "  -o, --output FILE     Файл виводу\n"
              << "  -f, --force           Примусовий перезапис\n";
}

int main(int argc, char *argv[]) {
    static const struct option long_options[] = {
        {"help",    no_argument,       nullptr, 'h'},
        {"version", no_argument,       nullptr, 'v'},
        {"output",  required_argument, nullptr, 'o'},
        {"force",   no_argument,       nullptr, 'f'},
        {nullptr,   0,                 nullptr, 0}
    };

    ProgramConfig config;
    int opt;

    while ((opt = ::getopt_long(argc, argv, "hvo:f", long_options, nullptr)) != -1) {
        switch (opt) {
        case 'h':
            print_usage(argv[0]);
            return 0;
        case 'v':
            std::cout << "cli_parser_cpp 1.4.0\n";
            return 0;
        case 'o':
            config.output_file = optarg;
            break;
        case 'f':
            config.force = true;
            break;
        case '?':
            return 2;
        default:
            return 2;
        }
    }

    if (config.output_file.empty()) {
        std::cerr << argv[0] << ": Помилка: опція -o/--output є обов'язковою\n";
        return 2;
    }

    for (int i = optind; i < argc; ++i) {
        config.positional_files.emplace_back(argv[i]);
    }

    std::cout << "Вивід: " << config.output_file << ", Force: " << std::boolalpha << config.force << "\n";
    std::cout << "Кількість позиційних файлів: " << config.positional_files.size() << "\n";

    for (const auto &file : config.positional_files) {
        std::cout << "  -> Операнд: [" << file << "]\n";
    }

    return 0;
}
