#include <iostream>
#include <thread>
#include <chrono>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main() {
    int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return 1;

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(9099);
    ::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        return 1;
    }

    ::send(fd, "hello ", 6, 0);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // Відправлення позасмугового байта
    ::send(fd, "!", 1, MSG_OOB);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    ::send(fd, "world\n", 6, 0);

    ::close(fd);
    return 0;
}
