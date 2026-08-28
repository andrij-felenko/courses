#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstddef>
#include <span>
#include <string_view>
#include <optional>

class MmapFile {
public:
    [[nodiscard]] static std::optional<MmapFile> open(std::string_view path) noexcept {
        int fd = ::open(path.data(), O_RDONLY);
        if (fd < 0) return std::nullopt;

        struct stat st;
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            return std::nullopt;
        }

        void* addr = ::mmap(nullptr, st.st_size, PROT_READ, MAP_SHARED, fd, 0);
        ::close(fd);

        if (addr == MAP_FAILED) return std::nullopt;
        return MmapFile(static_cast<std::byte*>(addr), static_cast<std::size_t>(st.st_size));
    }

    ~MmapFile() noexcept {
        if (data_) ::munmap(data_, size_);
    }

    [[nodiscard]] std::span<const std::byte> bytes() const noexcept {
        return {data_, size_};
    }

    MmapFile(const MmapFile&) = delete;
    MmapFile& operator=(const MmapFile&) = delete;
    MmapFile(MmapFile&& o) noexcept : data_(o.data_), size_(o.size_) { o.data_ = nullptr; }

private:
    MmapFile(std::byte* data, std::size_t size) noexcept : data_(data), size_(size) {}
    std::byte* data_{nullptr};
    std::size_t size_{0};
};
