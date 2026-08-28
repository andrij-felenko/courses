#include <sys/socket.h>
#include <system_error>
#include <iostream>

char oob_byte = 0;
ssize_t n = ::recv(sockfd, &oob_byte, 1, MSG_OOB);
if (n > 0) {
    std::cout << "Отримано терміновий байт: " << oob_byte << "\n";
} else if (n < 0 && (errno != EAGAIN && errno != EWOULDBLOCK)) {
    throw std::system_error(errno, std::generic_category(), "recv MSG_OOB failed");
}
