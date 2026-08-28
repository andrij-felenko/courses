#include <fcntl.h>
#include <system_error>
#include <memory>
#include <unistd.h>

struct FileDescriptorDeleter {
    void operator()(int* fd) const noexcept {
        if (fd && *fd >= 0) {
            ::close(*fd);
            delete fd;
        }
    }
};

using SafeFileDescriptor = std::unique_ptr<int, FileDescriptorDeleter>;

SafeFileDescriptor open_secure_certificate(const char* path) {
    int raw_fd = ::open(path, O_RDONLY | O_CLOEXEC);
    if (raw_fd == -1) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }
    return SafeFileDescriptor(new int(raw_fd));
}
