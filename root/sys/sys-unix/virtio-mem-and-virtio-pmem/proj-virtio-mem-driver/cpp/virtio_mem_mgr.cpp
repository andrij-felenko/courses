// virtio_mem_mgr.cpp — Ідіоматична реалізація мовою C++ (C++20)
#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <expected>
#include <format>
#include <span>

constexpr uint64_t kSubblockSize = 2 * 1024 * 1024ULL; // 2 МБ

enum class BlockState : uint8_t {
    Unplugged,
    Plugged,
    Unmovable
};

struct MemBlock {
    uint64_t gpa;
    BlockState state{BlockState::Unplugged};
};

class VirtioMemDevice {
public:
    explicit VirtioMemDevice(uint64_t base_gpa, size_t block_count)
        : base_gpa_(base_gpa) {
        blocks_.reserve(block_count);
        for (size_t i = 0; i < block_count; ++i) {
            blocks_.push_back(MemBlock{base_gpa + (i * kSubblockSize), BlockState::Unplugged});
        }
    }

    // Регулювання розміру пам'яті (RAII та безпечна обробка помилок)
    size_t adjust_size(uint64_t target_bytes) {
        if (target_bytes > plugged_size_) {
            return plug_until(target_bytes);
        } else if (target_bytes < plugged_size_) {
            return unplug_until(target_bytes);
        }
        return 0;
    }

    void mark_unmovable(size_t index) {
        if (index < blocks_.size()) {
            blocks_[index].state = BlockState::Unmovable;
        }
    }

    [[nodiscard]] uint64_t plugged_size() const noexcept { return plugged_size_; }
    [[nodiscard]] std::span<const MemBlock> blocks() const noexcept { return blocks_; }

private:
    size_t plug_until(uint64_t target_bytes) {
        size_t count = 0;
        for (auto& block : blocks_) {
            if (plugged_size_ >= target_bytes) break;
            if (block.state == BlockState::Unplugged) {
                block.state = BlockState::Plugged;
                plugged_size_ += kSubblockSize;
                ++count;
                std::cout << std::format("[virtio-mem C++] GPA 0x{:x} -> PLUGGED\n", block.gpa);
            }
        }
        return count;
    }

    size_t unplug_until(uint64_t target_bytes) {
        size_t count = 0;
        for (auto it = blocks_.rbegin(); it != blocks_.rend(); ++it) {
            if (plugged_size_ <= target_bytes) break;
            if (it->state == BlockState::Plugged) {
                it->state = BlockState::Unplugged;
                plugged_size_ -= kSubblockSize;
                ++count;
                std::cout << std::format("[virtio-mem C++] GPA 0x{:x} -> UNPLUGGED\n", it->gpa);
            } else if (it->state == BlockState::Unmovable) {
                std::cout << std::format("[virtio-mem C++] GPA 0x{:x} UNMOVABLE, skipping\n", it->gpa);
            }
        }
        return count;
    }

    uint64_t base_gpa_;
    uint64_t plugged_size_{0};
    std::vector<MemBlock> blocks_;
};

int main() {
    VirtioMemDevice dev(0x100000000ULL, 16);

    std::cout << "--- C++: Запит на 16 МБ ---\n";
    dev.adjust_size(16 * 1024 * 1024ULL);

    dev.mark_unmovable(3);

    std::cout << "\n--- C++: Зменшення до 4 МБ ---\n";
    dev.adjust_size(4 * 1024 * 1024ULL);

    std::cout << std::format("\nC++ Plugged size: {} МБ\n", dev.plugged_size() / (1024 * 1024));
    return 0;
}
