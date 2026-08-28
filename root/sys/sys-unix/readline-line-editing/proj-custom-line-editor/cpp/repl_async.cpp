// repl_async.cpp — Неблокуючий цикл подій із Readline та poll() на C++20
#include <iostream>
#include <string_view>
#include <memory>
#include <chrono>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <poll.h>
#include <readline/readline.h>
#include <readline/history.h>

namespace async_repl {

inline volatile sig_atomic_t g_running{1};
inline volatile sig_atomic_t g_resized{0};

extern "C" void SignalHandler(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        g_running = 0;
    } else if (sig == SIGWINCH) {
        g_resized = 1;
    }
}

// RAII обгортка для колбек-інтерфейсу Readline
class CallbackSession {
public:
    explicit CallbackSession(const char* prompt, rl_vcpfunc_t* handler) {
        rl_callback_handler_install(prompt, handler);
    }

    ~CallbackSession() {
        rl_callback_handler_remove();
    }

    CallbackSession(const CallbackSession&) = delete;
    CallbackSession& operator=(const CallbackSession&) = delete;

    void ReadChar() const noexcept {
        rl_callback_read_char();
    }

    void Resize() const noexcept {
        rl_resize_terminal();
    }
};

extern "C" void OnLineEntered(char* raw_line) {
    if (!raw_line) {
        g_running = 0;
        return;
    }

    std::unique_ptr<char, void(*)(void*)> line{raw_line, std::free};
    std::string_view text{line.get()};

    if (!text.empty()) {
        add_history(line.get());
        if (text == "quit" || text == "exit") {
            g_running = 0;
        } else {
            std::cout << "[Оброблено команду]: " << text << "\n";
        }
    }
}

} // namespace async_repl

int main() {
    struct sigaction sa{};
    sa.sa_handler = async_repl::SignalHandler;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, nullptr);
    sigaction(SIGTERM, &sa, nullptr);
    sigaction(SIGWINCH, &sa, nullptr);

    async_repl::CallbackSession session{"async-shell> ", async_repl::OnLineEntered};

    pollfd pfd{};
    pfd.fd = STDIN_FILENO;
    pfd.events = POLLIN;

    auto last_tick = std::chrono::steady_clock::now();

    while (async_repl::g_running) {
        if (async_repl::g_resized) {
            async_repl::g_resized = 0;
            session.Resize();
        }

        int ret = poll(&pfd, 1, 500);

        if (ret > 0 && (pfd.revents & POLLIN)) {
            session.ReadChar();
        }

        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - last_tick).count() >= 5) {
            last_tick = now;

            // Безпечне виведення фонового тексту без затирання введеного рядка
            rl_save_prompt();
            write(1, "\n[Фонова подія C++]: таймер спрацював\n", 40);
            rl_restore_prompt();
            rl_forced_update_display();
        }
    }

    std::cout << "\nАсинхронний цикл завершено.\n";
    return 0;
}
