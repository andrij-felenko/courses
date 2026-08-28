#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/fcntl.h>
#include <system_error>

int create_sealed_buffer(size_t size) {
    int fd = ::memfd_create("secure_shm", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "memfd_create failed");
    }

    if (::ftruncate(fd, size) < 0) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "ftruncate failed");
    }

    if (::fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL) < 0) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "fcntl F_ADD_SEALS failed");
    }
    return fd;
}
