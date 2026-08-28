// C++ Implementation: RAII /proc Inspector and Deleted File Detector using C++20
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <optional>
#include <cctype>
#include <algorithm>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

struct ProcessStat {
    pid_t pid{0};
    pid_t ppid{0};
    std::string comm;
    char state{'?'};
    unsigned long utime{0};
    unsigned long stime{0};
    unsigned long vsize{0};
    long rss{0};
};

class ProcInspector {
public:
    static std::optional<ProcessStat> parseStat(pid_t pid) {
        const std::string path = "/proc/" + std::to_string(pid) + "/stat";
        std::ifstream file(path);
        if (!file.is_open()) {
            return std::nullopt;
        }

        std::string line;
        if (!std::getline(file, line)) {
            return std::nullopt;
        }

        const auto openParen = line.find('(');
        const auto closeParen = line.rfind(')');
        if (openParen == std::string::npos || closeParen == std::string::npos || closeParen <= openParen) {
            return std::nullopt;
        }

        ProcessStat stat;
        stat.pid = pid;
        stat.comm = line.substr(openParen + 1, closeParen - openParen - 1);

        const std::string rest = line.substr(closeParen + 2);
        char state = '?';
        pid_t ppid = 0;
        unsigned long utime = 0, stime = 0, vsize = 0;
        long rss = 0;

        const int items = std::sscanf(rest.c_str(),
            "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*u %lu %ld",
            &state, &ppid, &utime, &stime, &vsize, &rss);

        if (items != 6) {
            return std::nullopt;
        }

        stat.state = state;
        stat.ppid = ppid;
        stat.utime = utime;
        stat.stime = stime;
        stat.vsize = vsize;
        stat.rss = rss;

        return stat;
    }

    static void scanDeletedDescriptors(pid_t pid, std::string_view comm) {
        const std::string fdDirPath = "/proc/" + std::to_string(pid) + "/fd";
        std::error_code ec;
        
        if (!fs::exists(fdDirPath, ec) || ec) {
            return;
        }

        for (const auto& entry : fs::directory_iterator(fdDirPath, fs::directory_options::skip_permission_denied, ec)) {
            if (ec) break;

            std::error_code readlinkEc;
            const auto target = fs::read_symlink(entry.path(), readlinkEc);
            if (readlinkEc) continue;

            const std::string targetStr = target.string();
            if (targetStr.find("(deleted)") != std::string::npos) {
                struct stat st{};
                off_t fileSize = 0;
                if (::stat(entry.path().c_str(), &st) == 0) {
                    fileSize = st.st_size;
                }

                std::cout << "[DELETED FILE LEAK] PID: " << pid
                          << " | Comm: " << comm
                          << " | FD: " << entry.path().filename().string()
                          << " | Size: " << fileSize << " bytes"
                          << " | File: " << targetStr << '\n';
            }
        }
    }

    static void runScan() {
        std::cout << "=== SCANNING SYSTEM PROCESSES & UNLINKED OPEN FILES (C++) ===\n";
        std::error_code ec;

        for (const auto& entry : fs::directory_iterator("/proc", fs::directory_options::skip_permission_denied, ec)) {
            if (ec) break;

            const std::string filename = entry.path().filename().string();
            if (!filename.empty() && std::all_of(filename.begin(), filename.end(), ::isdigit)) {
                const pid_t pid = std::stoi(filename);
                const auto statOpt = parseStat(pid);
                if (statOpt) {
                    if (statOpt->state == 'D') {
                        std::cout << "[UNINTERRUPTIBLE D-STATE] PID: " << statOpt->pid
                                  << " | Comm: " << statOpt->comm
                                  << " | PPID: " << statOpt->ppid << '\n';
                    }
                    scanDeletedDescriptors(pid, statOpt->comm);
                }
            }
        }
    }
};

int main() {
    ProcInspector::runScan();
    return 0;
}
