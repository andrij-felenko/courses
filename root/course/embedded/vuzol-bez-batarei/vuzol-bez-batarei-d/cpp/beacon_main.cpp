// beacon_main.cpp — Ідіоматична реалізація безбатарейного термомаяка на C++20
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <concepts>

namespace batteryless {

// Базові адреси периферійних модулів у пам'яті
inline constexpr std::uintptr_t RadioBaseAddress = 0x40001000UL;
inline constexpr std::uintptr_t FramStorageAddress = 0x20003F00UL;
inline constexpr std::uint32_t BootMagicValue = 0x55AA55AAUL;

// Апаратний регістр із типізованим доступом
template <typename T, std::uintptr_t Address>
struct HardwareRegister {
    static void write(T value) noexcept {
        *reinterpret_cast<volatile T *>(Address) = value;
    }
    [[nodiscard]] static T read() noexcept {
        return *reinterpret_cast<volatile T *>(Address);
    }
};

using RadioTasksTxEnable = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x000>;
using RadioTasksStart    = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x008>;
using RadioTasksDisable  = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x010>;
using RadioEventsReady   = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x100>;
using RadioEventsEnd     = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x10C>;
using RadioPacketPointer = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x504>;
using RadioFrequency     = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x508>;
using RadioTxPower       = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x50C>;
using RadioMode          = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x510>;
using RadioCrcConfig     = HardwareRegister<std::uint32_t, RadioBaseAddress + 0x534>;

#pragma pack(push, 1)
// Стан вузла, який гарантовано зберігається у FRAM між циклами Run-to-Die
struct NodeState {
    std::uint32_t magic{BootMagicValue};
    std::uint32_t sequence_id{0};
    std::int16_t  last_temperature_x10{0};
    std::uint16_t last_vcap_mv{0};
    std::uint16_t crc16{0};

    [[nodiscard]] bool isValid(std::uint16_t computed_crc) const noexcept {
        return magic == BootMagicValue && crc16 == computed_crc;
    }
};

// Формат нез'єднуваного рекламного пакета Bluetooth Low Energy
struct BleAdvertisementPacket {
    std::uint8_t header{0x42}; // ADV_NONCONN_IND | Random Address
    std::uint8_t length{sizeof(BleAdvertisementPacket) - 2};
    std::array<std::uint8_t, 6> mac_address{0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xC0};

    // Flags structure
    std::uint8_t ad1_len{0x02};
    std::uint8_t ad1_type{0x01};
    std::uint8_t ad1_flags{0x06};

    // Manufacturer Specific Data structure
    std::uint8_t  ad2_len{12};
    std::uint8_t  ad2_type{0xFF};
    std::uint16_t company_id{0xFFFF};
    std::uint32_t sequence_num{0};
    std::int16_t  temperature_x10{0};
    std::uint16_t voltage_mv{0};
    std::uint8_t  energy_source{0x01};
};
#pragma pack(pop)

// Обчислення CRC-16-CCITT під час компіляції або виконання
class Crc16Ccitt {
public:
    static constexpr std::uint16_t calculate(std::span<const std::uint8_t> data) noexcept {
        std::uint16_t crc = 0xFFFF;
        for (const auto byte : data) {
            crc ^= static_cast<std::uint16_t>(byte) << 8;
            for (std::uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }
};

// Керування станом в енергонезалежній пам'яті за принципом RAII
class FramStateManager {
public:
    FramStateManager() noexcept {
        auto *fram_ptr = reinterpret_cast<const NodeState *>(FramStorageAddress);
        state_ = *fram_ptr;

        const auto payload_span = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(&state_),
            sizeof(NodeState) - sizeof(std::uint16_t)
        );

        const auto expected_crc = Crc16Ccitt::calculate(payload_span);
        if (!state_.isValid(expected_crc)) {
            state_ = NodeState{}; // Скидання у початковий стан при холодному пуску
        }
    }

    [[nodiscard]] NodeState &get() noexcept { return state_; }
    [[nodiscard]] const NodeState &get() const noexcept { return state_; }

    void commit() noexcept {
        state_.sequence_id++;
        const auto payload_span = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t *>(&state_),
            sizeof(NodeState) - sizeof(std::uint16_t)
        );
        state_.crc16 = Crc16Ccitt::calculate(payload_span);

        auto *fram_target = reinterpret_cast<NodeState *>(FramStorageAddress);
        *fram_target = state_; // Миттєвий запис на шинній швидкості
    }

private:
    NodeState state_{};
};

// RAII-контролер радіотрансивера для гарантованого вимкнення живлення
class RadioTransceiver {
public:
    RadioTransceiver() noexcept {
        RadioMode::write(0x03);    // 1 Mbps BLE
        RadioTxPower::write(0x00); // 0 dBm
        RadioCrcConfig::write(0x103);
    }

    ~RadioTransceiver() noexcept {
        RadioTasksDisable::write(1);
    }

    void transmitChannel(std::uint8_t channel_index, const BleAdvertisementPacket &packet) const noexcept {
        static constexpr std::array<std::uint8_t, 3> FrequencyMap{2, 26, 80}; // Канали 37, 38, 39
        if (channel_index >= FrequencyMap.size()) {
            return;
        }

        RadioFrequency::write(FrequencyMap[channel_index]);
        RadioPacketPointer::write(reinterpret_cast<std::uint32_t>(&packet));
        RadioEventsReady::write(0);
        RadioEventsEnd::write(0);

        RadioTasksTxEnable::write(1);
        while (RadioEventsReady::read() == 0) {}

        RadioTasksStart::write(1);
        while (RadioEventsEnd::read() == 0) {}

        RadioTasksDisable::write(1);
    }
};

struct SensorReadings {
    std::int16_t  temperature_x10{0};
    std::uint16_t voltage_mv{0};
};

[[nodiscard]] inline SensorReadings sampleAdc() noexcept {
    // Емуляція зчитування АЦП за фіксований час
    return SensorReadings{.temperature_x10 = 245, .voltage_mv = 3180};
}

} // namespace batteryless

int main() {
    using namespace batteryless;

    // 1. Відновлення або ініціалізація стану у FRAM
    FramStateManager state_manager;
    auto &state = state_manager.get();

    // 2. Зчитування фізичних параметрів
    const auto [temp, vcap] = sampleAdc();
    state.last_temperature_x10 = temp;
    state.last_vcap_mv = vcap;

    // 3. Формування пакета передачі
    BleAdvertisementPacket packet{};
    packet.sequence_num = state.sequence_id;
    packet.temperature_x10 = state.last_temperature_x10;
    packet.voltage_mv = state.last_vcap_mv;

    // 4. Передача пакета на трьох рекламних каналах
    {
        const RadioTransceiver radio;
        radio.transmitChannel(0, packet);
        radio.transmitChannel(1, packet);
        radio.transmitChannel(2, packet);
    } // Деструктор RadioTransceiver гарантовано вимикає радіотракт

    // 5. Фіксація стану перед скиданням напруги
    state_manager.commit();

    // 6. Очікування вимкнення живлення
    while (true) {
        asm volatile("wfi");
    }

    return 0;
}
