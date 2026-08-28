// gem_dumb_prime.cpp - Виділення та експорт GEM буфера мовою C++
#include <iostream>
#include <memory>
#include <span>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

namespace drm {

// RAII обгортка для володіння файловим дескриптором
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

// RAII обгортка для GEM dumb-буфера
class DumbBuffer {
public:
    DumbBuffer(int drm_fd, uint32_t width, uint32_t height, uint32_t bpp)
        : drm_fd_(drm_fd), width_(width), height_(height)
    {
        struct drm_mode_create_dumb create_req{};
        create_req.width = width;
        create_req.height = height;
        create_req.bpp = bpp;

        if (::ioctl(drm_fd_, DRM_IOCTL_MODE_CREATE_DUMB, &create_req) < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося створити dumb буфер");
        }

        handle_ = create_req.handle;
        pitch_ = create_req.pitch;
        size_ = create_req.size;

        // Отримуємо фальшиве зміщення для mmap
        struct drm_mode_map_dumb map_req{};
        map_req.handle = handle_;
        if (::ioctl(drm_fd_, DRM_IOCTL_MODE_MAP_DUMB, &map_req) < 0) {
            cleanup();
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося отримати fake offset");
        }

        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_SHARED, drm_fd_, static_cast<off_t>(map_req.offset));
        if (ptr == MAP_FAILED) {
            cleanup();
            throw std::system_error(errno, std::generic_category(),
                                    "Помилка mmap буфера");
        }
        data_ = static_cast<uint8_t*>(ptr);
    }

    ~DumbBuffer() noexcept {
        cleanup();
    }

    DumbBuffer(const DumbBuffer&) = delete;
    DumbBuffer& operator=(const DumbBuffer&) = delete;

    DumbBuffer(DumbBuffer&& other) noexcept
        : drm_fd_(other.drm_fd_), handle_(other.handle_),
          pitch_(other.pitch_), size_(other.size_),
          width_(other.width_), height_(other.height_),
          data_(other.data_)
    {
        other.handle_ = 0;
        other.data_ = nullptr;
    }

    [[nodiscard]] uint32_t handle() const noexcept { return handle_; }
    [[nodiscard]] uint32_t pitch() const noexcept { return pitch_; }
    [[nodiscard]] uint64_t size() const noexcept { return size_; }
    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t height() const noexcept { return height_; }

    [[nodiscard]] std::span<uint8_t> bytes() noexcept {
        return {data_, static_cast<std::size_t>(size_)};
    }

    [[nodiscard]] UniqueFd export_prime_fd() const {
        struct drm_prime_handle prime_req{};
        prime_req.handle = handle_;
        prime_req.flags = DRM_CLOEXEC | DRM_RDWR;

        if (::ioctl(drm_fd_, DRM_IOCTL_PRIME_HANDLE_TO_FD, &prime_req) < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Помилка експорту в PRIME dma-buf");
        }
        return UniqueFd(prime_req.fd);
    }

    void render_gradient() {
        for (uint32_t y = 0; y < height_; ++y) {
            auto* row = reinterpret_cast<uint32_t*>(data_ + y * pitch_);
            for (uint32_t x = 0; x < width_; ++x) {
                uint8_t r = static_cast<uint8_t>((x * 255) / width_);
                uint8_t g = static_cast<uint8_t>((y * 255) / height_);
                uint8_t b = 128;
                row[x] = (0xFF << 24) | (r << 16) | (g << 8) | b;
            }
        }
    }

private:
    void cleanup() noexcept {
        if (data_ && data_ != MAP_FAILED) {
            ::munmap(data_, size_);
            data_ = nullptr;
        }
        if (handle_ != 0) {
            struct drm_mode_destroy_dumb destroy_req{};
            destroy_req.handle = handle_;
            ::ioctl(drm_fd_, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req);
            handle_ = 0;
        }
    }

    int drm_fd_{-1};
    uint32_t handle_{0};
    uint32_t pitch_{0};
    uint64_t size_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    uint8_t* data_{nullptr};
};

} // namespace drm

int main() {
    try {
        drm::UniqueFd drm_device(::open("/dev/dri/card0", O_RDWR | O_CLOEXEC));
        if (!drm_device.valid()) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося відкрити /dev/dri/card0");
        }

        std::cout << "[DRM] Відкрито графічний пристрій\n";

        // Створюємо та відображаємо буфер 640x480
        drm::DumbBuffer buffer(drm_device.get(), 640, 480, 32);
        std::cout << "[DRM] Створено буфер: хендл=" << buffer.handle()
                  << ", pitch=" << buffer.pitch()
                  << ", розмір=" << buffer.size() << " байтів\n";

        // Малюємо тестовий візерунок
        buffer.render_gradient();
        std::cout << "[CPU] Візерунок згенеровано через std::span\n";

        // Експортуємо дескриптор dma-buf для передавання через IPC
        drm::UniqueFd prime_fd = buffer.export_prime_fd();
        std::cout << "[PRIME] dma-buf експортовано успішно, fd=" << prime_fd.get() << "\n";

        // Тестуємо імпорт у новому дескрипторі
        drm::UniqueFd client_device(::open("/dev/dri/card0", O_RDWR | O_CLOEXEC));
        if (client_device.valid()) {
            struct drm_prime_handle import_req{};
            import_req.fd = prime_fd.get();

            if (::ioctl(client_device.get(), DRM_IOCTL_PRIME_FD_TO_HANDLE, &import_req) == 0) {
                std::cout << "[Клієнт] Імпортовано буфер: новий локальний хендл="
                          << import_req.handle << "\n";

                struct drm_gem_close close_req{.handle = import_req.handle, .pad = 0};
                ::ioctl(client_device.get(), DRM_IOCTL_GEM_CLOSE, &close_req);
            }
        }

        std::cout << "[Завершення] Усі ресурси автоматично звільняються RAII деструкторами.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
