#include <iostream>
#include <string_view>
#include <expected>
#include <string>
#include <memory>
#include <libvirt/libvirt.h>

struct VirDomainDeleter {
    void operator()(virDomainPtr ptr) const noexcept {
        if (ptr) virDomainFree(ptr);
    }
};
using UniqueVirDomain = std::unique_ptr<virDomain, VirDomainDeleter>;

std::expected<void, std::string> trigger_snapshot_commit(
    virDomainPtr dom,
    std::string_view disk,
    std::string_view base,
    std::string_view top
) {
    unsigned int flags = VIR_DOMAIN_BLOCK_COMMIT_ACTIVE | VIR_DOMAIN_BLOCK_COMMIT_PIVOT;
    int ret = virDomainBlockCommit(dom, disk.data(), base.data(), top.data(), 0, flags);
    if (ret < 0) {
        virErrorPtr err = virGetLastError();
        return std::unexpected(err && err->message ? err->message : "Unknown libvirt error");
    }
    return {};
}
