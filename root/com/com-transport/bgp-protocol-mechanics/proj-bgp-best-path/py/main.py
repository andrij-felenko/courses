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
