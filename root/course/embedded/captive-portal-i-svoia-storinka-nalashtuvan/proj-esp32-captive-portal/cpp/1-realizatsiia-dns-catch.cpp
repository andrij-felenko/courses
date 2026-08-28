#include <array>
#include <span>
#include <string_view>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace embedded::network {

class DnsCatchAllServer {
public:
    static constexpr uint16_t Port = 53;
    static constexpr size_t BufferCapacity = 512;
    static constexpr uint32_t TargetIp = 0xC0A80401; // 192.168.4.1 у network byte order

    void run() {
        int sockFd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (sockFd < 0) {
            ESP_LOGE(Tag.data(), "Помилка створення UDP сокета");
            return;
        }

        // RAII обгортка для безпечного закриття дескриптора сокета
        struct SocketGuard {
            int fd;
            ~SocketGuard() { if (fd >= 0) ::close(fd); }
        } guard{sockFd};

        sockaddr_in serverAddr{};
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);
        serverAddr.sin_port = htons(Port);

        if (bind(sockFd, reinterpret_cast<sockaddr*>(&serverAddr), sizeof(serverAddr)) < 0) {
            ESP_LOGE(Tag.data(), "Помилка прив'язки UDP сокета до порту 53");
            return;
        }

        ESP_LOGI(Tag.data(), "C++ DNS Catch-all сервер активний на порту %u", Port);

        std::array<uint8_t, BufferCapacity> packetBuffer{};
        sockaddr_in clientAddr{};
        socklen_t clientLen = sizeof(clientAddr);

        while (true) {
            ssize_t receivedBytes = recvfrom(sockFd, packetBuffer.data(), packetBuffer.size(), 0,
                                             reinterpret_cast<sockaddr*>(&clientAddr), &clientLen);
            if (receivedBytes < 12) {
                continue;
            }

            auto bufferSpan = std::span<uint8_t>(packetBuffer.data(), packetBuffer.size());
            size_t replyLen = buildSpoofedResponse(bufferSpan, static_cast<size_t>(receivedBytes));

            sendto(sockFd, packetBuffer.data(), replyLen, 0,
                   reinterpret_cast<sockaddr*>(&clientAddr), clientLen);
        }
    }

private:
    static constexpr std::string_view Tag = "DnsCatchAll";

    static size_t buildSpoofedResponse(std::span<uint8_t> buf, size_t queryLen) noexcept {
        // Встановлюємо прапорці заголовка: Response, Authoritative, No Error
        buf[2] = 0x81;
        buf[3] = 0x80;
        buf[6] = 0x00; buf[7] = 0x01; // ANCOUNT = 1
        buf[8] = 0x00; buf[9] = 0x00; // NSCOUNT = 0
        buf[10] = 0x00; buf[11] = 0x00; // ARCOUNT = 0

        size_t offset = queryLen;
        // Дописування Resource Record (Answer)
        buf[offset++] = 0xC0; buf[offset++] = 0x0C; // Name Pointer to QNAME
        buf[offset++] = 0x00; buf[offset++] = 0x01; // Type A
        buf[offset++] = 0x00; buf[offset++] = 0x01; // Class IN
        buf[offset++] = 0x00; buf[offset++] = 0x00; 
        buf[offset++] = 0x00; buf[offset++] = 0x0A; // TTL = 10s
        buf[offset++] = 0x00; buf[offset++] = 0x04; // Data Length = 4
        buf[offset++] = 192;  buf[offset++] = 168;
        buf[offset++] = 4;    buf[offset++] = 1;    // IP: 192.168.4.1

        return offset;
    }
};

} // namespace embedded::network

extern "C" void dns_server_task_cpp(void *pvParameters) {
    embedded::network::DnsCatchAllServer server;
    server.run();
    vTaskDelete(nullptr);
}
