import time
from typing import List, Optional

class ReplicaNode:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.is_alive = True
        self.applied_lsn = 0
        self.lag_ms = 0

class LagAwareRouter:
    def __init__(self, primary_endpoint: str, replica_endpoints: List[str], max_lag_ms: int = 2000, max_fallback_rps: int = 500):
        self.primary_endpoint = primary_endpoint
        self.replicas = [ReplicaNode(ep) for ep in replica_endpoints]
        self.max_lag_ms = max_lag_ms
        self.max_fallback_rps = max_fallback_rps
        self._rr_counter = 0
        self._fallback_window_sec = 0
        self._fallback_counter = 0

    @staticmethod
    def parse_lsn(lsn_str: str) -> int:
        if not lsn_str or "/" not in lsn_str:
            return 0
        high_str, low_str = lsn_str.strip().split("/")
        return (int(high_str, 16) << 32) | int(low_str, 16)

    @staticmethod
    def format_lsn(lsn: int) -> str:
        high = lsn >> 32
        low = lsn & 0xFFFFFFFF
        return f"{high:X}/{low:X}"

    def is_read_query(self, sql: str) -> bool:
        clean = sql.strip().upper()
        if clean.startswith("SELECT"):
            if "FOR UPDATE" in clean or "FOR SHARE" in clean:
                return False
            return True
        return False

    def route_query(self, sql: str, required_lsn: Optional[int] = None) -> str:
        if not self.is_read_query(sql):
            return self.primary_endpoint

        # Фільтрація реплік за доступністю, лагом та LSN
        candidates = [
            rep for rep in self.replicas
            if rep.is_alive
            and rep.lag_ms <= self.max_lag_ms
            and (required_lsn is None or rep.applied_lsn >= required_lsn)
        ]

        if candidates:
            selected = candidates[self._rr_counter % len(candidates)]
            self._rr_counter += 1
            return selected.endpoint

        # Fallback на Primary
        now_sec = int(time.time())
        if now_sec != self._fallback_window_sec:
            self._fallback_window_sec = now_sec
            self._fallback_counter = 0

        self._fallback_counter += 1
        if self._fallback_counter <= self.max_fallback_rps:
            return self.primary_endpoint

        raise RuntimeError("Усі репліки відстають, а ліміт Fallback на Primary вичерпано!")

if __name__ == "__main__":
    router = LagAwareRouter(
        primary_endpoint="postgres-primary:5432",
        replica_endpoints=["postgres-replica-1:5432", "postgres-replica-2:5432"]
    )

    router.replicas[0].applied_lsn = router.parse_lsn("0/16B3C00")
    router.replicas[0].lag_ms = 12

    router.replicas[1].applied_lsn = router.parse_lsn("0/16B3800")
    router.replicas[1].lag_ms = 450

    session_token = router.parse_lsn("0/16B3A40")
    selected_node = router.route_query("SELECT email FROM accounts WHERE id = 10", required_lsn=session_token)
    print(f"Маршрутизовано на: {selected_node}")
