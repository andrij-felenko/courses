#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <cstring>
#include <memory>

enum class VirtioGpuCmd : uint32_t {
    ResourceCreate2D      = 0x0101,
    ResourceUnref         = 0x0102,
    TransferToHost2D      = 0x0105,
    ResourceFlush         = 0x0104,
    ResourceAttachBacking = 0x0106,
    ResourceDetachBacking = 0x0107,
};

enum class VirtioGpuResp : uint32_t {
    OkNoData         = 0x1100,
    ErrUnspec        = 0x1200,
    ErrOutOfMemory   = 0x1201,
    ErrInvalidResId  = 0x1203,
};

enum class VirtioGpuFormat : uint32_t {
    B8G8R8A8_UNORM = 1,
};

struct virtio_gpu_ctrl_hdr {
    VirtioGpuCmd type;
    uint32_t flags{0};
    uint64_t fence_id{0};
    uint32_t ctx_id{0};
    uint8_t  ring_idx{0};
    uint8_t  padding[3]{};
};

struct virtio_gpu_rect {
    uint32_t x{0};
    uint32_t y{0};
    uint32_t width{0};
    uint32_t height{0};
};

struct virtio_gpu_mem_entry {
    uint64_t addr{0};
    uint32_t length{0};
    uint32_t padding{0};
};

class GpuResource {
public:
    GpuResource(uint32_t res_id, uint32_t width, uint32_t height)
        : resource_id_(res_id), width_(width), height_(height) {}

    ~GpuResource() noexcept {
        if (is_valid_) {
            [[maybe_unused]] auto res = destroy();
        }
    }

    // Заборона копіювання для запобігання подвійному звільненню
    GpuResource(const GpuResource&) = delete;
    GpuResource& operator=(const GpuResource&) = delete;

    // Переміщення ресурсу (Move semantics)
    GpuResource(GpuResource&& other) noexcept
        : resource_id_(other.resource_id_),
          width_(other.width_),
          height_(other.height_),
          is_valid_(other.is_valid_)
    {
        other.is_valid_ = false;
    }

    GpuResource& operator=(GpuResource&& other) noexcept {
        if (this != &other) {
            if (is_valid_) {
                [[maybe_unused]] auto res = destroy();
            }
            resource_id_ = other.resource_id_;
            width_ = other.width_;
            height_ = other.height_;
            is_valid_ = other.is_valid_;
            other.is_valid_ = false;
        }
        return *this;
    }

    [[nodiscard]] uint32_t id() const noexcept { return resource_id_; }
    [[nodiscard]] bool is_valid() const noexcept { return is_valid_; }

    [[nodiscard]] std::expected<virtio_gpu_ctrl_hdr, std::errc> attach_backing(
        std::span<const virtio_gpu_mem_entry> entries) noexcept
    {
        if (!is_valid_ || entries.empty()) {
            return std::unexpected(std::errc::invalid_argument);
        }

        // Симуляція надсилання ATTACH_BACKING в Virtqueue
        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }

    [[nodiscard]] std::expected<virtio_gpu_ctrl_hdr, std::errc> transfer_2d(
        uint64_t offset, virtio_gpu_rect rect) noexcept
    {
        if (!is_valid_ || rect.width == 0 || rect.height == 0) {
            return std::unexpected(std::errc::invalid_argument);
        }

        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }

    [[nodiscard]] std::expected<virtio_gpu_ctrl_hdr, std::errc> flush(
        virtio_gpu_rect rect) noexcept
    {
        if (!is_valid_) {
            return std::unexpected(std::errc::bad_file_descriptor);
        }

        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }

private:
    uint32_t resource_id_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    bool is_valid_{true};

    std::expected<virtio_gpu_ctrl_hdr, std::errc> destroy() noexcept {
        is_valid_ = false;
        virtio_gpu_ctrl_hdr response{
            .type = static_cast<VirtioGpuCmd>(VirtioGpuResp::OkNoData)
        };
        return response;
    }
};
