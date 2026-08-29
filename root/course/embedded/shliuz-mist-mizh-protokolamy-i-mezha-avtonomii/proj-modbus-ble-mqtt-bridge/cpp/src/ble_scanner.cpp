#include "ble_scanner.hpp"

#include <cstring>
#include <format>
#include <stdexcept>
#include <vector>

#include <sys/socket.h>

namespace gw {
namespace {

// Константи ABI ядра: оголошуємо їх тут, щоб не тягнути в шлюз увесь bluez.
constexpr int kAfBluetooth = 31;
constexpr int kBtProtoHci = 1;
constexpr unsigned short kHciChannelRaw = 0;
constexpr int kSolHci = 0;
constexpr int kHciFilterOpt = 2;

constexpr std::uint8_t kHciCommandPkt = 0x01;
constexpr std::uint8_t kHciEventPkt = 0x04;
constexpr std::uint8_t kEvtCmdComplete = 0x0E;
constexpr std::uint8_t kEvtLeMeta = 0x3E;
constexpr std::uint8_t kLeAdvertisingReport = 0x02;

// OGF 0x08 (LE Controller) → opcode = (OGF << 10) | OCF
constexpr std::uint16_t kOpLeSetScanParams = 0x200B;
constexpr std::uint16_t kOpLeSetScanEnable = 0x200C;

// Тип структури рекламних даних: Service Data з 16-бітним UUID.
constexpr std::uint8_t kAdServiceData16 = 0x16;
// Environmental Sensing Service — під цим UUID давач кладе свій блок:
// версія формату, int16 температури в сотих градуса, заряд у відсотках.
constexpr std::uint16_t kUuidEnvSensing = 0x181A;
constexpr std::uint8_t kSensorFormatV1 = 0x01;

struct sockaddr_hci {
    unsigned short hci_family;
    unsigned short hci_dev;
    unsigned short hci_channel;
};

struct hci_filter {
    std::uint32_t type_mask;
    std::uint32_t event_mask[2];
    std::uint16_t opcode;
};

// Розбір поля рекламних даних: послідовність структур «довжина, тип, вміст».
std::optional<BleSample> parseAdvertisingData(std::span<const std::uint8_t> ad) {
    std::size_t i = 0;
    while (i < ad.size()) {
        const std::size_t length = ad[i];
        if (length == 0) {
            break;  // нульова довжина — далі лише набивка
        }
        if (i + 1 + length > ad.size()) {
            return std::nullopt;  // кадр обрізаний, довіряти йому не можна
        }

        const std::uint8_t type = ad[i + 1];
        const auto body = ad.subspan(i + 2, length - 1);

        if (type == kAdServiceData16 && body.size() >= 6) {
            const auto uuid = static_cast<std::uint16_t>(body[0] | (body[1] << 8));
            if (uuid == kUuidEnvSensing && body[2] == kSensorFormatV1) {
                const auto centi = static_cast<std::int16_t>(body[3] | (body[4] << 8));
                BleSample sample;
                sample.temperatureC = centi / 100.0F;
                sample.batteryPercent = body[5];
                return sample;
            }
        }
        i += 1 + length;
    }
    return std::nullopt;
}

}  // namespace

std::string BleSample::addressText() const {
    return std::format("{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}", address[5], address[4],
                       address[3], address[2], address[1], address[0]);
}

BleScanner::BleScanner(int hciIndex) {
    fd_ = Fd{::socket(kAfBluetooth, SOCK_RAW, kBtProtoHci)};
    if (!fd_.valid()) {
        throw std::system_error{errno, std::generic_category(), "сокет HCI"};
    }

    sockaddr_hci addr{};
    addr.hci_family = kAfBluetooth;
    addr.hci_dev = static_cast<unsigned short>(hciIndex);
    addr.hci_channel = kHciChannelRaw;
    if (::bind(fd_.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        throw std::system_error{errno, std::generic_category(), std::format("hci{}", hciIndex)};
    }

    // Пропускаємо всі події й відсіюємо потрібні самі: розбір усе одно
    // зосереджено в одному місці, фільтр ядра тут нічого не заощадив би.
    hci_filter filter{};
    filter.type_mask = 1U << kHciEventPkt;
    filter.event_mask[0] = 0xFFFFFFFFU;
    filter.event_mask[1] = 0xFFFFFFFFU;
    if (::setsockopt(fd_.get(), kSolHci, kHciFilterOpt, &filter, sizeof(filter)) < 0) {
        throw std::system_error{errno, std::generic_category(), "фільтр HCI"};
    }

    // Скидаємо можливе попереднє сканування, інакше зміна параметрів
    // відхиляється з Command Disallowed.
    try {
        setScanEnable(false);
    } catch (const std::exception&) {
        // Контролер і так не сканував — це не привід не починати.
    }

    static constexpr std::uint8_t kScanParams[]{
        0x00,        // пасивне сканування: SCAN_REQ не шлемо, ефір не гріємо
        0xA0, 0x00,  // інтервал 0x00A0 × 0.625 мс = 100 мс
        0xA0, 0x00,  // вікно дорівнює інтервалу — слухаємо безперервно
        0x00,        // власна адреса публічна
        0x00,        // приймати від усіх, білого списку немає
    };
    sendCommand(kOpLeSetScanParams, kScanParams);
    setScanEnable(true);
}

BleScanner::~BleScanner() {
    try {
        setScanEnable(false);
    } catch (const std::exception&) {
        // Деструктор мовчить: сокет усе одно закриється, а кидати звідси не можна.
    }
}

void BleScanner::sendCommand(std::uint16_t opcode, std::span<const std::uint8_t> params) {
    std::vector<std::uint8_t> packet;
    packet.reserve(params.size() + 4);
    packet.push_back(kHciCommandPkt);
    packet.push_back(static_cast<std::uint8_t>(opcode & 0xFF));
    packet.push_back(static_cast<std::uint8_t>(opcode >> 8));
    packet.push_back(static_cast<std::uint8_t>(params.size()));
    packet.insert(packet.end(), params.begin(), params.end());
    fd_.writeAll(std::as_bytes(std::span{packet}));

    // Без Command Complete ми не знаємо, чи контролер узагалі почав сканувати.
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds{2};
    while (std::chrono::steady_clock::now() < deadline) {
        std::array<std::uint8_t, 260> buffer{};
        if (!fd_.waitReadable(std::chrono::milliseconds{200})) {
            continue;
        }
        const ssize_t n = ::read(fd_.get(), buffer.data(), buffer.size());
        if (n < 7) {
            continue;
        }
        if (buffer[0] != kHciEventPkt || buffer[1] != kEvtCmdComplete) {
            continue;
        }
        const auto answered = static_cast<std::uint16_t>(buffer[4] | (buffer[5] << 8));
        if (answered != opcode) {
            continue;
        }
        if (buffer[6] != 0x00) {
            throw std::runtime_error{
                std::format("контролер відхилив команду 0x{:04X}, статус 0x{:02X}", opcode, buffer[6])};
        }
        return;
    }
    throw std::runtime_error{std::format("контролер не підтвердив команду 0x{:04X}", opcode)};
}

void BleScanner::setScanEnable(bool enable) {
    const std::uint8_t params[]{static_cast<std::uint8_t>(enable ? 0x01 : 0x00), 0x01};
    sendCommand(kOpLeSetScanEnable, params);  // другий байт — фільтр дублів
}

std::optional<BleSample> BleScanner::next(std::chrono::milliseconds timeout) {
    if (!fd_.waitReadable(timeout)) {
        return std::nullopt;
    }

    std::array<std::uint8_t, 260> buffer{};
    const ssize_t n = ::read(fd_.get(), buffer.data(), buffer.size());
    if (n < 0) {
        if (errno == EINTR || errno == EAGAIN) {
            return std::nullopt;
        }
        throw std::system_error{errno, std::generic_category(), "читання HCI"};
    }
    if (n == 0) {
        throw std::runtime_error{"сокет HCI закрився"};
    }

    const std::span<const std::uint8_t> event{buffer.data(), static_cast<std::size_t>(n)};
    // Подія HCI: [тип пакета][код події][довжина][параметри]
    if (event.size() < 5 || event[0] != kHciEventPkt || event[1] != kEvtLeMeta ||
        event[3] != kLeAdvertisingReport) {
        return std::nullopt;
    }

    const std::size_t reports = event[4];
    std::size_t offset = 5;
    for (std::size_t r = 0; r < reports; ++r) {
        // Звіт: тип події(1), тип адреси(1), адреса(6), довжина(1), дані, RSSI(1)
        if (offset + 9 > event.size()) {
            return std::nullopt;
        }
        const std::size_t dataLength = event[offset + 8];
        if (offset + 9 + dataLength + 1 > event.size()) {
            return std::nullopt;
        }

        auto sample = parseAdvertisingData(event.subspan(offset + 9, dataLength));
        if (sample) {
            std::memcpy(sample->address.data(), event.data() + offset + 2, sample->address.size());
            sample->rssiDbm = static_cast<std::int8_t>(event[offset + 9 + dataLength]);
            return sample;
        }
        offset += 9 + dataLength + 1;
    }
    return std::nullopt;
}

}  // namespace gw
