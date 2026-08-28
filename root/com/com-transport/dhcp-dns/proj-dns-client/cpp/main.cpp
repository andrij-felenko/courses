#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <stdexcept>
#include <random>
#include <cstring>
#include <cstdint>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

namespace dns {

constexpr uint16_t Port = 53;
constexpr size_t BufferSize = 512;
constexpr size_t MaxHops = 16;
constexpr size_t MaxLabelLen = 63;

/* RAII-обгортка над файловим дескриптором сокета */
class UniqueSocket {
public:
    UniqueSocket() : fd_(socket(AF_INET, SOCK_DGRAM, 0)) {
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося створити UDP-сокет");
        }
    }

    ~UniqueSocket() noexcept {
        if (fd_ >= 0) {
            close(fd_);
        }
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void setTimeout(int seconds) {
        struct timeval tv = { .tv_sec = seconds, .tv_usec = 0 };
        if (setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            throw std::runtime_error("Не вдалося встановити таймаут сокета");
        }
    }

private:
    int fd_ = -1;
};

/* Результат розбору запису A */
struct RecordA {
    std::string name;
    std::string ip;
    uint32_t ttl;
};

/* Кодування текстового імені у формат міток DNS */
std::vector<uint8_t> encodeDomainName(std::string_view hostname) {
    std::vector<uint8_t> encoded;
    size_t start = 0;

    while (start < hostname.size()) {
        size_t dot = hostname.find('.', start);
        size_t len = (dot == std::string_view::npos) ? (hostname.size() - start) : (dot - start);

        if (len == 0 || len > MaxLabelLen) {
            throw std::invalid_argument("Некоректна довжина мітки доменного імені");
        }

        encoded.push_back(static_cast<uint8_t>(len));
        encoded.insert(encoded.end(), hostname.begin() + start, hostname.begin() + start + len);

        if (dot == std::string_view::npos) break;
        start = dot + 1;
    }

    encoded.push_back(0x00); /* Нульовий байт кореня */
    return encoded;
}

/* Декодування стисненого імені з буфера */
std::pair<std::string, size_t> decodeDomainName(std::span<const uint8_t> packet, size_t offset) {
    std::string name;
    size_t curr = offset;
    size_t initial_bytes = 0;
    bool jumped = false;
    size_t hops = 0;

    while (curr < packet.size() && hops < MaxHops) {
        uint8_t len = packet[curr];

        if (len == 0) {
            if (!jumped) initial_bytes = (curr - offset) + 1;
            break;
        }

        if ((len & 0xC0) == 0xC0) {
            if (curr + 1 >= packet.size()) {
                throw std::runtime_error("Помилка: покажчик виходить за межі пакета");
            }
            uint16_t ptr_offset = static_cast<uint16_t>(((len & 0x3F) << 8) | packet[curr + 1]);
            if (ptr_offset >= packet.size()) {
                throw std::runtime_error("Помилка: некоректне зміщення покажчика компресії");
            }

            if (!jumped) {
                initial_bytes = (curr - offset) + 2;
                jumped = true;
            }
            curr = ptr_offset;
            hops++;
            continue;
        }

        curr++;
        if (curr + len > packet.size()) {
            throw std::runtime_error("Помилка: мітка виходить за межі пакета");
        }

        if (!name.empty()) name.push_back('.');
        name.append(reinterpret_cast<const char*>(&packet[curr]), len);
        curr += len;

        if (!jumped) initial_bytes = curr - offset;
    }

    if (hops >= MaxHops) {
        throw std::runtime_error("Виявлено циклічний покажчик компресії (петлю)");
    }

    return {name, initial_bytes};
}

/* Виконання запиту та вилучення IP-адрес */
std::vector<RecordA> resolve(std::string_view hostname, std::string_view dnsServer = "8.8.8.8") {
    UniqueSocket sock;
    sock.setTimeout(3);

    struct sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(Port);
    if (inet_pton(AF_INET, dnsServer.data(), &serv_addr.sin_addr) <= 0) {
        throw std::invalid_argument("Некоректна IP-адреса DNS-сервера");
    }

    /* Генерація випадкового ID */
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint16_t> dist(1, 65535);
    uint16_t queryId = dist(gen);

    /* Побудова запиту */
    std::vector<uint8_t> queryPacket(12, 0);
    queryPacket[0] = static_cast<uint8_t>(queryId >> 8);
    queryPacket[1] = static_cast<uint8_t>(queryId & 0xFF);
    queryPacket[2] = 0x01; /* RD = 1 */
    queryPacket[3] = 0x00;
    queryPacket[4] = 0x00; /* QDCOUNT = 1 */
    queryPacket[5] = 0x01;

    auto encodedName = encodeDomainName(hostname);
    queryPacket.insert(queryPacket.end(), encodedName.begin(), encodedName.end());

    /* QTYPE = 1 (A), QCLASS = 1 (IN) */
    queryPacket.push_back(0x00); queryPacket.push_back(0x01);
    queryPacket.push_back(0x00); queryPacket.push_back(0x01);

    /* Надсилання */
    ssize_t sent = sendto(sock.get(), queryPacket.data(), queryPacket.size(), 0,
                          reinterpret_cast<struct sockaddr*>(&serv_addr), sizeof(serv_addr));
    if (sent < 0) {
        throw std::runtime_error("Помилка надсилання UDP-пакета");
    }

    /* Отримання */
    std::vector<uint8_t> respBuffer(BufferSize);
    socklen_t addrLen = sizeof(serv_addr);
    ssize_t received = recvfrom(sock.get(), respBuffer.data(), respBuffer.size(), 0,
                                reinterpret_cast<struct sockaddr*>(&serv_addr), &addrLen);
    if (received < 12) {
        throw std::runtime_error("Таймаут відповіді або неповний заголовок DNS");
    }
    respBuffer.resize(received);

    std::span<const uint8_t> respSpan(respBuffer);

    /* Перевірка заголовка */
    uint16_t respId = static_cast<uint16_t>((respSpan[0] << 8) | respSpan[1]);
    uint16_t flags = static_cast<uint16_t>((respSpan[2] << 8) | respSpan[3]);
    uint16_t qdcount = static_cast<uint16_t>((respSpan[4] << 8) | respSpan[5]);
    uint16_t ancount = static_cast<uint16_t>((respSpan[6] << 8) | respSpan[7]);

    if (respId != queryId) {
        throw std::runtime_error("Отримано відповідь із чужим Transaction ID");
    }

    uint8_t rcode = static_cast<uint8_t>(flags & 0x0F);
    if (rcode != 0) {
        throw std::runtime_error("Сервер повернув код помилки RCODE = " + std::to_string(rcode));
    }

    /* Пропуск Question */
    size_t curr = 12;
    for (uint16_t q = 0; q < qdcount; ++q) {
        auto [_, consumed] = decodeDomainName(respSpan, curr);
        curr += consumed + 4; /* Ім'я + QTYPE (2) + QCLASS (2) */
    }

    /* Розбір Answer */
    std::vector<RecordA> results;
    for (uint16_t a = 0; a < ancount; ++a) {
        if (curr >= respSpan.size()) break;

        auto [rrName, consumed] = decodeDomainName(respSpan, curr);
        curr += consumed;

        if (curr + 10 > respSpan.size()) break;
        uint16_t rtype = static_cast<uint16_t>((respSpan[curr] << 8) | respSpan[curr + 1]);
        uint16_t rclass = static_cast<uint16_t>((respSpan[curr + 2] << 8) | respSpan[curr + 3]);
        uint32_t ttl = (static_cast<uint32_t>(respSpan[curr + 4]) << 24) |
                       (static_cast<uint32_t>(respSpan[curr + 5]) << 16) |
                       (static_cast<uint32_t>(respSpan[curr + 6]) << 8)  |
                       (static_cast<uint32_t>(respSpan[curr + 7]));
        uint16_t rdlength = static_cast<uint16_t>((respSpan[curr + 8] << 8) | respSpan[curr + 9]);
        curr += 10;

        if (curr + rdlength > respSpan.size()) break;

        if (rtype == 1 && rclass == 1 && rdlength == 4) {
            char ipStr[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &respSpan[curr], ipStr, sizeof(ipStr));
            results.push_back({rrName, std::string(ipStr), ttl});
        }
        curr += rdlength;
    }

    return results;
}

} // namespace dns

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Ужиток: " << argv[0] << " <доменне ім'я> [DNS сервер]\n";
        return 1;
    }

    std::string_view hostname = argv[1];
    std::string_view server = (argc >= 3) ? argv[2] : "8.8.8.8";

    try {
        std::cout << "Розв'язання імені '" << hostname << "' через сервер " << server << "...\n";
        auto records = dns::resolve(hostname, server);

        std::cout << "Отримано адресні записи (" << records.size() << "):\n";
        for (const auto& r : records) {
            std::cout << "  -> " << r.name << " = " << r.ip << " (TTL: " << r.ttl << " с)\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
