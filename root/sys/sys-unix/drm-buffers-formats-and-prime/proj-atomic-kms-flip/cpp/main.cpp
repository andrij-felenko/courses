// C++ Idiomatic Implementation with RAII Resource Management
#include <fcntl.h>
#include <poll.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#include <cstdio>
#include <exception>
#include <iostream>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

namespace kms {

// RAII обгортка для файлового дескриптора DRM
class DrmDevice {
    int fd_{-1};
public:
    explicit DrmDevice(const std::string& path) {
        fd_ = ::open(path.c_str(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити пристрій DRM: " + path);
        }
        
        if (::drmSetClientCap(fd_, DRM_CLIENT_CAP_ATOMIC, 1) != 0 ||
            ::drmSetClientCap(fd_, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) != 0) {
            throw std::runtime_error("Атомарні можливості Atomic KMS не підтримуються ядром");
        }
    }

    ~DrmDevice() {
        if (fd_ >= 0) ::close(fd_);
    }

    DrmDevice(const DrmDevice&) = delete;
    DrmDevice& operator=(const DrmDevice&) = delete;
    DrmDevice(DrmDevice&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

// RAII обгортка для Dumb-буфера у пам'яті
class DumbBuffer {
    int fd_;
    uint32_t handle_{0};
    uint32_t fb_id_{0};
    uint32_t size_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    void* vaddr_{MAP_FAILED};

public:
    DumbBuffer(int fd, uint32_t width, uint32_t height)
        : fd_(fd), width_(width), height_(height) {
        
        drm_mode_create_dumb creq{.width = width, .height = height, .bpp = 32};
        if (::drmIoctl(fd_, DRM_IOCTL_MODE_CREATE_DUMB, &creq) < 0) {
            throw std::runtime_error("Не вдалося створити DUMB буфер через ioctl");
        }
        handle_ = creq.handle;
        size_ = creq.size;

        if (::drmModeAddFB(fd_, width, height, 24, 32, creq.pitch, handle_, &fb_id_) < 0) {
            throw std::runtime_error("Не вдалося зареєструвати фреймбуфер drmModeAddFB");
        }

        drm_mode_map_dumb mreq{.handle = handle_};
        if (::drmIoctl(fd_, DRM_IOCTL_MODE_MAP_DUMB, &mreq) < 0) {
            throw std::runtime_error("Помилка отримання зсуву пам'яті MAP_DUMB");
        }

        vaddr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, mreq.offset);
        if (vaddr_ == MAP_FAILED) {
            throw std::runtime_error("Помилка відображення пам'яті mmap");
        }
    }

    ~DumbBuffer() {
        if (vaddr_ != MAP_FAILED) ::munmap(vaddr_, size_);
        if (fb_id_) ::drmModeRmFB(fd_, fb_id_);
        if (handle_) {
            drm_mode_destroy_dumb dreq{.handle = handle_};
            ::drmIoctl(fd_, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);
        }
    }

    [[nodiscard]] uint32_t fb_id() const noexcept { return fb_id_; }
    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t height() const noexcept { return height_; }

    [[nodiscard]] std::span<uint32_t> pixels() noexcept {
        return {static_cast<uint32_t*>(vaddr_), size_ / sizeof(uint32_t)};
    }
};

// RAII обгортка для атомарного запиту
class AtomicRequest {
    drmModeAtomicReqPtr req_{nullptr};
public:
    AtomicRequest() : req_(::drmModeAtomicAlloc()) {
        if (!req_) throw std::bad_alloc();
    }
    ~AtomicRequest() {
        if (req_) ::drmModeAtomicFree(req_);
    }

    void add_property(uint32_t obj_id, uint32_t prop_id, uint64_t val) {
        if (::drmModeAtomicAddProperty(req_, obj_id, prop_id, val) < 0) {
            throw std::runtime_error("Помилка додавання властивості в атомарний запит");
        }
    }

    int commit(int fd, uint32_t flags, void* user_data) {
        return ::drmModeAtomicCommit(fd, req_, flags, user_data);
    }
};

} // namespace kms

int main() {
    try {
        kms::DrmDevice dev("/dev/dri/card0");
        std::cout << "Успішна ініціалізація DRM пристрою з Atomic KMS\n";
        // Логіка підключення об'єктів та кадрового циклу через RAII...
    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
