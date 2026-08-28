// repl_sync.cpp — Інтерактивний REPL із автодоповненням на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <readline/readline.h>
#include <readline/history.h>

namespace minidb {

// RAII обгортка для динамічної пам'яті, виділеної бібліотекою Readline
struct ReadlineDeleter {
    void operator()(char* ptr) const noexcept {
        std::free(ptr);
    }
};
using UniqueString = std::unique_ptr<char, ReadlineDeleter>;

// RAII менеджер персистентної історії команд
class HistoryManager {
public:
    explicit HistoryManager(std::string filename, int max_entries = 100)
        : filename_(std::move(filename)), max_entries_(max_entries) {
        read_history(filename_.c_str());
    }

    ~HistoryManager() {
        write_history(filename_.c_str());
        history_truncate_file(filename_.c_str(), max_entries_);
    }

    HistoryManager(const HistoryManager&) = delete;
    HistoryManager& operator=(const HistoryManager&) = delete;

private:
    std::string filename_;
    int max_entries_;
};

class Completer {
public:
    static constexpr std::string_view COMMANDS[] = {
        "SELECT", "INSERT", "UPDATE", "DELETE",
        "CREATE", "DROP", "SHOW", "HELP", "EXIT"
    };

    static constexpr std::string_view TABLES[] = {
        "users", "accounts", "orders", "audit_log"
    };

    static char* CommandGen(const char* text, int state) {
        static size_t idx = 0;
        static size_t len = 0;

        if (state == 0) {
            idx = 0;
            len = std::strlen(text);
        }

        while (idx < std::size(COMMANDS)) {
            const auto& cmd = COMMANDS[idx++];
            if (cmd.size() >= len && ::strncasecmp(cmd.data(), text, len) == 0) {
                return ::strdup(cmd.data());
            }
        }
        return nullptr;
    }

    static char* TableGen(const char* text, int state) {
        static size_t idx = 0;
        static size_t len = 0;

        if (state == 0) {
            idx = 0;
            len = std::strlen(text);
        }

        while (idx < std::size(TABLES)) {
            const auto& tbl = TABLES[idx++];
            if (tbl.size() >= len && ::strncasecmp(tbl.data(), text, len) == 0) {
                return ::strdup(tbl.data());
            }
        }
        return nullptr;
    }

    static char** Dispatcher(const char* text, int start, int /*end*/) {
        rl_attempted_completion_over = 1;
        if (start == 0) {
            return rl_completion_matches(text, CommandGen);
        }
        return rl_completion_matches(text, TableGen);
    }
};

} // namespace minidb

static void handle_sigint(int /*sig*/) {
    write(1, "\n", 1);
    rl_on_new_line();
    rl_replace_line("", 0);
    rl_redisplay();
}

int main() {
    struct sigaction sa{};
    sa.sa_handler = handle_sigint;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, nullptr);

    minidb::HistoryManager history{".repl_history", 100};
    rl_attempted_completion_function = minidb::Completer::Dispatcher;
    rl_readline_name = "MiniDB";

    std::cout << "MiniDB Console (GNU Readline C++20). Введіть HELP або EXIT.\n";

    while (true) {
        minidb::UniqueString raw_line{readline("minidb> ")};
        if (!raw_line) {
            break; // Отримано EOF (Ctrl+D)
        }

        std::string_view line{raw_line.get()};
        if (line.empty()) {
            continue;
        }

        add_history(raw_line.get());

        if (line == "EXIT" || line == "exit" || line == "quit") {
            break;
        }

        if (line == "HELP" || line == "help") {
            std::cout << "Доступні команди: SELECT, INSERT, UPDATE, DELETE, SHOW, HELP, EXIT\n";
        } else {
            std::cout << "[Виконано]: " << line << "\n";
        }
    }

    std::cout << "\nСеанс завершено.\n";
    return 0;
}
