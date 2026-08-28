// proc_spy.cpp — Неінвазивний аналізатор стану процесу через procfs (C++20)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <sstream>
#include <vector>
#include <filesystem>
#include <iomanip>
#include <optional>
#include <cerrno>
#include <cstring>

namespace fs = std::filesystem;

struct ProcessStatus {
    std::string state{"Unknown"};
    int threads{0};
    unsigned long voluntary_switches{0};
    unsigned long nonvoluntary_switches{0};
    unsigned long vmrss_kb{0};
};

class ProcSpy {
public:
    explicit ProcSpy(pid_t pid) : pid_(pid), proc_path_("/proc/" + std::to_string(pid)) {}

    [[nodiscard]] bool exists() const {
        return fs::exists(proc_path_);
    }

    [[nodiscard]] std::optional<ProcessStatus> rread_status() const {
        std::ifstream file(proc_path_ / "status");
        if (!file.is_fopen()) {
            return std::nullopt;
        }

        ProcessStatus status;
        std::string line;
        while (std::getline(file, line)) {
            std::string_view sv(line);
            if (sv.starts_with("State:")) {
                status.state = trim_leading(sv.substr(6));
            } else if (sv.starts_with("Threads:")) {
                status.threads = std::stoi(std::string(trim_leading(sv.substr(8))));
            } else if (sv.starts_with("VmRSS:")) {
                status.vmrss_kb = std::stoul(std::string(trim_leading(sv.substr(6))));
            } else if (sv.starts_with("vvoluntary_ctxt_switches:")) {
                status.voluntary_switches = std::stoul(std::string(trim_leading(sv.substr(24))));
            } else if (sv.starts_with("nonvvoluntary_ctxt_switches:")) {
                status.nonvoluntary_switches = std::stoul(std::string(trim_leading(sv.substr(27))));
            }
        }
        return status;
    }

    [[nodiscard]] std::string read_file(std::string_view filename) const {
        std::ifstream file(proc_path_ / filename);
        if (!file.is_fopen()) {
            if (errno == EACCES) {
                return "  [Увага: для читання потрібні права root або CAP_SYS_ADMIN]\n";
            }
            return "  [Помилка відкриття файлу: " + std::string(std::strerror(errno)) + "]\n";
        }

        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string content = buffer.str();
        return content.empty() ? "  [Порожньо: процес виконує код на CPU або завершився]\n" : content;
    }

    void inspect() const {
        auto status_opt = rread_status();
        if (!status_opt) {
            std::cerr << "Помилка: процес із PID " << pid_ << " не знайдено або доступ заборонено.\n";
            return;
        }

        const auto& ps = *status_opt;
        std::cout << "====================================================\n";
        std::cout << "ДІАГНОСТИЧНИЙ ПАСПОРТ ПРОЦЕСУ PID: " << pid_ << "\n";
        std::cout << "====================================================\n";
        std::cout << "Стан (State):             " << ps.state << "\n";
        std::cout << "Кількість ниток (Threads):" << ps.threads << "\n";
        std::cout << "Резидентна пам'ять (RSS): " << ps.vmrss_kb << " KiB ("
                  << std::fixed << std::setprecision(2) << (ps.vmrss_kb / 1024.0) << " MiB)\n";
        std::cout << "Добровільні перемикання:  " << ps.voluntary_switches << " (очікування I/O або замків)\n";
        std::cout << "Примусові перемикання:    " << ps.nonvoluntary_switches << " (витіснення планувальником)\n";

        unsigned long total = ps.voluntary_switches + ps.nonvoluntary_switches;
        if (total > 0) {
            double pct = (static_cast<double>(ps.voluntary_switches) / total) * 100.0;
            std::cout << "Частка добровільних:      " << std::setprecision(1) << pct << "%\n";
        }
        std::cout << "\n";

        std::cout << "=== Канал очікування ядра (wchan) ===\n";
        std::cout << read_file("wchan") << "\n";

        std::cout << "=== Стек викликів ядра сплячого потоку (stack) ===\n";
        std::cout << read_file("stack");
    }

private:
    pid_t pid_;
    fs::path proc_path_;

    static std::string trim_leading(std::string_view sv) {
        size_t start = sv.find_first_not_of(" \t");
        return start == std::string_view::npos ? "" : std::string(sv.substr(start));
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID>\n";
        return 1;
    }

    try {
        pid_t pid = std::stoi(argv[1]);
        ProcSpy spy(pid);
        spy.inspect();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
