#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>

struct GapConnectionRequirements {
    float    min_interval_ms{100.0f};
    float    max_interval_ms{200.0f};
    uint16_t slave_latency{4};
    uint16_t supervision_timeout_ms{4000};
};

class L2CapSignalingBuilder {
public:
    static constexpr size_t PacketSize = 16;
    static constexpr uint16_t BleSignalingCid = 0x0006;
    static constexpr uint8_t ParamUpdateReqOpcode = 0x12;

    /**
     * @brief Генерація бінарного кадру L2CAP_CONNECTION_PARAM_UPDATE_REQ.
     * @param transaction_id Унікальний лічильник транзакції.
     * @param reqs Бажані межі параметрів зв'язку.
     * @return Сформований масив байтів фіксованого розміру.
     */
    [[nodiscard]] static std::optional<std::array<uint8_t, PacketSize>> build_update_request(
        uint8_t transaction_id, 
        const GapConnectionRequirements& reqs) noexcept 
    {
        std::array<uint8_t, PacketSize> buffer{};

        // L2CAP Header (4 байти)
        buffer[0] = 0x0C; // Довжина поля сигналізації = 12 байтів
        buffer[1] = 0x00;
        buffer[2] = static_cast<uint8_t>(BleSignalingCid & 0xFF);
        buffer[3] = static_cast<uint8_t>((BleSignalingCid >> 8) & 0xFF);

        // Command Header (4 байти)
        buffer[4] = ParamUpdateReqOpcode;
        buffer[5] = transaction_id;
        buffer[6] = 0x08; // Довжина корисного навантаження команди = 8 байтів
        buffer[7] = 0x00;

        // Розрахунок протокольних одиниць
        const uint16_t int_min = static_cast<uint16_t>(reqs.min_interval_ms / 1.25f);
        const uint16_t int_max = static_cast<uint16_t>(reqs.max_interval_ms / 1.25f);
        const uint16_t timeout = static_cast<uint16_t>(reqs.supervision_timeout_ms / 10);

        // Запис значень у форматі Little-Endian
        buffer[8]  = static_cast<uint8_t>(int_min & 0xFF);
        buffer[9]  = static_cast<uint8_t>((int_min >> 8) & 0xFF);
        buffer[10] = static_cast<uint8_t>(int_max & 0xFF);
        buffer[11] = static_cast<uint8_t>((int_max >> 8) & 0xFF);
        buffer[12] = static_cast<uint8_t>(reqs.slave_latency & 0xFF);
        buffer[13] = static_cast<uint8_t>((reqs.slave_latency >> 8) & 0xFF);
        buffer[14] = static_cast<uint8_t>(timeout & 0xFF);
        buffer[15] = static_cast<uint8_t>((timeout >> 8) & 0xFF);

        return buffer;
    }
};
