// Приклад на C++20
#include <sys/socket.h>
#include <linux/tls.h>
#include <array>
#include <system_error>

void send_tls_alert_cpp(int sock_fd, uint8_t alert_code) {
    std::array<uint8_t, 2> payload{1, alert_code};
    struct iovec iov{ .iov_base = payload.data(), .iov_len = payload.size() };

    alignas(struct cmsghdr) std::array<char, CMSG_SPACE(sizeof(uint8_t))> cmsg_buffer{};
    struct msghdr msg{};
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buffer.data();
    msg.msg_controllen = cmsg_buffer.size();

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_TLS;
    cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint8_t));
    *reinterpret_cast<uint8_t*>(CMSG_DATA(cmsg)) = 21; // TLS Alert record

    if (::sendmsg(sock_fd, &msg, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося відправити TLS Alert cmsg");
    }
}
