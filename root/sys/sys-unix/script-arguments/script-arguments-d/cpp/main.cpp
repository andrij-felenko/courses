// Ідіоматичний розбір аргументів мовою C++20 із застосуванням std::string_view
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <getopt.h>

struct ProgramOptions {
    bool verbose{false};
    std::optional<std::string_view> output;
    std::vector<std::string_view> operands;
};

int main(int argc, char *argv[]) {
    static const struct option long_opts[] = {
        {"help",    no_argument,       nullptr, 'h'},
        {"verbose", no_argument,       nullptr, 'v'},
        {"output",  required_argument, nullptr, 'o'},
        {nullptr,   0,                 nullptr, 0}
    };

    ProgramOptions config;
    int opt;

    while ((opt = ::getopt_long(argc, argv, ":hvo:", long_opts, nullptr)) != -1) {
        switch (opt) {
        case 'h':
            std::cout << "Використання: " << argv[0] << " [-v] [-o FILE] [OPERANDS...]\n";
            return 0;
        case 'v':
            config.verbose = true;
            break;
        case 'o':
            config.output = std::string_view(optarg);
            break;
        case ':':
            std::cerr << argv[0] << ": опція вимагає значення аргументу\n";
            return 1;
        case '?':
            std::cerr << argv[0] << ": виявлено невідому опцію\n";
            return 1;
        default:
            return 1;
        }
    }

    for (int i = optind; i < argc; ++i) {
        config.operands.emplace_back(argv[i]);
    }

    return 0;
}
