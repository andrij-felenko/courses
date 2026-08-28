#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <random>
#include <cstdint>
#include <cstring>
#include <numeric>
#include <expected>
#include <iomanip>

namespace ucie {

constexpr size_t FlitPayloadSize = 64;
constexpr size_t FlitHeaderSize  = 2;
constexpr size_t FlitTotalSize   = 68;
constexpr size_t TotalDataLanes  = 64;
constexpr size_t SpareLanes      = 4;

enum class Protocol : uint8_t {
    PCIe_6_0    = 0x01,
    CXL_io      = 0x02,
    CXL_cache   = 0x03,
    CXL_mem     = 0x04,
    Streaming   = 0x05
};

enum class LinkError {
    CrcMismatch,
    Timeout,
    UnrecoverableLaneFault
};

/* 68-байтовий фліт D2D */
struct Flit {
    uint8_t seq_id{0};
    Protocol protocol{Protocol::PCIe_6_0};
    std::array<uint8_t, FlitPayloadSize> payload{};
    uint16_t crc16{0};

    [[nodiscard]] std::array<uint8_t, FlitTotalSize> serialize() const {
        std::array<uint8_t, FlitTotalSize> raw{};
        raw[0] = seq_id;
        raw[1] = static_cast<uint8_t>(protocol);
        std::copy(payload.begin(), payload.end(), raw.begin() + 2);
        raw[66] = static_cast<uint8_t>(crc16 >> 8);
        raw[67] = static_cast<uint8_t>(crc16 & 0xFF);
        return raw;
    }

    static Flit deserialize(std::span<const uint8_t, FlitTotalSize> raw) {
        Flit flit;
        flit.seq_id = raw[0];
        flit.protocol = static_cast<Protocol>(raw[1]);
        std::copy(raw.begin() + 2, raw.begin() + 2 + FlitPayloadSize, flit.payload.begin());
        flit.crc16 = static_cast<uint16_t>((raw[66] << 8) | raw[67]);
        return flit;
    }
};

/* Обчислення CRC-16 CCITT */
class CrcEngine {
public:
    static uint16_t compute(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int b = 0; b < 8; ++b) {
                crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
            }
        }
        return crc;
    }
};

/* Емулятор фізичного каналу D2D */
class D2DChannel {
public:
    D2DChannel(double capacitance_pf, double vdd)
        : cap_pf_(capacitance_pf), vdd_(vdd), rng_(1337), dist_(0.0, 1.0) {
        std::iota(remap_table_.begin(), remap_table_.end(), 0);
    }

    bool repair_lane(size_t bad_lane, size_t spare_idx) {
        if (bad_lane >= TotalDataLanes || spare_idx >= SpareLanes) return false;
        bad_lanes_mask_ |= (1ULL << bad_lane);
        remap_table_[bad_lane] = static_cast<int8_t>(TotalDataLanes + spare_idx);
        std::cout << "[PHY Repair] Лінію #" << bad_lane << " перепризначено на SPARE #" << spare_idx << "\n";
        return true;
    }

    void inject_hard_fault(size_t lane) {
        if (lane < TotalDataLanes) bad_lanes_mask_ |= (1ULL << lane);
    }

    [[nodiscard]] std::expected<Flit, LinkError> transmit(const Flit& tx_flit, double noise_rate) {
        auto raw_tx = tx_flit.serialize();
        std::array<uint8_t, FlitTotalSize> raw_rx{};

        for (size_offset_t offset = 0; offset < FlitTotalSize; offset += 8) {
            uint64_t current_word = 0;
            size_t chunk = std::min<size_t>(8, FlitTotalSize - offset);
            std::memcpy(&current_word, raw_tx.data() + offset, chunk);

            uint64_t toggles = current_word ^ prev_bus_state_;
            total_transitions_ += static_cast<uint64_t>(std::popcount(toggles));
            prev_bus_state_ = current_word;
            total_bits_sent_ += (chunk * 8);

            uint64_t rx_word = current_word;
            for (size_t lane = 0; lane < 64; ++lane) {
                if ((bad_lanes_mask_ & (1ULL << lane)) && (remap_table_[lane] == static_cast<int8_t>(lane))) {
                    rx_word &= ~(1ULL << lane);
                }
                if (dist_(rng_) < noise_rate) {
                    rx_word ^= (1ULL << lane);
                }
            }
            std::memcpy(raw_rx.data() + offset, &rx_word, chunk);
        }

        Flit rx_flit = Flit::deserialize(raw_rx);

        std::array<uint8_t, FlitHeaderSize + FlitPayloadSize> check_buf{};
        check_buf[0] = rx_flit.seq_id;
        check_buf[1] = static_cast<uint8_t>(rx_flit.protocol);
        std::copy(rx_flit.payload.begin(), rx_flit.payload.end(), check_buf.begin() + 2);

        if (CrcEngine::compute(check_buf) != rx_flit.crc16) {
            return std::unexpected(LinkError::CrcMismatch);
        }
        return rx_flit;
    }

    [[nodiscard]] double compute_energy_pj_per_bit() const noexcept {
        if (total_bits_sent_ == 0) return 0.0;
        double cap_f = cap_pf_ * 1e-12;
        double total_energy = 0.5 * cap_f * vdd_ * vdd_ * static_cast<double>(total_transitions_);
        return (total_energy / static_cast<double>(total_bits_sent_)) * 1e12;
    }

    [[nodiscard]] uint64_t total_bits() const noexcept { return total_bits_sent_; }
    [[nodiscard]] uint64_t total_transitions() const noexcept { return total_transitions_; }

private:
    double cap_pf_;
    double vdd_;
    uint64_t bad_lanes_mask_{0};
    std::array<int8_t, TotalDataLanes> remap_table_{};
    uint64_t prev_bus_state_{0};
    uint64_t total_transitions_{0};
    uint64_t total_bits_sent_{0};
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_;
};

/* Адаптер каналу з підтримкою ARQ */
class LinkAdapter {
public:
    explicit LinkAdapter(D2DChannel& channel) : channel_(channel) {}

    std::expected<Flit, LinkError> send_flit(uint8_t seq, Protocol proto,
                                             std::span<const uint8_t, FlitPayloadSize> data,
                                             int max_retries = 3) {
        Flit flit;
        flit.seq_id = seq;
        flit.protocol = proto;
        std::copy(data.begin(), data.end(), flit.payload.begin());

        std::array<uint8_t, FlitHeaderSize + FlitPayloadSize> check_buf{};
        check_buf[0] = flit.seq_id;
        check_buf[1] = static_cast<uint8_t>(flit.protocol);
        std::copy(flit.payload.begin(), flit.payload.end(), check_buf.begin() + 2);
        flit.crc16 = CrcEngine::compute(check_buf);

        for (int attempt = 0; attempt <= max_retries; ++attempt) {
            if (attempt > 0) {
                retries_++;
                std::cout << "  [ARQ Retry] Помилка CRC! Повторна передача SeqID="
                          << static_cast<int>(seq) << " (спроба " << attempt << ")\n";
            }
            auto result = channel_.transmit(flit, 0.001);
            if (result.has_value()) {
                return result.value();
            }
        }
        return std::unexpected(LinkError::Timeout);
    }

    [[nodiscard]] uint64_t retry_count() const noexcept { return retries_; }

private:
    D2DChannel& channel_;
    uint64_t retries_{0};
};

} // namespace ucie

int main() {
    using namespace ucie;

    std::cout << "=== Симуляція каналу зв'язку UCIe Die-to-Die (C++20) ===\n\n";

    D2DChannel channel(0.08 /* 80 фФ */, 0.75 /* 0.75 В */);
    LinkAdapter adapter(channel);

    std::array<uint8_t, FlitPayloadSize> test_payload{};
    for (size_t i = 0; i < FlitPayloadSize; ++i) {
        test_payload[i] = static_cast<uint8_t>(0x55 ^ i);
    }

    /* Відправлення серії пакетів */
    for (uint8_t seq = 0; seq < 5; ++seq) {
        auto res = adapter.send_flit(seq, Protocol::PCIe_6_0, test_payload);
        if (res.has_value()) {
            std::cout << "[ACK] Фліт SeqID=" << static_cast<int>(res->seq_id)
                      << " успішно прийнято. CRC=0x"
                      << std::hex << std::uppercase << std::setw(4) << std::setfill('0')
                      << res->crc16 << std::dec << "\n";
        }
    }

    /* Емуляція фізичного дефекту та його ремонт */
    std::cout << "\n[Аварія] Відмова контакту на лінії #18!\n";
    channel.inject_hard_fault(18);

    auto fail_res = adapter.send_flit(5, Protocol::CXL_mem, test_payload, 2);
    if (!fail_res.has_value()) {
        std::cout << "[Link Error] Передачу заблоковано через несправність лінії!\n";
    }

    channel.repair_lane(18, 0);

    auto recovered_res = adapter.send_flit(5, Protocol::CXL_mem, test_payload);
    if (recovered_res.has_value()) {
        std::cout << "[ACK] Після перепризначення лінії фліт SeqID=5 прийнято!\n";
    }

    std::cout << "\n=== Результати аналізу енергоспоживання ===\n";
    std::cout << "Всього передано бітів: " << channel.total_bits() << "\n";
    std::cout << "Кількість перемикань вентилів: " << channel.total_transitions() << "\n";
    std::cout << "Повторних відправлень (ARQ Retries): " << adapter.retry_count() << "\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Питома енергія передавання: " << channel.compute_energy_pj_per_bit() << " пДж / біт\n";

    return 0;
}
