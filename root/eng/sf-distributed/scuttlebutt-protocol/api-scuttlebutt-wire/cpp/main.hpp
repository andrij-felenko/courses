#ifndef SCUTTLEBUTT_API_HPP
#define SCUTTLEBUTT_API_HPP

#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <cstdint>
#include <span>
#include <memory>
#include <system_error>

namespace scuttlebutt {

enum class MessageType : uint8_t {
    Syn  = 0x01,
    Ack  = 0x02,
    Ack2 = 0x03
};

struct Config {
    uint32_t gossip_interval_ms{1000};
    uint32_t mtu_limit_bytes{1200};
    uint32_t failure_timeout_ms{10000};
};

struct StateValue {
    std::string value;
    uint64_t version{0};
};

class GossipSession {
public:
    explicit GossipSession(std::string local_node_id,
                          uint64_t generation_epoch,
                          Config config = Config{});
    ~GossipSession();

    GossipSession(const GossipSession&) = delete;
    GossipSession& operator=(const GossipSession&) = delete;
    GossipSession(GossipSession&&) noexcept;
    GossipSession& operator=(GossipSession&&) noexcept;

    // Оновлення стану власного вузла (атомарний інкремент MaxVersion)
    void set_local_state(std::string_view key, std::string_view value);

    // Отримання значення атрибута віддаленого вузла
    [[nodiscard]] std::optional<StateValue> get_state(std::string_view node_id,
                                                      std::string_view key) const noexcept;

    // Побудова SYN дейтаграми для випадкового партнера
    [[nodiscard]] std::vector<uint8_t> build_syn_packet() const;

    // Обробка вхідного мережевого пакета з опційним формуванням відповіді (ACK або ACK2)
    [[nodiscard]] std::optional<std::vector<uint8_t>> process_packet(std::span<const uint8_t> packet);

    // Перелік усіх живих вузлів кластера
    [[nodiscard]] std::vector<std::string> get_live_members() const;

private:
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace scuttlebutt

#endif // SCUTTLEBUTT_API_HPP
