#include <sys/mman.h>
#include <unistd.h>
#include <system_error>
#include <cstdint>

class UserEventsMemoryMap {
    char* status_map_{static_cast<char*>(MAP_FAILED)};
    std::size_t page_size_{0};

public:
    explicit UserEventsMemoryMap(int fd) {
        page_size_ = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        void* ptr = ::mmap(nullptr, page_size_, PROT_READ, MAP_SHARED, fd, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося виконати mmap статусу");
        }
        status_map_ = static_cast<char*>(ptr);
    }

    ~UserEventsMemoryMap() noexcept {
        if (status_map_ != MAP_FAILED) {
            ::munmap(status_map_, page_size_);
        }
    }

    [[nodiscard]] inline bool is_enabled(std::uint32_t status_index) const noexcept {
        return status_map_[status_index] != 0;
    }
};
