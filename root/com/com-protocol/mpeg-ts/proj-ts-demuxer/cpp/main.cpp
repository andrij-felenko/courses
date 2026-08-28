#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <cstdint>
#include <iomanip>

constexpr size_t TS_PACKET_SIZE = 188;
constexpr uint8_t TS_SYNC_BYTE  = 0x47;
constexpr size_t TS_MAX_PIDS    = 8192;

struct ElementaryStream {
    uint8_t  stream_type{0};
    uint16_t pid{0};
};

struct ProgramInfo {
    uint16_t program_number{0};
    uint16_t pmt_pid{0};
    uint16_t pcr_pid{0};
    std::vector<ElementaryStream> streams;
};

class TsDemuxer {
public:
    TsDemuxer() {
        m_last_cc.fill(-1);
        m_pid_seen.fill(false);
    }

    void process_packet(std::span<const uint8_t, TS_PACKET_SIZE> pkt) {
        if (pkt[0] != TS_SYNC_BYTE) {
            return;
        }
        ++m_packet_count;

        const bool tei  = (pkt[1] & 0x80) != 0;
        if (tei) {
            ++m_dropped_packets;
            return; // Спотворення радіоканалу (Uncorrectable FEC error)
        }

        const bool pusi = (pkt[1] & 0x40) != 0;
        const uint16_t pid = (static_cast<uint16_t>(pkt[1] & 0x1F) << 8) | pkt[2];
        const uint8_t afc  = (pkt[3] >> 4) & 0x03;
        const uint8_t cc   = pkt[3] & 0x0F;

        const bool has_payload = (afc == 0x01 || afc == 0x03);
        if (has_payload && pid != 0x1FFF) {
            check_continuity(pid, cc);
        }

        size_t offset = 4;
        if (afc == 0x02 || afc == 0x03) {
            const uint8_t af_len = pkt[offset];
            if (af_len > 0 && offset + 1 + af_len <= TS_PACKET_SIZE) {
                const uint8_t flags = pkt[offset + 1];
                const bool has_pcr = (flags & 0x10) != 0;
                if (has_pcr && af_len >= 7) {
                    const uint64_t pcr = parse_pcr(pkt.subspan(offset + 2, 6));
                    if (m_program && pid == m_program->pcr_pid && m_packet_count % 1000 == 0) {
                        std::cout << "[PCR] PID 0x" << std::hex << std::setw(4) << std::setfill('0') << pid
                                  << std::dec << ": " << std::fixed << std::setprecision(3)
                                  << (static_cast<double>(pcr) / 27000000.0) << " s\n";
                    }
                }
            }
            offset += 1 + af_len;
        }

        if (!has_payload || offset >= TS_PACKET_SIZE) {
            return;
        }

        const auto payload = pkt.subspan(offset);
        dispatch_payload(pid, pusi, payload);
    }

    [[nodiscard]] size_t packet_count() const noexcept { return m_packet_count; }
    [[nodiscard]] size_t dropped_packets() const noexcept { return m_dropped_packets; }
    [[nodiscard]] const std::optional<ProgramInfo>& program() const noexcept { return m_program; }

private:
    void check_continuity(uint16_t pid, uint8_t cc) {
        if (m_pid_seen[pid]) {
            const uint8_t expected_cc = (m_last_cc[pid] + 1) & 0x0F;
            if (cc != expected_cc && cc != m_last_cc[pid]) {
                const uint8_t lost = (cc >= expected_cc) ? (cc - expected_cc) : (16 + cc - expected_cc);
                m_dropped_packets += lost;
                std::cerr << "[ВТРАТА] PID 0x" << std::hex << pid << std::dec
                          << ": втрачено " << static_cast<int>(lost) << " пакетів\n";
            }
        }
        m_pid_seen[pid] = true;
        m_last_cc[pid] = cc;
    }

    static uint64_t parse_pcr(std::span<const uint8_t, 6> buf) noexcept {
        const uint64_t base = (static_cast<uint64_t>(buf[0]) << 25) |
                              (static_cast<uint64_t>(buf[1]) << 17) |
                              (static_cast<uint64_t>(buf[2]) << 9)  |
                              (static_cast<uint64_t>(buf[3]) << 1)  |
                              (static_cast<uint64_t>(buf[4] & 0x80) >> 7);
        const uint16_t ext = (static_cast<uint16_t>(buf[4] & 0x01) << 8) | buf[5];
        return base * 300 + ext;
    }

    static uint64_t parse_pts(std::span<const uint8_t> buf) noexcept {
        return (static_cast<uint64_t>(buf[0] & 0x0E) << 29) |
               (static_cast<uint64_t>(buf[1]) << 22) |
               (static_cast<uint64_t>(buf[2] & 0xFE) << 14) |
               (static_cast<uint64_t>(buf[3]) << 7) |
               (static_cast<uint64_t>(buf[4] & 0xFE) >> 1);
    }

    void dispatch_payload(uint16_t pid, bool pusi, std::span<const uint8_t> payload) {
        if (pid == 0x0000) {
            parse_pat(payload);
        } else if (m_program && pid == m_program->pmt_pid) {
            parse_pmt(payload);
        } else if (pusi && payload.size() >= 14) {
            if (payload[0] == 0x00 && payload[1] == 0x00 && payload[2] == 0x01) {
                const uint8_t stream_id = payload[3];
                const uint8_t pts_flags = (payload[7] >> 6) & 0x03;
                if ((pts_flags & 0x02) != 0) {
                    const uint64_t pts = parse_pts(payload.subspan(9, 5));
                    std::cout << "[PES] PID 0x" << std::hex << pid
                              << " StreamID 0x" << static_cast<int>(stream_id) << std::dec
                              << " -> PTS = " << std::fixed << std::setprecision(3)
                              << (static_cast<double>(pts) / 90000.0) << " s\n";
                }
            }
        }
    }

    void parse_pat(std::span<const uint8_t> payload) {
        if (payload.size() < 8) return;
        const uint8_t ptr_field = payload[0];
        if (1 + ptr_field >= payload.size()) return;
        auto sec = payload.subspan(1 + ptr_field);

        if (sec[0] != 0x00) return; // Table ID != PAT
        const uint16_t sec_len = (static_cast<uint16_t>(sec[1] & 0x0F) << 8) | sec[2];
        if (sec_len < 9 || 3 + sec_len > sec.size()) return;

        auto entries = sec.subspan(8, sec_len - 5 - 4); // Виключаємо заголовок і CRC32
        while (entries.size() >= 4) {
            const uint16_t prog_num = (static_cast<uint16_t>(entries[0]) << 8) | entries[1];
            const uint16_t pmt_pid  = (static_cast<uint16_t>(entries[2] & 0x1F) << 8) | entries[3];
            if (prog_num != 0) {
                m_program = ProgramInfo{prog_num, pmt_pid, 0, {}};
                std::cout << "[PAT] Програма " << prog_num << " -> PMT PID 0x"
                          << std::hex << pmt_pid << std::dec << "\n";
                break;
            }
            entries = entries.subspan(4);
        }
    }

    void parse_pmt(std::span<const uint8_t> payload) {
        if (payload.size() < 12) return;
        const uint8_t ptr_field = payload[0];
        if (1 + ptr_field >= payload.size()) return;
        auto sec = payload.subspan(1 + ptr_field);

        if (sec[0] != 0x02) return; // Table ID != PMT
        const uint16_t sec_len = (static_cast<uint16_t>(sec[1] & 0x0F) << 8) | sec[2];
        if (sec_len < 13 || 3 + sec_len > sec.size()) return;

        m_program->pcr_pid = (static_cast<uint16_t>(sec[8] & 0x1F) << 8) | sec[9];
        const uint16_t prog_info_len = (static_cast<uint16_t>(sec[10] & 0x0F) << 8) | sec[11];
        if (12 + prog_info_len > sec_len + 3) return;

        auto es_data = sec.subspan(12 + prog_info_len, (3 + sec_len - 4) - (12 + prog_info_len));
        m_program->streams.clear();

        while (es_data.size() >= 5) {
            const uint8_t stype = es_data[0];
            const uint16_t epid = (static_cast<uint16_t>(es_data[1] & 0x1F) << 8) | es_data[2];
            const uint16_t einfo_len = (static_cast<uint16_t>(es_data[3] & 0x0F) << 8) | es_data[4];

            m_program->streams.push_back({stype, epid});
            std::cout << "[PMT] Елементарний потік: Тип 0x" << std::hex << static_cast<int>(stype)
                      << ", PID 0x" << epid << std::dec << "\n";

            if (5 + einfo_len > es_data.size()) break;
            es_data = es_data.subspan(5 + einfo_len);
        }
    }

    std::array<int8_t, TS_MAX_PIDS> m_last_cc{};
    std::array<bool, TS_MAX_PIDS>   m_pid_seen{};
    size_t m_packet_count{0};
    size_t m_dropped_packets{0};
    std::optional<ProgramInfo> m_program;
};
