import math
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Dict, Optional

class VehicleStatus(IntEnum):
    NOMINAL  = 0
    ADVISORY = 1
    WARNING  = 2
    CRITICAL = 3

@dataclass
class VehicleTelemetry:
    vehicle_id: int
    lat: float = 0.0
    lon: float = 0.0
    screen_x: float = 0.0
    screen_y: float = 0.0
    battery_pct: float = 100.0
    speed_mps: float = 0.0
    last_heartbeat_s: float = field(default_factory=time.time)
    status: VehicleStatus = VehicleStatus.NOMINAL
    active: bool = False

@dataclass
class ScreenCluster:
    cluster_id: int
    member_ids: List[int]
    center_x: float
    center_y: float
    avg_speed_mps: float
    worst_status: VehicleStatus

class FleetAggregator:
    CLUSTER_RADIUS_PX: float = 45.0

    def __init__(self, max_vehicles: int = 64):
        self.vehicles: Dict[int, VehicleTelemetry] = {}
        self.clusters: List[ScreenCluster] = []

    def update_vehicle(self, vehicle_id: int, lat: float, lon: float,
                       screen_x: float, screen_y: float,
                       battery_pct: float, speed_mps: float) -> None:
        now = time.time()
        v = self.vehicles.get(vehicle_id)
        if v is None:
            v = VehicleTelemetry(vehicle_id=vehicle_id)
            self.vehicles[vehicle_id] = v

        v.lat = lat
        v.lon = lon
        v.screen_x = screen_x
        v.screen_y = screen_y
        v.battery_pct = battery_pct
        v.speed_mps = speed_mps
        v.last_heartbeat_s = now
        v.active = True

        # Класифікація винятків
        silence = now - v.last_heartbeat_s
        if battery_pct < 15.0 or silence > 3.0:
            v.status = VehicleStatus.CRITICAL
        elif battery_pct < 30.0 or silence > 1.5:
            v.status = VehicleStatus.WARNING
        elif battery_pct < 45.0:
            v.status = VehicleStatus.ADVISORY
        else:
            v.status = VehicleStatus.NOMINAL

    def recalculate_clusters(self) -> List[ScreenCluster]:
        self.clusters.clear()
        assigned = set()
        active_list = [v for v in self.vehicles.values() if v.active]

        for i, vi in enumerate(active_list):
            if vi.vehicle_id in assigned:
                continue

            cluster_members = [vi.vehicle_id]
            assigned.add(vi.vehicle_id)
            sum_x, sum_y = vi.screen_x, vi.screen_y
            sum_spd = vi.speed_mps
            worst = vi.status

            for vj in active_list[i + 1:]:
                if vj.vehicle_id in assigned:
                    continue

                dist = math.hypot(vi.screen_x - vj.screen_x, vi.screen_y - vj.screen_y)
                if dist <= self.CLUSTER_RADIUS_PX:
                    assigned.add(vj.vehicle_id)
                    cluster_members.append(vj.vehicle_id)
                    sum_x += vj.screen_x
                    sum_y += vj.screen_y
                    sum_spd += vj.speed_mps
                    if vj.status > worst:
                        worst = vj.status

            count = len(cluster_members)
            self.clusters.append(ScreenCluster(
                cluster_id=len(self.clusters) + 1,
                member_ids=cluster_members,
                center_x=sum_x / count,
                center_y=sum_y / count,
                avg_speed_mps=sum_spd / count,
                worst_status=worst
            ))
        return self.clusters

    def calculate_workload_pct(self) -> float:
        active_uavs = sum(1 for v in self.vehicles.values() if v.active)
        anomalies = sum(1 for v in self.vehicles.values() if v.active and v.status >= VehicleStatus.WARNING)

        # Базове фонове навантаження рою + штраф за активні інциденти
        workload = (active_uavs * 1.5) + (anomalies * 25.0)
        return min(100.0, workload)
