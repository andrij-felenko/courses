#include "modbus_master.hpp"

#include <algorithm>
#include <cstring>
#include <format>

#include <fcntl.h>
#include <termios.h>

namespace gw {
namespace {

constexpr std::uint8_t kFcReadHolding = 0x03;
constexpr std::uint8_t kFcWriteCoil = 0x05;

// Класичний Modbus CRC-16: поліном 0xA001, початкове значення 0xFFFF.
std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (const std::uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 1) ? static_cast<std::uint16_t>((crc >> 1) ^ 0xA001)
                            : static_cast<std::uint16_t>(crc >> 1);
        }
    }
    return crc;
}

speed_t baudConstant(int baud) {
    switch (baud) {
        case 9600:   return B9600;
        case 19200:  return B19200;
        case 38400:  return B38400;
        case 57600:  return B57600;
        case 115200: return B115200;
        default:     throw ModbusError{ModbusErrc::Io, std::format("швидкість {} не підтримується", baud)};
    }
}

}  // namespace

ModbusMaster::ModbusMaster(const std::string& device, int baud, std::chrono::milliseconds timeout)
    : timeout_{timeout} {
    const speed_t speed = baudConstant(baud);

    fd_ = Fd{::open(device.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK)};
    if (!fd_.valid()) {
        throw std::system_error{errno, std::generic_category(), device};
    }

    termios tio{};
    if (::tcgetattr(fd_.get(), &tio) != 0) {
        throw std::system_error{errno, std::generic_category(), "tcgetattr"};
    }
    ::cfmakeraw(&tio);
    tio.c_cflag &= ~static_cast<tcflag_t>(CSIZE | CSTOPB | PARODD | CRTSCTS);
    tio.c_cflag |= CS8 | PARENB | CLOCAL | CREAD;  // 8E1, як велить стандарт RTU
    tio.c_iflag |= INPCK;                          // збій парності ловить апарат
    tio.c_cc[VMIN] = 0;                            // усе чекання робить poll()
    tio.c_cc[VTIME] = 0;
    if (::cfsetispeed(&tio, speed) != 0 || ::cfsetospeed(&tio, speed) != 0 ||
        ::tcsetattr(fd_.get(), TCSANOW, &tio) != 0) {
        throw std::system_error{errno, std::generic_category(), "налаштування порту"};
    }
}

// Дописує CRC, віддає кадр і збирає відповідь. Довжину відповіді Modbus RTU у
// потоці не позначає — вона випливає з функції, тож читаємо рівно очікуване.
std::vector<std::uint8_t> ModbusMaster::transact(std::span<const std::uint8_t> request) {
    std::vector<std::uint8_t> frame{request.begin(), request.end()};
    const std::uint16_t crc = crc16(request);
    frame.push_back(static_cast<std::uint8_t>(crc & 0xFF));  // молодший байт уперед
    frame.push_back(static_cast<std::uint8_t>(crc >> 8));

    ::tcflush(fd_.get(), TCIFLUSH);  // луна попереднього обміну нам не потрібна
    fd_.writeAll(std::as_bytes(std::span{frame}));

    const auto deadline = std::chrono::steady_clock::now() + timeout_;
    std::vector<std::uint8_t> response(2);
    auto readInto = [&](std::size_t offset, std::size_t count) {
        response.resize(offset + count);
        const std::span<std::uint8_t> tail{response.data() + offset, count};
        if (!fd_.readExact(std::as_writable_bytes(tail), deadline)) {
            throw ModbusError{ModbusErrc::Timeout, "підлеглий не відповів"};
        }
    };

    readInto(0, 2);
    if (response[0] != request[0]) {
        throw ModbusError{ModbusErrc::Frame, "відповів не той адресат"};
    }

    const bool isException = (response[1] & 0x80) != 0;
    if (isException) {
        readInto(2, 3);  // код винятку + CRC
    } else if (response[1] != request[1]) {
        throw ModbusError{ModbusErrc::Frame, "відповідь не на ту функцію"};
    } else if (response[1] == kFcReadHolding) {
        readInto(2, 1);
        readInto(3, static_cast<std::size_t>(response[2]) + 2);
    } else {
        readInto(2, 6);  // FC 05 відповідає точною луною запиту
    }

    const std::span<const std::uint8_t> body{response.data(), response.size() - 2};
    const auto got = static_cast<std::uint16_t>(response[response.size() - 2] |
                                                (response[response.size() - 1] << 8));
    if (crc16(body) != got) {
        throw ModbusError{ModbusErrc::Crc, "CRC відповіді не збігся"};
    }
    if (isException) {
        throw ModbusError{ModbusErrc::Exception,
                          std::format("виняток Modbus 0x{:02X}", response[2]), response[2]};
    }
    return response;
}

std::vector<std::uint16_t> ModbusMaster::readHolding(std::uint8_t slave, std::uint16_t start,
                                                     std::uint16_t count) {
    if (count == 0 || count > 125) {
        throw ModbusError{ModbusErrc::Frame, "за раз читається від 1 до 125 регістрів"};
    }

    const std::uint8_t request[]{
        slave,
        kFcReadHolding,
        static_cast<std::uint8_t>(start >> 8),
        static_cast<std::uint8_t>(start & 0xFF),
        static_cast<std::uint8_t>(count >> 8),
        static_cast<std::uint8_t>(count & 0xFF),
    };

    std::lock_guard lock{mutex_};
    const auto response = transact(request);
    if (response[2] != static_cast<std::uint8_t>(count * 2)) {
        throw ModbusError{ModbusErrc::Frame, "довжина даних не збігається із запитом"};
    }

    std::vector<std::uint16_t> regs;
    regs.reserve(count);
    for (std::uint16_t i = 0; i < count; ++i) {
        regs.push_back(static_cast<std::uint16_t>((response[3 + i * 2] << 8) | response[4 + i * 2]));
    }
    return regs;
}

void ModbusMaster::writeCoil(std::uint8_t slave, std::uint16_t address, bool on) {
    const std::uint8_t request[]{
        slave,
        kFcWriteCoil,
        static_cast<std::uint8_t>(address >> 8),
        static_cast<std::uint8_t>(address & 0xFF),
        static_cast<std::uint8_t>(on ? 0xFF : 0x00),  // 0xFF00 — увімкнути
        0x00,
    };

    std::lock_guard lock{mutex_};
    const auto response = transact(request);
    // Луна мусить збігтися побайтово — інакше ми не знаємо, що саме спрацювало.
    if (!std::equal(request + 2, request + 6, response.begin() + 2)) {
        throw ModbusError{ModbusErrc::Frame, "луна запису котушки не збіглася"};
    }
}

float ModbusMaster::regsToFloat(std::span<const std::uint16_t, 2> regs) noexcept {
    const std::uint32_t raw = (static_cast<std::uint32_t>(regs[0]) << 16) | regs[1];
    float value{};
    std::memcpy(&value, &raw, sizeof(value));
    return value;
}

}  // namespace gw
