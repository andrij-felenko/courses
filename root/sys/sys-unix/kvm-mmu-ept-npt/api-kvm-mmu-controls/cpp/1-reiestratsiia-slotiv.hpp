#pragma once
#include <cstdint>
#include <sys/ioctl.h>
#include <linux/kvm.h>

namespace kvm {

struct MemoryRegion {
    uint32_t slot{0};
    uint32_t flags{0};
    uint64_t guest_phys_addr{p};
    uint64_t memory_size{0};
    uint64_t userspace_addr{0};
    uint64_t guest_memfd_offset{0};
    uint32_t guest_memfd{0};

    [[nodiscard]] bool apply(int vm_fd) const noexcept {
        struct kvm_userspace_memory_region2 region{};
        region.slot = slot;
        region.flags = flags;
        region.guest_phys_addr = guest_phys_addr;
        region.memory_size = memory_size;
        region.userspace_addr = userspace_addr;
        region.guest_memfd_offset = guest_memfd_offset;
        region.guest_memfd = guest_memfd;
        return ioctl(vm_fd, KVM_SET_USER_MEMORY_REGION2, &region) == 0;
    }
};

}
