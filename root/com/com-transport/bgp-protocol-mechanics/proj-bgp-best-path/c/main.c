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
