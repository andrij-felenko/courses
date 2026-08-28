#include <sys/socket.h>
#include <array>
#include <span>
#include <cstdint>

constexpr size_t BATCH_SIZE = 64;
constexpr size_t BUF_SIZE = 2000;

std::array<mmsghdr, BATCH_SIZE> msgs{};
std::array<iovec, BATCH_SIZE> iovecs{};
std::array<std::array<uint8_t, BUF_SIZE>, BATCH_SIZE> buffers{};

for (size_t i = 0; i < BATCH_SIZE; ++i) {
    iovecs[i].iov_base = buffers[i].data();
    iovecs[i].iov_len = buffers[i].size();
    msgs[i].msg_hdr.msg_iov = &iovecs[i];
    msgs[i].msg_hdr.msg_iovlen = 1;
}

int retval = recvmmsg(sockfd, msgs.data(), static_cast<unsigned int>(BATCH_SIZE), MSG_DONTWAIT, nullptr);
