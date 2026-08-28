#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <stdexcept>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <arpa/inet.h>

namespace ssh {

enum MessageType : uint8_t {
    AgentFailure = 5,
    AgentSuccess = 6,
    AgentcRequestIdentities = 11,
    AgentIdentitiesAnswer = 12,
    AgentcSignRequest = 13,
    AgentSignResponse = 14
};

/* RAII-обгортка дескриптора сокета */
class UnixSocket {
public:
    explicit UnixSocket(int fd) : fd_(fd) {
        if (fd_ < 0) throw std::system_error(errno, std::generic_category(), "Невалідний сокет");
    }

    ~UnixSocket() {
        if (fd_ >= 0) ::close(fd_);
    }

    UnixSocket(const UnixSocket&) = delete;
    UnixSocket& operator=(const UnixSocket&) = delete;

    UnixSocket(UnixSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UnixSocket& operator=(UnixSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void writeExact(std::span<const uint8_t> data) const {
        size_t total = 0;
        while (total < data.size()) {
            ssize_t w = ::write(fd_, data.data() + total, data.size() - total);
            if (w < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "write error");
            }
            total += static_cast<size_t>(w);
        }
    }

    void readExact(std::span<uint8_t> buffer) const {
        size_t total = 0;
        while (total < buffer.size()) {
            ssize_t r = ::read(fd_, buffer.data() + total, buffer.size() - total);
            if (r < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "read error");
            }
            if (r == 0) throw std::runtime_error("Передчасний розрив з'єднання з агентом");
            total += static_cast<size_t>(r);
        }
    }

private:
    int fd_{-1};
};

struct KeyIdentity {
    std::vector<uint8_t> blob;
    std::string comment;
};

class AgentClient {
public:
    static AgentClient connect() {
        const char* sockPath = std::getenv("SSH_AUTH_SOCK");
        if (!sockPath || std::strlen(sockPath) == 0) {
            throw std::runtime_error("Змінна середовища $SSH_AUTH_SOCK не встановлена");
        }

        int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "socket() failed");
        }

        struct sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        std::strncpy(addr.sun_path, sockPath, sizeof(addr.sun_path) - 1);

        if (::connect(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            throw std::system_error(errno, std::generic_category(), "connect() failed");
        }

        return AgentClient(UnixSocket(fd));
    }

    std::vector<KeyIdentity> requestIdentities() const {
        // Відправляємо запит
        uint32_t reqLen = htonl(1);
        uint8_t reqType = MessageType::AgentcRequestIdentities;

        std::vector<uint8_t> reqPacket(5);
        std::memcpy(reqPacket.data(), &reqLen, 4);
        reqPacket[4] = reqType;
        socket_.writeExact(reqPacket);

        // Читаємо довжину відповіді
        uint32_t respLenNet = 0;
        socket_.readExact(std::span<uint8_t>(reinterpret_cast<uint8_t*>(&respLenNet), 4));
        uint32_t respLen = ntohl(respLenNet);

        if (respLen < 5) throw std::runtime_error("Некоректний розмір відповіді від агента");

        std::vector<uint8_t> respPayload(respLen);
        socket_.readExact(respPayload);

        if (respPayload[0] != MessageType::AgentIdentitiesAnswer) {
            throw std::runtime_error("Агент повернув неочікуваний тип або помилку");
        }

        uint32_t nkeys = 0;
        std::memcpy(&nkeys, respPayload.data() + 1, 4);
        nkeys = ntohl(nkeys);

        std::vector<KeyIdentity> keys;
        keys.reserve(nkeys);

        size_t offset = 5;
        for (uint32_t i = 0; i < nkeys && offset + 4 <= respPayload.size(); ++i) {
            uint32_t klen = 0;
            std::memcpy(&klen, respPayload.data() + offset, 4);
            klen = ntohl(klen);
            offset += 4;

            if (offset + klen > respPayload.size()) break;
            std::vector<uint8_t> keyBlob(respPayload.begin() + offset, respPayload.begin() + offset + klen);
            offset += klen;

            if (offset + 4 > respPayload.size()) break;
            uint32_t clen = 0;
            std::memcpy(&clen, respPayload.data() + offset, 4);
            clen = ntohl(clen);
            offset += 4;

            if (offset + clen > respPayload.size()) break;
            std::string comment(reinterpret_cast<const char*>(respPayload.data() + offset), clen);
            offset += clen;

            keys.push_back({std::move(keyBlob), std::move(comment)});
        }

        return keys;
    }

    std::vector<uint8_t> signData(std::span<const uint8_t> keyBlob, std::span<const uint8_t> data, uint32_t flags = 0) const {
        uint32_t payloadLen = 1 + 4 + keyBlob.size() + 4 + data.size() + 4;
        std::vector<uint8_t> reqPacket;
        reqPacket.reserve(4 + payloadLen);

        uint32_t netPayloadLen = htonl(payloadLen);
        reqPacket.insert(reqPacket.end(), reinterpret_cast<uint8_t*>(&netPayloadLen), reinterpret_cast<uint8_t*>(&netPayloadLen) + 4);
        reqPacket.push_back(MessageType::AgentcSignRequest);

        auto appendField = [&reqPacket](std::span<const uint8_t> bytes) {
            uint32_t netLen = htonl(static_cast<uint32_t>(bytes.size()));
            reqPacket.insert(reqPacket.end(), reinterpret_cast<uint8_t*>(&netLen), reinterpret_cast<uint8_t*>(&netLen) + 4);
            reqPacket.insert(reqPacket.end(), bytes.begin(), bytes.end());
        };

        appendField(keyBlob);
        appendField(data);

        uint32_t netFlags = htonl(flags);
        reqPacket.insert(reqPacket.end(), reinterpret_cast<uint8_t*>(&netFlags), reinterpret_cast<uint8_t*>(&netFlags) + 4);

        socket_.writeExact(reqPacket);

        uint32_t respLenNet = 0;
        socket_.readExact(std::span<uint8_t>(reinterpret_cast<uint8_t*>(&respLenNet), 4));
        uint32_t respLen = ntohl(respLenNet);

        std::vector<uint8_t> respPayload(respLen);
        socket_.readExact(respPayload);

        if (respPayload.empty() || respPayload[0] != MessageType::AgentSignResponse) {
            throw std::runtime_error("Операція підпису була відхилена агентом");
        }

        if (respPayload.size() < 5) throw std::runtime_error("Пошкоджений підпис агента");

        uint32_t sigLen = 0;
        std::memcpy(&sigLen, respPayload.data() + 1, 4);
        sigLen = ntohl(sigLen);

        return std::vector<uint8_t>(respPayload.begin() + 5, respPayload.begin() + 5 + sigLen);
    }

private:
    explicit AgentClient(UnixSocket socket) : socket_(std::move(socket)) {}
    UnixSocket socket_;
};

} // namespace ssh

int main() {
    try {
        auto client = ssh::AgentClient::connect();
        auto keys = client.requestIdentities();

        std::cout << "Завантажено ключів в ssh-agent: " << keys.size() << "\n";
        for (size_t i = 0; i < keys.size(); ++i) {
            std::cout << "  [Ключ #" << (i + 1) << "] Розмір: " << keys[i].blob.size()
                      << " байтів, Коментар: \"" << keys[i].comment << "\"\n";
        }

        if (!keys.empty()) {
            std::string challenge = "challenge_session_auth_data_payload_2026";
            std::span<const uint8_t> challengeData(reinterpret_cast<const uint8_t*>(challenge.data()), challenge.size());

            auto signature = client.signData(keys[0].blob, challengeData);
            std::cout << "Успішний цифровий підпис отримано! Довжина підпису: " << signature.size() << " байтів.\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
