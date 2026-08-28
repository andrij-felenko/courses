#include <sys/socket.h>
#include <linux/tls.h>
#include <cstdint>
#include <cstring>
#include <system_error>

namespace ktls_utils {

[[nodiscard]] std::error_code send_tls_alert(int sockfd, uint8_t alert_code) noexcept {
    struct msghdr msg{};
    struct iovec iov{};
    alignas(struct cmsghdr) char cmsg_buf[CMSG_SPACE(sizeof(uint8_t))]{};

    iov.iov_base = &alert_code;
    iov.iov_len = sizeof(alert_code);

    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_TLS;
    cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint8_t));
    *reinterpret_cast<uint8_t*>(CMSG_DATA(cmsg)) = 21; // Alert

    if (::sendmsg(sockfd, &msg, 0) < 0) {
        return std::error_code(errno, std::generic_category());
    }
    return {};
}

} // namespace ktls_utils
