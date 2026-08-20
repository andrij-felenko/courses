# 📋 Контракт інтерфейсу топологічно-чутливого маршрутизатора пліток

У розподілених сервісних сітках (*Service Mesh*), базах даних класу NoSQL (Cassandra, ScyllaDB) та системах кластерної координації (Consul, Memberlist) модуль вибору партнерів для епідемічного обміну відокремлюється у спеціалізований інтерфейс маршрутизатора топології (*Topology-Aware Peer Selector / Router*).

Маршрутизатор інкапсулює знання про мережеву топологію хоста (стійка, зона доступності, регіон, рівень RTT), веде динамічні пули адрес і повертає список партнерів для кожного раунду зондування або поширення оновлень.

---

## 1. Архітектурна модель та стани вузлів у маршрутизаторі

Маршрутизатор керує пулом вузлів, розділених за рівнями локальності відносно поточного вузла. Кожен зареєстрований партнер проходить через життєвий цикл станів:

```
                  +-----------------------------------+
                  |      1. UNINITIALIZED             |
                  +-----------------------------------+
                                    │ UpsertPeer()
                                    ▼
                  +-----------------------------------+
                  |      2. ACTIVE (Здоровий)         | ◄──────────────+
                  +-----------------------------------+                │
                    │                               │                  │
   Тайм-аут прямого │              Успішний непрямий│                  │ Успішний пінг
             зонду  │              ACK (Ping-Req)   │                  │ (Lifeguard)
                    ▼                               ▼                  │
+-------------------------+       +-------------------------+          │
| 3. SUSPECT (Підозрілий) | ────> | 4. QUARANTINED (Карантин| ─────────+
+-------------------------+       +-------------------------+
                    │
   Тайм-аут підозри │ (T_suspect сплив)
                    ▼
+-------------------------+
| 5. DEAD (Виключений)    | ────> RemovePeer()
+-------------------------+
```

1. **Active:** Вузол доступний, бере участь у зваженому виборі для пліток та моніторингу.
2. **Suspect:** Прямий пінг не відповів протягом `rtt_timeout`; для вузла запускається процедура непрямого зондування через локальних посередників.
3. **Quarantined:** Вузол відновлює зв'язок після серії втрат, але перебуває під спостереженням із поступовим поверненням повної ваги вибору.
4. **Dead:** Вузол визнано мертвим; він виключається з активної маршрутизації та очікує остаточного видалення з пам'яті через `RemovePeer()`.

---

## 2. Специфікація інтерфейсу в C++20

Нижче наведено повний програмний контракт бібліотеки топологічної маршрутизації:

```cpp
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
```

---

## 3. Детальний опис методів та параметрів

### Метод `SetLocalCoordinates`
- **Призначення:** Встановлює базові фізичні координати поточного хоста (регіон, зону, стійку, IP-адресу).
- **Семантика:** Викликається одноразово під час запуску демона або під час зміни конфігурації хмарного провайдера. На основі цих координат маршрутизатор динамічно класифікує всіх зареєстрованих партнерів за шкалою `LocalityTier`.

### Метод `UpsertPeer`
- **Призначення:** Додає новий вузол або оновлює стан наявного.
- **Поведінка:** Якщо вузол уже існує, оновлюються його статус, прапорець `is_suspended` та координати. Вузол автоматично додається у внутрішні локальні списки (`same_rack_pool`, `same_zone_pool`, `cross_region_pool`).
- **Складність:** `O(1)` амортизована за рахунок геш-таблиці індексів.

### Метод `SelectGossipTargets`
- **Призначення:** Формує вибірку з `fanout` партнерів для чергового епідемічного раунду.
- **Алгоритм:** Маршрутизатор генерує випадкове число `r ∈ [0.0, 1.0)`. Згідно з налаштуваннями `weight_same_rack`, `weight_same_zone` та `weight_cross_region`, запит спрямовується до відповідного пулу локальності. Якщо обраний пул порожній, маршрутизатор автоматично деградує вибір до сусіднього доступного рівня (Graceful Tier Fallback).

### Метод `SelectIndirectProxy`
- **Призначення:** Обирає посередника для відправлення непрямого запиту `PING_REQ` під час збою прямого зв'язку.
- **Критична вимога:** Посередник обирається з того самого дата-центру або тієї самої стійки, де розташований підозрюваний сервер `suspect_node_id`. Це гарантує, що непрямий зонд перевірить доступність цілі зсередини її локальної мережі, виключаючи хибні спрацьовування через тимчасову недоступність зовнішнього шлюзу.

---

## 4. Специфікація інтерфейсу на мові Go

:::tabs
```cpp
// Контракт C++20 наведено вище у розділі 2
```
```go
package topology

import (
	"errors"
	"time"
)

type LocalityTier uint8

const (
	TierSameHost LocalityTier = iota
	TierSameRack
	TierSameZone
	TierSameRegion
	TierCrossRegion
)

type NodeCoordinates struct {
	Region      string
	Zone        string
	Rack        string
	HostAddress string
	GossipPort  uint16
}

type PeerEndpoint struct {
	NodeID      string
	Coords      NodeCoordinates
	Tier        LocalityTier
	EwmaRTT     time.Duration
	IsSeedNode  bool
	IsSuspended bool
}

type RouterConfig struct {
	WeightSameRack    float64
	WeightSameZone    float64
	WeightCrossRegion float64
	Fanout            int
	MaxWANEgressBurst int
	ProbeInterval     time.Duration
	RTTTimeout        time.Duration
}

type RouterMetrics struct {
	TotalRounds            uint64
	IntraRackDispatches    uint64
	IntraZoneDispatches    uint64
	CrossRegionDispatches  uint64
	DegradedTierFallbacks  uint64
	DroppedWANBursts       uint64
}

var (
	ErrEmptyPeerPool          = errors.New("peer pool is empty")
	ErrNoReachablePeersInTier = errors.New("no reachable peers found in requested tier")
	ErrPeerNotFound           = errors.New("peer not found")
	ErrInvalidConfig          = errors.New("invalid configuration: weights must sum to 1.0")
)

type TopologyRouter interface {
	SetLocalCoordinates(coords NodeCoordinates) error
	UpsertPeer(peer PeerEndpoint) error
	RemovePeer(nodeID string) error
	ReportRTT(nodeID string, rtt time.Duration)
	SelectGossipTargets() ([]PeerEndpoint, error)
	SelectIndirectProxy(suspectNodeID string, excluded []string) (PeerEndpoint, error)
	GetPeerCount(tier LocalityTier) int
	GetMetrics() RouterMetrics
}
```
:::

---

## 5. Діагностика, метрики та обробка виняткових ситуацій

Під час промислової експлуатації маршрутизатор генерує критичні метрики для систем моніторингу (Prometheus / OpenTelemetry):

1. **`cross_region_dispatches_total` (Лічильник):**
   Кількість дейтаграм, відправлених за межі локального регіону. Різке зростання цього лічильника свідчить про помилку в налаштуванні ваг або збій фільтрації локальних пулів.

2. **`degraded_tier_fallbacks_total` (Лічильник деградацій):**
   Фіксує випадки, коли алгоритм не зміг знайти вузол у цільовому рівні (наприклад, усі вузли в стійці вийшли з ладу) і був змушений обрати партнера з вищого рівня. Сплеск цієї метрики є прямим індикатором локальної мережевої ізоляції стійки (*ToR isolation*).

3. **`ewma_rtt_microseconds` (Гістограма):**
   Розподіл експоненційного середнього часу кругового обігу пакетів до партнерів. Дозволяє автоматично виявляти перевантажені оптичні лінії між регіонами та тимчасово знижувати пріоритет вибору деградованих маршрутів.

---

## 6. Інтеграція з мережевим транспортом UDP та керування MTU

У промислових реалізаціях модуль топологічної маршрутизації безпосередньо взаємодіє з транспортним рівнем сокетів ОС:

1. **Упаковка оновлень у межі MTU (без IP-фрагментації):**
   Маршрутизатор обмежує розмір корисного навантаження дейтаграми пліток до 1400 байтів (залишаючи 28 байтів під заголовки IP/UDP). Якщо оновлення містить великий список подій членства, воно автоматично розбивається на окремі дейтаграми, кожна з яких маршрутизується за топологічними вагами.

2. **Керування сокетними буферами (`SO_RCVBUF` / `SO_SNDBUF`):**
   Оскільки високочастотний локальний gossip усередині стійки може генерувати сплески до 10 000 пакетів на секунду під час рестарту сервісів, системні буфери сокетів ядра Linux мають бути збільшені щонайменше до 4–8 МБ (`sysctl -w net.core.rmem_max=8388608`).

---

## 7. Керування пам'яттю та оптимізація виділень (Zero-Copy Buffer Views)

Високопродуктивна маршрутизація вимагає відсутності динамічних виділень пам'яті (`malloc`/`new`) на гарячому шляху вибору партнерів.

Метод `SelectGossipTargets` приймає попередньо виділений буфер у вигляді `std::span<PeerEndpoint>`, а не повертає новий вектор через `std::vector`. Робочий потік виділяє фіксований стек масивів для збереження обраних дескрипторів, що зводить накладні витрати процесора до кількох десятків наносекунд на раунд.

---

## 8. Інваріанти, правила потокобезпечності та обробка помилок

1. **Нормування конфігураційних ваг:**
   Сума ймовірностей вибору повинна дорівнювати одиниці:
   ```
   weight_same_rack + weight_same_zone + weight_cross_region == 1.0 (з похибкою не більше 0.001)
   ```
   Якщо сума відрізняється від `1.0`, виклик `SetLocalCoordinates` або конструктор повертає помилку `RouterErrorCode::InvalidConfiguration`.

2. **Потокобезпечність (Thread-Safety Model):**
   Маршрутизатор спроектовано для роботи в багатопотоковому середовищі високопродуктивних серверів. Операції читання (`SelectGossipTargets`, `SelectIndirectProxy`, `GetPeerCountByTier`) виконуються паралельно багатьма робочими потоками без блокувань або з використанням легких блокувань читача-письменника (`std::shared_mutex`). Модифікації списків (`UpsertPeer`, `RemovePeer`) виконуються монопольно з атомарною підміною вказівника на снапшот пулу.

3. **Захист від шторму через обмеження Egress-бюджету (`max_wan_egress_burst`):**
   Маршрутизатор гарантує, що кількість дейтаграм, відправлених за межі локального дата-центру за один інтервал `probe_interval`, строго обмежена параметром `max_wan_egress_burst`. Якщо черга оновлень перевищує цей ліміт, пакети WAN упаковуються в агреговані батчі або відкладаються до наступного такту таймера.
