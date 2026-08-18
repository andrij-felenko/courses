# ⚙️ Реалізація алгоритму BGP Best Path Selection

Практична програмна реалізація рушія прийняття рішень протоколу BGP (англ. *BGP Decision Process*) відповідно до стандарту RFC 4271 з повною підтримкою стандартної ієрархії порівняння атрибутів шляху: перевірки досяжності `NEXT_HOP`, локального пріоритету `LOCAL_PREF`, локального походження маршруту, довжини `AS_PATH`, типу `ORIGIN`, метрики `MED`, переваги зовнішніх маршрутів `eBGP` над `iBGP`, вартості досягнення шлюзу в протоколі IGP (Hot Potato Routing), а також детермінованих тайбрейкерів (Router ID та IP-адреси сусіднього вузла). Матеріал містить робочі реалізації мовами C, C++ та Python, а також покроковий розбір складного вибору між конкуруючими шляхами.

---

## 1. Архітектура та математика вибору шляху

Коли BGP-маршрутизатор отримує кілька повідомлень `UPDATE` з однаковим префіксом мережі (NLRI) від різних сусідів (або через різні сесії), він не усереднює метрики й не підсумовує вартості лінків, як це роблять протоколи типу Distance-Vector чи Link-State. Натомість рушій BGP Decision Engine запускає послідовний конвеєр лексикографічного порівняння атрибутів між кожним новим кандидатом та поточним найкращим шляхом (*Current Best*).

### Математична модель відбору

Нехай `R1` та `R2` — два альтернативні маршрути до одного префікса. Відбір найкращого маршруту `R_best = min(R1, R2)` здійснюється за каскадом строгих предикатів:

```
[Початок порівняння двох шляхів: R1 та R2]
  │
  ├─ 1. Валідність Next-Hop: чи є маршрут до R.next_hop в таблиці IGP/RIB?
  │      Якщо тільки один валідний -> обираємо його.
  │
  ├─ 2. LOCAL_PREF: max(R1.local_pref, R2.local_pref)
  │      (вищий пріоритет виходу з AS завжди перемагає).
  │
  ├─ 3. Походження: R.is_local > R.is_learned
  │      (локально інжектований префікс перемагає отриманий від сусіда).
  │
  ├─ 4. Довжина AS_PATH: min(len(R1.as_path), len(R2.as_path))
  │      (рахуються лише елементи в AS_SEQUENCE; AS_SET рахується як 1).
  │
  ├─ 5. Код ORIGIN: min(R1.origin, R2.origin)
  │      (пріоритет: IGP [0] < EGP [1] < INCOMPLETE [2]).
  │
  ├─ 6. Метрика MED: min(R1.med, R2.med)
  │      (порівнюється ТІЛЬКИ якщо обидва маршрути отримані від однієї сусідньої AS).
  │
  ├─ 7. Тип пірингу: eBGP (зовнішній) перемагає iBGP (внутрішній).
  │
  ├─ 8. IGP Metric до Next-Hop: min(R1.igp_cost, R2.igp_cost)
  │      (Hot Potato: якнайшвидший скид трафіку на найближчий вихідний шлюз).
  │
  ├─ 9. Найстаріший маршрут eBGP (запобігає флапінгу та перемиканню сесій).
  │
  ├─ 10. Найменший BGP Router ID відправника: min(R1.router_id, R2.router_id).
  │
  └─ 11. Найменша IP-адреса піра: min(R1.peer_ip, R2.peer_ip).
```

---

## 2. Робоча реалізація рушія Best Path

Нижче наведено модульну реалізацію рушія вибору шляху трьома мовами програмування. Реалізація приймає набір конкуруючих маршрутів, валідує досяжність `NEXT_HOP` через таблицю IGP і повертає єдиний переможний маршрут з детальним логуванням причини перемоги на кожному етапі.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <arpa/inet.h>

#define MAX_AS_PATH_LEN 32

typedef enum {
    ORIGIN_IGP = 0,
    ORIGIN_EGP = 1,
    ORIGIN_INCOMPLETE = 2
} bgp_origin_t;

typedef enum {
    PEER_EBGP = 0,
    PEER_IBGP = 1
} bgp_peer_type_t;

typedef struct {
    const char* prefix;
    uint32_t local_pref;
    bool is_locally_originated;
    uint32_t as_path[MAX_AS_PATH_LEN];
    size_t as_path_len;
    bgp_origin_t origin;
    uint32_t med;
    uint32_t neighbor_as;
    bgp_peer_type_t peer_type;
    uint32_t igp_metric_to_nexthop;
    bool is_nexthop_reachable;
    uint32_t router_id; // IPv4 у числовиковому форматі
    uint32_t peer_ip;
    const char* route_name;
} bgp_route_t;

// Повертає:
//  1 якщо route_a кращий за route_b,
// -1 якщо route_b кращий за route_a,
//  0 якщо шляхи абсолютно ідентичні
int compare_bgp_routes(const bgp_route_t* a, const bgp_route_t* b, const char** win_reason) {
    // Крок 0: Перевірка досяжності Next-Hop
    if (a->is_nexthop_reachable && !b->is_nexthop_reachable) {
        *win_reason = "Next-Hop reachable (B is unreachable)";
        return 1;
    }
    if (!a->is_nexthop_reachable && b->is_nexthop_reachable) {
        *win_reason = "Next-Hop reachable (A is unreachable)";
        return -1;
    }
    if (!a->is_nexthop_reachable && !b->is_nexthop_reachable) {
        *win_reason = "Both Next-Hops unreachable";
        return 0;
    }

    // Крок 1: Найвищий LOCAL_PREF
    if (a->local_pref > b->local_pref) {
        *win_reason = "Higher LOCAL_PREF";
        return 1;
    }
    if (a->local_pref < b->local_pref) {
        *win_reason = "Higher LOCAL_PREF";
        return -1;
    }

    // Крок 2: Локально згенерований маршрут переважає отриманий по BGP
    if (a->is_locally_originated && !b->is_locally_originated) {
        *win_reason = "Locally originated route";
        return 1;
    }
    if (!a->is_locally_originated && b->is_locally_originated) {
        *win_reason = "Locally originated route";
        return -1;
    }

    // Крок 3: Найкоротший AS_PATH
    if (a->as_path_len < b->as_path_len) {
        *win_reason = "Shorter AS_PATH length";
        return 1;
    }
    if (a->as_path_len > b->as_path_len) {
        *win_reason = "Shorter AS_PATH length";
        return -1;
    }

    // Крок 4: Найнижчий код ORIGIN (IGP < EGP < INCOMPLETE)
    if (a->origin < b->origin) {
        *win_reason = "Lower ORIGIN code (IGP preferred)";
        return 1;
    }
    if (a->origin > b->origin) {
        *win_reason = "Lower ORIGIN code (IGP preferred)";
        return -1;
    }

    // Крок 5: Найменший MED (порівнюється лише якщо маршрути від однієї сусідньої AS)
    if (a->neighbor_as == b->neighbor_as) {
        if (a->med < b->med) {
            *win_reason = "Lowest MED from same neighbor AS";
            return 1;
        }
        if (a->med > b->med) {
            *win_reason = "Lowest MED from same neighbor AS";
            return -1;
        }
    }

    // Крок 6: eBGP переважає iBGP
    if (a->peer_type == PEER_EBGP && b->peer_type == PEER_IBGP) {
        *win_reason = "eBGP over iBGP";
        return 1;
    }
    if (a->peer_type == PEER_IBGP && b->peer_type == PEER_EBGP) {
        *win_reason = "eBGP over iBGP";
        return -1;
    }

    // Крок 7: Найменша метрика IGP до NEXT_HOP (Hot Potato Routing)
    if (a->igp_metric_to_nexthop < b->igp_metric_to_nexthop) {
        *win_reason = "Lowest IGP metric to Next-Hop";
        return 1;
    }
    if (a->igp_metric_to_nexthop > b->igp_metric_to_nexthop) {
        *win_reason = "Lowest IGP metric to Next-Hop";
        return -1;
    }

    // Крок 8: Тайбрейкер за найменшим Router ID
    if (a->router_id < b->router_id) {
        *win_reason = "Lowest BGP Router ID";
        return 1;
    }
    if (a->router_id > b->router_id) {
        *win_reason = "Lowest BGP Router ID";
        return -1;
    }

    // Крок 9: Тайбрейкер за найменшою IP-адресою піра
    if (a->peer_ip < b->peer_ip) {
        *win_reason = "Lowest Neighbor IP Address";
        return 1;
    }
    if (a->peer_ip > b->peer_ip) {
        *win_reason = "Lowest Neighbor IP Address";
        return -1;
    }

    *win_reason = "Identical paths (Tie)";
    return 0;
}

const bgp_route_t* select_best_path(const bgp_route_t routes[], size_t count) {
    if (count == 0) return NULL;

    const bgp_route_t* best = &routes[0];
    const char* reason = "Initial candidate";

    for (size_t i = 1; i < count; ++i) {
        const char* step_reason = NULL;
        int cmp = compare_bgp_routes(&routes[i], best, &step_reason);
        if (cmp > 0) {
            printf("[BGP Decision] Route '%s' defeats '%s' -> Reason: %s\n",
                   routes[i].route_name, best->route_name, step_reason);
            best = &routes[i];
            reason = step_reason;
        } else if (cmp < 0) {
            printf("[BGP Decision] Current best '%s' retains lead over '%s' -> Reason: %s\n",
                   best->route_name, routes[i].route_name, step_reason);
        }
    }

    printf("\n>>> WINNING BEST PATH: '%s' (Reason: %s) <<<\n", best->route_name, reason);
    return best;
}

int main(void) {
    bgp_route_t candidates[] = {
        {
            .route_name = "Path-A (ISP-1)",
            .prefix = "203.0.113.0/24",
            .local_pref = 100,
            .is_locally_originated = false,
            .as_path = {64500, 65001},
            .as_path_len = 2,
            .origin = ORIGIN_IGP,
            .med = 50,
            .neighbor_as = 64500,
            .peer_type = PEER_EBGP,
            .igp_metric_to_nexthop = 10,
            .is_nexthop_reachable = true,
            .router_id = 0xC0000201, // 192.0.2.1
            .peer_ip = 0xC0000201
        },
        {
            .route_name = "Path-B (ISP-2-Backup)",
            .prefix = "203.0.113.0/24",
            .local_pref = 100,
            .is_locally_originated = false,
            .as_path = {64502, 64503, 65001},
            .as_path_len = 3,
            .origin = ORIGIN_IGP,
            .med = 10,
            .neighbor_as = 64502,
            .peer_type = PEER_EBGP,
            .igp_metric_to_nexthop = 5,
            .is_nexthop_reachable = true,
            .router_id = 0xC0000202, // 192.0.2.2
            .peer_ip = 0xC0000202
        },
        {
            .route_name = "Path-C (Direct-Peer-HighPref)",
            .prefix = "203.0.113.0/24",
            .local_pref = 200, // Вищий Local Preference!
            .is_locally_originated = false,
            .as_path = {64510, 64511, 65001},
            .as_path_len = 3,
            .origin = ORIGIN_INCOMPLETE,
            .med = 100,
            .neighbor_as = 64510,
            .peer_type = PEER_EBGP,
            .igp_metric_to_nexthop = 25,
            .is_nexthop_reachable = true,
            .router_id = 0xC0000203,
            .peer_ip = 0xC0000203
        }
    };

    select_best_path(candidates, sizeof(candidates) / sizeof(candidates[0]));
    return 0;
}
```

@tab cpp
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <cstdint>

enum class BgpOrigin : uint8_t {
    Igp = 0,
    Egp = 1,
    Incomplete = 2
};

enum class PeerType : uint8_t {
    Ebgp = 0,
    Ibgp = 1
};

struct BgpRoute {
    std::string route_name;
    std::string prefix;
    uint32_t local_pref{100};
    bool is_locally_originated{false};
    std::vector<uint32_t> as_path;
    BgpOrigin origin{BgpOrigin::Igp};
    uint32_t med{0};
    uint32_t neighbor_as{0};
    PeerType peer_type{PeerType::Ebgp};
    uint32_t igp_metric_to_nexthop{0};
    bool is_nexthop_reachable{true};
    uint32_t router_id{0};
    uint32_t peer_ip{0};
};

struct ComparisonResult {
    int outcome; // > 0: a wins, < 0: b wins, 0: tie
    std::string_view reason;
};

ComparisonResult compare_routes(const BgpRoute& a, const BgpRoute& b) noexcept {
    // Крок 0: Валідність наступного шлюзу
    if (a.is_nexthop_reachable != b.is_nexthop_reachable) {
        return a.is_nexthop_reachable 
            ? ComparisonResult{1, "Next-Hop reachable (peer unreachable)"}
            : ComparisonResult{-1, "Next-Hop reachable (peer unreachable)"};
    }
    if (!a.is_nexthop_reachable && !b.is_nexthop_reachable) {
        return {0, "Both Next-Hops unreachable"};
    }

    // Крок 1: Найвищий LOCAL_PREF
    if (a.local_pref != b.local_pref) {
        return a.local_pref > b.local_pref 
            ? ComparisonResult{1, "Higher LOCAL_PREF"}
            : ComparisonResult{-1, "Higher LOCAL_PREF"};
    }

    // Крок 2: Локальне походження
    if (a.is_locally_originated != b.is_locally_originated) {
        return a.is_locally_originated 
            ? ComparisonResult{1, "Locally originated route"}
            : ComparisonResult{-1, "Locally originated route"};
    }

    // Крок 3: Найкоротший AS_PATH
    if (a.as_path.size() != b.as_path.size()) {
        return a.as_path.size() < b.as_path.size()
            ? ComparisonResult{1, "Shorter AS_PATH length"}
            : ComparisonResult{-1, "Shorter AS_PATH length"};
    }

    // Крок 4: Найнижчий ORIGIN
    if (a.origin != b.origin) {
        return a.origin < b.origin
            ? ComparisonResult{1, "Lower ORIGIN code (IGP preferred)"}
            : ComparisonResult{-1, "Lower ORIGIN code (IGP preferred)"};
    }

    // Крок 5: Найменший MED (тільки для тієї самої сусідньої AS)
    if (a.neighbor_as == b.neighbor_as && a.med != b.med) {
        return a.med < b.med
            ? ComparisonResult{1, "Lowest MED from same neighbor AS"}
            : ComparisonResult{-1, "Lowest MED from same neighbor AS"};
    }

    // Крок 6: eBGP над iBGP
    if (a.peer_type != b.peer_type) {
        return a.peer_type == PeerType::Ebgp
            ? ComparisonResult{1, "eBGP over iBGP"}
            : ComparisonResult{-1, "eBGP over iBGP"};
    }

    // Крок 7: Найменша метрика IGP до Next-Hop (Hot Potato)
    if (a.igp_metric_to_nexthop != b.igp_metric_to_nexthop) {
        return a.igp_metric_to_nexthop < b.igp_metric_to_nexthop
            ? ComparisonResult{1, "Lowest IGP metric to Next-Hop"}
            : ComparisonResult{-1, "Lowest IGP metric to Next-Hop"};
    }

    // Крок 8: Найменший Router ID
    if (a.router_id != b.router_id) {
        return a.router_id < b.router_id
            ? ComparisonResult{1, "Lowest BGP Router ID"}
            : ComparisonResult{-1, "Lowest BGP Router ID"};
    }

    // Крок 9: Найменша IP-адреса піра
    if (a.peer_ip != b.peer_ip) {
        return a.peer_ip < b.peer_ip
            ? ComparisonResult{1, "Lowest Neighbor IP Address"}
            : ComparisonResult{-1, "Lowest Neighbor IP Address"};
    }

    return {0, "Identical paths (Tie)"};
}

std::optional<BgpRoute> select_best_path(std::span<const BgpRoute> routes) {
    if (routes.empty()) return std::nullopt;

    const BgpRoute* best = &routes[0];
    std::string_view last_reason = "Initial candidate";

    for (size_t i = 1; i < routes.size(); ++i) {
        auto [outcome, reason] = compare_routes(routes[i], *best);
        if (outcome > 0) {
            std::cout << "[BGP Decision] '" << routes[i].route_name 
                      << "' defeats '" << best->route_name 
                      << "' -> Reason: " << reason << '\n';
            best = &routes[i];
            last_reason = reason;
        } else if (outcome < 0) {
            std::cout << "[BGP Decision] Current best '" << best->route_name 
                      << "' retains lead over '" << routes[i].route_name 
                      << "' -> Reason: " << reason << '\n';
        }
    }

    std::cout << "\n>>> WINNING BEST PATH: '" << best->route_name 
              << "' (Reason: " << last_reason << ") <<<\n";
    return *best;
}

int main() {
    const std::vector<BgpRoute> candidates = {
        {
            .route_name = "Path-A (ISP-1)",
            .prefix = "203.0.113.0/24",
            .local_pref = 100,
            .is_locally_originated = false,
            .as_path = {64500, 65001},
            .origin = BgpOrigin::Igp,
            .med = 50,
            .neighbor_as = 64500,
            .peer_type = PeerType::Ebgp,
            .igp_metric_to_nexthop = 10,
            .is_nexthop_reachable = true,
            .router_id = 0xC0000201,
            .peer_ip = 0xC0000201
        },
        {
            .route_name = "Path-B (ISP-2-Backup)",
            .prefix = "203.0.113.0/24",
            .local_pref = 100,
            .is_locally_originated = false,
            .as_path = {64502, 64503, 65001},
            .as_path_len = 3,
            .origin = BgpOrigin::Igp,
            .med = 10,
            .neighbor_as = 64502,
            .peer_type = PeerType::Ebgp,
            .igp_metric_to_nexthop = 5,
            .is_nexthop_reachable = true,
            .router_id = 0xC0000202,
            .peer_ip = 0xC0000202
        },
        {
            .route_name = "Path-C (Direct-Peer-HighPref)",
            .prefix = "203.0.113.0/24",
            .local_pref = 200,
            .is_locally_originated = false,
            .as_path = {64510, 64511, 65001},
            .origin = BgpOrigin::Incomplete,
            .med = 100,
            .neighbor_as = 64510,
            .peer_type = PeerType::Ebgp,
            .igp_metric_to_nexthop = 25,
            .is_nexthop_reachable = true,
            .router_id = 0xC0000203,
            .peer_ip = 0xC0000203
        }
    };

    select_best_path(candidates);
    return 0;
}
```

@tab python
```python
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional, Tuple


class BgpOrigin(IntEnum):
    IGP = 0
    EGP = 1
    INCOMPLETE = 2


class PeerType(IntEnum):
    EBGP = 0
    IBGP = 1


@dataclass
class BgpRoute:
    route_name: str
    prefix: str
    local_pref: int = 100
    is_locally_originated: bool = False
    as_path: List[int] = field(default_factory=list)
    origin: BgpOrigin = BgpOrigin.IGP
    med: int = 0
    neighbor_as: int = 0
    peer_type: PeerType = PeerType.EBGP
    igp_metric_to_nexthop: int = 0
    is_nexthop_reachable: bool = True
    router_id: int = 0  # Числове представлення IP (uint32)
    peer_ip: int = 0


def compare_bgp_routes(a: BgpRoute, b: BgpRoute) -> Tuple[int, str]:
    """
    Повертає:
      (1, reason)  якщо route 'a' кращий за 'b'
      (-1, reason) якщо route 'b' кращий за 'a'
      (0, reason)  якщо шляхи еквівалентні
    """
    # 0. Перевірка досяжності Next-Hop
    if a.is_nexthop_reachable != b.is_nexthop_reachable:
        return (1, "Next-Hop reachable (peer unreachable)") if a.is_nexthop_reachable else (-1, "Next-Hop reachable (peer unreachable)")
    if not a.is_nexthop_reachable and not b.is_nexthop_reachable:
        return (0, "Both Next-Hops unreachable")

    # 1. Найвищий LOCAL_PREF
    if a.local_pref != b.local_pref:
        return (1, "Higher LOCAL_PREF") if a.local_pref > b.local_pref else (-1, "Higher LOCAL_PREF")

    # 2. Локально згенерований маршрут
    if a.is_locally_originated != b.is_locally_originated:
        return (1, "Locally originated route") if a.is_locally_originated else (-1, "Locally originated route")

    # 3. Найкоротший AS_PATH
    if len(a.as_path) != len(b.as_path):
        return (1, "Shorter AS_PATH length") if len(a.as_path) < len(b.as_path) else (-1, "Shorter AS_PATH length")

    # 4. Найнижчий ORIGIN
    if a.origin != b.origin:
        return (1, "Lower ORIGIN code (IGP preferred)") if a.origin < b.origin else (-1, "Lower ORIGIN code (IGP preferred)")

    # 5. Найменший MED (тільки для маршрутів від однакової сусідньої AS)
    if a.neighbor_as == b.neighbor_as and a.med != b.med:
        return (1, "Lowest MED from same neighbor AS") if a.med < b.med else (-1, "Lowest MED from same neighbor AS")

    # 6. eBGP перед iBGP
    if a.peer_type != b.peer_type:
        return (1, "eBGP over iBGP") if a.peer_type == PeerType.EBGP else (-1, "eBGP over iBGP")

    # 7. Найменша метрика IGP до Next-Hop (Hot Potato Routing)
    if a.igp_metric_to_nexthop != b.igp_metric_to_nexthop:
        return (1, "Lowest IGP metric to Next-Hop") if a.igp_metric_to_nexthop < b.igp_metric_to_nexthop else (-1, "Lowest IGP metric to Next-Hop")

    # 8. Найменший BGP Router ID
    if a.router_id != b.router_id:
        return (1, "Lowest BGP Router ID") if a.router_id < b.router_id else (-1, "Lowest BGP Router ID")

    # 9. Найменша IP-адреса піра
    if a.peer_ip != b.peer_ip:
        return (1, "Lowest Neighbor IP Address") if a.peer_ip < b.peer_ip else (-1, "Lowest Neighbor IP Address")

    return (0, "Identical paths (Tie)")


def select_best_path(routes: List[BgpRoute]) -> Optional[BgpRoute]:
    if not routes:
        return None

    best = routes[0]
    win_reason = "Initial candidate"

    for candidate in routes[1:]:
        outcome, reason = compare_bgp_routes(candidate, best)
        if outcome > 0:
            print(f"[BGP Decision] '{candidate.route_name}' defeats '{best.route_name}' -> Reason: {reason}")
            best = candidate
            win_reason = reason
        elif outcome < 0:
            print(f"[BGP Decision] Current best '{best.route_name}' retains lead over '{candidate.route_name}' -> Reason: {reason}")

    print(f"\n>>> WINNING BEST PATH: '{best.route_name}' (Reason: {win_reason}) <<<\n")
    return best


if __name__ == "__main__":
    candidates = [
        BgpRoute(
            route_name="Path-A (ISP-1)",
            prefix="203.0.113.0/24",
            local_pref=100,
            as_path=[64500, 65001],
            origin=BgpOrigin.IGP,
            med=50,
            neighbor_as=64500,
            peer_type=PeerType.EBGP,
            igp_metric_to_nexthop=10,
            router_id=0xC0000201,
            peer_ip=0xC0000201,
        ),
        BgpRoute(
            route_name="Path-B (ISP-2-Backup)",
            prefix="203.0.113.0/24",
            local_pref=100,
            as_path=[64502, 64503, 65001],
            origin=BgpOrigin.IGP,
            med=10,
            neighbor_as=64502,
            peer_type=PeerType.EBGP,
            igp_metric_to_nexthop=5,
            router_id=0xC0000202,
            peer_ip=0xC0000202,
        ),
        BgpRoute(
            route_name="Path-C (Direct-Peer-HighPref)",
            prefix="203.0.113.0/24",
            local_pref=200,  # Найвищий пріоритет виходу перемагає коротший AS_PATH
            as_path=[64510, 64511, 65001],
            origin=BgpOrigin.INCOMPLETE,
            med=100,
            neighbor_as=64510,
            peer_type=PeerType.EBGP,
            igp_metric_to_nexthop=25,
            router_id=0xC0000203,
            peer_ip=0xC0000203,
        ),
    ]

    select_best_path(candidates)
```
:::

---

## 3. Покроковий розбір етапів алгоритму прийняття рішень

Алгоритм вибору найкращого шляху BGP (англ. *BGP Best Path Selection Algorithm*) є строго детермінованим конвеєром. Маршрутизатор розглядає множину всіх валідних шляхів для кожного конкретного префікса мережі і відсіює кандидатів крок за кроком, доки не залишиться рівно один переможець (або кілька рівноцінних шляхів для BGP Multipath ECMP).

### Крок 0. Досяжність адреси наступного шлюзу (NEXT_HOP Reachability)

Перш ніж будь-який атрибут маршруту буде порівняно з іншими, маршрутизатор зобов'язаний перевірити, чи є адреса, вказана в атрибуті `NEXT_HOP`, досяжною через внутрішню таблицю маршрутизації (IGP або локальні статичні/підключені маршрути).

Якщо адреса `NEXT_HOP` відсутня в таблиці маршрутизації ядра або вказує на інтерфейс у стані `DOWN`, маршрут отримує статус *Inaccessible* (недосяжний). Такий маршрут:
1. Залишається в загальній базі даних BGP RIB-In для збереження стану сесії.
2. Повністю виключається з процесу вибору найкращого шляху.
3. Ніколи не встановлюється в апаратну таблицю комутації FIB (*Forwarding Information Base*).
4. Ніколи не анонсується іншим сусіднім маршрутизаторам.

У практичній роботі недосяжність `NEXT_HOP` є найчастішою причиною відсутності маршрутів у таблиці iBGP, коли прикордонний роутер забуває увімкнути команду `next-hop-self` при передачі eBGP-маршрутів усередину власної автономної системи.

### Крок 1. Вага маршруту (Cisco/Vendor Weight)

Атрибут `Weight` є пропрієтарним локальним параметром маршрутизатора (введеним компанією Cisco і згодом підтриманим іншими виробниками, такими як FRRouting, Arista, Juniper у вигляді спеціальних аналогів).
- Значення коливається від `0` до `65535` (за замовчуванням `0` для отриманих маршрутів і `32768` для локально створених префіксів).
- Атрибут є строго локальним для конкретного фізичного роутера: він ніколи не кодується в пакетах `UPDATE` і не передається іншим BGP-спікерам навіть усередині однієї AS.
- Маршрут із найбільшим значенням `Weight` негайно перемагає всіх інших кандидатів.

### Крок 2. Локальний пріоритет (LOCAL_PREF)

Атрибут `LOCAL_PREF` (Well-Known Discretionary, код `5`) є головним стандартизованим інструментом керування вихідним трафіком (*Outbound Traffic Engineering*) автономної системи.
- Значення передається між усіма внутрішніми маршрутизаторами в межах iBGP-сесій.
- Стандартне значення за замовчуванням дорівнює `100`.
- Маршрутизатор обирає шлях із **найвищим** значенням `LOCAL_PREF`.
- Використання: якщо організація має два канали зв'язку — основний високошвидкісний (Primary) та резервний дорогий (Backup), на прикордонному роутері для основного каналу виставляється `LOCAL_PREF 200`, а для резервного — `LOCAL_PREF 50`. Усі внутрішні роутери автономної системи автоматично спрямують вихідні пакети через основний шлюз.

### Крок 3. Локально згенеровані маршрути (Locally Originated)

Маршрутизатор віддає перевагу маршрутам, які були створені ним самим локально, перед тими, які були отримані від інших BGP-сусідів.
Ієрархія локального походження:
1. Маршрути, додані через явну директиву `network` або агреговані командою `aggregate-address`.
2. Маршрути, отримані шляхом редистрибуції з протоколів IGP (OSPF, IS-IS, статичні маршрути).
3. Маршрути, отримані від віддалених BGP-пірів.

### Крок 4. Довжина послідовності автономних систем (AS_PATH Length)

Маршрутизатор підраховує кількість номерів AS в атрибуті `AS_PATH` і обирає шлях із **найменшою** довжиною.
Особливості підрахунку:
- Враховуються лише елементи у сегментах типу `AS_SEQUENCE`.
- Сегмент типу `AS_SET` (невпорядкована множина ASN після агрегації) рахується рівно як один ASN, незалежно від реальної кількості номерів усередині множини.
- Номери під-AS у конфедераціях (`AS_CONFED_SEQUENCE` та `AS_CONFED_SET`) повністю ігноруються і не додаються до загальної довжини шляху під час міждоменного порівняння.

Маніпуляція довжиною `AS_PATH` за допомогою механізму *AS-Path Prepending* (штучне багаторазове додавання власного ASN) є основним способом впливу на вхідний трафік від зовнішніх провайдерів без використання складних спільнот.

### Крок 5. Тип походження маршруту (ORIGIN)

Атрибут `ORIGIN` вказує, яким чином маршрут первинно потрапив у таблицю BGP. Алгоритм віддає перевагу маршрутам із меншим числовим значенням коду:
1. `IGP` (значення `0`): префікс створено командою `network` у BGP.
2. `EGP` (значення `1`): історичний спадок протоколу EGP (RFC 904), практично не зустрічається.
3. `INCOMPLETE` (значення `2`): префікс потрапив у BGP через механізм редистрибуції (`redistribute ospf/connected/static`).

### Крок 6. Дискримінатор множинного виходу (MULTI_EXIT_DISC / MED)

Атрибут `MED` (Optional Non-Transitive, код `4`) дозволяє автономній системі повідомити сусідній AS, через який саме з кількох спільних каналів зв'язку бажано надсилати вхідний трафік.
- Менше значення `MED` є кращим (*Metric* = `0` краще за *Metric* = `100`).
- **Правило однієї AS:** за замовчуванням (RFC 4271) роутер порівнює `MED` виключно між тими кандидатами, у яких перший ASN в `AS_PATH` є однаковим.
- Спеціальна директива `bgp always-compare-med` дозволяє зняти це обмеження й порівнювати `MED` від різних сусідніх AS (використовується в корпоративних ізольованих мережах).

### Крок 7. Зовнішній eBGP над внутрішнім iBGP

Якщо довжина `AS_PATH`, `ORIGIN` та `MED` однакові, маршрутизатор завжди обирає маршрут, отриманий через **зовнішню eBGP-сесію**, перед маршрутом, отриманим через **внутрішню iBGP-сесію** (або конфедеративну eBGP-сесію).
Логіка правила: швидше передати трафік зовнішньому партнеру без додаткового навантаження власної магістральної мережі.

### Крок 8. Метрика IGP до наступного шлюзу (Hot Potato Routing)

Якщо обидва маршрути є внутрішніми iBGP або обидва є зовнішніми eBGP, роутер аналізує вартість досягнення адреси `NEXT_HOP` за внутрішньою таблицею протоколу IGP (OSPF або IS-IS).
- Обирається шлях із **найменшою метрикою IGP** до точки виходу.
- Це явище має назву **Hot Potato Routing** («гаряча картопля»): автономна система намагається позбутися транзитного пакета якомога швидше через найближчий географічний вихідний шлюз, мінімізуючи витрати ресурсів власних каналів зв'язку.

### Крок 9. Балансування навантаження (BGP Multipath)

Якщо на даному етапі залишається кілька шляхів із повністю ідентичними параметрами (однаковий `Weight`, `LOCAL_PREF`, `AS_PATH`, `ORIGIN`, `MED`, тип пірингу та IGP-вартість), і на маршрутизаторі ввімкнено режим `maximum-paths N`, алгоритм зупиняє подальший відсів. Усі ці шляхи встановлюються в таблицю комутації FIB для рівномірного розподілу трафіку (ECMP — *Equal-Cost Multi-Path*).

### Крок 10. Детерміновані тайбрейкери (Tie-breakers)

Якщо балансування не налаштовано, маршрутизатор застосовує фінальні критерії для детермінованого вибору рівно одного переможця:
1. **Найстаріший eBGP-шлях:** якщо один із маршрутів eBGP був отриманий раніше за інші й перебуває у стабільному стані, він зберігає лідерство. Це мінімізує маршрутний флапінг (*Route Flapping*) під час тимчасових коливань зв'язку.
2. **Найменший BGP Router ID:** обирається маршрут від сусіда з найменшим 32-бітним ідентифікатором (якщо маршрут отримано через Route Reflector, замість Router ID сусіда порівнюється атрибут `ORIGINATOR_ID`).
3. **Найкоротший CLUSTER_LIST:** у мережах із Route Reflectors перевага надається шляху, що пройшов крізь найменшу кількість кластерів відбиття.
4. **Найменша IP-адреса сусіда:** якщо Router ID виявилися однаковими (наприклад, між двома роутерами піднято дві паралельні сесії), обирається маршрут із найменшою IP-адресою піра, на яку встановлено TCP-з'єднання.

---

## 4. Комплексний тестовий сценарій та порівняльна таблиця

Розглянемо практичний приклад, у якому прикордонний маршрутизатор `R_Core` отримує чотири конкуруючі оголошення для префікса `198.51.100.0/24` від різних партнерів:

| Параметр | Кандидат 1 (ISP-Transit-A) | Кандидат 2 (ISP-Transit-B) | Кандидат 3 (Direct-IX-Peer) | Кандидат 4 (Internal-Backup) |
| :--- | :--- | :--- | :--- | :--- |
| **Next-Hop Reachable** | Так (IGP cost = 15) | Так (IGP cost = 20) | Так (IGP cost = 10) | Так (IGP cost = 5) |
| **LOCAL_PREF** | `100` | `100` | `150` | `100` |
| **Локальне походження** | Ні | Ні | Ні | Ні |
| **AS_PATH** | `64500 65000` (довжина 2) | `64501 65000` (довжина 2) | `64510 64520 65000` (довжина 3) | `65000` (довжина 1) |
| **ORIGIN** | `IGP` (0) | `IGP` (0) | `INCOMPLETE` (2) | `IGP` (0) |
| **MED** | `50` | `10` | `0` | `0` |
| **Тип сесії** | `eBGP` | `eBGP` | `eBGP` | `iBGP` |
| **Router ID** | `192.0.2.1` | `192.0.2.2` | `192.0.2.3` | `10.0.0.1` |

### Покроковий аналіз вибору:

1. **Аналіз Кандидата 4 (Internal-Backup):** хоча маршрут має найкоротший `AS_PATH` (довжина 1) і найменшу метрику IGP (5), його `LOCAL_PREF` дорівнює `100`.
2. **Аналіз Кандидата 3 (Direct-IX-Peer):** має довгий `AS_PATH` (3 автономні системи) та найгірший `ORIGIN` (`INCOMPLETE`), але оператор призначив йому `LOCAL_PREF 150` на точці обміну трафіком (IXP).
3. **Результат роботи конвеєра:** Кандидат 3 перемагає всіх конкурентів на Кроці 2 (`LOCAL_PREF`), оскільки `150 > 100`. Довжина `AS_PATH` та метрики інших кандидатів навіть не оцінюються. Трафік прямує через точку прямого обміну трафіком.

Якщо ж Кандидат 3 пропаде через аварію лінка на IXP, почнеться порівняння між Кандидатами 1, 2 та 4:
---

## 5. Аномалії вибору шляху та методи їхнього усунення

Складна багатокритеріальна логіка алгоритму вибору шляху за певних топологій та налаштувань політик може призводити до небезпечних аномалій маршрутизації:

### 5.1. Недетермінований вибір через порядок надходження пакетів (Non-Deterministic MED)

Якщо опцію `bgp deterministic-med` вимкнено, порядок надходження маршрутів від різних провайдерів суттєво впливає на кінцевий вибір.

Розглянемо ситуацію, коли роутер має три шляхи:
1. `Шлях A`: від AS 64500, `MED = 50`, `Router ID = 10.1.1.1`.
2. `Шлях B`: від AS 64500, `MED = 100`, `Router ID = 10.2.2.2`.
3. `Шлях C`: від AS 64501, `MED = 10`, `Router ID = 10.3.3.3`.

- **Сценарій 1 (порядок A -> B -> C):**
  - Порівнюються A та B: обидва від AS 64500, тому порівнюється `MED`. Оскільки `50 < 100`, перемагає A.
  - Порівнюються A та C: вони від різних AS, тому `MED` не порівнюється. За тайбрейкером Router ID перемагає A (`10.1.1.1 < 10.3.3.3`).
  - **Переможець: Шлях A.**

- **Сценарій 2 (порядок B -> C -> A):**
  - Порівнюються B та C: від різних AS, `MED` ігнорується. За Router ID перемагає B (`10.2.2.2 < 10.3.3.3`).
  - Порівнюються B та A: від однієї AS 64500. За `MED` перемагає A (`50 < 100`).
  - **Переможець: Шлях A.**

- **Сценарій 3 (порядок C -> B -> A):**
  - Порівнюються C та B: від різних AS, перемагає B за Router ID (`10.2.2.2 < 10.3.3.3`).
  - Але якщо в іншій реалізації BGP спочатку порівнює C з іншим маршрутом або видаляє C, тимчасові стани можуть спричинити зациклення або вибір неоптимального шляху.

Увімкнення команди `bgp deterministic-med` змушує маршрутизатор групувати всі шляхи за сусідніми AS перед початком глобального порівняння, гарантуючи 100% математичний детермінізм незалежно від хронології сесій.

### 5.2. Проблема стійких маршрутних осциляцій (BGP Persistent Route Oscillation, RFC 3345)

У великих iBGP-мережах із серверами Route Reflector вибір за метрикою IGP (Hot Potato) може утворювати безкінечний цикл відбиття маршрутів:
- Роутер RR1 обирає шлях через східний вихідний шлюз, тому що метрика IGP до нього менша.
- Після відбиття цього вибору клієнтам роутер RR2 бачить оновлення і перемикається на нього.
- Але перемикання RR2 змінює вибір для RR1, змушуючи його повернутися до західного шлюзу.
- Цей процес повторюється кожні кілька секунд, генеруючи неперервний шторм повідомлень `UPDATE`.

**Рішення:** використання механізму **BGP ADD-PATH (RFC 7911)**, який дозволяє передавати кілька альтернативних шляхів для одного префікса через iBGP, або топологічне розміщення Route Reflectors суворо узгоджено з ієрархією внутрішніх метрик IGP.

---

## 6. Діагностика та перевірка вибору в продуктивних операційних системах

Для перевірки роботи алгоритму в реальних мережевих середовищах оператори використовують спеціалізовані команди діагностики BGP RIB:

### Cisco IOS-XE / FRRouting:
```text
router# show ip bgp 203.0.113.0/24
BGP routing table entry for 203.0.113.0/24, version 142
Paths: (3 available, best #3, table default)
  Advertised to non-peer-group peers:
    10.0.0.2 10.0.0.3
  64500 65001
    198.51.100.1 from 198.51.100.1 (192.0.2.1)
      Origin IGP, metric 50, localpref 100, valid, external
  64502 64503 65001
    198.51.100.5 from 198.51.100.5 (192.0.2.2)
      Origin IGP, metric 10, localpref 100, valid, external
  64510 64511 65001
    198.51.100.9 from 198.51.100.9 (192.0.2.3)
      Origin incomplete, metric 100, localpref 200, valid, external, best (Local-Pref)
```
Позначка `*` вказує на валідність (`valid`), а знак `>` або слово `best (Local-Pref)` позначає маршрут-переможець із причиною його вибору.

### BIRD Internet Routing Daemon:
```text
bird> show route for 203.0.113.0/24 all
Table master4:
203.0.113.0/24       unicast [bgp_direct_peer 15:42:01.120] * (100/25) [AS65001i]
    via 198.51.100.9 on eth2
    Type: BGP univ
    BGP.origin: Incomplete
    BGP.as_path: 64510 64511 65001
    BGP.next_hop: 198.51.100.9
    BGP.local_pref: 200
    BGP.med: 100
                     unicast [bgp_isp1 15:40:12.890] (100/10) [AS65001i]
    via 198.51.100.1 on eth0
    Type: BGP univ
    BGP.origin: IGP
    BGP.as_path: 64500 65001
    BGP.next_hop: 198.51.100.1
    BGP.local_pref: 100
    BGP.med: 50
```
---

## 7. Безпека вибору маршруту: інтеграція з RPKI та GTSM

Сучасний процес вибору найкращого шляху BGP розширюється механізмами криптографічної валідації походження префіксів (RPKI) та захисту транспортного рівня:

### 7.1. Валідація походження префіксів (RPKI Route Origin Validation, RFC 6811)

До початку виконання стандартного алгоритму Best Path маршрутизатор перевіряє відповідність пари `<Prefix, Origin ASN>` у базі криптографічних сертифікатів ROA (*Route Origin Authorization*):
1. **Valid (Валідний):** маршрут відповідає підписаному сертифікату ROA. Отримує найвищий пріоритет.
2. **NotFound / Unknown (Невідомий):** сертифікат для даного префікса відсутній у глобальній базі RPKI. Маршрут допускається до стандартного вибору Best Path.
3. **Invalid (Невалідний):** префікс оголошено неавторизованою автономною системою або довжина маски перевищує `maxLength` у ROA. Такий маршрут **негайно відкидається** на етапі перевірки предикатів і ніколи не потрапляє в BGP Decision Process, захищаючи автономну систему від атак перехоплення трафіку (*BGP Hijacking*).

Для перевірки дійсності сертифікатів ROA BGP-демони використовують протокол RPKI-to-Router (RTR, RFC 6810 / RFC 8210), отримуючи оновлені кеші криптографічних записів від локальних валідаторів (Routinator, OctoRPKI, Fort). Це дозволяє виконувати фільтрацію префіксів без затримок у реальному часі безпосередньо в оперативній пам'яті маршрутизатора.

### 7.2. Захист сесій через GTSM (Generalized TTL Security Mechanism, RFC 5082)

Для прямих eBGP-сесій зловмисники можуть генерувати підроблені TCP-пакети з віддалених хостів інтернету. Замість класичного `TTL = 1` механізм GTSM налаштовує відправника надсилати пакети з максимальним значенням `TTL = 255`, а приймач перевіряє:
```
TTL_incoming >= 255 - hop_count
```
Оскільки кожен проміжний маршрутизатор інтернету зменшує поле TTL щонайменше на 1, атакуючий пакет, надісланий через кілька вузлів, фізично не зможе досягти цільового роутера зі значенням `255`, що гарантує відкидання підроблених пакетів апаратними фільтрами мережевої карти без навантаження на процесор маршрутизатора.




