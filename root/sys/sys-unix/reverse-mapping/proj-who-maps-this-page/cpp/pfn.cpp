/* pfn.cpp — у який фізичний кадр дивиться ця віртуальна адреса.
 *   g++ -O2 -Wall -std=c++20 -o pfn pfn.cpp
 *   sudo ./pfn 1234 0x7f2a4c014000
 */
#include <iostream>
#include <fstream>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <fcntl.h>
#include <unistd.h>

static uint64_t read_u64(const std::string &path, off_t off)
{
    uint64_t v = 0;
    int fd = ::open(path.c_str(), O_RDONLY);
    if (fd < 0) { perror(path.c_str()); exit(1); }
    if (::pread(fd, &v, sizeof(v), off) != sizeof(v)) { perror("pread"); exit(1); }
    ::close(fd);
    return v;
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        std::cerr << "вжиток: " << argv[0] << " <pid> <адреса>\n";
        return 2;
    }

    uint64_t va = std::stoull(argv[2], nullptr, 0);
    std::string path = std::string("/proc/") + argv[1] + "/pagemap";

    uint64_t e = read_u64(path, static_cast<off_t>(va / 4096 * 8));
    if (!(e & (1ULL << 63))) {
        std::cout << "кадру немає: сторінка не в пам'яті\n";
        return 1;
    }

    uint64_t pfn = e & ((1ULL << 55) - 1);
    if (!pfn) {
        std::cout << "кадр 0 — найпевніше бракує CAP_SYS_ADMIN\n";
        return 1;
    }

    uint64_t count = read_u64("/proc/kpagecount", static_cast<off_t>(pfn * 8));
    std::cout << "кадр 0x" << std::hex << pfn << std::dec
              << ", відображень " << count << "\n";
    return 0;
}
