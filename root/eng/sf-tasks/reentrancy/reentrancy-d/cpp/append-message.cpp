#include <iostream>
#include <array>
#include <csignal>
#include <unistd.h>

namespace UnsafeLogging {
    // Статичний масив та лічильник у просторі імен
    static std::array<char, 256> g_log_buffer;
    static std::size_t g_write_pos = 0;

    // Нереентерабельна функція формування повідомлення
    void append_message(const char* text) {
        g_write_pos = 0;
        
        for (std::size_t i = 0; text[i] != '\0'; ++i) {
            if (g_write_pos < g_log_buffer.size() - 1) {
                g_log_buffer[g_write_pos] = text[i];
                g_write_pos++;
                usleep(1);
            }
        }
        g_log_buffer[g_write_pos] = '\0';
    }
}

void cpp_signal_handler(int sig) {
    (void)sig;
    UnsafeLogging::append_message("[SIGNAL_CPP] Interrupted!");
}
