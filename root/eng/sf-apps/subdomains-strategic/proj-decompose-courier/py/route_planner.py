# routing/domain/route_planner.py — ПОРТ. Мова ядра, жодного OR-Tools.
from typing import Protocol
from dataclasses import dataclass

@dataclass
class VehicleSpec:
    id: str
    capacity_kg: float

@dataclass
class PlanRequest:
    shipments: list[Shipment]
    vehicles: list[VehicleSpec]

class RoutePlanner(Protocol):
    def plan(self, req: PlanRequest) -> list[Route]:
        ...                              # дай план НАШИМИ поняттями
