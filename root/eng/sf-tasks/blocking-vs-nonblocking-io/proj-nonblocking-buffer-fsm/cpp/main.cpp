#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <sys/socket.h>

enum class IoStatus {
    Ok,
    WantRead,
    WantWrite,
    PeerClosed,
    Error
};

enum class ParserState {
    ReadHeader,
    ReadPayload
};

class NonblockingConnection {
public:
    static constexpr size_t MaxPayloadSize = 1024 * 1024; // 1 МБ

    explicit NonblockingConnection(int fd) : fd_(fd) {
        int flags = fcntl(fd_, F_GETFL, 0);
        fcntl(fd_, F_SETFL, flags | O_NONBLOCK);
        rx_buf_.reserve(4096);
        tx_buf_.reserve(4096);
    }

    ~NonblockingConnection() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NonblockingConnection(const NonblockingConnection&) = delete;
    NonblockingConnection& operator=(const NonblockingConnection&) = delete;
    NonblockingConnection(NonblockingConnection&& other) noexcept 
        : fd_(other.fd_), rx_buf_(std::move(other.rx_buf_)), tx_buf_(std::move(other.tx_buf_)),
          rx_offset_(other.rx_offset_), tx_offset_(other.tx_offset_),
          rx_state_(other.rx_state_), expected_payload_len_(other.expected_payload_len_) {
        other.fd_ = -1;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    IoStatus read_nonblocking() {
        while (true) {
            compact_rx();
            size_t old_size = rx_buf_.size();
            rx_buf_.resize(old_size + 4096);

            ssize_t n = ::read(fd_, rx_buf_.data() + old_size, 4096);
            if (n > 0) {
                rx_buf_.resize(old_size + static_cast<size_t>(n));
                continue;
            }
            rx_buf_.resize(old_size);

            if (n == 0) return IoStatus::PeerClosed;
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return IoStatus::WantRead;
            return IoStatus::Error;
        }
    }

    template <typename Callback>
    bool parse_frames(Callback&& on_frame) {
        while (true) {
            size_t available = rx_buf_.size() - rx_offset_;

            if (rx_state_ == ParserState::ReadHeader) {
                if (available < sizeof(uint32_t)) return true;
                uint32_t net_len = 0;
                std::memcpy(&net_len, rx_buf_.data() + rx_offset_, sizeof(uint32_t));
                expected_payload_len_ = ntohl(net_len);
                rx_offset_ += sizeof(uint32_t);

                if (expected_payload_len_ > MaxPayloadSize) return false;
                rx_state_ = ParserState::ReadPayload;
                available = rx_buf_.size() - rx_offset_;
            }

            if (rx_state_ == ParserState::ReadPayload) {
                if (available < expected_payload_len_) return true;
                std::span<const std::byte> payload(
                    reinterpret_cast<const std::byte*>(rx_buf_.data() + rx_offset_),
                    expected_payload_len_
                );
                on_frame(payload);
                rx_offset_ += expected_payload_len_;

                rx_state_ = ParserState::ReadHeader;
                expected_payload_len_ = 0;
            }
        }
    }

    bool enqueue_message(std::span<const std::byte> payload) {
        if (payload.size() > MaxPayloadSize) return false;
        compact_tx();

        uint32_t net_len = htonl(static_cast<uint32_t>(payload.size()));
        const auto* len_bytes = reinterpret_cast<const uint8_t*>(&net_len);
        tx_buf_.insert(tx_buf_.end(), len_bytes, len_bytes + sizeof(uint32_t));

        const auto* payload_bytes = reinterpret_cast<const uint8_t*>(payload.data());
        tx_buf_.insert(tx_buf_.end(), payload_bytes, payload_bytes + payload.size());
        return true;
    }

    IoStatus flush_write() {
        while (tx_offset_ < tx_buf_.size()) {
            size_t to_write = tx_buf_.size() - tx_offset_;
            ssize_t n = ::write(fd_, tx_buf_.data() + tx_offset_, to_write);

            if (n > 0) {
                tx_offset_ += static_cast<size_t>(n);
                continue;
            }
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return IoStatus::WantWrite;
            return IoStatus::Error;
        }
        compact_tx();
        return IoStatus::Ok;
    }

private:
    void compact_rx() {
        if (rx_offset_ == 0) return;
        if (rx_offset_ >= rx_buf_.size()) {
            rx_buf_.clear();
        } else {
            rx_buf_.erase(rx_buf_.begin(), rx_buf_.begin() + static_cast<std::ptrdiff_t>(rx_offset_));
        }
        rx_offset_ = 0;
    }

    void compact_tx() {
        if (tx_offset_ == 0) return;
        if (tx_offset_ >= tx_buf_.size()) {
            tx_buf_.clear();
        } else {
            tx_buf_.erase(tx_buf_.begin(), tx_buf_.begin() + static_cast<std::ptrdiff_t>(tx_offset_));
        }
        tx_offset_ = 0;
    }

    int fd_{-1};
    std::vector<uint8_t> rx_buf_;
    std::vector<uint8_t> tx_buf_;
    size_t rx_offset_{0};
    size_t tx_offset_{0};
    ParserState rx_state_{ParserState::ReadHeader};
    uint32_t expected_payload_len_{0};
};
