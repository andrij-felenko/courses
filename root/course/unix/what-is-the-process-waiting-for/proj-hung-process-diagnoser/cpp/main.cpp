#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <filesystem>
#include <system_error>
#include <unistd.h>

namespace fs = std::filesystem;

struct SyscallInfo {
    long nr{-1};
    unsigned long arg0{0};
    unsigned long arg1{0};
    unsigned long arg2{0};
    std::string name{"RUNNING_IN_USERSPACE"};
};

struct ThreadDiagnostic {
    pid_t tid{0};
    std::string name{"unknown"};
    char state{'?'};
    long vol_switches{-1};
    long nonvol_switches{-1};
    std::string wchan{"unknown"};
    SyscallInfo syscall;
    std::optional<std::string> fd_target;
    std::vector<std::string> kernel_stack;
};

// Декодування номерів системних викликів x86_64
std::string decode_syscall_name(long nr) {
    switch (nr) {
        case 0:   return "read";
        case 1:   return "write";
        case 7:   return "poll";
        case 23:  return "select";
        case 35:  return "nanosleep";
        case 42:  return "connect";
        case 43:  return "accept";
        case 45:  return "recvfrom";
        case 74:  return "fsync";
        case 202: return "futex";
        case 232: return "epoll_wait";
        case 288: return "accept4";
        case -1:  return "RUNNING_IN_USERSPACE";
        default:  return "other_syscall";
    }
}

// Зчитування першого рядка файлу
std::string read_single_line(const fs::path& p) {
    std::ifstream is(p);
    std::string line;
    if (std::getline(is, line)) {
        return line;
    }
    return "";
}

// Інспекція цільового файлового дескриптора
std::string resolve_fd_target(pid_t pid, unsigned long fd_num) {
    fs::path fd_path = fs::path("/proc") / std::to_string(pid) / "fd" / std::to_string(fd_num);
    std::error_code ec;
    fs::path target = fs::read_symlink(fd_path, ec);
    if (!ec) {
        return target.string();
    }
    return "unknown/closed (" + ec.message() + ")";
}

// Збір інформації про окремий потік
ThreadDiagnostic collect_thread(pid_t tgid, pid_t tid) {
    ThreadDiagnostic diag;
    diag.tid = tid;

    const fs::path base = fs::path("/proc") / std::to_string(tgid) / "task" / std::to_string(tid);

    // 1. Статус потоку
    std::ifstream sf(base / "status");
    if (sf.is_open()) {
        std::string line;
        while (std::getline(sf, line)) {
            if (line.starts_with("Name:")) {
                diag.name = line.substr(line.find_first_not_of(" \t", 5));
            } else if (line.starts_with("State:")) {
                size_t pos = line.find_first_not_of(" \t", 6);
                if (pos != std::string::npos) diag.state = line[pos];
            } else if (line.starts_with("voluntary_ctxt_switches:")) {
                diag.vol_switches = std::stol(line.substr(24));
            } else if (line.starts_with("nonvoluntary_ctxt_switches:")) {
                diag.nonvol_switches = std::stol(line.substr(27));
            }
        }
    }

    // 2. wchan
    diag.wchan = read_single_line(base / "wchan");
    if (diag.wchan.empty()) diag.wchan = "0 (running/hidden)";

    // 3. syscall
    std::string sys_raw = read_single_line(base / "syscall");
    if (!sys_raw.empty() && sys_raw[0] != 'r') {
        std::istringstream iss(sys_raw);
        iss >> diag.syscall.nr;
        std::string a0, a1, a2;
        iss >> a0 >> a1 >> a2;
        try {
            if (!a0.empty()) diag.syscall.arg0 = std::stoul(a0, nullptr, 16);
            if (!a1.empty()) diag.syscall.arg1 = std::stoul(a1, nullptr, 16);
            if (!a2.empty()) diag.syscall.arg2 = std::stoul(a2, nullptr, 16);
        } catch (...) {}
        diag.syscall.name = decode_syscall_name(diag.syscall.nr);

        // Якщо це ввід-вивід з дескриптором
        if (diag.syscall.nr == 0 || diag.syscall.nr == 1 || diag.syscall.nr == 45 || diag.syscall.nr == 232) {
            diag.fd_target = resolve_fd_target(tgid, diag.syscall.arg0);
        }
    }

    // 4. Kernel Call Stack
    std::ifstream stf(base / "stack");
    if (stf.is_open()) {
        std::string stack_line;
        while (std::getline(stf, stack_line)) {
            if (!stack_line.empty()) {
                diag.kernel_stack.push_back(stack_line);
            }
        }
    }

    return diag;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID>\n";
        return 1;
    }

    pid_t pid = static_cast<pid_t>(std::stoi(argv[1]));
    const fs::path task_dir = fs::path("/proc") / std::to_string(pid) / "task";

    std::error_code ec;
    if (!fs::exists(task_dir, ec) || !fs::is_directory(task_dir, ec)) {
        std::cerr << "Помилка: процес із PID " << pid << " не знайдено в /proc.\n";
        return 1;
    }

    std::cout << "=== Діагностичний зріз процесу PID: " << pid << " ===\n\n";

    for (const auto& entry : fs::directory_iterator(task_dir, ec)) {
        if (!entry.is_directory()) continue;
        std::string filename = entry.path().filename().string();
        try {
            pid_t tid = static_cast<pid_t>(std::stoi(filename));
            ThreadDiagnostic diag = collect_thread(pid, tid);

            std::cout << "  [+] Потік TID: " << diag.tid << " (" << diag.name << ") | Стан: " << diag.state << "\n";
            std::cout << "      Перемикання контексту: добровільні=" << diag.vol_switches 
                      << ", примусові=" << diag.nonvol_switches << "\n";
            std::cout << "      Символ wchan: " << diag.wchan << "\n";
            std::cout << "      Системний виклик: #" << diag.syscall.nr << " (" << diag.syscall.name << ")\n";

            if (diag.fd_target) {
                std::cout << "      -> Блокування на FD " << diag.syscall.arg0 << ": " << *diag.fd_target << "\n";
            } else if (diag.syscall.nr == 202) {
                std::cout << "      -> Блокування FUTEX на адресі: 0x" << std::hex << diag.syscall.arg0 
                          << " (op=0x" << diag.syscall.arg1 << ", val=" << std::dec << diag.syscall.arg2 << ")\n";
            }

            if (!diag.kernel_stack.empty()) {
                std::cout << "      Ядерний стек (Kernel Call Stack):\n";
                for (size_t i = 0; i < diag.kernel_stack.size(); ++i) {
                    std::cout << "        #" << i << " " << diag.kernel_stack[i] << "\n";
                }
            }
            std::cout << "\n";
        } catch (...) {
            continue;
        }
    }

    return 0;
}
