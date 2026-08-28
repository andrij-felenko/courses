// RAII-обгортка для відображення MMIO пам'яті в C++20
class MmappedResource {
public:
    MmappedResource(const std::filesystem::path& path, std::size_t size) : size_(size) {
        int fd = ::open(path.c_str(), O_RDWR | O_SYNC);
        if (fd >= 0) {
            addr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            ::close(fd);
        }
    }
    ~MmappedResource() {
        if (addr_ && addr_ != MAP_FAILED) ::munmap(addr_, size_);
    }
    [[nodiscard]] std::span<std::byte> bytes() const {
        return {static_cast<std::byte*>(addr_), size_};
    }
private:
    void* addr_{MAP_FAILED};
    std::size_t size_{0};
};
