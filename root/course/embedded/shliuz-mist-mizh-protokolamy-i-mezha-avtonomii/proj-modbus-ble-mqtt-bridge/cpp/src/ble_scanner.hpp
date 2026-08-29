#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <optional>
#include <span>
#include <string>

#include "posix_fd.hpp"

namespace gw {

struct BleSample {
    std::array<std::uint8_t, 6> address{};  // як у HCI: молодшим байтом уперед
    float temperatureC{};
    std::uint8_t batteryPercent{};
    std::int8_t rssiDbm{};

    [[nodiscard]] std::string addressText() const;
};

// Пасивне сканування BLE через сирий HCI-сокет ядра.
//
// Давачі на рухомих підшипниках не тримають з'єднання: прокинувся, кинув
// рекламний кадр, заснув. Тож ніякого GATT тут немає — лише розбір реклами.
// Конструктор вмикає сканування, деструктор вимикає: радіо, забуте ввімкненим,
// їсть акумулятор шлюза цілодобово.
//
// Потрібні CAP_NET_RAW і CAP_NET_ADMIN; bluetoothd на цьому ж адаптері
// сканувати одночасно не повинен — він перезапише параметри.
class BleScanner {
public:
    explicit BleScanner(int hciIndex);
    ~BleScanner();

    BleScanner(const BleScanner&) = delete;
    BleScanner& operator=(const BleScanner&) = delete;

    // std::nullopt — за відведений час придатного кадру не було.
    // Виняток — сокет помер (адаптер вимкнули чи забрали).
    [[nodiscard]] std::optional<BleSample> next(std::chrono::milliseconds timeout);

private:
    void sendCommand(std::uint16_t opcode, std::span<const std::uint8_t> params);
    void setScanEnable(bool enable);

    Fd fd_;
};

}  // namespace gw
