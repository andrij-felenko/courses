#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstdint>
#include <string_view>
#include <stdexcept>

class mmap_bloom_file {
public:
    explicit mmap_bloom_file(std::string_view filepath, std::size_t expected_size)
        : file_size_(expected_size) {
        fd_ = open(filepath.data(), O_RDWR | O_CREAT, 0644);
        if (fd_ < 0) throw std::runtime_error("Cannot open file");
        
        ftruncate(fd_, expected_size);
        void* ptr = mmap(nullptr, expected_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, 0);
        if (ptr == MAP_FAILED) {
            close(fd_);
            throw std::runtime_error("mmap failed");
        }
        mapped_bits_ = static_cast<std::uint8_t*>(ptr);
    }

    ~mmap_bloom_file() noexcept {
        if (mapped_bits_ && mapped_bits_ != MAP_FAILED) {
            munmap(mapped_bits_, file_size_);
        }
        if (fd_ >= 0) close(fd_);
    }

private:
    int fd_{-1};
    std::size_t file_size_{0};
    std::uint8_t* mapped_bits_{nullptr};
};
