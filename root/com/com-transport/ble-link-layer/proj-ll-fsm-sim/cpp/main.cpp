#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <cstdint>
#include <optional>
#include <iomanip>

namespace ble::ll {

constexpr uint32_t Crc24Poly = 0x00065Bu;
constexpr uint32_t Crc24Init = 0x555555u;
constexpr uint32_t TIfsUs = 150u;
constexpr size_t MaxPayloadLen = 251;

enum class State {
    Standby,
    Advertising,
    Scanning,
    Initiating,
    ConnectionMaster,
    ConnectionSlave
};

struct DataPdu {
    uint8_t llid{0x02}; /* 10b: Start of L2CAP message */
    uint8_t nesn{0};
    uint8_t sn{0};
    uint8_t md{0};
    uint8_t length{0};
    std::vector<uint8_t> payload{};
    uint32_t crc{0};
};

/* Обчислення контрольної суми CRC-24 (LFSR) через std::span */
[[nodiscard]] constexpr uint32_t calculate_crc24(std::span<const uint8_t> data, uint32_t init = Crc24Init) noexcept {
    uint32_t state = init & 0x00FFFFFFu;
    for (uint8_t byte : data) {
        for (int bit = 0; bit < 8; ++bit) {
            uint8_t data_bit = (byte >> bit) & 1u;
            uint8_t state_bit23 = (state >> 23) & 1u;
            state = (state << 1) & 0x00FFFFFFu;
            if (data_bit ^ state_bit23) {
                state ^= Crc24Poly;
            }
        }
    }
    return state & 0x00FFFFFFu;
}

/* Розрахунок розширення вікна прийому */
[[nodiscard]] constexpr uint32_t calculate_window_widening(uint16_t master_ppm, uint16_t slave_ppm, uint32_t sleep_time_us) noexcept {
    const uint64_t total_ppm = static_cast<uint64_t>(master_ppm) + static_cast<uint64_t>(slave_ppm);
    const auto drift = static_cast<uint32_t>((total_ppm * sleep_time_us) / 1'000'000ULL);
    return drift + 16u; /* +16 мкс захисного джиттеру */
}

class LinkLayerNode {
public:
    explicit LinkLayerNode(State initial_state, uint16_t sca_ppm, uint32_t interval_us, uint16_t latency = 0)
        : state_{initial_state}, sca_ppm_{sca_ppm}, conn_interval_us_{interval_us}, slave_latency_{latency} {}

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint8_t transmit_sn() const noexcept { return transmit_sn_; }
    [[nodiscard]] uint8_t next_expected_sn() const noexcept { return next_expected_sn_; }
    [[nodiscard]] uint16_t sca_ppm() const noexcept { return sca_ppm_; }
    [[nodiscard]] uint32_t conn_interval_us() const noexcept { return conn_interval_us_; }
    [[nodiscard]] uint16_t slave_latency() const noexcept { return slave_latency_; }

    [[nodiscard]] DataPdu build_pdu(std::string_view payload_str, bool more_data = false) {
        DataPdu pdu{};
        pdu.llid = 0x02;
        pdu.sn = transmit_sn_;
        pdu.nesn = next_expected_sn_;
        pdu.md = more_data ? 1 : 0;
        pdu.length = static_cast<uint8_t>(payload_str.size());
        pdu.payload.assign(payload_str.begin(), payload_str.end());

        std::vector<uint8_t> raw_header_and_payload;
        raw_header_and_payload.reserve(2 + pdu.payload.size());
        raw_header_and_payload.push_back(static_cast<uint8_t>(pdu.llid | (pdu.nesn << 2) | (pdu.sn << 3) | (pdu.md << 4)));
        raw_header_and_payload.push_back(pdu.length);
        raw_header_and_payload.insert(raw_header_and_payload.end(), pdu.payload.begin(), pdu.payload.end());

        pdu.crc = calculate_crc24(raw_header_and_payload);
        return pdu;
    }

    bool receive_pdu(const DataPdu& pdu, bool simulate_crc_error = false) {
        std::vector<uint8_t> raw;
        raw.reserve(2 + pdu.payload.size());
        raw.push_back(static_cast<uint8_t>(pdu.llid | (pdu.nesn << 2) | (pdu.sn << 3) | (pdu.md << 4)));
        raw.push_back(pdu.length);
        raw.insert(raw.end(), pdu.payload.begin(), pdu.payload.end());

        const uint32_t expected_crc = calculate_crc24(raw);
        if (simulate_crc_error || pdu.crc != expected_crc) {
            std::cout << "  [Rx] Помилка CRC! Пакет відкинуто. Очікуваний NESN лишається "
                      << static_cast<int>(next_expected_sn_) << "\n";
            return false;
        }

        if (pdu.sn == next_expected_sn_) {
            std::string_view msg{reinterpret_cast<const char*>(pdu.payload.data()), pdu.payload.size()};
            std::cout << "  [Rx] Прийнято НОВИЙ пакет [SN=" << static_cast<int>(pdu.sn)
                      << ", NESN=" << static_cast<int>(pdu.nesn) << ", len=" << static_cast<int>(pdu.length)
                      << "]: \"" << msg << "\"\n";
            next_expected_sn_ = static_cast<uint8_t>(1u - next_expected_sn_);
        } else {
            std::cout << "  [Rx] Прийнято ДУБЛІКАТ [SN=" << static_cast<int>(pdu.sn)
                      << "]. Повторно підтверджуємо поточний стан.\n";
        }

        if (pdu.nesn != transmit_sn_) {
            transmit_sn_ = static_cast<uint8_t>(1u - transmit_sn_);
        }
        return true;
    }

private:
    State state_{State::Standby};
    uint8_t transmit_sn_{0};
    uint8_t next_expected_sn_{0};
    uint16_t sca_ppm_{50};
    uint32_t conn_interval_us_{20000};
    uint16_t slave_latency_{0};
};

} // namespace ble::ll

int main() {
    using namespace ble::ll;

    LinkLayerNode master{State::ConnectionMaster, 50, 20000, 4};
    LinkLayerNode slave{State::ConnectionSlave, 250, 20000, 4};

    std::cout << "=== СИМУЛЯТОР BLE LINK LAYER (C++20 RAII & ARQ) ===\n\n";

    const uint32_t sleep_time_us = master.conn_interval_us() * (master.slave_latency() + 1);
    const uint32_t widening_us = calculate_window_widening(master.sca_ppm(), slave.sca_ppm(), sleep_time_us);

    std::cout << "[1] Розрахунок вікна розширення (Window Widening):\n"
              << "    connInterval = " << master.conn_interval_us() << " мкс, Slave Latency = " << master.slave_latency() << "\n"
              << "    Час сну Slave = " << sleep_time_us << " мкс\n"
              << "    Спільний дрейф = " << (master.sca_ppm() + slave.sca_ppm())
              << " ppm -> Розширення вікна прийому = " << widening_us << " мкс\n\n";

    /* Подія 1: Успішна передача */
    std::cout << "[2] Подія 1: Master передає пакет 1 -> Slave:\n";
    auto pdu1 = master.build_pdu("Hello BLE C++");
    std::cout << "  [Tx Master] Пакет відправлено: SN=" << static_cast<int>(pdu1.sn)
              << ", NESN=" << static_cast<int>(pdu1.nesn) << ", CRC=0x"
              << std::hex << std::uppercase << std::setfill('0') << std::setw(6) << pdu1.crc << std::dec << "\n";
    slave.receive_pdu(pdu1, false);

    auto ack1 = slave.build_pdu("");
    std::cout << "  [Tx Slave]  Відповідь ACK:     SN=" << static_cast<int>(ack1.sn)
              << ", NESN=" << static_cast<int>(ack1.nesn) << "\n";
    master.receive_pdu(ack1, false);
    std::cout << "\n";

    /* Подія 2: Помилка CRC */
    std::cout << "[3] Подія 2: Master передає пакет 2 (симуляція завади в ефірі):\n";
    auto pdu2 = master.build_pdu("Data block 2");
    std::cout << "  [Tx Master] Пакет відправлено: SN=" << static_cast<int>(pdu2.sn)
              << ", NESN=" << static_cast<int>(pdu2.nesn) << "\n";
    slave.receive_pdu(pdu2, true);

    auto nack = slave.build_pdu("");
    std::cout << "  [Tx Slave]  Відповідь NACK:    SN=" << static_cast<int>(nack.sn)
              << ", NESN=" << static_cast<int>(nack.nesn) << " (NESN не перемкнуто)\n";
    master.receive_pdu(nack, false);
    std::cout << "\n";

    /* Подія 3: Повторна передача */
    std::cout << "[4] Подія 3: Master фіксує незмінний NESN та повторює пакет 2:\n";
    pdu2 = master.build_pdu("Data block 2");
    std::cout << "  [Tx Master] Retransmit:        SN=" << static_cast<int>(pdu2.sn)
              << ", NESN=" << static_cast<int>(pdu2.nesn) << "\n";
    slave.receive_pdu(pdu2, false);

    ack1 = slave.build_pdu("");
    std::cout << "  [Tx Slave]  Відповідь ACK:     SN=" << static_cast<int>(ack1.sn)
              << ", NESN=" << static_cast<int>(ack1.nesn) << "\n";
    master.receive_pdu(ack1, false);

    return 0;
}
