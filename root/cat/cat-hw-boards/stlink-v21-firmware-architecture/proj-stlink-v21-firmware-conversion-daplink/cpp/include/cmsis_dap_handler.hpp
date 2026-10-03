#ifndef CMSIS_DAP_HANDLER_HPP
#define CMSIS_DAP_HANDLER_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <span>
#include <string_view>
#include <optional>

// Максимальний розмір USB Bulk пакета для CMSIS-DAP v1.x (стандартний розмір Full-Speed)
constexpr size_t DAP_PACKET_SIZE = 64;

// Ідентифікатори команд протоколу CMSIS-DAP
enum class DapCommand : uint8_t {
    Info = 0x00,
    HostStatus = 0x01,
    Connect = 0x02,
    Disconnect = 0x03,
    TransferConfigure = 0x04,
    Transfer = 0x05,
    TransferBlock = 0x06,
    WriteABORT = 0x08,
    Delay = 0x09,
    ResetTarget = 0x0A,
    SwjPins = 0x10,
    SwjClock = 0x11,
    SwjSequence = 0x12,
    SwdConfigure = 0x13
};

// Режими роботи зневаджувального порту
enum class SwdPortMode : uint8_t {
    Disabled = 0x00,
    SWD = 0x01,
    JTAG = 0x02
};

// Статуси відповідей CMSIS-DAP
enum class DapResponseStatus : uint8_t {
    Ok = 0x00,
    Error = 0xFF
};

// Вирівняна структура буфера USB-пакета CMSIS-DAP з методами безпечної обробки
struct DapPacketBuffer {
    std::array<uint8_t, DAP_PACKET_SIZE> data{};
    size_t length{0};

    void clear() {
        data.fill(0);
        length = 0;
    }

    bool write_u8(uint8_t val) {
        if (length >= DAP_PACKET_SIZE) return false;
        data[length++] = val;
        return true;
    }

    bool write_u16(uint16_t val) {
        if (length + 2 > DAP_PACKET_SIZE) return false;
        data[length++] = static_cast<uint8_t>(val & 0xFF);
        data[length++] = static_cast<uint8_t>((val >> 8) & 0xFF);
        return true;
    }

    bool write_u32(uint32_t val) {
        if (length + 4 > DAP_PACKET_SIZE) return false;
        data[length++] = static_cast<uint8_t>(val & 0xFF);
        data[length++] = static_cast<uint8_t>((val >> 8) & 0xFF);
        data[length++] = static_cast<uint8_t>((val >> 16) & 0xFF);
        data[length++] = static_cast<uint8_t>((val >> 24) & 0xFF);
        return true;
    }

    [[nodiscard]] uint8_t read_u8(size_t offset) const {
        if (offset >= DAP_PACKET_SIZE) return 0;
        return data[offset];
    }

    [[nodiscard]] uint16_t read_u16(size_t offset) const {
        if (offset + 2 > DAP_PACKET_SIZE) return 0;
        return static_cast<uint16_t>(data[offset]) |
               (static_cast<uint16_t>(data[offset + 1]) << 8);
    }

    [[nodiscard]] uint32_t read_u32(size_t offset) const {
        if (offset + 4 > DAP_PACKET_SIZE) return 0;
        return static_cast<uint32_t>(data[offset]) |
               (static_cast<uint32_t>(data[offset + 1]) << 8) |
               (static_cast<uint32_t>(data[offset + 2]) << 16) |
               (static_cast<uint32_t>(data[offset + 3]) << 24);
    }
};

// Клас обробника CMSIS-DAP та керування SWD-інтерфейсом ST-Link V2.1
class CmsisDapHandler {
public:
    CmsisDapHandler();
    ~CmsisDapHandler() = default;

    // Обробка вхідного USB Bulk-пакета та формування відповіді
    bool process_packet(const DapPacketBuffer& rx_buf, DapPacketBuffer& tx_buf);

    // Ініціалізація та розрив SWD-з'єднання
    bool connect_swd();
    void disconnect();

    // Налаштування частоти тактування SWCLK (у Гц)
    bool set_clock(uint32_t clock_hz);

    // Низькорівневі транзакції SWD регістрів DP (Debug Port) та AP (Access Port)
    bool swd_write_dp(uint8_t reg_addr, uint32_t data);
    bool swd_read_dp(uint8_t reg_addr, uint32_t& data);
    bool swd_write_ap(uint8_t reg_addr, uint32_t data);
    bool swd_read_ap(uint8_t reg_addr, uint32_t& data);

    // Прямий доступ до пам'яті цільового МК через MEM-AP
    bool swd_read_mem32(uint32_t address, uint32_t& data);
    bool swd_write_mem32(uint32_t address, uint32_t data);

    // Високорівневі методи програмування Flash для Drag-and-Drop прошивача
    bool target_halt();
    bool target_resume();
    bool target_flash_unlock();
    bool target_flash_erase_sector(uint32_t sector_address);
    bool target_flash_program_page(uint32_t address, std::span<const uint8_t> data);
    bool target_reset_and_run();

    [[nodiscard]] SwdPortMode get_port_mode() const { return port_mode_; }
    [[nodiscard]] bool is_connected() const { return port_mode_ != SwdPortMode::Disabled; }

private:
    SwdPortMode port_mode_{SwdPortMode::Disabled};
    uint32_t clock_hz_{1000000}; // За замовчуванням 1 МГц
    uint8_t idle_cycles_{0};
    uint16_t retry_count_{100};
    uint32_t cached_select_reg_{0xFFFFFFFF}; // Кєш регістра APSELECT

    // Фізичні стани ліній ST-Link V2.1
    bool swclk_pin_{false};
    bool swdio_pin_{false};
    bool nrst_pin_{true};
    bool status_led_{false};

    // Внутрішні методи обробки окремих команд
    void handle_cmd_info(const DapPacketBuffer& rx, DapPacketBuffer& tx);
    void handle_cmd_connect(const DapPacketBuffer& rx, DapPacketBuffer& tx);
    void handle_cmd_disconnect(const DapPacketBuffer& rx, DapPacketBuffer& tx);
    void handle_cmd_transfer(const DapPacketBuffer& rx, DapPacketBuffer& tx);
    void handle_cmd_swj_clock(const DapPacketBuffer& rx, DapPacketBuffer& tx);
    void handle_cmd_swj_pins(const DapPacketBuffer& rx, DapPacketBuffer& tx);
};

#endif // CMSIS_DAP_HANDLER_HPP
