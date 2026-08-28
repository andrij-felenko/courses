#include <mutex>
#include <iostream>
#include <string_view>

namespace safe_logger {

static std::mutex g_log_mutex{};

void log_message(std::string_view msg) {
    std::lock_guard<std::mutex> guard(g_log_mutex);
    /* Критична секція запису в лог */
    std::cout << "[LOG]: " << msg << '\n';
}

} // namespace safe_logger
