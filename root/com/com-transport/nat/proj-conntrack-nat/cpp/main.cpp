#include <cstdint>
#include <chrono>
#include <vector>
#include <unordered_map>
#include <optional>
#include <span>
#include <memory>

class NatEngine {
public:
    static constexpr uint16_t PortStart = 1024;
    static constexpr uint16_t PortEnd = 65535;

    struct Endpoint {
        uint32_t ip{0};
        uint16_t port{0};

        bool operator==(const Endpoint&) const = default;
    };

    struct FlowTuple {
        Endpoint src;
        Endpoint dst;
        uint8_t  proto{0};

        bool operator==(const FlowTuple&) const = default;
    };

    struct TupleHash {
        std::size_t operator()(const FlowTuple& t) const noexcept {
            std::size_t h1 = (static_cast<std::size_t>(t.src.ip) << 16) ^ t.src.port;
            std::size_t h2 = (static_cast<std::size_t>(t.dst.ip) << 16) ^ t.dst.port;
            return h1 ^ (h2 << 1) ^ (static_cast<std::size_t>(t.proto) << 24);
        }
    };

    struct NatSession {
        FlowTuple original;
        FlowTuple reply;
        uint16_t  assigned_port{0};
        std::chrono::steady_clock::time_point last_seen;
    };

    explicit NatEngine(uint32_t wan_ip)
        : wan_ip_(wan_ip), port_allocated_(PortEnd - PortStart + 1, false) {}

    // Обробка вихідного пакета LAN -> WAN (SNAT)
    bool process_outbound(std::span<uint8_t> packet) {
        if (packet.size() < 20) return false;
        uint8_t ihl = (packet[0] & 0x0F) * 4;
        if (packet.size() < static_cast<std::size_t>(ihl + 8)) return false;

        uint8_t proto = packet[9];
        if (proto != 6 && proto != 17) return false;

        uint32_t src_ip = read_u32(&packet[12]);
        uint32_t dst_ip = read_u32(&packet[16]);
        uint16_t src_port = read_u16(&packet[ihl]);
        uint16_t dst_port = read_u16(&packet[ihl + 2]);

        FlowTuple orig_tuple{ {src_ip, src_port}, {dst_ip, dst_port}, proto };

        auto it = forward_table_.find(orig_tuple);
        if (it == forward_table_.end()) {
            auto port_opt = allocate_port();
            if (!port_opt) return false;

            uint16_t nat_port = *port_opt;
            FlowTuple reply_tuple{ {dst_ip, dst_port}, {wan_ip_, nat_port}, proto };

            NatSession session{
                .original = orig_tuple,
                .reply = reply_tuple,
                .assigned_port = nat_port,
                .last_seen = std::chrono::steady_clock::now()
            };

            auto [ins_it, _] = forward_table_.emplace(orig_tuple, session);
            reverse_table_.emplace(reply_tuple, orig_tuple);
            it = ins_it;
        } else {
            it->second.last_seen = std::chrono::steady_clock::now();
        }

        uint16_t assigned_port = it->second.assigned_port;

        // 1. Модифікація IP-заголовка
        uint16_t ip_csum = read_u16(&packet[10]);
        ip_csum = csum_update_u32(ip_csum, src_ip, wan_ip_);
        write_u16(&packet[10], ip_csum);
        write_u32(&packet[12], wan_ip_);

        // 2. Модифікація L4-заголовка
        if (proto == 6) { // TCP
            uint16_t tcp_csum = read_u16(&packet[ihl + 16]);
            uint16_t c = csum_update_u32(tcp_csum, src_ip, wan_ip_);
            c = csum_update_u16(c, src_port, assigned_port);
            write_u16(&packet[ihl + 16], c);
        } else if (proto == 17) { // UDP
            uint16_t udp_csum = read_u16(&packet[ihl + 6]);
            if (udp_csum != 0x0000) {
                uint16_t c = csum_update_u32(udp_csum, src_ip, wan_ip_);
                c = csum_update_u16(c, src_port, assigned_port);
                write_u16(&packet[ihl + 6], (c == 0x0000) ? 0xFFFF : c);
            }
        }
        write_u16(&packet[ihl], assigned_port);
        return true;
    }

    // Обробка вхідного пакета WAN -> LAN (зворотний DNAT)
    bool process_inbound(std::span<uint8_t> packet) {
        if (packet.size() < 20) return false;
        uint8_t ihl = (packet[0] & 0x0F) * 4;
        if (packet.size() < static_cast<std::size_t>(ihl + 8)) return false;

        uint8_t proto = packet[9];
        if (proto != 6 && proto != 17) return false;

        uint32_t src_ip = read_u32(&packet[12]);
        uint32_t dst_ip = read_u32(&packet[16]);
        uint16_t src_port = read_u16(&packet[ihl]);
        uint16_t dst_port = read_u16(&packet[ihl + 2]);

        FlowTuple reply_key{ {src_ip, src_port}, {dst_ip, dst_port}, proto };

        auto rev_it = reverse_table_.find(reply_key);
        if (rev_it == reverse_table_.end()) {
            return false; // Невідома сесія
        }

        auto fwd_it = forward_table_.find(rev_it->second);
        if (fwd_it == forward_table_.end()) {
            return false;
        }

        fwd_it->second.last_seen = std::chrono::steady_clock::now();
        uint32_t lan_ip = fwd_it->second.original.src.ip;
        uint16_t lan_port = fwd_it->second.original.src.port;

        // 1. Модифікація IP-заголовка: dst_ip -> lan_ip
        uint16_t ip_csum = read_u16(&packet[10]);
        ip_csum = csum_update_u32(ip_csum, dst_ip, lan_ip);
        write_u16(&packet[10], ip_csum);
        write_u32(&packet[16], lan_ip);

        // 2. Модифікація L4-заголовка: dst_port -> lan_port
        if (proto == 6) {
            uint16_t tcp_csum = read_u16(&packet[ihl + 16]);
            uint16_t c = csum_update_u32(tcp_csum, dst_ip, lan_ip);
            *reinterpret_cast<uint16_t*>(&packet[ihl + 16]) = csum_update_u16(c, dst_port, lan_port);
        } else if (proto == 17) {
            uint16_t udp_csum = read_u16(&packet[ihl + 6]);
            if (udp_csum != 0x0000) {
                uint16_t c = csum_update_u32(udp_csum, dst_ip, lan_ip);
                c = csum_update_u16(c, dst_port, lan_port);
                write_u16(&packet[ihl + 6], (c == 0x0000) ? 0xFFFF : c);
            }
        }
        write_u16(&packet[ihl + 2], lan_port);
        return true;
    }

    // Очищення застарілих сесій за тайм-аутом
    void prune_stale_sessions(std::chrono::seconds timeout) {
        auto now = std::chrono::steady_clock::now();
        for (auto it = forward_table_.begin(); it != forward_table_.end(); ) {
            if (now - it->second.last_seen > timeout) {
                uint16_t port = it->second.assigned_port;
                if (port >= PortStart && port <= PortEnd) {
                    port_allocated_[port - PortStart] = false;
                }
                reverse_table_.erase(it->second.reply);
                it = forward_table_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    uint32_t wan_ip_;
    std::unordered_map<FlowTuple, NatSession, TupleHash> forward_table_;
    std::unordered_map<FlowTuple, FlowTuple, TupleHash>  reverse_table_;
    std::vector<bool> port_allocated_;
    uint16_t next_port_scan_{0};

    static constexpr uint16_t csum_update_u16(uint16_t old_csum, uint16_t old_val, uint16_t new_val) noexcept {
        uint32_t sum = static_cast<uint32_t>(~old_csum & 0xFFFF) +
                       static_cast<uint32_t>(~old_val & 0xFFFF) +
                       static_cast<uint32_t>(new_val);
        while (sum >> 16) {
            sum = (sum & 0xFFFF) + (sum >> 16);
        }
        return static_cast<uint16_t>(~sum & 0xFFFF);
    }

    static constexpr uint16_t csum_update_u32(uint16_t old_csum, uint32_t old_val, uint32_t new_val) noexcept {
        uint16_t c = csum_update_u16(old_csum, static_cast<uint16_t>(old_val >> 16), static_cast<uint16_t>(new_val >> 16));
        return csum_update_u16(c, static_cast<uint16_t>(old_val & 0xFFFF), static_cast<uint16_t>(new_val & 0xFFFF));
    }

    std::optional<uint16_t> allocate_port() {
        const uint16_t total = PortEnd - PortStart + 1;
        for (uint16_t i = 0; i < total; ++i) {
            uint16_t idx = (next_port_scan_ + i) % total;
            if (!port_allocated_[idx]) {
                port_allocated_[idx] = true;
                next_port_scan_ = (idx + 1) % total;
                return PortStart + idx;
            }
        }
        return std::nullopt;
    }

    static uint16_t read_u16(const uint8_t* p) noexcept {
        return (static_cast<uint16_t>(p[0]) << 8) | p[1];
    }
    static void write_u16(uint8_t* p, uint16_t v) noexcept {
        p[0] = static_cast<uint8_t>(v >> 8);
        p[1] = static_cast<uint8_t>(v & 0xFF);
    }
    static uint32_t read_u32(const uint8_t* p) noexcept {
        return (static_cast<uint32_t>(p[0]) << 24) | (static_cast<uint32_t>(p[1]) << 16) |
               (static_cast<uint32_t>(p[2]) << 8) | p[3];
    }
    static void write_u32(uint8_t* p, uint32_t v) noexcept {
        p[0] = static_cast<uint8_t>(v >> 24);
        p[1] = static_cast<uint8_t>(v >> 16);
        p[2] = static_cast<uint8_t>(v >> 8);
        p[3] = static_cast<uint8_t>(v & 0xFF);
    }
};
