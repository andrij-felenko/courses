import json
from collections import deque, defaultdict
from enum import Enum
from typing import Dict, List, Set, Optional, Any


class ActionType(Enum):
    NOOP = "NOOP"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    REPLACE = "REPLACE"
    DESTROY = "DESTROY"


class Resource:
    def __init__(self, r_type: str, name: str, props: Dict[str, Any], deps: Optional[List[str]] = None, immutable_keys: Optional[Set[str]] = None):
        self.r_type = r_type
        self.name = name
        self.props = props
        self.deps = deps or []
        self.immutable_keys = immutable_keys or set()

    @property
    def urn(self) -> str:
        return f"{self.r_type}.{self.name}"


class ResourceState:
    def __init__(self, urn: str, physical_id: str, props: Dict[str, Any]):
        self.urn = urn
        self.physical_id = physical_id
        self.props = props

    def to_dict(self) -> Dict[str, Any]:
        return {"urn": self.urn, "physical_id": self.physical_id, "props": self.props}


class PlanItem:
    def __init__(self, urn: str, action: ActionType, old_props: Optional[Dict[str, Any]], new_props: Optional[Dict[str, Any]], physical_id: Optional[str] = None):
        self.urn = urn
        self.action = action
        self.old_props = old_props
        self.new_props = new_props
        self.physical_id = physical_id

    def __repr__(self) -> str:
        return f"[{self.action.value}] {self.urn} (ID: {self.physical_id or 'pending'})"


class MockCloudProvider:
    """Симулятор хмарного API (AWS/GCP/Azure)"""
    def __init__(self):
        self._cloud_resources: Dict[str, Dict[str, Any]] = {}
        self._id_counter = 1000

    def create(self, r_type: str, props: Dict[str, Any]) -> str:
        self._id_counter += 1
        phys_id = f"{r_type.lower()}-{self._id_counter}"
        self._cloud_resources[phys_id] = dict(props)
        return phys_id

    def update(self, phys_id: str, props: Dict[str, Any]) -> None:
        if phys_id not in self._cloud_resources:
            raise RuntimeError(f"Хмарний ресурс {phys_id} не знайдено для оновлення")
        self._cloud_resources[phys_id].update(props)

    def delete(self, phys_id: str) -> None:
        if phys_id in self._cloud_resources:
            del self._cloud_resources[phys_id]

    def read(self, phys_id: str) -> Optional[Dict[str, Any]]:
        return self._cloud_resources.get(phys_id)


class StateStore:
    """Сховище файлу стану з розподіленим блокуванням"""
    def __init__(self):
        self.resources: Dict[str, ResourceState] = {}
        self.locked = False

    def acquire_lock(self) -> bool:
        if self.locked:
            return False
        self.locked = True
        return True

    def release_lock(self) -> None:
        self.locked = False

    def get(self, urn: str) -> Optional[ResourceState]:
        return self.resources.get(urn)

    def set(self, state: ResourceState) -> None:
        self.resources[state.urn] = state

    def remove(self, urn: str) -> None:
        self.resources.pop(urn, None)


class IaCEngine:
    def __init__(self, provider: MockCloudProvider, state: StateStore):
        self.provider = provider
        self.state = state

    def build_dag_and_sort(self, desired: Dict[str, Resource]) -> List[str]:
        """Топологічне сортування за алгоритмом Кана з виявленням циклів"""
        in_degree = {urn: 0 for urn in desired}
        adj = defaultdict(list)

        for urn, res in desired.items():
            for dep in res.deps:
                if dep in desired:
                    adj[dep].append(urn)
                    in_degree[urn] += 1
                else:
                    raise ValueError(f"Ресурс {urn} посилається на невідому залежність {dep}")

        queue = deque([urn for urn, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(desired):
            raise ValueError("Виявлено циклічну залежність в графі ресурсів (Circular Dependency)!")

        return order

    def compute_plan(self, desired: Dict[str, Resource]) -> List[PlanItem]:
        plan: List[PlanItem] = []
        visited = set()

        # 1. Перевірка ресурсів, що описані в бажаному стані
        for urn, res in desired.items():
            visited.add(urn)
            current_state = self.state.get(urn)

            if not current_state:
                plan.append(PlanItem(urn, ActionType.CREATE, None, res.props))
            else:
                real_props = self.provider.read(current_state.physical_id)
                if real_props is None:
                    # Ресурс видалили руками в консолі (дрейф стану)
                    plan.append(PlanItem(urn, ActionType.CREATE, None, res.props))
                    continue

                if real_props == res.props:
                    plan.append(PlanItem(urn, ActionType.NOOP, real_props, res.props, current_state.physical_id))
                else:
                    # Перевірка, чи змінилися імутабельні ключі (потрібен Replace)
                    needs_replace = any(
                        res.props.get(k) != real_props.get(k)
                        for k in res.immutable_keys
                    )
                    action = ActionType.REPLACE if needs_replace else ActionType.UPDATE
                    plan.append(PlanItem(urn, action, real_props, res.props, current_state.physical_id))

        # 2. Перевірка ресурсів для видалення (є у стані, але видалені з коду)
        for urn, st in self.state.resources.items():
            if urn not in visited:
                plan.append(PlanItem(urn, ActionType.DESTROY, st.props, None, st.physical_id))

        return plan

    def apply(self, desired: Dict[str, Resource]) -> None:
        if not self.state.acquire_lock():
            raise RuntimeError("Не вдалося отримати блокування стану (State Lock is active). Інший процес уже виконує розгортання.")

        try:
            order = self.build_dag_and_sort(desired)
            plan = self.compute_plan(desired)
            plan_map = {item.urn: item for item in plan}

            print("--- ПОЧАТОК ВИКОНАННЯ ПЛАНУ (APPLY) ---")
            
            # Спочатку видаляємо застарілі ресурси (DESTROY)
            for urn, item in plan_map.items():
                if item.action == ActionType.DESTROY:
                    print(f"-> Знищення: {urn} ({item.physical_id})")
                    self.provider.delete(item.physical_id)
                    self.state.remove(urn)

            # Створення та оновлення за топологічним порядком
            for urn in order:
                item = plan_map.get(urn)
                if not item:
                    continue

                if item.action == ActionType.NOOP:
                    print(f"-> Без змін: {urn}")
                elif item.action == ActionType.CREATE:
                    print(f"-> Створення: {urn} з параметрами {item.new_props}")
                    phys_id = self.provider.create(desired[urn].r_type, item.new_props)
                    self.state.set(ResourceState(urn, phys_id, item.new_props))
                elif item.action == ActionType.UPDATE:
                    print(f"-> Оновлення на місці: {urn} ({item.physical_id})")
                    self.provider.update(item.physical_id, item.new_props)
                    self.state.set(ResourceState(urn, item.physical_id, item.new_props))
                elif item.action == ActionType.REPLACE:
                    print(f"-> Перестворення (Replace): {urn} ({item.physical_id})")
                    self.provider.delete(item.physical_id)
                    phys_id = self.provider.create(desired[urn].r_type, item.new_props)
                    self.state.set(ResourceState(urn, phys_id, item.new_props))

            print("--- ЗБІЖНІСТЬ ДОСЯГНУТА УСПІШНО ---")
        finally:
            self.state.releaseLock() if hasattr(self.state, 'releaseLock') else self.state.release_lock()
