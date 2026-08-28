#include <iostream>
#include <span>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

std::expected<std::uint64_t, std::error_code> submit_nvme_append_cpp(
    int fd, 
    std::uint32_t nsid, 
    std::uint64_t zslba, 
    std::span<const std::byte> buffer
) noexcept {
    uint32_t nlb = static_cast<uint32_t>(buffer.size() / 512);
    struct nvme_passthru_cmd cmd{};

    cmd.opcode      = 0x7d; // Zone Append
    cmd.nsid        = nsid;
    cmd.addr        = reinterpret_cast<std::uint64_t>(buffer.data());
    cmd.data_len    = static_cast<std::uint32_t>(buffer.size());
    cmd.cdw10       = static_cast<std::uint32_t>(zslba & 0xFFFFFFFF);
    cmd.cdw11       = static_cast<std::uint32_t>(zslba >> 32);
    cmd.cdw12       = nlb - 1; // 0-based NLB
    cmd.timeout_ms  = 1000;

    if (::ioctl(fd, NVME_IOCTL_IO_CMD, &cmd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return cmd.result;
}
