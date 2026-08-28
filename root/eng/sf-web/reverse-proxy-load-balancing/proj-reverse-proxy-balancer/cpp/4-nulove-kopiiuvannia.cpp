// Ідіоматична C++ обгортка над zero-copy передачею через RAII-канал pipe
class KernelPipe {
    int fds_[2]{-1, -1};
public:
    KernelPipe() {
        if (::pipe(fds_) != 0) {
            throw std::system_error(errno, std::generic_category());
        }
    }
    ~KernelPipe() {
        if (fds_[0] >= 0) ::close(fds_[0]);
        if (fds_[1] >= 0) ::close(fds_[1]);
    }
    [[nodiscard]] int read_fd() const noexcept { return fds_[0]; }
    [[nodiscard]] int write_fd() const noexcept { return fds_[1]; }
};

void transfer_zero_copy(int client_fd, int backend_fd, size_t max_bytes) {
    KernelPipe pipe;
    ssize_t spliced_in = ::splice(client_fd, nullptr, pipe.write_fd(), nullptr, 
                                  max_bytes, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    if (spliced_in > 0) {
        ::splice(pipe.read_fd(), nullptr, backend_fd, nullptr, 
                 spliced_in, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    }
}
