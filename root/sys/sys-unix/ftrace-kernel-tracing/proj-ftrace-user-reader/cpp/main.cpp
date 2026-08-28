#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <csignal>
#include <system_error>
#include <memory>
#include <vector>
#include <array>
#include <fcntl.h>
#include <unistd.h>

namespace fs = std::filesystem;

namespace ftrace {

static volatile std::sig_atomic_t g_stop_requested = 0;

void signal_handler(int) {
    g_stop_requested = 1;
}

class TracefsSession {
public:
    explicit TracefsSession(fs::path tracefs_root = "/sys/kernel/tracing")
        : root_path_(std::move(tracefs_root))
    {
        if (!fs::exists(root_path_)) {
            throw std::runtime_error("tracefs не змонтовано за шляхом: " + root_path_.string());
        }
        
        // Зберігаємо початкові налаштування для відновлення в деструкторі (RAII)
        stop_tracing();
        set_file_content("set_ftrace_filter", "");
        set_file_content("set_ftrace_notrace", "");
    }

    ~TracefsSession() noexcept {
        try {
            stop_tracing();
            set_file_content("current_tracer", "nop");
            set_file_content("set_ftrace_filter", "");
            std::cout << "[+] RAII: Ресурси tracefs успішно відновлено.\n";
        } catch (const std::exception& e) {
            std::cerr << "[-] Помилка в деструкторі TracefsSession: " << e.what() << '\n';
        }
    }

    // Заборона копіювання (семантика володіння ресурсом)
    TracefsSession(const TracefsSession&) = delete;
    TracefsSession& operator=(const TracefsSession&) = delete;

    void configure_function_tracer(std::string_view filter_pattern) {
        stop_tracing();
        set_file_content("set_ftrace_filter", filter_pattern);
        set_file_content("current_tracer", "function");
    }

    void start_tracing() {
        set_file_content("tracing_on", "1");
    }

    void stop_tracing() {
        set_file_content("tracing_on", "0");
    }

    void stream_pipe() {
        const auto pipe_path = root_path_ / "trace_pipe";
        int fd = ::open(pipe_path.c_str(), O_RDONLY);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити trace_pipe");
        }

        std::array<char, 4096> buffer{};
        while (!g_stop_requested) {
            ssize_t count = ::read(fd, buffer.data(), buffer.size() - 1);
            if (count > 0) {
                buffer[static_cast<size_t>(count)] = '\0';
                std::cout.write(buffer.data(), count);
                std::cout.flush();
            } else if (count < 0) {
                if (errno == EINTR) continue;
                ::close(fd);
                throw std::system_error(errno, std::generic_category(), "Помилка читання з trace_pipe");
            }
        }
        ::close(fd);
    }

private:
    fs::path root_path_;

    void set_file_content(std::string_view relative_file, std::string_view value) {
        const auto target = root_path_ / relative_file;
        std::ofstream ofs(target);
        if (!ofs.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл керування: " + target.string());
        }
        ofs << value;
        if (!ofs) {
            throw std::runtime_error("Помилка запису в файл керування: " + target.string());
        }
    }
};

} // namespace ftrace

int main() {
    std::signal(SIGINT, ftrace::signal_handler);
    std::signal(SIGTERM, ftrace::signal_handler);

    try {
        std::cout << "[+] Ініціалізація RAII-сесії ftrace...\n";
        ftrace::TracefsSession session;

        session.configure_function_tracer("do_sys_open*");
        session.start_tracing();

        std::cout << "[+] Моніторинг відкриття файлів через tracefs (Ctrl+C для виходу)...\n";
        session.stream_pipe();

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
