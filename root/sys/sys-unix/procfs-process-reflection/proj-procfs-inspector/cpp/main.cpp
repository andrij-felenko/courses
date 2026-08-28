#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <filesystem>
#include <system_error>
#include <cstdio>
#include <unistd.h>

namespace fs = std::filesystem;

struct ProcessMetrics {
    pid_t pid{0};
    std::string comm;
    char state{'?'};
    pid_t ppid{0};
    unsigned long utime{0};
    unsigned long stime{0};
    long num_threads{0};
    unsigned long vsize{0};
    long rss_pages{0};
};

class ProcfsInspector {
public:
    // Безпечний розбір /proc/[pid]/stat через string_view та rfind
    static std::optional<ProcessMetrics> readStat(pid_t pid) {
        const std::string path = "/proc/" + std::to_string(pid) + "/stat";
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;

        std::string content;
        std::getline(file, content);
        if (content.empty()) return std::nullopt;

        const size_t first_paren = content.find('(');
        const size_t last_paren = content.rfind(')');

        if (first_paren == std::string::npos || last_paren == std::string::npos || first_paren >= last_paren) {
            return std::nullopt;
        }

        ProcessMetrics metrics;
        metrics.pid = std::stoi(content.substr(0, first_paren));
        metrics.comm = content.substr(first_paren + 1, last_paren - first_paren - 1);

        // Парсимо залишок рядка після останньої закриваючої дужки
        std::string_view rest(content.data() + last_paren + 2, content.size() - last_paren - 2);
        
        // Розбираємо параметри після ')'
        int assigned = ::sscanf(rest.data(),
            "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %ld %*d %*u %lu %ld",
            &metrics.state,
            &metrics.ppid,
            &metrics.utime,
            &metrics.stime,
            &metrics.num_threads,
            &metrics.vsize,
            &metrics.rss_pages);

        if (assigned != 7) return std::nullopt;
        return metrics;
    }

    // Читання командного рядка із заміною нуль-байтів
    static std::string readCmdline(pid_t pid) {
        const std::string path = "/proc/" + std::to_string(pid) + "/cmdline";
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) return "";

        std::string cmdline((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        if (cmdline.empty()) return "[ядерний потік або порожньо]";

        for (size_t i = 0; i < cmdline.size() - 1; ++i) {
            if (cmdline[i] == '\0') cmdline[i] = ' ';
        }
        return cmdline;
    }

    // Перегляд відкритих файлових дескрипторів через std::filesystem
    static std::vector<std::pair<std::string, std::string>> inspectFds(pid_t pid, size_t limit = 5) {
        std::vector<std::pair<std::string, std::string>> result;
        const std::string fd_dir = "/proc/" + std::to_string(pid) + "/fd";

        std::error_code ec;
        if (!fs::exists(fd_dir, ec)) return result;

        size_t count = 0;
        for (const auto& entry : fs::directory_iterator(fd_dir, ec)) {
            if (ec) break;
            
            std::error_code read_ec;
            auto target = fs::read_symlink(entry.path(), read_ec);
            if (!read_ec) {
                result.emplace_back(entry.path().filename().string(), target.string());
                if (++count >= limit) break;
            }
        }
        return result;
    }
};

int main() {
    pid_t pid = ::getpid();
    std::cout << "=== C++ Інспектор процесу (PID: " << pid << ") ===\n";

    if (auto metrics = ProcfsInspector::readStat(pid)) {
        std::cout << "Comm:    " << metrics->comm << "\n";
        std::cout << "State:   " << metrics->state << "\n";
        std::cout << "PPID:    " << metrics->ppid << "\n";
        std::cout << "Threads: " << metrics->num_threads << "\n";
        std::cout << "VSize:   " << (metrics->vsize / 1024) << " KB\n";
        std::cout << "RSS:     " << metrics->rss_pages << " сторінок\n";
    } else {
        std::cerr << "Помилка розбору /proc/PID/stat\n";
    }

    std::cout << "Cmdline: " << ProcfsInspector::readCmdline(pid) << "\n";

    std::cout << "Відкриті дескриптори:\n";
    for (const auto& [fd, target] : ProcfsInspector::inspectFds(pid)) {
        std::cout << "  fd " << fd << " -> " << target << "\n";
    }

    return 0;
}
