/* whomaps.cpp — за номером фізичного кадру знайти всі його відображення в системі.
 *   g++ -O2 -Wall -Wextra -std=c++20 -o whomaps whomaps.cpp
 *   sudo ./whomaps 0x11e347
 */
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem>
#include <cstdint>
#include <cinttypes>
#include <cstdio>
#include <cctype>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>

namespace fs = std::filesystem;

constexpr uint64_t PAGE_SZ = 4096ULL;
constexpr uint64_t ENTRY   = 8ULL;
constexpr size_t   CHUNK   = 1024;

constexpr uint64_t PM_PRESENT   = 1ULL << 63;
constexpr uint64_t PM_EXCLUSIVE = 1ULL << 56;
constexpr uint64_t PM_PFN_MASK  = (1ULL << 55) - 1;

constexpr uint64_t KPF_ANON = 1ULL << 12;
constexpr uint64_t KPF_KSM  = 1ULL << 21;
constexpr uint64_t KPF_THP  = 1ULL << 22;

static uint64_t target_pfn = 0;
static unsigned long found_count = 0;

static bool kpage_u64(const std::string &path, uint64_t pfn, uint64_t &out)
{
    int fd = ::open(path.c_str(), O_RDONLY);
    if (fd < 0) return false;
    ssize_t got = ::pread(fd, &out, ENTRY, static_cast<off_t>(pfn * ENTRY));
    ::close(fd);
    return got == static_cast<ssize_t>(ENTRY);
}

static void scan_range(int pmfd, int pid, const std::string &comm,
                       uint64_t start, uint64_t end, const std::string &label)
{
    std::vector<uint64_t> buf(CHUNK);

    for (uint64_t va = start; va < end; ) {
        uint64_t left = (end - va) / PAGE_SZ;
        size_t n = left > CHUNK ? CHUNK : static_cast<size_t>(left);

        ssize_t got = ::pread(pmfd, buf.data(), n * ENTRY, static_cast<off_t>(va / PAGE_SZ * ENTRY));
        if (got <= 0) return;

        size_t k = static_cast<size_t>(got) / ENTRY;
        for (size_t i = 0; i < k; ++i) {
            uint64_t e = buf[i];
            if (!(e & PM_PRESENT)) continue;
            if ((e & PM_PFN_MASK) != target_pfn) continue;

            std::cout << "  pid " << pid << "  " << comm << "  0x"
                      << std::hex << (va + i * PAGE_SZ) << std::dec
                      << "  " << label
                      << ((e & PM_EXCLUSIVE) ? "   [єдине відображення]" : "") << "\n";
            found_count++;
        }
        va += k * PAGE_SZ;
    }
}

static void scan_pid(int pid)
{
    std::string pid_str = std::to_string(pid);
    std::ifstream maps("/proc/" + pid_str + "/maps");
    if (!maps.is_open()) return;

    int pmfd = ::open(("/proc/" + pid_str + "/pagemap").c_str(), O_RDONLY);
    if (pmfd < 0) return;

    std::string comm = "?";
    std::ifstream comm_file("/proc/" + pid_str + "/comm");
    if (comm_file.is_open()) {
        std::getline(comm_file, comm);
    }

    std::string line;
    while (std::getline(maps, line)) {
        if (line.empty()) continue;
        std::stringstream ss(line);
        std::string range, perms, offset, dev, inode;
        if (!(ss >> range >> perms >> offset >> dev >> inode)) continue;

        auto dash = range.find('-');
        if (dash == std::string::npos) continue;

        uint64_t start = std::stoull(range.substr(0, dash), nullptr, 16);
        uint64_t end   = std::stoull(range.substr(dash + 1), nullptr, 16);

        std::string label;
        std::getline(ss >> std::ws, label);
        if (label.empty()) label = "[анонімна]";
        if (label == "[vsyscall]") continue;

        scan_range(pmfd, pid, comm, start, end, label);
    }
    ::close(pmfd);
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        std::cerr << "вжиток: " << argv[0] << " <кадр> | <pid>@<адреса>\n";
        return 2;
    }

    std::string arg = argv[1];
    auto at = arg.find('@');
    if (at != std::string::npos) {
        std::string pid_str = arg.substr(0, at);
        uint64_t va = std::stoull(arg.substr(at + 1), nullptr, 0);
        uint64_t e = 0;

        int fd = ::open(("/proc/" + pid_str + "/pagemap").c_str(), O_RDONLY);
        if (fd < 0 || ::pread(fd, &e, ENTRY, static_cast<off_t>(va / PAGE_SZ * ENTRY)) != static_cast<ssize_t>(ENTRY)) {
            perror("pagemap");
            return 1;
        }
        ::close(fd);
        if (!(e & PM_PRESENT)) {
            std::cerr << "за цією адресою зараз немає кадру (біт 63 = 0)\n";
            return 1;
        }
        target_pfn = e & PM_PFN_MASK;
    } else {
        target_pfn = std::stoull(arg, nullptr, 0);
    }

    if (target_pfn == 0) {
        std::cerr << "кадр 0: найпевніше бракує CAP_SYS_ADMIN\n";
        return 1;
    }

    uint64_t count = 0, flags = 0;
    bool have_count = kpage_u64("/proc/kpagecount", target_pfn, count);
    bool have_flags = kpage_u64("/proc/kpageflags", target_pfn, flags);

    std::cout << "кадр 0x" << std::hex << target_pfn
              << "  (фізична адреса 0x" << (target_pfn * PAGE_SZ) << ")\n" << std::dec;
    if (have_flags) {
        std::cout << "прапорці 0x" << std::hex << flags << std::dec
                  << ((flags & KPF_ANON) ? "  ANON" : "")
                  << ((flags & KPF_KSM)  ? "  KSM"  : "")
                  << ((flags & KPF_THP)  ? "  THP"  : "") << "\n";
    }
    if (have_count) {
        std::cout << "ядро налічує відображень: " << count << "\n";
    }
    std::cout << "знайдено:\n";

    if (fs::exists("/proc")) {
        for (const auto &entry : fs::directory_iterator("/proc")) {
            std::string name = entry.path().filename().string();
            if (!name.empty() && std::isdigit(static_cast<unsigned char>(name[0]))) {
                scan_pid(std::stoi(name));
            }
        }
    }

    std::cout << "разом " << found_count;
    if (have_count) std::cout << ", ядро каже " << count;
    std::cout << "\n";
    return 0;
}
