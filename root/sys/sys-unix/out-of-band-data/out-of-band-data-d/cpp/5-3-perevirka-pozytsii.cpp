#include <sys/ioctl.h>
#include <system_error>
#include <iostream>

int atmark = 0;
if (::ioctl(sockfd, SIOCATMARK, &atmark) < 0) {
    throw std::system_error(errno, std::generic_category(), "ioctl SIOCATMARK failed");
}
if (atmark != 0) {
    std::cout << "Наступний байт є терміновим маркером OOB!\n";
}
