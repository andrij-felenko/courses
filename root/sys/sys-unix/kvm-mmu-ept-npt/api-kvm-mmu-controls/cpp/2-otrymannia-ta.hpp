#pragma once
#include <cstdint>
#include <vector>
#include <sys/ioctl.h>
#include <linux/kvm.h>

namespace kvm {

class DirtyLogManager {
public:
    static bool fetch_dirty_log(int vm_fd, uint32_t slot, std::vector<uint64_t>& bitmap_buffer) {
        struct kvm_dirty_log log{};
        log.slot = slot;
        log.dirty_bitmap = bitmap_buffer.data();
        return ioctl(vm_fd, KVM_GET_DIRTY_LOG, &log) == 0;
    }

    static bool clear_dirty_log(int vm_fd, uint32_t slot, uint64_t first_page, uint32_t num_pages, const std::vector<uint64_t>& bitmap_buffer) {
        struct kvm_clear_dirty_log clear{};
        clear.slot = slot;
        clear.first_page = first_page;
        clear.num_pages = num_pages;
        clear.dirty_bitmap = const_cast<uint64_t*>(bitmap_buffer.data());
        return ioctl(vm_fd, KVM_CLEAR_DIRTY_LOG, &clear) == 0;
    }
};

}
