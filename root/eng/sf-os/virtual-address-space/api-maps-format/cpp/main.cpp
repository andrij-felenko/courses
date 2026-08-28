#include <fcntl.h>
#include <linux/fs.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <sys/ioctl.h>
#include <unistd.h>

class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) : fd_{fd} {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const { return fd_; }
    [[nodiscard]] bool valid() const { return fd_ >= 0; }
};

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "вжиток: " << argv[0] << " <pid> <адреса-16>\n";
        return 2;
    }

    std::string path = std::string("/proc/") + argv[1] + "/maps";
    FileDescriptor fd{::open(path.c_str(), O_RDONLY | O_CLOEXEC)};
    if (!fd.valid()) {
        std::perror(path.c_str());
        return 1;
    }

    char name[256] = "";
    struct procmap_query q{};

    q.size          = sizeof(q);
    q.query_addr    = std::strtoull(argv[2], nullptr, 16);
    q.query_flags   = PROCMAP_QUERY_COVERING_OR_NEXT_VMA;
    q.vma_name_addr = static_cast<std::uint64_t>(reinterpret_cast<std::uintptr_t>(name));
    q.vma_name_size = sizeof(name);

    if (::ioctl(fd.get(), PROCMAP_QUERY, &q) < 0) {
        std::perror("PROCMAP_QUERY");
        return 1;
    }

    std::cout << std::hex << q.vma_start << '-' << q.vma_end << ' '
              << (q.vma_flags & PROCMAP_QUERY_VMA_READABLE   ? 'r' : '-')
              << (q.vma_flags & PROCMAP_QUERY_VMA_WRITABLE   ? 'w' : '-')
              << (q.vma_flags & PROCMAP_QUERY_VMA_EXECUTABLE ? 'x' : '-')
              << (q.vma_flags & PROCMAP_QUERY_VMA_SHARED     ? 's' : 'p')
              << " зсув " << q.vma_offset << "  "
              << q.dev_major << ':' << q.dev_minor << "  "
              << std::dec << "inode " << q.inode << "  "
              << (q.vma_name_size ? name : "") << '\n';

    return 0;
}
