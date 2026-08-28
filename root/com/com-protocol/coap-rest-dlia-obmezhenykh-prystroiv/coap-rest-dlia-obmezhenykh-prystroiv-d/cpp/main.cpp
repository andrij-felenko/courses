#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <array>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

class CoapSocketServer {
public:
    static constexpr uint16_t DefaultPort = 5683;
    static constexpr size_t BufferSize = 512;

    explicit CoapSocketServer(uint16_t port = DefaultPort) {
        sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd_ >= 0) {
            sockaddr_in servaddr{};
            servaddr.sin_family = AF_INET;
            servaddr.sin_addr.s_addr = INADDR_ANY;
            servaddr.sin_port = htons(port);
            if (bind(sockfd_, reinterpret_cast<const sockaddr*>(&servaddr), sizeof(servaddr)) < 0) {
                close(sockfd_);
                sockfd_ = -1;
            }
        }
    }

    ~CoapSocketServer() {
        if (sockfd_ >= 0) {
            close(sockfd_);
        }
    }

    CoapSocketServer(const CoapSocketServer&) = delete;
    CoapSocketServer& operator=(const CoapSocketServer&) = delete;

    void run() {
        if (sockfd_ < 0) return;

        std::array<uint8_t, BufferSize> rx_buf{};
        std::array<uint8_t, BufferSize> tx_buf{};

        while (true) {
            sockaddr_in cliaddr{};
            socklen_t clen = sizeof(cliaddr);
            ssize_t n = recvfrom(sockfd_, rx_buf.data(), rx_buf.size(), 0,
                                 reinterpret_cast<sockaddr*>(&cliaddr), &clen);
            if (n > 0) {
                size_t resp_len = process_packet(std::span<const uint8_t>(rx_buf.data(), n),
                                                 std::span<uint8_t>(tx_buf.data(), tx_buf.size()));
                if (resp_len > 0) {
                    sendto(sockfd_, tx_buf.data(), resp_len, 0,
                           reinterpret_cast<const sockaddr*>(&cliaddr), clen);
                }
            }
        }
    }

private:
    int sockfd_{-1};

    size_t process_packet(std::span<const uint8_t> in, std::span<uint8_t> out) noexcept {
        if (in.size() < 4) return 0;

        const uint8_t version = (in[0] >> 6) & 0x03;
        const uint8_t tkl = in[0] & 0x0F;
        const uint8_t code = in[1];
        const uint16_t mid = (static_cast<uint16_t>(in[2]) << 8) | in[3];

        if (version != 1 || tkl > 8 || in.size() < 4 + tkl) {
            return 0;
        }

        const auto token = in.subspan(4, tkl);
        size_t offset = 4 + tkl;

        char path_buf[64]{};
        size_t path_len = 0;
        uint16_t cur_opt = 0;

        while (offset < in.size() && in[offset] != 0xFF) {
            uint8_t h = in[offset++];
            uint16_t delta = (h >> 4) & 0x0F;
            uint16_t len = h & 0x0F;

            if (delta == 13) delta = static_cast<uint16_t>(in[offset++]) + 13;
            if (len == 13) len = static_cast<uint16_t>(in[offset++]) + 13;

            cur_opt += delta;
            if (cur_opt == 11 && len < sizeof(path_buf) - path_len - 2) {
                if (path_len > 0) path_buf[path_len++] = '/';
                std::memcpy(&path_buf[path_len], &in[offset], len);
                path_len += len;
            }
            offset += len;
        }

        std::string_view path(path_buf, path_len);

        out[0] = static_cast<uint8_t>((1 << 6) | (2 << 4) | (tkl & 0x0F)); // ACK
        out[2] = static_cast<uint8_t>(mid >> 8);
        out[3] = static_cast<uint8_t>(mid & 0xFF);
        size_t resp_len = 4;

        if (tkl > 0) {
            std::memcpy(&out[resp_len], token.data(), tkl);
            resp_len += tkl;
        }

        if (code == 1 && path == "temp") {
            out[1] = (2 << 5) | 5; // 2.05 Content
            out[resp_len++] = (12 << 4) | 0; // Content-Format: text/plain
            out[resp_len++] = 0xFF; // Marker
            constexpr std::string_view payload = "23.5 C";
            std::memcpy(&out[resp_len], payload.data(), payload.size());
            resp_len += payload.size();
        } else if (code == 3 && path == "led") {
            out[1] = (2 << 5) | 4; // 2.04 Changed
        } else {
            out[1] = (4 << 5) | 4; // 4.04 Not Found
        }

        return resp_len;
    }
};

int main() {
    CoapSocketServer server;
    server.run();
    return 0;
}
