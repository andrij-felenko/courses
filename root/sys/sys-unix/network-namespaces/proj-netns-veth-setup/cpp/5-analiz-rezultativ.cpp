#include <iostream>
#include <system_error>

struct AckResponse {
    nlmsghdr nlh;
    nlmsgerr err;
} ack_res{};

const auto received = ::recv(nl_fd, &ack_res, sizeof(ack_res), 0);
if (received >= static_cast<ssize_t>(sizeof(ack_res))
    && ack_res.nlh.nlmsg_type == NLMSG_ERROR && ack_res.err.error != 0) {
    std::cerr << "Помилка ядра Netlink: " 
              << std::system_category().message(-ack_res.err.error) << '\n';
}
