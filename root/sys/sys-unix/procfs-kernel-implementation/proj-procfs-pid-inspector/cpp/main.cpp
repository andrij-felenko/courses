#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <optional>
#include <system_error>

namespace fs = std::filesystem;

struct ProcessInfo {
    int pid;
    std::string name;
    std::string state;
    long vm_rss_kb{0};
    std::string exe_path;
    int open_fds_count{0};
};

class ProcInspector {
public:
    static std::optional<ProcessInfo> inspect(int pid) {
        if (pid <= 0) return std::nullopt;

        ProcessInfo info;
        info.pid = pid;

        const fs::path proc_dir = fs::path("/proc") / std::to_string(pid);
        if (!fs::exists(proc_dir)) {
            return std::nullopt;
        }

        // 1. Отримання символічного посилання exe за допомогою std::filesystem
        std::error_code ec;
        auto exe_target = fs::read_symlink(proc_dir / "exe", ec);
        if (!ec) {
            info.exe_path = exe_target.string();
        } else {
            info.exe_path = "<недоступно або недостатньо прав>";
        }

        // 2. Зчитування метаданих status за допомогою RAII потоків
        std::ifstream status_file(proc_dir / "status");
        if (!status_file.is_open()) {
            return std::nullopt;
        }

        std::string line;
        while (std::getline(status_file, line)) {
            std::string_view sv(line);
            if (sv.starts_with("Name:")) {
                auto val = sv.substr(5);
                size_t first = val.find_first_not_of(" \t");
                if (first != std::string_view::npos) {
                    info.name = std::string(val.substr(first));
                }
            } else if (sv.starts_with("State:")) {
                auto val = sv.substr(6);
                size_t first = val.find_first_not_of(" \t");
                if (first != std::string_view::npos) {
                    info.state = std::string(val.substr(first));
                }
            } else if (sv.starts_with("VmRSS:")) {
                auto val = sv.substr(6);
                size_t first = val.find_first_not_of(" \t");
                if (first != std::string_view::npos) {
                    info.vm_rss_kb = std::stol(std::string(val.substr(first)));
                }
            }
        }

        // 3. Підрахунок відкритих файлових дескрипторів за допомогою directory_iterator
        const fs::path fd_dir = proc_dir / "fd";
        ec.clear();
        fs::directory_iterator fd_it(fd_dir, ec);
        if (ec) {
            info.open_fds_count = -1; // Немає прав на каталог fd або процес уже помер
        } else {
            for (const auto& entry : fd_it) {
                (void)entry;
                info.open_fds_count++;
            }
        }

        return info;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID>\n";
        return 1;
    }

    int pid = std::stoi(argv[1]);
    auto info_opt = ProcInspector::inspect(pid);

    if (!info_opt) {
        std::cerr << "Помилка: Не вдалося прочитати /proc/" << pid << "\n";
        return 1;
    }

    const auto& info = *info_opt;
    std::cout << "=== Інспекція процесу PID " << info.pid << " ===\n"
              << "Назва:       " << info.name << "\n"
              << "Стан:        " << info.state << "\n"
              << "Шлях бінарн: " << info.exe_path << "\n"
              << "Пам'ять RSS: " << info.vm_rss_kb << " КБ\n";
    if (info.open_fds_count >= 0) {
        std::cout << "Дескриптори: " << info.open_fds_count << " відкритих fd\n";
    } else {
        std::cout << "Дескриптори: <немає доступу до /proc/" << info.pid << "/fd>\n";
    }

    return 0;
}
