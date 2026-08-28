// cli_parser.cpp — ідіоматична реалізація на C++20
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <span>
#include <charconv>
#include <cstdlib>
#include <getopt.h>

namespace cli {

struct Config {
    bool verbose{false};
    bool quiet{false};
    std::optional<std::string_view> output_file{};
    std::size_t buffer_size{4096};
    std::string_view color_mode{"auto"};
    std::vector<std::string_view> input_files{};
};

class ProgramInfo {
public:
    static constexpr std::string_view Name{"fileproc"};
    static constexpr std::string_view Version{"1.4.0"};

    static void print_version(std::ostream &os = std::cout) noexcept {
        os << Name << " version " << Version << "\n"
           << "Copyright (C) 2026 Open Systems Foundation.\n"
           << "License: MIT (free and open source software).\n";
    }

    static void print_help(std::ostream &os = std::cout) noexcept {
        os << "Usage: " << Name << " [OPTION]... [FILE]...\n"
           << "Process input files with customizable buffering and formatting.\n\n"
           << "Main operation mode:\n"
           << "  -o, --output=FILE       write processed data to FILE [default: stdout]\n"
           << "  -b, --buffer=BYTES      set processing buffer size in bytes [default: 4096]\n"
           << "      --color[=WHEN]      colorize console output; WHEN can be 'always',\n"
           << "                            'never', or 'auto' [default: auto]\n\n"
           << "Diagnostic and verbosity options:\n"
           << "  -v, --verbose           print detailed processing diagnostics\n"
           << "  -q, --quiet             suppress all warning and diagnostic messages\n\n"
           << "Informational options:\n"
           << "  -h, --help              display this help and exit\n"
           << "  -V, --version           output version information and exit\n\n"
           << "With no FILE, or when FILE is -, read standard input.\n"
           << "Exit status: 0 if OK, 1 if minor problems, 2 if serious trouble / invalid syntax.\n";
    }
};

class CommandLineParser {
public:
    static Config parse(std::span<char *> args) {
        Config cfg;
        const int argc = static_cast<int>(args.size());
        char **argv = args.data();

        // Скидаємо глобальний індекс для повторних запусків
        optind = 1;

        static constexpr const char *short_opts = "o:b:vqhV";
        static constexpr option long_opts[] = {
            {"output",   required_argument, nullptr, 'o'},
            {"buffer",   required_argument, nullptr, 'b'},
            {"color",    optional_argument, nullptr, 'c'},
            {"verbose",  no_argument,       nullptr, 'v'},
            {"quiet",    no_argument,       nullptr, 'q'},
            {"help",     no_argument,       nullptr, 'h'},
            {"version",  no_argument,       nullptr, 'V'},
            {nullptr, 0, nullptr, 0}
        };

        int opt;
        while ((opt = getopt_long(argc, argv, short_opts, long_opts, nullptr)) != -1) {
            switch (opt) {
                case 'o':
                    cfg.output_file = std::string_view{optarg};
                    break;
                case 'b': {
                    std::string_view sv{optarg};
                    std::size_t val = 0;
                    auto [ptr, ec] = std::from_chars(sv.data(), sv.data() + sv.size(), val);
                    if (ec != std::errc{} || ptr != sv.data() + sv.size() || val == 0) {
                        std::cerr << ProgramInfo::Name << ": invalid buffer size '" << sv << "'\n"
                                  << "Try '" << ProgramInfo::Name << " --help' for more information.\n";
                        std::exit(2);
                    }
                    cfg.buffer_size = val;
                    break;
                }
                case 'c':
                    if (optarg) {
                        std::string_view mode{optarg};
                        if (mode != "always" && mode != "never" && mode != "auto") {
                            std::cerr << ProgramInfo::Name << ": unrecognized color mode '" << mode << "'\n"
                                      << "Try '" << ProgramInfo::Name << " --help' for more information.\n";
                            std::exit(2);
                        }
                        cfg.color_mode = mode;
                    } else {
                        cfg.color_mode = "always";
                    }
                    break;
                case 'v':
                    cfg.verbose = true;
                    break;
                case 'q':
                    cfg.quiet = true;
                    break;
                case 'h':
                    ProgramInfo::print_help(std::cout);
                    std::exit(0);
                case 'V':
                    ProgramInfo::print_version(std::cout);
                    std::exit(0);
                case '?':
                default:
                    std::cerr << "Try '" << ProgramInfo::Name << " --help' for more information.\n";
                    std::exit(2);
            }
        }

        if (cfg.verbose && cfg.quiet) {
            std::cerr << ProgramInfo::Name << ": options --verbose and --quiet are mutually exclusive\n";
            std::exit(2);
        }

        for (int i = optind; i < argc; ++i) {
            cfg.input_files.emplace_back(argv[i]);
        }

        return cfg;
    }
};

} // namespace cli

int main(int argc, char *argv[]) {
    const auto cfg = cli::CommandLineParser::parse(std::span(argv, argc));

    if (cfg.verbose) {
        std::cout << "[DEBUG] Буфер: " << cfg.buffer_size
                  << " байт, Колір: " << cfg.color_mode
                  << ", Вивід: " << cfg.output_file.value_or("<stdout>") << "\n"
                  << "[DEBUG] Вхідних файлів для обробки: " << cfg.input_files.size() << "\n";
    }

    if (cfg.input_files.empty()) {
        if (!cfg.quiet) std::cout << "Читання даних зі стандартного вводу (stdin)...\n";
    } else {
        for (const auto &file : cfg.input_files) {
            if (!cfg.quiet) std::cout << "Обробка файлу: " << file << "\n";
        }
    }

    return 0;
}
