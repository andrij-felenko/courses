#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <drm/drm.h>

struct AccelGemCreate {
    std::uint64_t size;
    std::uint32_t handle;
    std::uint32_t pad;
};

struct AccelGemMmap {
    std::uint32_t handle;
    std::uint32_t pad;
    std::uint64_t offset;
};

struct AccelCommandDesc {
    std::uint32_t handle;
    std::uint32_t size;
    std::uint64_t offset;
};

struct AccelSubmit {
    std::uint64_t cmds_ptr;
    std::uint32_t cmd_count;
    std::uint32_t out_syncobj;
    std::uint64_t flags;
};

#define DRM_IOCTL_ACCEL_GEM_CREATE  DRM_IOWR(DRM_COMMAND_BASE + 0x01, AccelGemCreate)
#define DRM_IOCTL_ACCEL_GEM_MMAP    DRM_IOWR(DRM_COMMAND_BASE + 0x02, AccelGemMmap)
#define DRM_IOCTL_ACCEL_SUBMIT      DRM_IOWR(DRM_COMMAND_BASE + 0x03, AccelSubmit)

class AccelDevice {
public:
    explicit AccelDevice(std::string_view path) {
        fd_ = ::open(path.data(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити NPU прискорювач");
        }
    }

    ~AccelDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    AccelDevice(const AccelDevice&) = delete;
    AccelDevice& operator=(const AccelDevice&) = delete;

    AccelDevice(AccelDevice&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    AccelDevice& operator=(AccelDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int fd() const noexcept { return fd_; }

    [[nodiscard]] std::uint32_t create_gem(std::size_t size) const {
        AccelGemCreate req{.size = static_cast<std::uint64_t>(size)};
        if (::ioctl(fd_, DRM_IOCTL_ACCEL_GEM_CREATE, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виділення GEM-буфера");
        }
        return req.handle;
    }

    void close_gem(std::uint32_t handle) const noexcept {
        drm_gem_close req{.handle = handle};
        ::ioctl(fd_, DRM_IOCTL_GEM_CLOSE, &req);
    }

    [[nodiscard]] std::uint64_t get_mmap_offset(std::uint32_t handle) const {
        AccelGemMmap req{.handle = handle};
        if (::ioctl(fd_, DRM_IOCTL_ACCEL_GEM_MMAP, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка картографування GEM");
        }
        return req.offset;
    }

    [[nodiscard]] std::uint32_t create_syncobj() const {
        drm_syncobj_create req{.flags = 0};
        if (::ioctl(fd_, DRM_IOCTL_SYNCOBJ_CREATE, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення syncobj");
        }
        return req.handle;
    }

    void destroy_syncobj(std::uint32_t handle) const noexcept {
        drm_syncobj_destroy req{.handle = handle};
        ::ioctl(fd_, DRM_IOCTL_SYNCOBJ_DESTROY, &req);
    }

    void submit_job(std::uint32_t cmd_handle, std::size_t cmd_size, std::uint32_t out_syncobj) const {
        AccelCommandDesc desc{
            .handle = cmd_handle,
            .size = static_cast<std::uint32_t>(cmd_size),
            .offset = 0,
        };

        AccelSubmit req{
            .cmds_ptr = reinterpret_cast<std::uint64_t>(&desc),
            .cmd_count = 1,
            .out_syncobj = out_syncobj,
            .flags = 0,
        };

        if (::ioctl(fd_, DRM_IOCTL_ACCEL_SUBMIT, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка подання обчислювального завдання");
        }
    }

    bool wait_syncobj(std::uint32_t handle, std::uint64_t timeout_ns = 5'000'000'000ULL) const {
        std::uint64_t h_val = handle;
        drm_syncobj_wait req{
            .handles = reinterpret_cast<std::uint64_t>(&h_val),
            .timeout_nsec = static_cast<std::int64_t>(timeout_ns),
            .count_handles = 1,
            .flags = DRM_SYNCOBJ_WAIT_FLAGS_WAIT_ALL,
            .first_signaled = 0,
            .pad = 0,
        };

        return (::ioctl(fd_, DRM_IOCTL_SYNCOBJ_WAIT, &req) == 0);
    }

private:
    int fd_{-1};
};

/* RAII Обгортка для GEM буфера */
class GemBuffer {
public:
    GemBuffer(const AccelDevice& dev, std::size_t size) : dev_(dev), size_(size) {
        handle_ = dev_.create_gem(size_);
        std::uint64_t offset = dev_.get_mmap_offset(handle_);
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, dev_.fd(), static_cast<off_t>(offset));
        if (ptr == MAP_FAILED) {
            dev_.close_gem(handle_);
            throw std::system_error(errno, std::generic_category(), "Помилка mmap для GEM-буфера");
        }
        mapped_ptr_ = static_cast<std::uint8_t*>(ptr);
    }

    ~GemBuffer() {
        if (mapped_ptr_ != nullptr) {
            ::munmap(mapped_ptr_, size_);
        }
        if (handle_ != 0) {
            dev_.close_gem(handle_);
        }
    }

    GemBuffer(const GemBuffer&) = delete;
    GemBuffer& operator=(const GemBuffer&) = delete;

    [[nodiscard]] std::uint32_t handle() const noexcept { return handle_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

    [[nodiscard]] std::span<std::uint8_t> bytes() noexcept {
        return std::span<std::uint8_t>(mapped_ptr_, size_);
    }

private:
    const AccelDevice& dev_;
    std::size_t size_{0};
    std::uint32_t handle_{0};
    std::uint8_t* mapped_ptr_{nullptr};
};

/* RAII Обгортка для Syncobj */
class ScopedSyncobj {
public:
    explicit ScopedSyncobj(const AccelDevice& dev) : dev_(dev) {
        handle_ = dev_.create_syncobj();
    }

    ~ScopedSyncobj() {
        if (handle_ != 0) {
            dev_.destroy_syncobj(handle_);
        }
    }

    ScopedSyncobj(const ScopedSyncobj&) = delete;
    ScopedSyncobj& operator=(const ScopedSyncobj&) = delete;

    [[nodiscard]] std::uint32_t handle() const noexcept { return handle_; }

private:
    const AccelDevice& dev_;
    std::uint32_t handle_{0};
};

int main() {
    try {
        AccelDevice accel("/dev/accel/accel0");
        constexpr std::size_t buffer_size = 4096;

        /* Створення буферів з автоочищенням RAII */
        GemBuffer data_buf(accel, buffer_size);
        GemBuffer cmd_buf(accel, buffer_size);
        ScopedSyncobj syncobj(accel);

        /* Заповнюємо тензори через std::span */
        std::fill(data_buf.bytes().begin(), data_buf.bytes().end(), static_cast<std::uint8_t>(0x7E));
        std::fill(cmd_buf.bytes().begin(), cmd_buf.bytes().end(), static_cast<std::uint8_t>(0x00));

        std::cout << "[C++ RAII] GEM буфери та syncobj успішно створені\n";

        /* Подання обчислювального завдання */
        accel.submit_job(cmd_buf.handle(), cmd_buf.size(), syncobj.handle());
        std::cout << "[C++ RAII] Завдання відправлено в NPU. Чекаємо syncobj...\n";

        if (accel.wait_syncobj(syncobj.handle())) {
            std::cout << "[C++ RAII] Успішно! Обчислення на NPU завершено.\n";
        } else {
            std::cerr << "[C++ RAII] Таймаут або помилка виконання обчислень\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
