// gbm-kms-pipeline.cpp — ідіоматичний конвеєр виділення з RAII та std::span
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <inttypes.h>
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <system_error>
#include <vector>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <gbm.h>
#include <drm_fourcc.h>

namespace drm {

// RAII обгортка для файлового дескриптора
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

// RAII обгортка для буферного об'єкта GBM
struct GbmBoDeleter {
    void operator()(gbm_bo* bo) const noexcept {
        if (bo) gbm_bo_destroy(bo);
    }
};
using UniqueGbmBo = std::unique_ptr<gbm_bo, GbmBoDeleter>;

// Клас кадрового буфера KMS з автоматичним видаленням
class KmsFramebuffer {
public:
    KmsFramebuffer(int drm_fd, uint32_t fb_id, uint32_t width, uint32_t height,
                   uint32_t format, uint64_t modifier, std::vector<UniqueFd> plane_fds)
        : drm_fd_(drm_fd), fb_id_(fb_id), width_(width), height_(height),
          format_(format), modifier_(modifier), plane_fds_(std::move(plane_fds)) {}

    ~KmsFramebuffer() noexcept {
        if (fb_id_ != 0 && drm_fd_ >= 0) {
            drmModeRmFB(drm_fd_, fb_id_);
        }
    }

    KmsFramebuffer(const KmsFramebuffer&) = delete;
    KmsFramebuffer& operator=(const KmsFramebuffer&) = delete;
    KmsFramebuffer(KmsFramebuffer&&) noexcept = default;
    KmsFramebuffer& operator=(KmsFramebuffer&&) noexcept = default;

    [[nodiscard]] uint32_t id() const noexcept { return fb_id_; }
    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t height() const noexcept { return height_; }
    [[nodiscard]] uint32_t format() const noexcept { return format_; }
    [[nodiscard]] uint64_t modifier() const noexcept { return modifier_; }

    // Фабричний метод виділення буфера
    static std::unique_ptr<KmsFramebuffer> create(
        int drm_fd, gbm_device* gbm, uint32_t width, uint32_t height,
        uint32_t format, std::span<const uint64_t> modifiers)
    {
        if (!gbm || modifiers.empty()) {
            throw std::invalid_argument("Некоректні параметри GBM або порожній список модифікаторів");
        }

        // 1. Створення буфера з модифікаторами через GBM
        UniqueGbmBo bo(gbm_bo_create_with_modifiers2(
            gbm, width, height, format, modifiers.data(),
            static_cast<uint32_t>(modifiers.size()),
            GBM_BO_USE_RENDERING | GBM_BO_USE_SCANOUT
        ));

        if (!bo) {
            throw std::system_error(errno, std::generic_category(), "gbm_bo_create_with_modifiers2 не вдався");
        }

        const uint64_t chosen_mod = gbm_bo_get_modifier(bo.get());
        const int plane_count = gbm_bo_get_plane_count(bo.get());
        if (plane_count <= 0 || plane_count > 4) {
            throw std::runtime_error("Некоректна кількість площин: " + std::to_string(plane_count));
        }

        uint32_t handles[4] = {0};
        uint32_t strides[4] = {0};
        uint32_t offsets[4] = {0};
        uint64_t mods[4] = {0};
        std::vector<UniqueFd> plane_fds;
        plane_fds.reserve(plane_count);

        // 2. Експорт кожної площини
        for (int p = 0; p < plane_count; ++p) {
            int fd = gbm_bo_get_fd_for_plane(bo.get(), p);
            if (fd < 0) {
                throw std::system_error(errno, std::generic_category(), "gbm_bo_get_fd_for_plane помилка");
            }
            plane_fds.emplace_back(fd);

            strides[p] = gbm_bo_get_stride_for_plane(bo.get(), p);
            offsets[p] = gbm_bo_get_offset(bo.get(), p);
            mods[p] = chosen_mod;

            int ret = drmPrimeFDToHandle(drm_fd, fd, &handles[p]);
            if (ret < 0) {
                throw std::system_error(-ret, std::generic_category(), "drmPrimeFDToHandle помилка");
            }
        }

        // 3. Реєстрація у KMS
        uint32_t fb_id = 0;
        int ret = drmModeAddFB2WithModifiers(
            drm_fd, width, height, format,
            handles, strides, offsets, mods,
            &fb_id, DRM_MODE_FB_MODIFIERS
        );

        // Закриття локальних хендлів GEM
        for (int p = 0; p < plane_count; ++p) {
            drm_gem_close req{ .handle = handles[p] };
            drmIoctl(drm_fd, DRM_IOCTL_GEM_CLOSE, &req);
        }

        if (ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "drmModeAddFB2WithModifiers помилка");
        }

        std::cout << "KMS Framebuffer створено успішно: ID=" << fb_id
                  << ", Mod=0x" << std::hex << chosen_mod << std::dec
                  << ", Planes=" << plane_count << "\n";

        return std::make_unique<KmsFramebuffer>(
            drm_fd, fb_id, width, height, format, chosen_mod, std::move(plane_fds)
        );
    }

private:
    int drm_fd_{-1};
    uint32_t fb_id_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    uint32_t format_{0};
    uint64_t modifier_{DRM_FORMAT_MOD_INVALID};
    std::vector<UniqueFd> plane_fds_;
};

} // namespace drm
