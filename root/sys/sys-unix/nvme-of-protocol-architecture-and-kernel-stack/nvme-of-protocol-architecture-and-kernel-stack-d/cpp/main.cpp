// cpp
#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <expected>
#include <system_error>
#include <cerrno>
#include <concepts>
#include <span>
#include <bit>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace nvme_of {

// Поля NVMe/TCP — little-endian. На LE-платформі перетворення нічого не міняє,
// на BE-платформі байти треба переставити; std::byteswap наосліп псував би LE.
template <std::integral T>
[[nodiscard]] constexpr T to_le(T value) noexcept {
    if constexpr (std::endian::native == std::endian::big) {
        return std::byteswap(value);
    } else {
        return value;
    }
}

#pragma pack(push, 1)
struct Header {
    std::uint8_t  type{0x04};
    std::uint8_t  flags{0};
    std::uint8_t  hlen{72};
    std::uint8_t  pdo{0};
    std::uint32_t plen{72};
};

struct CommandPdu {
    Header header{};
    std::array<std::uint8_t, 64> sqe{};
};
#pragma pack(pop)

class NvmeSocket {
private:
    int fd_{-1};

public:
    explicit NvmeSocket(int fd) noexcept : fd_(fd) {}
    ~NvmeSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NvmeSocket(const NvmeSocket&) = delete;
    NvmeSocket& operator=(const NvmeSocket&) = delete;
    NvmeSocket(NvmeSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    NvmeSocket& operator=(NvmeSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] std::expected<std::size_t, std::error_code> send_pdu(const CommandPdu& pdu) const noexcept {
        std::span<const std::byte> bytes{
            reinterpret_cast<const std::byte*>(&pdu), sizeof(CommandPdu)
        };

        ssize_t res = ::send(fd_, bytes.data(), bytes.size(), MSG_NOSIGNAL);
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (static_cast<std::size_t>(res) != bytes.size()) {
            return std::unexpected(std::make_error_code(std::errc::message_size));
        }
        return static_cast<std::size_t>(res);
    }
};

[[nodiscard]] std::expected<CommandPdu, std::error_code>
build_read_pdu(std::uint32_t nsid, std::uint64_t lba, std::uint16_t blocks) noexcept {
    // NVMe кодує кількість блоків як «N-1», тож нуль блоків — недійсний запит
    if (blocks == 0) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    CommandPdu pdu{};
    pdu.header.plen = to_le(static_cast<std::uint32_t>(sizeof(CommandPdu)));

    pdu.sqe[0] = 0x02; // NVMe Read Opcode

    const auto cmd_id = to_le<std::uint16_t>(0x1001);
    std::memcpy(&pdu.sqe[2], &cmd_id, sizeof(cmd_id));

    const auto nsid_le = to_le(nsid);
    std::memcpy(&pdu.sqe[4], &nsid_le, sizeof(nsid_le));

    const auto lba_le = to_le(lba);
    std::memcpy(&pdu.sqe[40], &lba_le, sizeof(lba_le));

    // Байти 24..39 SQE — SGL-описувач буфера даних; приклад лишає його нульовим
    const auto count_le = to_le(static_cast<std::uint16_t>(blocks - 1));
    std::memcpy(&pdu.sqe[48], &count_le, sizeof(count_le));

    return pdu;
}

} // namespace nvme_of
