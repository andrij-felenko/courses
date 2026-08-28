#include <cstdint>
#include <array>

enum class ClusterMsgType : uint16_t {
    Ping = 0,
    Pong = 1,
    Meet = 2,
    Fail = 3,
    Publish = 4
};

#pragma pack(push, 1)
struct ClusterMsg {
    std::array<char, 4> sig;                 // Сигнатура "RCmb"
    uint32_t totlen;                         // Загальна довжина кадру
    uint16_t ver;                            // Версія протоколу
    uint16_t port;                           // Клієнтський порт
    ClusterMsgType type;                     // Типізований enum повідомлення
    uint16_t count;                          // Кількість записів Gossip
    uint64_t current_epoch;                  // Глобальна епоха
    uint64_t config_epoch;                   // Локальна епоха вузла
    uint64_t replication_offset;             // Зсув реплікації
    std::array<char, 40> sender_node_id;     // 160-бітний SHA1 ID вузла
    std::array<uint8_t, 2048> slot_bitmap;   // 16 384 бітів закріплених слотів
    std::array<char, 40> master_node_id;     // ID ведучого вузла
    std::array<uint16_t, 16> sender_ip;      // IP-адреса вузла
    uint16_t tls_port;                       // Порт TLS
    uint16_t cluster_bus_port;               // Порт шини Cluster Bus
    uint16_t node_flags;                     // Бітові прапорці ролі й стану
    uint8_t cluster_state;                   // Стан кластера (OK / FAIL)
    std::array<uint8_t, 3> message_flags;    // Додаткові службові прапорці
};
#pragma pack(pop)
