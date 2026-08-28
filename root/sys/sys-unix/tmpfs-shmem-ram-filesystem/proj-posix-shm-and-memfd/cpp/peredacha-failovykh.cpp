// Ідіоматична передача дескриптора у C++
struct msghdr msg{};
alignas(struct cmsghdr) std::array<std::byte, CMSG_SPACE(sizeof(int))> buf{};

msg.msg_control = buf.data();
msg.msg_controllen = buf.size();

auto* cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type = SCM_RIGHTS;
cmsg->cmsg_len = CMSG_LEN(sizeof(int));

std::memcpy(CMSG_DATA(cmsg), &memfd, sizeof(int));
if (::sendmsg(socket_fd, &msg, 0) < 0) {
    throw std::system_error(errno, std::generic_category());
}
