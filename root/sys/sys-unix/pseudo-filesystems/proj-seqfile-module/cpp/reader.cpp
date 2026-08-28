// reader.cpp — той самий приклад з ідіоматичним RAII у C++
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <string_view>

class UniqueFd {
    int fd_ = -1;
public:
    explicit UniqueFd(const char* path, int flags) : fd_(::open(path, flags)) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    int get() const { return fd_; }
    explicit operator bool() const { return fd_ >= 0; }
};

static void dump(std::string_view tag, int fd) {
    char buf[8192];
    ::lseek(fd, 0, SEEK_SET);                  // почати вміст спочатку
    ssize_t n = ::read(fd, buf, sizeof(buf));
    if (n > 0) {
        std::cout << "--- " << tag << " ---\n";
        std::cout.write(buf, static_cast<std::streamsize>(n));
    }
}

int main() {
    UniqueFd fd("/proc/heartbeat", O_RDONLY);
    if (!fd) return 1;
    dump("одразу після open", fd.get());
    ::sleep(3);
    dump("через три секунди, той самий дескриптор", fd.get());
    return 0;
}
