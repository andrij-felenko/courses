// RAII-обгортка для файлового дескриптора; помилки повертаємо через std::expected
class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& o) noexcept {
        if (this != &o) { reset(); fd_ = o.fd_; o.fd_ = -1; }
        return *this;
    }
    [[nodiscard]] int get() const { return fd_; }
    void reset() { if (fd_ >= 0) { ::close(fd_); fd_ = -1; } }
    [[nodiscard]] int release() { int ret = fd_; fd_ = -1; return ret; }
};

std::expected<void, std::error_code> safe_network_write(
    const std::filesystem::path& path,
    std::span<const std::byte> data
) {
    int raw_fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (raw_fd < 0)
        return std::unexpected(std::error_code(errno, std::generic_category()));
    
    FileDescriptor fd(raw_fd);

    if (::write(fd.get(), data.data(), data.size()) != static_cast<ssize_t>(data.size()))
        return std::unexpected(std::error_code(errno, std::generic_category()));

    if (::fsync(fd.get()) < 0)
        return std::unexpected(std::error_code(errno, std::generic_category()));

    // Відключаємо RAII-автозакриття, щоб явний close() повернув помилку запису
    int raw = fd.release();
    if (::close(raw) < 0)
        return std::unexpected(std::error_code(errno, std::generic_category()));

    return {};
}
