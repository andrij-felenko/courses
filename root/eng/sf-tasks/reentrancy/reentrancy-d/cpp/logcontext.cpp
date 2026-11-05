#include <iostream>
#include <array>
#include <string_view>

namespace ReentrantLogging {
    // Структура контексту виклику без глобального чи статичного стану
    struct LogContext {
        std::array<char, 256> buffer{};
        std::size_t write_pos{0};
    };

    // Повністю реентерабельна функція формування повідомлення
    void append_message(LogContext& ctx, std::string_view text) {
        for (char ch : text) {
            if (ctx.write_pos < ctx.buffer.size() - 1) {
                ctx.buffer[ctx.write_pos] = ch;
                ctx.write_pos++;
            }
        }
        ctx.buffer[ctx.write_pos] = '\0';
    }
}

void safe_cpp_signal_handler(int sig) {
    (void)sig;
    ReentrantLogging::LogContext signal_ctx;
    ReentrantLogging::append_message(signal_ctx, "[SIGNAL_CPP_SAFE] Executed safely!");
}
