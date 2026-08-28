/* forklab.cpp — той самий кадр у кількох процесах і що з ним робить запис (RAII).
 *   g++ -O2 -Wall -std=c++20 -o forklab forklab.cpp && sudo ./forklab
 */
#include <iostream>
#include <cstdint>
#include <cinttypes>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/wait.h>

constexpr size_t PAGE = 4096;
constexpr int KIDS = 4;

struct FileDescriptor {
    int fd = -1;
    explicit FileDescriptor(int f = -1) : fd(f) {}
    ~FileDescriptor() { if (fd >= 0) ::close(fd); }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    FileDescriptor(FileDescriptor &&o) noexcept : fd(o.fd) { o.fd = -1; }
    FileDescriptor &operator=(FileDescriptor &&o) noexcept {
        if (this != &o) { if (fd >= 0) ::close(fd); fd = o.fd; o.fd = -1; }
        return *this;
    }
};

static uint64_t read_u64(const char *path, off_t off)
{
    uint64_t v = 0;
    FileDescriptor fd(::open(path, O_RDONLY));
    if (fd.fd < 0) return 0;
    if (::pread(fd.fd, &v, sizeof(v), off) != sizeof(v)) return 0;
    return v;
}

static uint64_t pfn_of(const void *addr)
{
    uint64_t e = read_u64("/proc/self/pagemap", static_cast<off_t>(reinterpret_cast<uintptr_t>(addr) / PAGE * 8));
    return (e & (1ULL << 63)) ? (e & ((1ULL << 55) - 1)) : 0;
}

static uint64_t mapcount_of(uint64_t pfn)
{
    return read_u64("/proc/kpagecount", static_cast<off_t>(pfn * 8));
}

int main()
{
    int go_fds[2], hold_fds[2];
    if (::pipe(go_fds) || ::pipe(hold_fds)) return 1;

    char *p = static_cast<char *>(::mmap(nullptr, PAGE, PROT_READ | PROT_WRITE,
                                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    if (p == MAP_FAILED) return 1;
    p[0] = 'A';

    uint64_t pfn = pfn_of(p);
    if (!pfn) {
        std::cerr << "кадр 0: потрібен CAP_SYS_ADMIN\n";
        ::munmap(p, PAGE);
        return 1;
    }

    std::cout << "кадр 0x" << std::hex << pfn << std::dec
              << ",  до fork      відображень: " << mapcount_of(pfn) << "\n" << std::flush;

    for (int i = 0; i < KIDS; ++i) {
        if (::fork() == 0) {
            char c = 0;
            ::close(go_fds[1]);
            ::close(hold_fds[1]);
            (void)::read(go_fds[0], &c, 1);
            p[0] = static_cast<char>('a' + i);
            (void)::read(hold_fds[0], &c, 1);
            ::_exit(0);
        }
    }

    ::sleep(1);
    std::cout << "             після fork    відображень: " << mapcount_of(pfn) << "\n";

    (void)::write(go_fds[1], "xxxx", KIDS);
    ::sleep(1);
    std::cout << "             після запису  відображень: " << mapcount_of(pfn) << "\n";

    ::close(hold_fds[1]);
    while (::wait(nullptr) > 0) {}
    ::munmap(p, PAGE);
    return 0;
}
