#include <libzbd/zbd.h>
#include <fcntl.h>
#include <cerrno>
#include <cstdint>
#include <memory>
#include <system_error>

// C++ Обгортка для роботи з libzbd
class ZbdDevice {
private:
    int m_fd{-1};
    struct zbd_info m_info{};

public:
    explicit ZbdDevice(const char* filename) {
        m_fd = zbd_open(filename, O_RDWR, &m_info);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити ZBD пристрій через libzbd");
        }
    }

    ~ZbdDevice() {
        if (m_fd >= 0) zbd_close(m_fd);
    }

    [[nodiscard]] uint32_t zone_size() const noexcept { return m_info.zone_size; }
    [[nodiscard]] uint32_t nr_zones() const noexcept { return m_info.nr_zones; }
};
