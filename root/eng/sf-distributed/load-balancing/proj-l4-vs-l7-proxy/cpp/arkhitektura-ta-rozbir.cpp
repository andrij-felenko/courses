#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <array>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class L7HttpProxy {
    static constexpr uint16_t API_PORT = 8081;
    static constexpr uint16_t STATIC_PORT = 8082;

    static int connectToBackend(uint16_t port) {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return -1;

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        ::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            return -1;
        }
        return fd;
    }

public:
    static void handleConnection(int rawClientFd, std::string_view clientIp) {
        auto clientFd = std::unique_ptr<int, void(*)(int*)>(
            new int(rawClientFd), [](int* fd) { if (fd) { ::close(*fd); delete fd; } }
        );

        std::array<char, 8192> reqBuffer{};
        ssize_t bytesRead = ::read(*clientFd, reqBuffer.data(), reqBuffer.size() - 1);
        if (bytesRead <= 0) return;
        reqBuffer[bytesRead] = '\0';

        std::string_view request(reqBuffer.data(), bytesRead);
        auto lineEnd = request.find("\r\n");
        if (lineEnd == std::string_view::npos) return;

        std::string_view startLine = request.substr(0, lineEnd);
        auto firstSpace = startLine.find(' ');
        auto secondSpace = startLine.rfind(' ');
        if (firstSpace == std::string_view::npos || secondSpace == firstSpace) return;

        std::string_view path = startLine.substr(firstSpace + 1, secondSpace - firstSpace - 1);

        /* Вибір цільового бекенда за шляхом */
        uint16_t targetPort = path.starts_with("/api") ? API_PORT : STATIC_PORT;
        int rawBackendFd = connectToBackend(targetPort);
        if (rawBackendFd < 0) return;

        auto backendFd = std::unique_ptr<int, void(*)(int*)>(
            new int(rawBackendFd), [](int* fd) { if (fd) { ::close(*fd); delete fd; } }
        );

        /* Ін'єкція заголовка X-Forwarded-For без зайвих алокацій пам'яті */
        std::string mutatedRequest;
        mutatedRequest.reserve(request.size() + 64);
        mutatedRequest.append(request.substr(0, lineEnd + 2));
        mutatedRequest.append("X-Forwarded-For: ");
        mutatedRequest.append(clientIp);
        mutatedRequest.append("\r\n");
        mutatedRequest.append(request.substr(lineEnd + 2));

        ::write(*backendFd, mutatedRequest.data(), mutatedRequest.size());

        std::array<char, 8192> resBuffer{};
        ssize_t n = 0;
        while ((n = ::read(*backendFd, resBuffer.data(), resBuffer.size())) > 0) {
            ::write(*clientFd, resBuffer.data(), n);
        }
    }
};
