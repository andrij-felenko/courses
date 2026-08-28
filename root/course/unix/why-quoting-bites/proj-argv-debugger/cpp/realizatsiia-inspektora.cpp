#include <iostream>
#include <string_view>
#include <vector>
#include <iomanip>
#include <span>
#include <cctype>

class ArgvInspector {
public:
    /* Статичний метод для повного форматованого аналізу аргументів */
    static void print_dump(std::span<char*> args) {
        std::cout << "==================== ARGV DUMP ====================\n";
        std::cout << "Кількість аргументів (argc): " << args.size() << "\n";
        std::cout << "---------------------------------------------------\n";

        for (std::size_t i = 0; i < args.size(); ++i) {
            std::string_view sv(args[i]);
            std::cout << "argv[" << std::setw(2) << i << "] (довжина: "
                      << std::setw(3) << sv.size() << " б) : \"" << sv << "\"\n";
            dump_bytes(sv);
        }
        std::cout << "===================================================\n";
    }

private:
    static void dump_bytes(std::string_view sv) {
        std::cout << "    [hex] ";
        for (unsigned char c : sv) {
            std::cout << std::hex << std::setw(2) << std::setfill('0')
                      << static_cast<int>(c) << " " << std::dec << std::setfill(' ');
        }
        std::cout << "\n    [asc] ";
        for (unsigned char c : sv) {
            if (std::isprint(c)) {
                std::cout << " " << static_cast<char>(c) << " ";
            } else if (c == '\n') {
                std::cout << "\\n ";
            } else if (c == '\t') {
                std::cout << "\\t ";
            } else if (c == ' ') {
                std::cout << "·  ";
            } else {
                std::cout << "?? ";
            }
        }
        std::cout << "\n";
    }
};

int main(int argc, char *argv[]) {
    std::span<char*> args(argv, static_cast<std::size_t>(argc));
    ArgvInspector::print_dump(args);
    return 0;
}
