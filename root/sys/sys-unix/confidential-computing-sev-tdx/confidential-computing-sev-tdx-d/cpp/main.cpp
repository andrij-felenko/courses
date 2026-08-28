/* Реалізація виклику KVM_CREATE_GUEST_MEMFD у сучасному C++23/RAII wrapper */
namespace kvm {

struct GuestMemfdConfig {
    uint64_t size_bytes{8 * 1024 * 1024 * 1024ULL};
    uint64_t flags{0};
};

[[nodiscard]] auto create_private_guest_memfd(int vm_fd, const GuestMemfdConfig& cfg) 
    -> std::expected<int, std::system_error> 
{
    kvm_create_guest_memfd args{.size = cfg.size_bytes, .flags = cfg.flags};
    int memfd = ::ioctl(vm_fd, KVM_CREATE_GUEST_MEMFD, &args);
    if (memfd < 0) {
        return std::unexpected(std::system_error(errno, std::generic_category(), "KVM_CREATE_GUEST_MEMFD failed"));
    }
    return memfd;
}

} // namespace kvm
