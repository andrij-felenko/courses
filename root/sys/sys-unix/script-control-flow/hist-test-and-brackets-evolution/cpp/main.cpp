#include <iostream>
#include <string_view>
#include <span>
#include <cstdlib>

int main(int argc, char* argv[]) {
    std::span<char*> args(argv, argc);
    if (!args.empty()) {
        std::string_view prog_name = args.front();
        if (prog_name == "[" || prog_name == "/bin/[" || prog_name.ends_with("/[")) {
            if (args.size() < 2 || std::string_view(args.back()) != "]") {
                std::cerr << "[: missing ]\n";
                return 2;
            }
            /* Відкидаємо останній аргумент ']' */
            args = args.subspan(0, args.size() - 1);
        }
    }
    /* Подальший розбір предикатів test */
    return 0;
}
