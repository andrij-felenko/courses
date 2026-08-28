// sctp_client.cpp — Ідіоматичний еквівалент клієнта на C++20
#include <iostream>
#include <string_view>
#include <format>
#include <array>
#include <chrono>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

namespace sctp {
constexpr std::string_view ServerIp = "127.0.0.1";
constexpr uint16_t ServerPort = 9899;
constexpr uint16_t StreamControl = 0;
constexpr uint16_t StreamTelemetry = 1;
constexpr uint32_t PpidControl = 0x0100;
constexpr uint32_t PpidTelemetry = 0x0200;
}

int main() {
    int sd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (sd < 0) {
        std::cerr << "Помилка створення сокета: " << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }

    sctp_initmsg initmsg{};
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    ::setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg));

    sockaddr_in servaddr{};
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(sctp::ServerPort);
    ::inet_pton(AF_INET, sctp::ServerIp.data(), &servaddr.sin_addr);

    std::cout << std::format("Підключення до SCTP сервера {}:{}...\n", sctp::ServerIp, sctp::ServerPort);
    if (::connect(sd, reinterpret_cast<sockaddr*>(&servaddr), sizeof(servaddr)) < 0) {
        std::cerr << "Помилка connect: " << std::generic_category().message(errno) << '\n';
        ::close(sd);
        return EXIT_FAILURE;
    }
    std::cout << "Асоціацію успішно встановлено!\n";

    // 1. Відправка впорядкованих команд на Потоці 0
    std::array<std::string_view, 4> commands = {
        "CMD:INIT_SYSTEM",
        "CMD:CALIBRATE_SENSORS",
        "CMD:ARM_MOTORS",
        "CMD:TAKEOFF_ALT_20M"
    };

    for (const auto& cmd : commands) {
        ::sctp_sendmsg(sd, cmd.data(), cmd.size(), nullptr, 0,
                       htonl(sctp::PpidControl), 0, sctp::StreamControl, 0, 0);
        std::cout << std::format("[КЛІЄНТ] Надіслано на Потік {} (Ordered): {}\n", sctp::StreamControl, cmd);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    // 2. Відправка телеметрії на Потоці 1 (Unordered)
    for (int i = 1; i <= 5; ++i) {
        std::string telem = std::format("TELEM:pkt={};lat=50.4501;lon=30.5234;alt={}.5", i, 20 + i);
        ::sctp_sendmsg(sd, telem.data(), telem.size(), nullptr, 0,
                       htonl(sctp::PpidTelemetry), SCTP_UNORDERED, sctp::StreamTelemetry, 0, 0);
        std::cout << std::format("[КЛІЄНТ] Надіслано на Потік {} (Unordered): {}\n", sctp::StreamTelemetry, telem);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }

    // 3. Очікування відповідей
    std::array<char, 256> recv_buf{};
    sctp_sndrcvinfo sinfo{};
    int flags = 0;
    for (int i = 0; i < 4; ++i) {
        ssize_t n = ::sctp_recvmsg(sd, recv_buf.data(), recv_buf.size() - 1, nullptr, 0, &sinfo, &flags);
        if (n > 0) {
            std::string_view resp(recv_buf.data(), static_cast<size_t>(n));
            std::cout << std::format("[КЛІЄНТ ВІДПОВІДЬ] Потік {}: {}\n", sinfo.sinfo_stream, resp);
        }
    }

    std::cout << "Завершення роботи клієнта.\n";
    ::close(sd);
    return EXIT_SUCCESS;
}
