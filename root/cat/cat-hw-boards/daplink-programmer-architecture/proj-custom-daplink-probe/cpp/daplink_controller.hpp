#ifndef DAPLINK_CONTROLLER_HPP
#define DAPLINK_CONTROLLER_HPP

#include <cstdint>
#include <vector>
#include <span>
#include <optional>
#include <iostream>

/* Коди команд протоколу CMSIS-DAP v1/v2 */
enum class DAPCommand : std::uint8_t {
    DAP_INFO            = 0x00,
    DAP_CONNECT         = 0x02,
    DAP_DISCONNECT      = 0x03,
    DAP_TRANSFER_CONFIGURE = 0x04,
    DAP_TRANSFER        = 0x05,
    DAP_SWJ_CLOCK       = 0x11,
    DAP_RESET_TARGET    = 0x0A
};

/* Коди режимів підключення порту зневадження */
enum class DAPPort : std::uint8_t {
    DEFAULT = 0x00,
    SWD     = 0x01,
    JTAG    = 0x02
};

/* Коди відповідей статусу виконання команд */
enum class DAPStatus : std::uint8_t {
    DAP_OK    = 0x00,
    DAP_ERROR = 0xFF
};

/**
 * @brief Структура для формування та декодування пакетів команд CMSIS-DAP
 */
struct DAPPacket {
    std::vector<std::uint8_t> buffer;

    explicit DAPPacket(size_t initial_size = 64) {
        buffer.reserve(initial_size);
    }

    void clear() {
        buffer.clear();
    }

    void append_byte(std::uint8_t byte) {
        buffer.push_back(byte);
    }

    void append_u32(std::uint32_t value) {
        buffer.push_back(static_cast<std::uint8_t>(value & 0xFF));
        buffer.push_back(static_cast<std::uint8_t>((value >> 8) & 0xFF));
        buffer.push_back(static_cast<std::uint8_t>((value >> 16) & 0xFF));
        buffer.push_back(static_cast<std::uint8_t>((value >> 24) & 0xFF));
    }

    [[nodiscard]] std::span<const std::uint8_t> data() const {
        return {buffer.data(), buffer.size()};
    }
};

/**
 * @brief Клас обгортки для управління сесією зневадження DAPLink
 */
class DAPLinkController {
public:
    DAPLinkController() = default;
    ~DAPLinkController() = default;

    /* Заборона копіювання контролера */
    DAPLinkController(const DAPLinkController&) = delete;
    DAPLinkController& operator=(const DAPLinkController&) = delete;

    /* Методи ініціалізації та конфігурування інтерфейсу */
    bool connect(DAPPort port);
    bool disconnect();
    bool set_clock(std::uint32_t clock_hz);
    
    /* Методи зчитування даних та керування ціллю */
    std::optional<std::uint32_t> read_idcode();
    bool reset_target();

    /* Низькорівневе керування станами сигнальних ліній */
    void set_swclk(bool level);
    void set_swdio(bool level);
    void set_nreset(bool level);

private:
    bool is_connected_{false};
    std::uint32_t current_clock_{1000000}; /* 1 МГц за замовчуванням */

    /* Імітація передачі буфера через USB-ендпоінт та прийому відповіді */
    DAPPacket send_packet(const DAPPacket& request);
};

#endif // DAPLINK_CONTROLLER_HPP
