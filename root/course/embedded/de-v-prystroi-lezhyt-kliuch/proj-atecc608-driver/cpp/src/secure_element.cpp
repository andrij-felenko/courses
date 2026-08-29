#include "secure_element.hpp"

#include <algorithm>
#include <thread>

namespace atecc {
namespace {

using namespace std::chrono_literals;

// Перший байт транзакції — Word Address: він каже чипу, що робити з рештою
// пакета або, коли пакета немає, змінює режим живлення.
constexpr std::uint8_t kWordAddressSleep = 0x01;
constexpr std::uint8_t kWordAddressCommand = 0x03;

constexpr std::uint8_t kOpcodeRead = 0x02;
constexpr std::uint8_t kOpcodeSign = 0x41;
constexpr std::uint8_t kSignModeExternal = 0x80; // Param1: підписати переданий дайджест

// Статус-байти з таблиці відповідей ATECC608.
constexpr std::uint8_t kStatusSuccess = 0x00;
constexpr std::uint8_t kStatusMiscompare = 0x01; // звірення не збіглося / відхилено
constexpr std::uint8_t kStatusParse = 0x03;      // хибні параметри або заборонений доступ
constexpr std::uint8_t kStatusEccFault = 0x05;
constexpr std::uint8_t kStatusSelfTest = 0x07;
constexpr std::uint8_t kStatusExecution = 0x0F;
constexpr std::uint8_t kStatusAfterWake = 0x11;
constexpr std::uint8_t kStatusWatchdog = 0xEE;
constexpr std::uint8_t kStatusComm = 0xFF;

constexpr auto kWakeDelay = 2ms;   // t_WHI ≥ 1.5 мс
constexpr auto kPollStep = 4ms;
constexpr auto kSignExecMin = 50ms;
constexpr auto kSignExecMax = 250ms; // значно менше за сторожовий таймер (1.7 с)
constexpr auto kReadExecMin = 1ms;
constexpr auto kReadExecMax = 50ms;

constexpr std::size_t kStatusPacketSize = 4;
constexpr std::size_t kSignResponseSize = 67; // 1 + 64 + 2
constexpr std::size_t kReadResponseSize = 35; // 1 + 32 + 2

std::uint16_t littleEndian(std::uint8_t low, std::uint8_t high) noexcept
{
    return static_cast<std::uint16_t>(low | (static_cast<std::uint16_t>(high) << 8));
}

// Складання командного пакета. Count рахує сам себе, заголовок, дані й CRC,
// але не рахує байт Word Address — той живе поза командою.
template <std::size_t DataSize>
std::array<std::uint8_t, DataSize + 8> buildCommand(std::uint8_t opcode, std::uint8_t param1,
                                                    std::uint16_t param2,
                                                    std::span<const std::uint8_t, DataSize> data)
{
    std::array<std::uint8_t, DataSize + 8> frame{};
    const auto count = static_cast<std::uint8_t>(DataSize + 7);

    frame[0] = kWordAddressCommand;
    frame[1] = count;
    frame[2] = opcode;
    frame[3] = param1;
    frame[4] = static_cast<std::uint8_t>(param2 & 0xFF);
    frame[5] = static_cast<std::uint8_t>((param2 >> 8) & 0xFF);
    std::ranges::copy(data, frame.begin() + 6);

    // CRC — від байта Count до останнього байта даних.
    const std::uint16_t crc = crc16(std::span<const std::uint8_t>(frame).subspan(1, count - 2u));
    frame[DataSize + 6] = static_cast<std::uint8_t>(crc & 0xFF);
    frame[DataSize + 7] = static_cast<std::uint8_t>((crc >> 8) & 0xFF);
    return frame;
}

} // namespace

std::uint16_t crc16(std::span<const std::uint8_t> data) noexcept
{
    std::uint16_t crc = 0x0000;

    for (const std::uint8_t byte : data) {
        // Біти кожного байта заходять від молодшого — так рахує сам чип.
        for (std::uint8_t mask = 0x01; mask != 0x00; mask = static_cast<std::uint8_t>(mask << 1)) {
            const std::uint8_t dataBit = (byte & mask) ? 1 : 0;
            const std::uint8_t crcBit = static_cast<std::uint8_t>((crc >> 15) & 0x01);
            crc = static_cast<std::uint16_t>(crc << 1);
            if (dataBit != crcBit) {
                crc ^= 0x8005;
            }
        }
    }
    return crc;
}

std::expected<void, Error> SecureElement::wake()
{
    static constexpr std::array<std::uint8_t, 1> kZero{0x00};

    // Імпульс пробудження. Запис нульового байта на зарезервовану адресу 0x00
    // тримає SDA внизу дев'ять бітових інтервалів — на 100 кГц це ≈90 мкс,
    // тобто більше за потрібні 60 мкс (t_WLO). Цю адресу не підтверджує ніхто,
    // тому результат свідомо відкидаємо.
    static_cast<void>(bus_.write(0x00, kZero));
    std::this_thread::sleep_for(kWakeDelay);

    awake_ = false;
    std::array<std::uint8_t, 4> response{};
    if (!bus_.read(address_, response)) {
        return std::unexpected(Error::Io);
    }
    if (response[0] != 0x04) {
        return std::unexpected(Error::Protocol);
    }
    if (littleEndian(response[2], response[3]) != crc16(std::span(response).first(2))) {
        return std::unexpected(Error::Crc);
    }

    status_ = response[1];
    if (status_ != kStatusAfterWake) {
        return std::unexpected(Error::Device);
    }

    awake_ = true;
    return {};
}

void SecureElement::sleep() noexcept
{
    if (!awake_) {
        return;
    }
    // Без цього чип тримає генератор до спрацювання сторожового таймера й
    // тягне мікроампери замість наноамперів.
    static constexpr std::array<std::uint8_t, 1> kSleep{kWordAddressSleep};
    static_cast<void>(bus_.write(address_, kSleep));
    awake_ = false;
}

std::expected<std::span<const std::uint8_t>, Error> SecureElement::readPacket()
{
    std::array<std::uint8_t, 1> lengthByte{};
    if (!bus_.read(address_, lengthByte)) {
        return std::unexpected(Error::Io);
    }

    const std::size_t count = lengthByte[0];
    if (count < kStatusPacketSize || count > rx_.size()) {
        return std::unexpected(Error::Protocol);
    }

    // Нове читання змушує чип віддати вихідний буфер спочатку, тож байт
    // довжини приходить удруге — уже разом з усім пакетом.
    const std::span<std::uint8_t> packet(rx_.data(), count);
    if (!bus_.read(address_, packet)) {
        return std::unexpected(Error::Io);
    }
    if (packet[0] != count) {
        return std::unexpected(Error::Protocol);
    }
    if (littleEndian(packet[count - 2], packet[count - 1]) != crc16(packet.first(count - 2))) {
        return std::unexpected(Error::Crc);
    }

    return std::span<const std::uint8_t>(packet);
}

std::expected<std::span<const std::uint8_t>, Error> SecureElement::transact(
    std::span<const std::uint8_t> command, Milliseconds execMin, Milliseconds execMax)
{
    if (!awake_) {
        if (auto woken = wake(); !woken) {
            return std::unexpected(woken.error());
        }
    }

    status_ = kStatusSuccess;
    if (!bus_.write(address_, command)) {
        awake_ = false; // команда не дійшла — стан чипа невідомий
        return std::unexpected(Error::Io);
    }

    std::this_thread::sleep_for(execMin);
    auto waited = execMin;
    int crcRetries = 0;

    for (;;) {
        auto packet = readPacket();

        if (packet) {
            if (packet->size() == kStatusPacketSize) {
                status_ = (*packet)[1];
                if (status_ == kStatusSuccess) {
                    return packet;
                }
                if (status_ == kStatusAfterWake) {
                    awake_ = false; // чип перезапустився й забув команду
                }
                return std::unexpected(Error::Device);
            }
            return packet;
        }

        if (packet.error() == Error::Crc) {
            // Побитий пакет чип віддає повторно, поки хост не забрав його
            // цілим; двох спроб досить, далі це вже не перешкода на лінії.
            if (++crcRetries > 2) {
                return std::unexpected(Error::Crc);
            }
            continue;
        }
        if (packet.error() != Error::Io) {
            return std::unexpected(packet.error());
        }

        // NACK на адресу: криптоядро ще рахує точку кривої.
        if (waited >= execMax) {
            return std::unexpected(Error::Timeout);
        }
        std::this_thread::sleep_for(kPollStep);
        waited += kPollStep;
    }
}

std::expected<Signature, Error> SecureElement::signDigest(std::uint8_t slot, Digest digest)
{
    if (slot > 15) {
        return std::unexpected(Error::BadArgument);
    }

    const auto command = buildCommand<kDigestSize>(kOpcodeSign, kSignModeExternal, slot, digest);
    auto response = transact(command, kSignExecMin, kSignExecMax);
    if (!response) {
        return std::unexpected(response.error());
    }
    if (response->size() != kSignResponseSize) {
        return std::unexpected(Error::Protocol);
    }

    Signature signature{};
    std::ranges::copy(response->subspan(1, kSignatureSize), signature.begin());
    return signature;
}

std::expected<LockState, Error> SecureElement::lockState()
{
    // Read зони конфігурації, блок 2 — байти 64..95. Param1: біт 7 просить
    // 32 байти, молодші біти вибирають зону (0 — конфігурація).
    // Param2 = (номер блока << 3) | зсув слова всередині блока.
    constexpr std::uint16_t kBlockTwo = 2u << 3;
    const auto command = buildCommand<0>(kOpcodeRead, 0x80, kBlockTwo,
                                         std::span<const std::uint8_t, 0>{});

    auto response = transact(command, kReadExecMin, kReadExecMax);
    if (!response) {
        return std::unexpected(response.error());
    }
    if (response->size() != kReadResponseSize) {
        return std::unexpected(Error::Protocol);
    }

    // Байт 86 конфігурації — LockValue (зона даних), байт 87 — LockConfig.
    // У блоці з початком на байті 64 це зсуви 22 і 23, плюс байт Count.
    return LockState{
        .configuration = (*response)[1 + 23] != 0x55,
        .data = (*response)[1 + 22] != 0x55,
    };
}

std::string_view describe(Error error) noexcept
{
    switch (error) {
    case Error::Io:          return "шина I2C не відповіла";
    case Error::Crc:         return "CRC16 відповіді не збіглася";
    case Error::Timeout:     return "чип не відповів у межах часу виконання";
    case Error::Protocol:    return "несподівана довжина пакета";
    case Error::Device:      return "чип повернув код помилки";
    case Error::NotLocked:   return "зони пам'яті не заблоковані";
    case Error::BadArgument: return "хибний аргумент";
    }
    return "невідома помилка";
}

std::string_view describeStatus(std::uint8_t status) noexcept
{
    switch (status) {
    case kStatusSuccess:    return "0x00 виконано";
    case kStatusMiscompare: return "0x01 звірення не збіглося або команду відхилено";
    case kStatusParse:      return "0x03 хибні параметри або заборонений доступ";
    case kStatusEccFault:   return "0x05 збій обчислення на кривій";
    case kStatusSelfTest:   return "0x07 не пройдено самоперевірку";
    case kStatusExecution:  return "0x0F команду неможливо виконати в цьому стані";
    case kStatusAfterWake:  return "0x11 чип щойно прокинувся";
    case kStatusWatchdog:   return "0xEE сторожовий таймер ось-ось вимкне генератор";
    case kStatusComm:       return "0xFF помилка CRC або зв'язку";
    default:                return "невідомий статус";
    }
}

} // namespace atecc
