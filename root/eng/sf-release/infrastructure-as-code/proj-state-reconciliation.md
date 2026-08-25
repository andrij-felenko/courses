# ⚙️ Реалізація рушія узгодження стану та графа залежностей

У цій вставці реалізовано повністю функціональну спрощену модель декларативного рушія інфраструктури як коду (Infrastructure as Code Engine). Модель розкриває внутрішній механізм роботи систем класу Terraform, OpenTofu, Pulumi та контролерів Kubernetes: від побудови орієнтованого ациклічного графа залежностей (DAG) до генерації плану спекулятивних змін (Plan), тристоронньої звірки (3-way merge) та атомарної актуалізації стану (Apply).

## Архітектурні компоненти декларативного рушія

Декларативний рушій не виконує накази послідовно зверху вниз, як звичайний командний інтерпретатор. Його завдання — знайти мінімальну множину мутацій, необхідну для переведення поточної хмарної реальності у стан, що строго відповідає коду. Процес розбивається на п'ять взаємопов'язаних етапів:

1. **Модель ресурсів та схема файлу стану (State Representation):** кожен інфраструктурний ресурс ідентифікується уніфікованим іменем ресурсу (Uniform Resource Name, URN) у форматі `тип.ім'я` (наприклад, `aws_vpc.primary`). Файл стану (`StateStore`) виступає єдиним авторитетним джерелом правди про те, які саме фізичні об'єкти хмари (ідентифікатори екземплярів `i-0a1b2c`, ідентифікатори підмереж `subnet-987`, ARN баз даних) належать цьому коду. Без файлу стану рушій не зміг би відрізнити ресурс, створений ним минулого разу, від чужого ресурсу в тому самому обліковому записі хмари.
2. **Побудова та топологічне сортування графа (DAG & Topological Sort):** рушій аналізує конфігурацію і витягує зв'язки двох типів:
   - **Неявні залежності (Implicit Dependencies):** коли один ресурс посилається на вихідний атрибут іншого (наприклад, параметр `subnet.vpc_id = vpc.id`).
   - **Явні залежності (Explicit Dependencies):** директиви примусового порядку (наприклад, `depends_on = [aws_iam_role_policy.cluster]`), коли прямого обміну даними немає, але порядок ініціалізації критичний.
   На основі цих зв'язків будується орієнтований ациклічний граф (Directed Acyclic Graph, DAG), де вершини — це ресурси, а ребра — відношення залежності. За допомогою алгоритму Кана граф сортується у топологічний порядок створення та оновлення.
3. **Тристороннє обчислення дифу (3-Way Merge & Plan Engine):** для формування плану дій рушій порівнює три сутності:
   - **Desired State (Бажаний стан):** що написано в поточному Git-коміті.
   - **Prior State (Збережений стан):** зліпок ресурсів після попереднього успішного запуску.
   - **Current State (Актуальна реальність):** поточний стан хмари, отриманий прямими запитами читання до API провайдера (фаза Refresh).
   Порівняння дозволяє виявити не лише планові зміни в коді, а й зовнішній дрейф конфігурації (наприклад, якщо хтось видалив базу даних або змінив правила фаєрвола вручну через веб-консоль).
4. **Розподілене блокування стану (Distributed State Lock):** оскільки файл стану є критичною точкою синхронізації, будь-яка мутація вимагає попереднього захоплення розподіленого локу (наприклад, запис мітки блокування в DynamoDB або etcd). Це унеможливлює стан гонитви (Race Condition), коли два паралельні CI/CD пайплайни одночасно намагаються змінювати спільні ресурси.
5. **Виконання плану (Apply) та обробка збоїв:** мутації застосовуються за рівнями топологічного графа. Ресурси одного рівня, які не залежать один від одного, можуть створюватися паралельно. Для видалення застарілих ресурсів (`DESTROY`) граф інвертується: дочірні ресурси завжди знищуються раніше за батьківські, щоб запобігти помилкам типу `DependencyViolation`.

## Реалізація рушія

:::tabs
```py
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
```
```ts
export enum ActionType {
  NOOP = "NOOP",
  CREATE = "CREATE",
  UPDATE = "UPDATE",
  REPLACE = "REPLACE",
  DESTROY = "DESTROY"
}

export interface ResourceConfig {
  rType: string;
  name: string;
  props: Record<string, any>;
  deps?: string[];
  immutableKeys?: string[];
}

export class Resource {
  public readonly urn: string;
  constructor(public readonly config: ResourceConfig) {
    this.urn = `${config.rType}.${config.name}`;
  }
}

export interface ResourceState {
  urn: string;
  physicalId: string;
  props: Record<string, any>;
}

export interface PlanItem {
  urn: string;
  action: ActionType;
  oldProps?: Record<string, any>;
  newProps?: Record<string, any>;
  physicalId?: string;
}

export class MockCloudProvider {
  private cloudResources = new Map<string, Record<string, any>>();
  private idCounter = 1000;

  async create(rType: string, props: Record<string, any>): Promise<string> {
    this.idCounter += 1;
    const physId = `${rType.toLowerCase()}-${this.idCounter}`;
    this.cloudResources.set(physId, JSON.parse(JSON.stringify(props)));
    return physId;
  }

  async update(physId: string, props: Record<string, any>): Promise<void> {
    if (!this.cloudResources.has(physId)) {
      throw new Error(`Хмарний ресурс ${physId} не знайдено`);
    }
    const current = this.cloudResources.get(physId)!;
    this.cloudResources.set(physId, { ...current, ...props });
  }

  async delete(physId: string): Promise<void> {
    this.cloudResources.delete(physId);
  }

  async read(physId: string): Promise<Record<string, any> | null> {
    return this.cloudResources.get(physId) ? { ...this.cloudResources.get(physId)! } : null;
  }
}

export class StateStore {
  private resources = new Map<string, ResourceState>();
  private locked = false;

  acquireLock(): boolean {
    if (this.locked) return false;
    this.locked = true;
    return true;
  }

  releaseLock(): void {
    this.locked = false;
  }

  get(urn: string): ResourceState | undefined {
    return this.resources.get(urn);
  }

  set(state: ResourceState): void {
    this.resources.set(state.urn, state);
  }

  remove(urn: string): void {
    this.resources.delete(urn);
  }

  getAll(): ResourceState[] {
    return Array.from(this.resources.values());
  }
}

export class IaCEngine {
  constructor(private provider: MockCloudProvider, private state: StateStore) {}

  buildDagAndSort(desired: Map<string, Resource>): string[] {
    const inDegree = new Map<string, number>();
    const adj = new Map<string, string[]>();

    for (const urn of desired.keys()) {
      inDegree.set(urn, 0);
      adj.set(urn, []);
    }

    for (const [urn, res] of desired.entries()) {
      const deps = res.config.deps || [];
      for (const dep of deps) {
        if (!desired.has(dep)) {
          throw new Error(`Ресурс ${urn} посилається на невідому залежність ${dep}`);
        }
        adj.get(dep)!.push(urn);
        inDegree.set(urn, (inDegree.get(urn) || 0) + 1);
      }
    }

    const queue: string[] = [];
    for (const [urn, deg] of inDegree.entries()) {
      if (deg === 0) queue.push(urn);
    }

    const order: string[] = [];
    while (queue.length > 0) {
      const node = queue.shift()!;
      order.push(node);
      for (const neighbor of adj.get(node)!) {
        const nextDeg = inDegree.get(neighbor)! - 1;
        inDegree.set(neighbor, nextDeg);
        if (nextDeg === 0) queue.push(neighbor);
      }
    }

    if (order.length !== desired.size) {
      throw new Error("Виявлено циклічну залежність в графі ресурсів!");
    }

    return order;
  }

  async computePlan(desired: Map<string, Resource>): Promise<PlanItem[]> {
    const plan: PlanItem[] = [];
    const visited = new Set<string>();

    for (const [urn, res] of desired.entries()) {
      visited.add(urn);
      const currState = this.state.get(urn);

      if (!currState) {
        plan.push({ urn, action: ActionType.CREATE, newProps: res.config.props });
      } else {
        const realProps = await this.provider.read(currState.physicalId);
        if (!realProps) {
          plan.push({ urn, action: ActionType.CREATE, newProps: res.config.props });
          continue;
        }

        const isSame = JSON.stringify(realProps) === JSON.stringify(res.config.props);
        if (isSame) {
          plan.push({ urn, action: ActionType.NOOP, oldProps: realProps, newProps: res.config.props, physicalId: currState.physicalId });
        } else {
          const immKeys = res.config.immutableKeys || [];
          const needsReplace = immKeys.some((k) => realProps[k] !== res.config.props[k]);
          const action = needsReplace ? ActionType.REPLACE : ActionType.UPDATE;
          plan.push({ urn, action, oldProps: realProps, newProps: res.config.props, physicalId: currState.physicalId });
        }
      }
    }

    for (const st of this.state.getAll()) {
      if (!visited.has(st.urn)) {
        plan.push({ urn: st.urn, action: ActionType.DESTROY, oldProps: st.props, physicalId: st.physicalId });
      }
    }

    return plan;
  }

  async apply(desired: Map<string, Resource>): Promise<void> {
    if (!this.state.acquireLock()) {
      throw new Error("Помилка: файл стану заблокований іншим процесом");
    }

    try {
      const order = this.buildDagAndSort(desired);
      const plan = await this.computePlan(desired);
      const planMap = new Map(plan.map((p) => [p.urn, p]));

      for (const item of plan) {
        if (item.action === ActionType.DESTROY && item.physicalId) {
          await this.provider.delete(item.physicalId);
          this.state.remove(item.urn);
        }
      }

      for (const urn of order) {
        const item = planMap.get(urn);
        if (!item) continue;

        if (item.action === ActionType.CREATE) {
          const res = desired.get(urn)!;
          const physId = await this.provider.create(res.config.rType, item.newProps!);
          this.state.set({ urn, physicalId: physId, props: item.newProps! });
        } else if (item.action === ActionType.UPDATE && item.physicalId) {
          await this.provider.update(item.physicalId, item.newProps!);
          this.state.set({ urn, physicalId: item.physicalId, props: item.newProps! });
        } else if (item.action === ActionType.REPLACE && item.physicalId) {
          const res = desired.get(urn)!;
          await this.provider.delete(item.physicalId);
          const newPhysId = await this.provider.create(res.config.rType, item.newProps!);
          this.state.set({ urn, physicalId: newPhysId, props: item.newProps! });
        }
      }
    } finally {
      this.state.releaseLock();
    }
  }
}
```
```go
package main

import (
	"errors"
	"fmt"
	"sync"
)

type ActionType string

const (
	ActionNoop    ActionType = "NOOP"
	ActionCreate  ActionType = "CREATE"
	ActionUpdate  ActionType = "UPDATE"
	ActionReplace ActionType = "REPLACE"
	ActionDestroy ActionType = "DESTROY"
)

type Resource struct {
	Type          string
	Name          string
	Props         map[string]string
	Deps          []string
	ImmutableKeys []string
}

func (r Resource) URN() string {
	return fmt.Sprintf("%s.%s", r.Type, r.Name)
}

type ResourceState struct {
	URN        string
	PhysicalID string
	Props      map[string]string
}

type PlanItem struct {
	URN        string
	Action     ActionType
	OldProps   map[string]string
	NewProps   map[string]string
	PhysicalID string
}

type MockCloudProvider struct {
	mu        sync.Mutex
	resources map[string]map[string]string
	counter   int
}

func NewMockCloudProvider() *MockCloudProvider {
	return &MockCloudProvider{
		resources: make(map[string]map[string]string),
		counter:   1000,
	}
}

func (p *MockCloudProvider) Create(rType string, props map[string]string) string {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.counter++
	id := fmt.Sprintf("%s-%d", rType, p.counter)
	cp := make(map[string]string)
	for k, v := range props {
		cp[k] = v
	}
	p.resources[id] = cp
	return id
}

func (p *MockCloudProvider) Update(id string, props map[string]string) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if _, ok := p.resources[id]; !ok {
		return errors.New("ресурс не знайдено")
	}
	for k, v := range props {
		p.resources[id][k] = v
	}
	return nil
}

func (p *MockCloudProvider) Delete(id string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	delete(p.resources, id)
}

func (p *MockCloudProvider) Read(id string) (map[string]string, bool) {
	p.mu.Lock()
	defer p.mu.Unlock()
	val, ok := p.resources[id]
	if !ok {
		return nil, false
	}
	cp := make(map[string]string)
	for k, v := range val {
		cp[k] = v
	}
	return cp, true
}

type StateStore struct {
	mu        sync.Mutex
	locked    bool
	resources map[string]ResourceState
}

func NewStateStore() *StateStore {
	return &StateStore{
		resources: make(map[string]ResourceState),
	}
}

func (s *StateStore) AcquireLock() bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.locked {
		return false
	}
	s.locked = true
	return true
}

func (s *StateStore) ReleaseLock() {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.locked = false
}

type IaCEngine struct {
	provider *MockCloudProvider
	state    *StateStore
}

func NewIaCEngine(provider *MockCloudProvider, state *StateStore) *IaCEngine {
	return &IaCEngine{provider: provider, state: state}
}

func (e *IaCEngine) BuildDAGAndSort(desired map[string]Resource) ([]string, error) {
	inDegree := make(map[string]int)
	adj := make(map[string][]string)

	for urn := range desired {
		inDegree[urn] = 0
		adj[urn] = []string{}
	}

	for urn, res := range desired {
		for _, dep := range res.Deps {
			if _, ok := desired[dep]; !ok {
				return nil, fmt.Errorf("невідома залежність %s у %s", dep, urn)
			}
			adj[dep] = append(adj[dep], urn)
			inDegree[urn]++
		}
	}

	queue := make([]string, 0)
	for urn, deg := range inDegree {
		if deg == 0 {
			queue = append(queue, urn)
		}
	}

	order := make([]string, 0, len(desired))
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		order = append(order, node)

		for _, neighbor := range adj[node] {
			inDegree[neighbor]--
			if inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}

	if len(order) != len(desired) {
		return nil, errors.New("виявлено циклічну залежність в графі")
	}

	return order, nil
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <optional>
#include <memory>
#include <stdexcept>

enum class ActionType {
    NOOP,
    CREATE,
    UPDATE,
    REPLACE,
    DESTROY
};

struct Resource {
    std::string type;
    std::string name;
    std::unordered_map<std::string, std::string> props;
    std::vector<std::string> deps;
    std::unordered_set<std::string> immutable_keys;

    [[nodiscard]] std::string urn() const {
        return type + "." + name;
    }
};

struct ResourceState {
    std::string urn;
    std::string physical_id;
    std::unordered_map<std::string, std::string> props;
};

struct PlanItem {
    std::string urn;
    ActionType action;
    std::unordered_map<std::string, std::string> old_props;
    std::unordered_map<std::string, std::string> new_props;
    std::string physical_id;
};

class MockCloudProvider {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, std::string>> resources_;
    int id_counter_{1000};

public:
    std::string create_resource(const std::string& type, const std::unordered_map<std::string, std::string>& props) {
        id_counter_++;
        std::string id = type + "-" + std::to_string(id_counter_);
        resources_[id] = props;
        return id;
    }

    void update_resource(const std::string& id, const std::unordered_map<std::string, std::string>& props) {
        auto it = resources_.find(id);
        if (it == resources_.end()) {
            throw std::runtime_error("Хмарний ресурс " + id + " не знайдено");
        }
        for (const auto& [k, v] : props) {
            it->second[k] = v;
        }
    }

    void delete_resource(const std::string& id) {
        resources_.erase(id);
    }

    std::optional<std::unordered_map<std::string, std::string>> read_resource(const std::string& id) const {
        auto it = resources_.find(id);
        if (it != resources_.end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

class StateStore {
private:
    std::unordered_map<std::string, ResourceState> resources_;
    bool locked_{false};

public:
    bool acquire_lock() {
        if (locked_) return false;
        locked_ = true;
        return true;
    }

    void release_lock() {
        locked_ = false;
    }

    std::optional<ResourceState> get(const std::string& urn) const {
        auto it = resources_.find(urn);
        if (it != resources_.end()) return it->second;
        return std::nullopt;
    }

    void set(const ResourceState& state) {
        resources_[state.urn] = state;
    }

    void remove(const std::string& urn) {
        resources_.erase(urn);
    }

    const std::unordered_map<std::string, ResourceState>& all() const {
        return resources_;
    }
};

class IaCEngine {
private:
    std::shared_ptr<MockCloudProvider> provider_;
    std::shared_ptr<StateStore> state_;

public:
    IaCEngine(std::shared_ptr<MockCloudProvider> provider, std::shared_ptr<StateStore> state)
        : provider_(std::move(provider)), state_(std::move(state)) {}

    std::vector<std::string> build_dag_and_sort(const std::unordered_map<std::string, Resource>& desired) {
        std::unordered_map<std::string, int> in_degree;
        std::unordered_map<std::string, std::vector<std::string>> adj;

        for (const auto& [urn, _] : desired) {
            in_degree[urn] = 0;
            adj[urn] = {};
        }

        for (const auto& [urn, res] : desired) {
            for (const auto& dep : res.deps) {
                if (desired.find(dep) == desired.end()) {
                    throw std::runtime_error("Невідома залежність " + dep + " у " + urn);
                }
                adj[dep].push_back(urn);
                in_degree[urn]++;
            }
        }

        std::queue<std::string> queue;
        for (const auto& [urn, deg] : in_degree) {
            if (deg == 0) queue.push(urn);
        }

        std::vector<std::string> order;
        while (!queue.empty()) {
            std::string node = queue.front();
            queue.pop();
            order.push_back(node);

            for (const auto& neighbor : adj[node]) {
                in_degree[neighbor]--;
                if (in_degree[neighbor] == 0) {
                    queue.push(neighbor);
                }
            }
        }

        if (order.size() != desired.size()) {
            throw std::runtime_error("Виявлено циклічну залежність в графі (Circular Dependency)!");
        }

        return order;
    }
};
```
:::

## Покроковий розбір наскрізного сценарію розгортання

Розглянемо практичний приклад роботи рушія на трирівневому стеку веб-застосунку:
- Базовий мережевий рівень: Віртуальна приватна хмара `aws_vpc.primary` (`cidr = "10.0.0.0/16"`).
- Рівень підмереж: Підмережа бази даних `aws_subnet.db` (`cidr = "10.0.1.0/24"`, залежить від `aws_vpc.primary`) та публічна веб-підмережа `aws_subnet.web` (`cidr = "10.0.2.0/24"`, залежить від `aws_vpc.primary`).
- Рівень сховища та обчислень: Кластер бази даних `aws_rds.main` (залежить від `aws_subnet.db`) та сервер додатку `aws_instance.app` (залежить від `aws_subnet.web` та `aws_rds.main`).

### 1. Формування матриці суміжності та обчислення рівнів паралелізму
Рушій зчитує граф і будує таблицю вхідних степенів:
- `aws_vpc.primary`: `in_degree = 0` (Рівень 0);
- `aws_subnet.db`: `in_degree = 1` (залежить від `aws_vpc.primary`);
- `aws_subnet.web`: `in_degree = 1` (залежить від `aws_vpc.primary`);
- `aws_rds.main`: `in_degree = 1` (залежить від `aws_subnet.db`);
- `aws_instance.app`: `in_degree = 2` (залежить від `aws_subnet.web` та `aws_rds.main`).

На старті черга алгоритму Кана отримує лише `aws_vpc.primary`. Після його обробки вхідні степені обох підмереж стають `0`. Рушій додає `aws_subnet.db` та `aws_subnet.web` у чергу паралельного виконання (Рівень 1). Їхнє створення виконується одночасно двома незалежними потоками виконання. Коли `aws_subnet.db` завершує створення, розблоковується `aws_rds.main` (Рівень 2). Лише після того, як база даних та публічна підмережа перейшли у стан готовності, створюється `aws_instance.app` (Рівень 3).

### 2. Структура файлу стану після першого запуску
Після завершення початкового розгортання сховище `StateStore` зберігає наступний детермінований знімок:

```json
{
  "version": 4,
  "serial": 1,
  "resources": {
    "aws_vpc.primary": {
      "physical_id": "vpc-1001",
      "props": { "cidr": "10.0.0.0/16" }
    },
    "aws_subnet.db": {
      "physical_id": "subnet-1002",
      "props": { "cidr": "10.0.1.0/24", "vpc_id": "vpc-1001" }
    },
    "aws_subnet.web": {
      "physical_id": "subnet-1003",
      "props": { "cidr": "10.0.2.0/24", "vpc_id": "vpc-1001" }
    },
    "aws_rds.main": {
      "physical_id": "rds-1004",
      "props": { "engine": "postgres", "subnet_id": "subnet-1002" }
    },
    "aws_instance.app": {
      "physical_id": "instance-1005",
      "props": { "type": "t3.medium", "subnet_id": "subnet-1003", "db_endpoint": "rds-1004" }
    }
  }
}
```

## Матриця рішень диференціального рушія (Diff Decision Matrix)

Тристороннє зіставлення станів (3-way merge) охоплює всі можливі комбінації наявності та властивостей ресурсу. Нижче наведено формальну логіку ухвалення рішень рушієм:

| Desired (Код) | Prior (Файл стану) | Live (Хмарний API) | Рівність властивостей | Дія рушія (Action) | Пояснення сценарію |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Присутній | Відсутній | Відсутній | — | `CREATE` | Новий ресурс, щойно доданий розробником у конфігурацію |
| Присутній | Відсутній | Присутній | — | **Помилка / Collision** | Ресурс із таким ім'ям уже існує в хмарі поза контролем цього коду |
| Присутній | Присутній | Відсутній | — | `CREATE` (Drift Remediation) | Ресурс було випадково видалено вручну в веб-консолі хмари |
| Присутній | Присутній | Присутній | Desired == Live | `NOOP` | Ресурс повністю узгоджений, жодних дій не потрібно |
| Присутній | Присутній | Присутній | Desired != Live (Mutable) | `UPDATE` | Зміна мутабельних параметрів (наприклад, зміна тегів або розміру пам'яті) |
| Присутній | Присутній | Присутній | Desired != Live (Immutable) | `REPLACE` | Зміна імутабельних параметрів (наприклад, типу ОС чи зони доступності) |
| Відсутній | Присутній | Присутній | — | `DESTROY` | Ресурс видалено з коду Git, рушій зобов'язаний видалити його з хмари |
| Відсутній | Присутній | Відсутній | — | `PURGE_STATE` | Ресурс видалено і з коду, і з хмари — запис просто вилучається зі стану |

Ця таблиця наочно демонструє математичну повноту алгоритму: кожна комбінація вхідних даних має детермінований і безпечний вихід.

## Граф безпечного видалення ресурсів (Destruction Graph)

Одне з найнебезпечніших місць в експлуатації інфраструктури — видалення застарілих ресурсів. Якщо видаляти ресурси в прямому топологічному порядку (наприклад, спробувати спочатку видалити `aws_vpc.primary`), хмарний API негайно поверне фатальну помилку `DependencyViolation: The vpc has active subnets and cannot be deleted`.

Щоб коректно видалити інфраструктуру, рушій виконує **інверсію графа залежностей**:
1. Будується транзитивний граф знищення, де всі ребра орієнтовані у зворотний бік: якщо `A` було передумовою для `B`, то в графі видалення `B` стає передумовою для `A` (`B → A`).
2. Ресурс `aws_instance.app` видаляється першим, оскільки він стоїть на вершині піраміди залежностей і від нього ніхто не залежить.
3. Після зупинки сервера паралельно знищуються `aws_rds.main` та `aws_subnet.web`.
4. Після звільнення бази даних видаляється `aws_subnet.db`.
5. Лише коли в мережі не залишилося жодного підключеного мережевого інтерфейсу (ENI), безпечно знищується сама віртуальна мережа `aws_vpc.primary`.

## Імпорт наявних ресурсів та адопція хмари

Коли команда починає впроваджувати інфраструктуру як код у компанії з багаторічною історією, в хмарі вже працюють сотні віртуальних машин, баз даних і мереж, створених вручну або застарілими скриптами. Повне знищення цієї інфраструктури заради створення заново через код є неприпустимим через ризик простою бізнесу.

Для вирішення цієї проблеми рушій надає механізм **імпорту ресурсів (Resource Adoption/Import)**:
1. Інженер пише в коді нове оголошення ресурсу, наприклад `resource "aws_vpc" "legacy" { ... }`.
2. Виконується команда прив'язки: рушій отримує фізичний ідентифікатор хмарного об'єкта (наприклад, `vpc-0987654321`) та логічне ім'я в коді `aws_vpc.legacy`.
3. Рушій викликає метод `provider.read("vpc-0987654321")`, зчитує всі реальні параметри мережі з хмари та формує новий запис у файлі стану, **не виконуючи виклик `CREATE`**.
4. Під час наступного запуску `plan` рушій порівнює код із щойно імпортованим станом. Якщо параметри в коді трохи відрізняються від конфігурації живої машини, рушій пропонує план точкового вирівнювання (`UPDATE`), плавно беручи існуючу інфраструктуру під повний версійний контроль без жодної секунди простою.

## Оптимізація паралелізму та редукування транзитивних зв'язків

У великих корпоративних проєктах граф інфраструктури може містити понад 2 000 вершин і десятки тисяч ребер. Якщо граф містить транзитивні ребра (наприклад, пряме посилання `A → C` при одночасній наявності ланцюжка `A → B → C`), це призводить до надлишкових перевірок і сповільнює розрахунок розкладу виконання.

Перед сортуванням рушій виконує **транзитивне редукування (Transitive Reduction)** графа DAG:
- Знаходиться мінімальний граф, який має таку саму транзитивну досяжність, як і вихідний, але містить мінімальну кількість ребер.
- Усуваються всі прямі ребра, які дублюються непрямими шляхами більшої довжини.
- Отриманий оптимізований граф розбивається на незалежні шари паралельного виконання (Concurreny Layers). Якщо на рівні доступно 15 незалежних ресурсів, рушій виділяє пул воркерів (Worker Pool) і надсилає до хмарного провайдера 15 одночасних неблокуючих HTTP-запитів, прискорюючи розгортання в 10–12 разів у порівнянні з послідовним виконанням.

## Обробка складних крайових випадків у розподіленому середовищі

### Виявлення взаємних циклічних блокувань (Deadlock Cycles)
Взаємні посилання між ресурсами — типова помилка під час ручного конструювання інфраструктури. Наприклад, балансувальник навантаження `aws_alb` вимагає вказати групу безпеки `sg_alb`, а група безпеки бекенд-серверів `sg_app` дозволяє вхідний трафік лише від `sg_alb`. Якщо розробник спробує передати ідентифікатор `sg_app` у правила `sg_alb`, виникає циклічна залежність.

Завдяки алгоритму Кана в нашій реалізації черга вершин із нульовим вхідним степенем виявиться порожньою на певному кроці, і `len(order)` складе менше загальної кількості ресурсів. Рушій не робить жодного виклику до хмари й миттєво повертає зрозумілу діагностику помилки. Вирішенням такої проблеми на практиці є винесення правил зв'язку в окремі атомарні ресурси (наприклад, `aws_security_group_rule`), які створюються після ініціалізації обох груп безпеки.

### Атомарність оновлення файлу стану проти аварій мережі
Якщо процес `apply` примусово переривається користувачем (сигнал `SIGINT` / комбінація клавіш `Ctrl+C`) або вбивається агентом контейнеризації через вичерпання ліміту пам'яті (OOM-killer), рушій повинен захистити файл стану:
- Стан записується не в пам'ять, а через створення тимчасового файлу з подальшим атомарним системним викликом перейменування (`rename()` у POSIX або `MoveFileEx()` у Windows). Це гарантує, що файл стану ні за яких обставин не виявиться обрізаним на середині JSON-структури.
- Кожна окрема дія з конкретним фізичним ресурсом фіксується у файлі стану негайно після отримання коду відповіді `200 OK` від API хмари. Якщо з 10 нових серверів створено 4, а на 5-му стався розрив з'єднання, у файлі стану залишаться збереженими саме 4 ресурси. Наступний запуск автоматично продовжить роботу з 5-го сервера.

### Логіка заміни з мінімізацією простою (Create-Before-Destroy)
За замовчуванням дія `REPLACE` спочатку знищує старий екземпляр, а потім створює новий (`Destroy-then-Create`). Для баз даних чи веб-серверів це призводить до вимушеного простою (Downtime) довжиною в кілька хвилин.

Розширені рушії підтримують інвертований життєвий цикл **Create-Before-Destroy**:
1. Рушій створює новий ресурс із тимчасовим унікальним фізичним ідентифікатором поруч зі старим працюючим ресурсом.
2. Оновлюються точки маршрутизації (DNS-записи, таргети балансувальника).
3. Після перевірки працездатності (Health Check) старий екземпляр безболісно видаляється.

### Механізм мітки пошкодження (Resource Tainting)
У реальному середовищі процес створення ресурсу складається з виділення фізичної сутності в хмарі та її наступної ініціалізації (наприклад, виконання скрипта `user_data` для встановлення драйверів на віртуальну машину або запуск міграцій бази даних). Якщо віртуальна машина успішно створилася, але скрипт ініціалізації впав із ненульовим кодом завершення, ресурс опиняється в напівробочому стані.

Рушій фіксує такий стан, записуючи у файл стану спеціальний прапорець `"tainted": true`. Під час наступного виконання команди `plan` або `apply` рушій розцінює пошкоджений ресурс як непридатний до експлуатації і автоматично генерує план його примусового перестворення (`REPLACE`), забезпечуючи 100% чистоту та передбачуваність інфраструктурного середовища.

### Таргетування та ізоляція підграфів (-target)
У критичних виробничих інцидентах інженерам іноді необхідно терміново змінити один конкретний параметр (наприклад, відкрити доступ у групі безпеки або змінити розмір одного диска), не ризикуючи випадково зачепити решту 500 ресурсів великого монолітного стеку.

Для цього рушій підтримує операцію **таргетування (Targeted Execution)**:
1. Користувач задає цільовий ресурс: `-target=aws_security_group.emergency_access`.
2. Рушій виконує пошук у глибину (DFS) назад від цільового вузла, обчислюючи **замикання предків (Ancestors Closure)** — усі ресурси, від яких строго залежить ця група безпеки.
3. Усі непов'язані ресурси відсікаються з графа виконання. Рушій виконує `plan` та `apply` виключно для ізольованого підграфа.
4. *Попередження щодо безпеки:* тривале використання таргетування призводить до накопичення прихованого дрейфу у відсічених гілках графа, тому після ліквідації аварії завжди потрібен повний глобальний прогін без прапорця `-target`.

### Конвертне шифрування та маскування секретів (Envelope Encryption & Masking)
Оскільки файл стану зберігає повну копію конфігурації хмари, він неминуче містить конфіденційні дані: паролі до баз даних, приватні TLS-ключі, токени доступу сторонніх API та рядки з'єднання. Зберігання файлу стану у відкритому JSON є критичною вразливістю.

Сучасні рушії реалізують двоконтурний захист:
1. **Клієнтське конвертне шифрування (Client-side Envelope Encryption):** перед записом на віддалений бекенд (S3/GCS) рушій локально в пам'яті генерує випадковий 256-бітний симетричний ключ даних (Data Encryption Key, DEK). Файл стану шифрується алгоритмом AES-256-GCM. Потім відкритий ключ DEK надсилається в апаратний модуль безпеки (AWS KMS / HashiCorp Vault), шифрується асиметричним майстер-ключем (Key Encryption Key, KEK) і прикріплюється до зашифрованого шифротексту. Сам відкритий DEK негайно затирається в оперативній пам'яті.
2. **Динамічне поширення мітки чутливості (Taint Analysis / Sensitive Masking):** якщо будь-який атрибут ресурсу (наприклад, вихідний пароль `random_password.db.result`) позначено як `sensitive`, рушій відстежує всі зв'язки в графі DAG і автоматично позначає всі похідні атрибути інших ресурсів як чутливі. Під час виведення плану в термінал або веб-інтерфейс CI/CD рушій примусово замінює значення на `(sensitive value)`, унеможливлюючи витік паролів у логи збірки.

### Дзеркалювання стану та детекція фантомних ресурсів (Ghost Resource Purging)
У розподілених хмарах трапляються ситуації, коли запит на створення ресурсу отримав від API статус тайм-ауту (`504 Gateway Timeout`), але на стороні хмари асинхронний бекенд насправді завершив ініціалізацію машини. Якщо рушій не зафіксував цей факт у файлі стану через обрив сокета, у хмарі виникає некерований «ресурс-фантом» (Ghost Resource).

Для боротьби з цим явищем розширені рушії використовують **детерміновані клієнтські токени запитів (Idempotency Request Tokens)**:
- Кожен виклик `CREATE` передає в заголовку унікальний хеш `ClientRequestToken = SHA256(URN + ConfigProps)`.
- Якщо повторний запуск `apply` викликає `CREATE` з тим самим токеном, хмарний API повертає ідентифікатор уже існуючого ресурсу замість створення дубліката.
- Рушій звіряє повернутий фізичний ID, вносить його у файл стану та відновлює повну узгодженість без фінансових перевитрат на дубльовані машини.

### Економіка опитування та ліміти хмарних API (Rate Limiting & Exponential Backoff)
Масштабні інфраструктури, що налічують тисячі ресурсів, створюють значне навантаження на API хмарного провайдера під час фази `Refresh`. Якщо рушій надішле 3 000 одночасних запитів `GET /v1/instances/*`, хмара увімкне захисні ліміти швидкості (Rate Limiting) і почне відкидати запити з кодом `429 Too Many Requests` (або `ThrottlingException` в AWS).

Щоб запобігти зупинці процесу розгортання, рушій узгодження стану реалізує адаптивний механізм **експоненційного відтермінування з випадковим джитером (Exponential Backoff with Full Jitter)**:

```
T_wait = random(0, min(T_max, T_base · 2^retry_count))
```

де `T_base = 100` мс, а `T_max = 20` секунд. Додавання випадкового розкиду (джитеру) розбиває щільні хвилі повторних запитів і рівномірно розподіляє навантаження на шлюз провайдера, забезпечуючи гарантоване завершення тристоронньої звірки навіть в умовах жорстких квот хмарної платформи.


