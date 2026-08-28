#include <iostream>
#include <vector>
#include <memory>
#include <cstdint>
#include <cstring>
#include <atomic>
#include <span>
#include <optional>
#include <stdexcept>

enum class DescriptorFlags : uint16_t {
    None = 0,
    Next = 1,
    Write = 2
};

inline DescriptorFlags operator|(DescriptorFlags a, DescriptorFlags b) {
    return static_cast<DescriptorFlags>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

struct alignas(16) VirtqDesc {
    uint64_t addr{0};
    uint32_t len{0};
    uint16_t flags{0};
    uint16_t next{0};
};

struct VirtqAvail {
    uint16_t flags{0};
    uint16_t idx{0};
    uint16_t ring[16]{0};
    uint16_t used_event{0};
};

struct VirtqUsedElem {
    uint32_t id{0};
    uint32_t len{0};
};

struct VirtqUsed {
    uint16_t flags{0};
    uint16_t idx{0};
    VirtqUsedElem ring[16]{0};
    uint16_t avail_event{0};
};

class VirtqueueDriver {
public:
    explicit VirtqueueDriver(uint16_t queue_size = 16)
        : num_{queue_size}, num_free_{queue_size}, free_head_{0}, last_used_idx_{0} {
        
        if ((queue_size & (queue_size - 1)) != 0) {
            throw std::invalid_argument("Розмір черги має бути степенем двійки!");
        }

        desc_storage_.resize(queue_size);
        avail_storage_ = std::make_unique<VirtqAvail>();
        used_storage_ = std::make_unique<VirtqUsed>();

        for (uint16_t i = 0; i < queue_size - 1; ++i) {
            desc_storage_[i].next = i + 1;
        }
        desc_storage_[queue_size - 1].next = 0xFFFF;
    }

    std::optional<uint16_t> add_buffer(std::span<const std::byte> buffer, bool is_write) {
        if (num_free_ == 0) {
            return std::nullopt;
        }

        uint16_t head = free_head_;
        VirtqDesc& desc = desc_storage_[head];
        desc.addr = reinterpret_cast<uint64_t>(buffer.data());
        desc.len = static_cast<uint32_t>(buffer.size());
        desc.flags = static_cast<uint16_t>(is_write ? DescriptorFlags::Write : DescriptorFlags::None);

        free_head_ = desc.next;
        --num_free_;

        std::atomic_thread_fence(std::memory_order_release);

        uint16_t avail_slot = avail_storage_->idx & (num_ - 1);
        avail_storage_->ring[avail_slot] = head;

        std::atomic_thread_fence(std::memory_order_release);
        avail_storage_->idx++;

        return head;
    }

    void kick(volatile uint32_t* doorbell = nullptr) const noexcept {
        std::atomic_thread_fence(std::memory_order_seq_cst);
        if (doorbell) {
            *doorbell = 0;
        }
    }

    struct CompletedBuffer {
        uint16_t head;
        uint32_t len_written;
    };

    std::optional<CompletedBuffer> poll_used() noexcept {
        std::atomic_thread_fence(std::memory_order_acquire);

        if (last_used_idx_ == used_storage_->idx) {
            return std::nullopt;
        }

        uint16_t used_slot = last_used_idx_ & (num_ - 1);
        const VirtqUsedElem& elem = used_storage_->ring[used_slot];

        uint16_t head = static_cast<uint16_t>(elem.id);
        uint32_t len = elem.len;

        desc_storage_[head].next = free_head_;
        free_head_ = head;
        ++num_free_;

        ++last_used_idx_;
        return CompletedBuffer{head, len};
    }

    VirtqUsed* raw_used() noexcept { return used_storage_.get(); }
    uint16_t avail_idx() const noexcept { return avail_storage_->idx; }

private:
    uint16_t num_;
    uint16_t num_free_;
    uint16_t free_head_;
    uint16_t last_used_idx_;

    std::vector<VirtqDesc> desc_storage_;
    std::unique_ptr<VirtqAvail> avail_storage_;
    std::unique_ptr<VirtqUsed> used_storage_;
};

int main() {
    try {
        VirtqueueDriver vq(16);

        std::string payload = "Дані для передачі через Virtqueue C++ RAII";
        std::span<const std::byte> bytes_span{
            reinterpret_cast<const std::byte*>(payload.data()), payload.size()
        };

        auto head_opt = vq.add_buffer(bytes_span, false);
        if (head_opt) {
            std::cout << "Буфер додано у vring C++: head = " << *head_opt 
                      << ", avail_idx = " << vq.avail_idx() << std::endl;
        }

        vq.kick();

        auto* used = vq.raw_used();
        used->ring[0].id = *head_opt;
        used->ring[0].len = static_cast<uint32_t>(payload.size());
        used->idx = 1;

        auto result = vq.poll_used();
        if (result) {
            std::cout << "Завершено обробку у C++: head = " << result->head 
                      << ", оброблено байтів = " << result->len_written << std::endl;
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
