// Ідіоматична C++ обгортка для реєстрації генератора GNU Readline
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <cstring>
#include <readline/readline.h>
#include <readline/history.h>

class ShellCompleter {
public:
    static inline const std::vector<std::string> kCommands = {
        "status", "start", "stop", "restart", "reload", "isolate"
    };

    static char* Generator(const char* text, int state) {
        static size_t index = 0;
        static size_t len = 0;

        if (state == 0) {
            index = 0;
            len = std::strlen(text);
        }

        while (index < kCommands.size()) {
            const auto& candidate = kCommands[index++];
            if (candidate.compare(0, len, text) == 0) {
                // Readline вимагає пам'ять, виділену через malloc
                char* match = static_cast<char*>(std::malloc(candidate.size() + 1));
                if (match) {
                    std::strcpy(match, candidate.c_str());
                }
                return match;
            }
        }
        return nullptr;
    }

    static char** AttemptedCompletion(const char* text, int start, int /*end*/) {
        if (start == 0) {
            return rl_completion_matches(text, Generator);
        }
        return nullptr; // Перехід до стандартного пошуку файлів
    }
};

int main() {
    rl_attempted_completion_function = ShellCompleter::AttemptedCompletion;

    while (true) {
        std::unique_ptr<char, void(*)(void*)> input(readline("my-shell> "), std::free);
        if (!input) {
            break;
        }
        if (*input.get() != '\0') {
            add_history(input.get());
            std::cout << "Виконання: " << input.get() << '\n';
        }
    }
    return 0;
}
