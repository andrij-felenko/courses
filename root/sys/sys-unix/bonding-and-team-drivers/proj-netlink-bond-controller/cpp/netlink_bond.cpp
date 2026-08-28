// netlink_bond.cpp — C++20 ідіоматична реалізація з RAII та std::expected
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <span>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_bonding.h>

namespace netlink {

// RAII обгортка для мережевого сокета
class NetlinkSocket {
    int fd_{-1};
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, protocol);
    }
    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Програмована збірка Rtnetlink повідомлення
class NetlinkMessageBuilder {
    std::vector<uint8_t> buffer_;

public:
    explicit NetlinkMessageBuilder(uint16_t msg_type, uint16_t flags) {
        buffer_.resize(NLMSG_HDRLEN + sizeof(struct ifinfomsg), 0);
        auto* hdr = header();
        hdr->nlmsg_type = msg_type;
        hdr->nlmsg_flags = flags;
        hdr->nlmsg_len = static_cast<uint32_t>(buffer_.size());

        auto* ifi = reinterpret_cast<struct ifinfomsg*>(buffer_.data() + NLMSG_HDRLEN);
        ifi->ifi_family = AF_UNSPEC;
    }

    void add_attribute(uint16_t type, std::span<const uint8_t> data) {
        const uint16_t len = RTA_LENGTH(data.size());
        const size_t old_size = buffer_.size();
        const size_t aligned_size = NLMSG_ALIGN(old_size) + RTA_ALIGN(len);

        buffer_.resize(aligned_size, 0);

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + NLMSG_ALIGN(old_size));
        rta->rta_type = type;
        rta->rta_len = len;

        if (!data.empty()) {
            std::memcpy(RTA_DATA(rta), data.data(), data.size());
        }

        header()->nlmsg_len = static_cast<uint32_t>(aligned_size);
    }

    void add_string_attribute(uint16_t type, std::string_view str) {
        std::vector<uint8_t> bytes(str.begin(), str.end());
        bytes.push_back('\0');
        add_attribute(type, bytes);
    }

    template <typename T>
    void add_scalar_attribute(uint16_t type, T value) {
        static_assert(std::is_trivially_copyable_v<T>);
        const auto* ptr = reinterpret_cast<const uint8_t*>(&value);
        add_attribute(type, std::span<const uint8_t>(ptr, sizeof(T)));
    }

    class NestedAttribute {
        NetlinkMessageBuilder& builder_;
        size_t offset_;
    public:
        NestedAttribute(NetlinkMessageBuilder& builder, uint16_t type)
            : builder_(builder), offset_(NLMSG_ALIGN(builder.buffer_.size())) {
            builder_.add_attribute(type, {});
        }

        ~NestedAttribute() {
            auto* rta = reinterpret_cast<struct rtattr*>(builder_.buffer_.data() + offset_);
            rta->rta_len = static_cast<unsigned short>(builder_.buffer_.size() - offset_);
        }
    };

    [[nodiscard]] std::nested_container_tag create_nested(uint16_t type) {
        return {};
    }

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return buffer_;
    }

    [[nodiscard]] struct nlmsghdr* header() noexcept {
        return reinterpret_cast<struct nlmsghdr*>(buffer_.data());
    }
};

// Створення bonding-інтерфейсу
std::expected<void, std::string> create_bonding_device(std::string_view name, uint8_t mode, uint32_t miimon_ms) {
    NetlinkSocket socket(NETLINK_ROUTE);
    if (!socket.valid()) {
        return std::unexpected("Не вдалося відкрити AF_NETLINK сокет: " + std::string(strerror(errno)));
    }

    NetlinkMessageBuilder builder(RTM_NEWLINK, NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK);
    builder.add_string_attribute(IFLA_IFNAME, name);

    {
        NetlinkMessageBuilder::NestedAttribute linkinfo(builder, IFLA_LINKINFO);
        builder.add_string_attribute(IFLA_INFO_KIND, "bond");

        {
            NetlinkMessageBuilder::NestedAttribute infodata(builder, IFLA_INFO_DATA);
            builder.add_scalar_attribute(IFLA_BOND_MODE, mode);
            builder.add_scalar_attribute(IFLA_BOND_MIIMON, miimon_ms);
        }
    }

    struct sockaddr_nl sa{};
    sa.nl_family = AF_NETLINK;

    const auto msg_data = builder.data();
    if (::sendto(socket.get(), msg_data.data(), msg_data.size(), 0,
                 reinterpret_cast<const struct sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected("Помилка відправки sendto: " + std::string(strerror(errno)));
    }

    std::vector<uint8_t> ack_buf(4096);
    const ssize_t len = ::recv(socket.get(), ack_buf.data(), ack_buf.size(), 0);
    if (len < 0) {
        return std::unexpected("Помилка прийому ACK від ядра: " + std::string(strerror(errno)));
    }

    const auto* ack_hdr = reinterpret_cast<const struct nlmsghdr*>(ack_buf.data());
    if (ack_hdr->nlmsg_type == NLMSG_ERROR) {
        const auto* err = reinterpret_cast<const struct nlmsgerr*>(NLMSG_DATA(ack_hdr));
        if (err->error != 0) {
            return std::unexpected("Помилка ядра Rtnetlink: " + std::string(strerror(-err->error)));
        }
    }

    return {};
}

} // namespace netlink

int main() {
    constexpr std::string_view bond_name = "bond0";
    constexpr uint8_t bond_mode = BOND_MODE_8023AD; // Mode 4 LACP
    constexpr uint32_t mii_interval = 100;           // 100 ms

    auto result = netlink::create_bonding_device(bond_name, bond_mode, mii_interval);
    if (!result) {
        std::cerr << "Створення пристрою не вдалося: " << result.error() << '\n';
        return 1;
    }

    std::cout << "Пристрій '" << bond_name << "' успішно створено через C++ Rtnetlink API!\n";
    return 0;
}
