# device_twin_repository.py — Ідіоматичний Python-еквівалент шва для BFF
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class HomeState:
    def __init__(self, home_id: str, version_seq: int, state_data: Dict[str, Any]):
        self.home_id = home_id
        self.version_seq = version_seq
        self.state_data = state_data

class IDeviceTwinRepository(ABC):
    @abstractmethod
    def get_home_state(self, home_id: str) -> Optional[HomeState]:
        pass

    @abstractmethod
    def update_device_state(self, home_id: str, device_id: str, update_payload: Dict[str, Any], expected_version: int) -> bool:
        pass
