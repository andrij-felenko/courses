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
