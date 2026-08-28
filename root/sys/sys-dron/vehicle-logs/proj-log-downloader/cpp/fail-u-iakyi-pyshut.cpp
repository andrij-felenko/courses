#include <cerrno>
#include <cstdio>
#include <fcntl.h>
#include <unistd.h>

class LogFile {
public:
    bool open(const char* path, uint64_t size) {
        fd_ = ::open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd_ < 0) return false;
        return ::ftruncate(fd_, off_t(size)) == 0;   // розтягуємо наперед
    }

    bool writeAt(uint64_t ofs, const uint8_t* p, uint32_t n) {
        while (n) {
            const ssize_t k = ::pwrite(fd_, p, n, off_t(ofs));
            if (k < 0) { if (errno == EINTR) continue; return false; }
            p += k;  n -= uint32_t(k);  ofs += uint64_t(k);
        }
        return true;
    }

    bool finish(uint64_t realSize) {
        bool ok = (::ftruncate(fd_, off_t(realSize)) == 0);
        ok = (::fsync(fd_) == 0) && ok;              // один раз, наприкінці
        ::close(fd_);  fd_ = -1;
        return ok;
    }

private:
    int fd_ = -1;
};
