#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/xfrm.h>

namespace xfrm {

/* RAII-обгортка для файлового дескриптора сокету Netlink */
class NetlinkSocket {
    int fd_{-1};
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити сокет Netlink");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

/* Буфер повідомлення Netlink із підтримкою динамічного додавання атрибутів */
class MessageBuffer {
    std::vector<uint8_t> buffer_;

public:
    explicit MessageBuffer(uint16_t msg_type, uint16_t flags, uint32_t payload_size) {
        uint32_t total_len = NLMSG_LENGTH(payload_size);
        buffer_.resize(total_len, 0);

        auto* n = header();
        n->nlmsg_len = total_len;
        n->nlmsg_type = msg_type;
        n->nlmsg_flags = flags;
        n->nlmsg_seq = 1;
        n->nlmsg_pid = static_cast<uint32_t>(::getpid());
    }

    [[nodiscard]] struct nlmsghdr* header() noexcept {
        return reinterpret_cast<struct nlmsghdr*>(buffer_.data());
    }

    [[nodiscard]] void* payload() noexcept {
        return NLMSG_DATA(header());
    }

    void add_attribute(uint16_t type, std::span<const uint8_t> data) {
        uint32_t rta_len = RTA_LENGTH(data.size());
        size_t old_size = buffer_.size();
        size_t aligned_old = NLMSG_ALIGN(old_size);
        buffer_.resize(aligned_old + RTA_ALIGN(rta_len), 0);

        header()->nlmsg_len = static_cast<uint32_t>(buffer_.size());

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + aligned_old);
        rta->rta_type = type;
        rta->rta_len = rta_len;
        std::memcpy(RTA_DATA(rta), data.data(), data.size());
    }

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return buffer_;
    }
};

void add_security_association(NetlinkSocket& sock,
                              std::string_view src_ip,
                              std::string_view dst_ip,
                              uint32_t spi,
                              std::span<const uint8_t> aes_key,
                              std::span<const uint8_t> hmac_key) {
    MessageBuffer msg(XFRM_MSG_NEWSA, NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK, sizeof(struct xfrm_usersa_info));

    auto* sa = static_cast<struct xfrm_usersa_info*>(msg.payload());
    ::inet_pton(AF_INET, src_ip.data(), &sa->saddr.a4);
    ::inet_pton(AF_INET, dst_ip.data(), &sa->id.daddr.a4);
    sa->id.spi = htonl(spi);
    sa->id.proto = IPPROTO_ESP;
    sa->family = AF_INET;
    sa->mode = XFRM_MODE_TUNNEL;
    sa->reqid = 100;

    /* Додавання алгоритму шифрування */
    std::vector<uint8_t> crypt_raw(sizeof(struct xfrm_algo) + aes_key.size(), 0);
    auto* alg_crypt = reinterpret_cast<struct xfrm_algo*>(crypt_raw.data());
    std::strncpy(alg_crypt->alg_name, "cbc(aes)", sizeof(alg_crypt->alg_name));
    alg_crypt->alg_key_len = static_cast<uint32_t>(aes_key.size() * 8);
    std::memcpy(alg_crypt->alg_key, aes_key.data(), aes_key.size());
    msg.add_attribute(XFRMA_ALG_CRYPT, crypt_raw);

    /* Додавання алгоритму аутентифікації */
    std::vector<uint8_t> auth_raw(sizeof(struct xfrm_algo) + hmac_key.size(), 0);
    auto* alg_auth = reinterpret_cast<struct xfrm_algo*>(auth_raw.data());
    std::strncpy(alg_auth->alg_name, "hmac(sha256)", sizeof(alg_auth->alg_name));
    alg_auth->alg_key_len = static_cast<uint32_t>(hmac_key.size() * 8);
    std::memcpy(alg_auth->alg_key, hmac_key.data(), hmac_key.size());
    msg.add_attribute(XFRMA_ALG_AUTH, auth_raw);

    /* Відправка у сокет */
    struct sockaddr_nl sa_dst{};
    sa_dst.nl_family = AF_NETLINK;

    if (::sendto(sock.get(), msg.data().data(), msg.data().size(), 0,
                 reinterpret_cast<struct sockaddr*>(&sa_dst), sizeof(sa_dst)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка sendto до Netlink XFRM");
    }

    /* Зчитування відповіді */
    std::vector<uint8_t> resp_buf(512);
    ssize_t len = ::recv(sock.get(), resp_buf.data(), resp_buf.size(), 0);
    if (len < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка recv від Netlink XFRM");
    }

    auto* resp = reinterpret_cast<struct nlmsghdr*>(resp_buf.data());
    if (resp->nlmsg_type == NLMSG_ERROR) {
        auto* err = static_cast<struct nlmsgerr*>(NLMSG_DATA(resp));
        if (err->error != 0) {
            throw std::system_error(-err->error, std::generic_category(), "Помилка реєстрації SA ядром");
        }
    }
}

} // namespace xfrm

int main() {
    try {
        xfrm::NetlinkSocket sock(NETLINK_XFRM);
        const uint8_t aes_key[16] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
        std::vector<uint8_t> hmac_key(32, 0xAA);

        xfrm::add_security_association(sock, "192.168.1.1", "192.168.2.1", 0x1000, aes_key, hmac_key);
        std::cout << "Успіх: XFRM SA зареєстровано через C++ RAII Netlink API.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
