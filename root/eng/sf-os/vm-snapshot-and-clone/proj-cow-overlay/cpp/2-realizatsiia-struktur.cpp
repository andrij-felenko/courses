#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <span>
#include <array>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>

constexpr uint32_t COW_MAGIC = 0x434F5731;
constexpr uint32_t COW_VERSION = 1;
constexpr size_t SECTOR_SIZE = 512;
constexpr size_t MAX_PATH_LEN = 256;

#pragma pack(push, 1)
struct CowHeader {
    uint32_t magic{COW_MAGIC};
    uint32_t version{COW_VERSION};
    uint64_t total_sectors{0};
    uint64_t bitmap_offset{SECTOR_SIZE};
    uint64_t bitmap_bytes{0};
    uint64_t data_offset{0};
    char backing_path[MAX_PATH_LEN]{0};
    uint8_t reserved[216]{0};
};
#pragma pack(pop)

static_assert(sizeof(CowHeader) == SECTOR_SIZE, "CowHeader must be exactly 512 bytes");

class CowNode {
public:
    int fd{-1};
    bool is_overlay{false};
    CowHeader header{};
    std::vector<uint8_t> bitmap{};
    std::unique_ptr<CowNode> backing_node{nullptr};

    ~CowNode() noexcept {
        if (fd >= 0) {
            ::close(fd);
        }
    }

    CowNode() = default;
    CowNode(const CowNode&) = delete;
    CowNode& operator=(const CowNode&) = delete;

    CowNode(CowNode&& other) noexcept 
        : fd(other.fd), is_overlay(other.is_overlay), header(other.header),
          bitmap(std::move(other.bitmap)), backing_node(std::move(other.backing_node)) {
        other.fd = -1;
    }

    CowNode& operator=(CowNode&& other) noexcept {
        if (this != &other) {
            if (fd >= 0) ::close(fd);
            fd = other.fd;
            is_overlay = other.is_overlay;
            header = other.header;
            bitmap = std::move(other.bitmap);
            backing_node = std::move(other.backing_node);
            other.fd = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_sector_allocated(uint64_t sector) const noexcept {
        if (!is_overlay || bitmap.empty() || (sector / 8) >= bitmap.size()) {
            return false;
        }
        return (bitmap[sector / 8] & (1 << (sector % 8))) != 0;
    }

    void mark_sector_allocated(uint64_t sector) noexcept {
        if ((sector / 8) < bitmap.size()) {
            bitmap[sector / 8] |= (1 << (sector % 8));
        }
    }
};
