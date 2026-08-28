#include <iostream>
#include <string>
#include <string_view>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

namespace bt {

class RfcommSocket {
public:
    RfcommSocket() : fd_(::socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)) {}
    
    explicit RfcommSocket(int fd) noexcept : fd_(fd) {}
    
    ~RfcommSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    RfcommSocket(const RfcommSocket&) = delete;
    RfcommSocket& operator=(const RfcommSocket&) = delete;

    RfcommSocket(RfcommSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    RfcommSocket& operator=(RfcommSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    std::expected<void, std::error_code> bind_and_listen(uint8_t channel, int backlog = 1) {
        if (!is_valid()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        sockaddr_rc addr{};
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_bdaddr = *BDADDR_ANY;
        addr.rc_channel = channel;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(fd_, backlog) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

    std::expected<void, std::error_code> connect(std::string_view dest_mac, uint8_t channel) {
        if (!is_valid()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        sockaddr_rc addr{};
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_channel = channel;

        std::string mac_str(dest_mac);
        if (str2ba(mac_str.c_str(), &addr.rc_bdaddr) < 0) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        if (::connect(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

    std::expected<std::pair<RfcommSocket, std::string>, std::error_code> accept_client() {
        sockaddr_rc rem_addr{};
        socklen_t opt = sizeof(rem_addr);
        int client_fd = ::accept(fd_, reinterpret_cast<sockaddr*>(&rem_addr), &opt);
        if (client_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        char mac_str[18]{};
        ba2str(&rem_addr.rc_bdaddr, mac_str);
        return std::make_pair(RfcommSocket(client_fd), std::string(mac_str));
    }

    std::expected<size_t, std::error_code> send(std::span<const uint8_t> data) {
        ssize_t sent = ::write(fd_, data.data(), data.size());
        if (sent < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(sent);
    }

    std::expected<size_t, std::error_code> receive(std::span<uint8_t> buffer) {
        ssize_t recvd = ::read(fd_, buffer.data(), buffer.size());
        if (recvd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(recvd);
    }

private:
    int fd_{-1};
};

} // namespace bt

int main() {
    bt::RfcommSocket server;
    if (!server.is_valid()) {
        std::cerr << "Не вдалося відкрити Bluetooth сокет\n";
        return 1;
    }

    constexpr uint8_t channel = 1;
    if (auto res = server.bind_and_listen(channel); !res) {
        std::cerr << "Помилка запуску сервера: " << res.error().message() << '\n';
        return 1;
    }

    std::cout << "C++ RFCOMM сервер запущено на каналі " << int(channel) << '\n';

    auto client_res = server.accept_client();
    if (!client_res) {
        std::cerr << "Помилка accept: " << client_res.error().message() << '\n';
        return 1;
    }

    auto [client, client_mac] = std::move(*client_res);
    std::cout << "Підключено клієнта з адресою: " << client_mac << '\n';

    std::vector<uint8_t> buffer(1024);
    auto recv_res = client.receive(buffer);
    if (recv_res && *recv_res > 0) {
        std::string_view msg(reinterpret_cast<char*>(buffer.data()), *recv_res);
        std::cout << "Отримано повідомлення: " << msg << '\n';
        auto send_res = client.send(std::span(buffer.data(), *recv_res));
        if (!send_res) {
            std::cerr << "Помилка відправки ехо: " << send_res.error().message() << '\n';
        }
    }

    return 0;
}
