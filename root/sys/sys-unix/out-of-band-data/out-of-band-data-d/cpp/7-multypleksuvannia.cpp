#include <poll.h>
#include <array>
#include <iostream>

std::array<pollfd, 1> fds{};
fds[0].fd = sockfd;
fds[0].events = POLLIN | POLLPRI;

int ret = ::poll(fds.data(), fds.size(), -1);
if (ret > 0) {
    if (fds[0].revents & POLLPRI) {
        char oob_byte = 0;
        ::recv(sockfd, &oob_byte, 1, MSG_OOB);
        std::cout << "Отримано OOB через poll(POLLPRI): " << oob_byte << "\n";
    }
    if (fds[0].revents & POLLIN) {
        // Читання звичайних даних
    }
}
