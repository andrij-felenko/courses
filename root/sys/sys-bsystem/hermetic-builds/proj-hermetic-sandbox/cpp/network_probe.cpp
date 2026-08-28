// network_probe.cpp
#include <iostream>
#include <expected>
#include <string>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace probe {

[[nodiscard]] std::expected<void, std::string> verify_network_isolation() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return std::unexpected("Створення сокета заблоковано ядром: " + std::string(strerror(errno)));
    }

    struct sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(80);
    inet_pton(AF_INET, "93.184.216.34", &addr.sin_addr);

    if (connect(sock, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) != 0) {
        std::string err = "З'єднання заблоковано: " + std::string(strerror(errno));
        close(sock);
        return std::unexpected(err);
    }

    close(sock);
    return {};
}

} // namespace probe

int main() {
    if (auto res = probe::verify_network_isolation(); !res) {
        std::cout << "[УСПІХ ІЗОЛЯЦІЇ] " << res.error() << "\n";
        return 0;
    }
    std::cerr << "[ПОМИЛКА] Мережевий доступ не заблоковано!\n";
    return 1;
}
