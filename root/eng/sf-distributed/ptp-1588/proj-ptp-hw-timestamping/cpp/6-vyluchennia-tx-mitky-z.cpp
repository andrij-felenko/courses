std::array<char, 512> control{};
std::array<uint8_t, 256> dummy_buf{};
iovec iov{dummy_buf.data(), dummy_buf.size()};
msghdr msg{};
msg.msg_iov = &iov;
msg.msg_iovlen = 1;
msg.msg_control = control.data();
msg.msg_controllen = control.size();

int res = ::recvmsg(sock_fd, &msg, MSG_ERRQUEUE);
if (res >= 0) {
    for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            auto* ts = reinterpret_cast<timespec*>(CMSG_DATA(cmsg));
            std::cout << "TX Hardware Timestamp (t1): " << ts[2].tv_sec << "." << ts[2].tv_nsec << " s\n";
        }
    }
}
