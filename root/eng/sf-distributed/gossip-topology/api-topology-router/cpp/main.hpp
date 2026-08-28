#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <span>
#include <cstdint>

namespace gossip::topology {

/// Рівень мережевої близькості відносно локального вузла
enum class LocalityTier : uint8_t {
    SameHost = 0,     ///< Локальний процес / контейнер (IPC/loopback)
    SameRack = 1,     ///< Спільна серверна стійка (ToR switch, < 0.1 ms)
    SameZone = 2,     ///< Спільна зона доступності / ДЦ (< 1.0 ms)
    SameRegion = 3,   ///< Спільний географічний регіон (1–5 ms)
    CrossRegion = 4   ///< Міжрегіональний канал WAN (> 20 ms)
};

/// Дескриптор розташування вузла в інфраструктурі
struct NodeCoordinates {
    std::string region;       ///< Географічний регіон (напр. "us-east-1", "eu-central-1")
    std::string zone;         ///< Зона доступності (напр. "az-a", "rack-4")
    std::string rack;         ///< Ідентифікатор стійки (ToR switch ID)
    std::string host_address; ///< IPv4/IPv6 або FQDN вузла
    uint16_t gossip_port;     ///< Порт UDP-слухача пліток
};

/// Стан та метадані віддаленого вузла в пулі маршрутизатора
struct PeerEndpoint {
    std::string node_id;
    NodeCoordinates coords;
    LocalityTier tier;
    std::chrono::microseconds ewma_rtt{0}; ///< Експоненційне ковзне середнє RTT
    bool is_seed_node{false};              ///< Чи є вузол статичним насінням (Seed)
    bool is_suspended{false};              ///< Тимчасово призупинений через підозру
};

/// Конфігурація ймовірностей та бюджетів топологічного маршрутизатора
struct TopologyRouterConfig {
    double weight_same_rack{0.60};    ///< Базова ймовірність вибору у своїй стійці
    double weight_same_zone{0.30};    ///< Базова ймовірність вибору у своїй зоні
    double weight_cross_region{0.10}; ///< Ймовірність вибору міжрегіонального партнера
    
    uint32_t fanout{3};               ///< Кількість партнерів на один раунд
    uint32_t max_wan_egress_burst{5}; ///< Максимальна кількість пакетів WAN на раунд
    
    std::chrono::milliseconds probe_interval{1000}; ///< Інтервал циклу пліток
    std::chrono::milliseconds rtt_timeout{250};     ///< Поріг відсікання зонду
    
    bool prefer_healthy_seeds_on_wan{true}; ///< Примусово пінгувати Seed-вузли при деградації WAN
};

/// Коди помилок операцій маршрутизатора
enum class RouterErrorCode {
    Success = 0,
    EmptyPeerPool,
    NoReachablePeersInTier,
    LocalityUnavailable,
    InvalidConfiguration,
    PeerAlreadyExists,
    PeerNotFound
};

/// Метрики та телеметрія маршрутизатора
struct RouterMetricsSnapshot {
    uint64_t total_gossip_rounds{0};
    uint64_t intra_rack_dispatches{0};
    uint64_t intra_zone_dispatches{0};
    uint64_t cross_region_dispatches{0};
    uint64_t degraded_tier_fallbacks{0};
    uint64_t dropped_wan_bursts{0};
};

/// Основний контракт топологічного маршрутизатора
class ITopologyRouter {
public:
    virtual ~ITopologyRouter() = default;

    /// Ініціалізація локальних координат сервера
    virtual std::expected<void, RouterErrorCode> SetLocalCoordinates(const NodeCoordinates& local_coords) = 0;

    /// Реєстрація або оновлення інформації про партнера
    virtual std::expected<void, RouterErrorCode> UpsertPeer(const PeerEndpoint& peer) = 0;

    /// Видалення вузла зі списків маршрутизації (наприклад, після фіксації смерті)
    virtual std::expected<void, RouterErrorCode> RemovePeer(std::string_view node_id) = 0;

    /// Оновлення виміряного мережевого RTT для коригування ваг
    virtual void ReportRttMeasurement(std::string_view node_id, std::chrono::microseconds rtt) = 0;

    /// Вибір k партнерів для поточного раунду розповсюдження пліток
    /// @param out_peers Буфер для запису обраних дескрипторів партнерів
    /// @return Кількість фактично обраних партнерів або код помилки
    virtual std::expected<size_t, RouterErrorCode> SelectGossipTargets(std::span<PeerEndpoint> out_peers) = 0;

    /// Вибір цільового вузла для непрямого зондування (Ping-Req у протоколі SWIM)
    /// Віддає перевагу вузлам у тій самій локалі, що й підозрюваний вузол
    virtual std::expected<PeerEndpoint, RouterErrorCode> SelectIndirectProxy(
        std::string_view suspect_node_id,
        std::span<const std::string_view> excluded_nodes
    ) = 0;

    /// Отримання поточної кількості зареєстрованих вузлів за рівнями локальності
    virtual size_t GetPeerCountByTier(LocalityTier tier) const noexcept = 0;

    /// Експорт знімка телеметричних метрик
    virtual RouterMetricsSnapshot GetMetrics() const noexcept = 0;
};

} // namespace gossip::topology
