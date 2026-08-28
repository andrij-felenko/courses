#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <thread>
#include <expected>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>

enum class BootloaderError {
    PortOpenFailed,
    ConfigurationFailed,
    SyncFailed,
    AckTimeout,
    NackReceived,
    WriteFailed,
    InvalidParameter
};

class SerialPort {
public:
    explicit SerialPort(const std::string& port_name) {
        fd_ = open(port_name.c_str(), O_RDWR | O_NOCTTY | O_SYNC);
        if (fd_ < 0) return;

        struct termios tty{};
        if (tcgetattr(fd_, &tty) != 0) {
            closePort();
            return;
        }

        cfsetospeed(&tty, B115200);
        cfsetispeed(&tty, B115200);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8 бітів даних
        tty.c_cflag |= PARENB;                      // Контроль парності
        tty.c_cflag &= ~PARODD;                     // Even
        tty.c_cflag &= ~CSTOPB;                     // 1 стоп-біт
        tty.c_cflag &= ~CRTSCTS;
        tty.c_cflag |= (CLOCAL | CREAD);

        tty.c_iflag &= ~(IXON | IXOFF | IXANY);
        tty.c_lflag = 0;
        tty.c_oflag = 0;
        tty.c_cc[VMIN]  = 0;
        tty.c_cc[VTIME] = 10;                       // Таймаут 1.0 с

        if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
            closePort();
        }
    }

    ~SerialPort() {
        closePort();
    }

    // Заборона копіювання для суворого контролю дескриптора (RAII)
    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    SerialPort(SerialPort&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    [[nodiscard]] bool isOpen() const noexcept { return fd_ >= 0; }

    bool writeBytes(std::span<const uint8_t> data) const {
        if (!isOpen()) return false;
        return write(fd_, data.data(), data.size()) == static_cast<ssize_t>(data.size());
    }

    bool readBytes(std::span<uint8_t> buffer) const {
        if (!isOpen()) return false;
        size_t total = 0;
        while (total < buffer.size()) {
            ssize_t res = read(fd_, buffer.data() + total, buffer.size() - total);
            if (res <= 0) return false;
            total += static_cast<size_t>(res);
        }
        return true;
    }

    void flush() const {
        if (isOpen()) tcflush(fd_, TCIOFLUSH);
    }

private:
    int fd_{-1};

    void closePort() noexcept {
        if (fd_ >= 0) {
            close(fd_);
            fd_ = -1;
        }
    }
};

class Stm32Flasher {
public:
    static constexpr uint8_t ACK_BYTE   = 0x79;
    static constexpr uint8_t NACK_BYTE  = 0x1F;
    static constexpr uint8_t CMD_GET_ID = 0x02;
    static constexpr uint8_t CMD_ERASE  = 0x44;
    static constexpr uint8_t CMD_WRITE  = 0x31;
    static constexpr uint8_t CMD_GO     = 0x21;

    explicit Stm32Flasher(SerialPort& port) : port_(port) {}

    std::expected<void, BootloaderError> sync() {
        port_.flush();
        const uint8_t sync_byte = 0x7F;
        if (!port_.writeBytes(std::span{&sync_byte, 1})) {
            return std::unexpected(BootloaderError::WriteFailed);
        }
        return waitAck(std::chrono::seconds(2));
    }

    std::expected<uint16_t, BootloaderError> getChipId() {
        const uint8_t cmd[2] = {CMD_GET_ID, static_cast<uint8_t>(~CMD_GET_ID)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return std::unexpected(ack_res.error());

        uint8_t len = 0;
        if (!port_.readBytes(std::span{&len, 1}) || len != 1) {
            return std::unexpected(BootloaderError::InvalidParameter);
        }

        uint8_t pid_buf[2]{};
        if (!port_.readBytes(pid_buf)) return std::unexpected(BootloaderError::SyncFailed);
        
        auto ack_end = waitAck(std::chrono::seconds(1));
        if (!ack_end) return std::unexpected(ack_end.error());

        return (static_cast<uint16_t>(pid_buf[0]) << 8) | pid_buf[1];
    }

    std::expected<void, BootloaderError> massErase() {
        const uint8_t cmd[2] = {CMD_ERASE, static_cast<uint8_t>(~CMD_ERASE)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return ack_res;

        // Код глобального стирання 0xFFFF та XOR сума 0x00
        const uint8_t params[3] = {0xFF, 0xFF, 0x00};
        if (!port_.writeBytes(params)) return std::unexpected(BootloaderError::WriteFailed);

        // Повне стирання матриці Flash вимагає тривалого таймауту
        return waitAck(std::chrono::seconds(30));
    }

    std::expected<void, BootloaderError> writeBlock(uint32_t address, std::span<const uint8_t> data) {
        if (data.empty() || data.size() > 256) {
            return std::unexpected(BootloaderError::InvalidParameter);
        }

        const uint8_t cmd[2] = {CMD_WRITE, static_cast<uint8_t>(~CMD_WRITE)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return ack_res;

        const uint8_t addr_buf[5] = {
            static_cast<uint8_t>((address >> 24) & 0xFF),
            static_cast<uint8_t>((address >> 16) & 0xFF),
            static_cast<uint8_t>((address >> 8) & 0xFF),
            static_cast<uint8_t>(address & 0xFF),
            static_cast<uint8_t>(((address >> 24) ^ (address >> 16) ^ (address >> 8) ^ address) & 0xFF)
        };

        if (!port_.writeBytes(addr_buf)) return std::unexpected(BootloaderError::WriteFailed);
        auto ack_addr = waitAck(std::chrono::seconds(1));
        if (!ack_addr) return ack_addr;

        std::vector<uint8_t> packet;
        packet.reserve(data.size() + 2);
        
        const auto n = static_cast<uint8_t>(data.size() - 1);
        packet.push_back(n);
        uint8_t checksum = n;

        for (uint8_t byte : data) {
            packet.push_back(byte);
            checksum ^= byte;
        }
        packet.push_back(checksum);

        if (!port_.writeBytes(packet)) return std::unexpected(BootloaderError::WriteFailed);
        return waitAck(std::chrono::seconds(2));
    }

    std::expected<void, BootloaderError> jumpToApp(uint32_t address) {
        const uint8_t cmd[2] = {CMD_GO, static_cast<uint8_t>(~CMD_GO)};
        if (!port_.writeBytes(cmd)) return std::unexpected(BootloaderError::WriteFailed);
        
        auto ack_res = waitAck(std::chrono::seconds(1));
        if (!ack_res) return ack_res;

        const uint8_t addr_buf[5] = {
            static_cast<uint8_t>((address >> 24) & 0xFF),
            static_cast<uint8_t>((address >> 16) & 0xFF),
            static_cast<uint8_t>((address >> 8) & 0xFF),
            static_cast<uint8_t>(address & 0xFF),
            static_cast<uint8_t>(((address >> 24) ^ (address >> 16) ^ (address >> 8) ^ address) & 0xFF)
        };

        if (!port_.writeBytes(addr_buf)) return std::unexpected(BootloaderError::WriteFailed);
        return waitAck(std::chrono::seconds(1));
    }

private:
    SerialPort& port_;

    std::expected<void, BootloaderError> waitAck(std::chrono::milliseconds timeout) {
        const auto start = std::chrono::steady_clock::now();
        while (std::chrono::steady_clock::now() - start < timeout) {
            uint8_t byte = 0;
            if (port_.readBytes(std::span{&byte, 1})) {
                if (byte == ACK_BYTE) return {};
                if (byte == NACK_BYTE) return std::unexpected(BootloaderError::NackReceived);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        return std::unexpected(BootloaderError::AckTimeout);
    }
};
