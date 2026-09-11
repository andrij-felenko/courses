#include <sys/socket.h>
#include <cstring>
#include <array>

struct AlignedControlStorage {
    // Об'єднання для вирівнювання пам'яті керуючого повідомлення на стеку в C++
    union {
        std::array<char, CMSG_SPACE(sizeof(int))> raw{};
        struct cmsghdr align;
    } storage;
};

void prepare_single_fd_message(struct msghdr& msg, struct iovec& iov, char& data_byte, AlignedControlStorage& control) {
    std::memset(&msg, 0, sizeof(msg));

    data_byte = 'S';
    iov.iov_base = &data_byte;
    iov.iov_len = 1;

    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = control.storage.raw.data();
    msg.msg_controllen = control.storage.raw.size();
}
