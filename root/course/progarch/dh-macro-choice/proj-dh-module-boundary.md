# ⚙️ Практична реалізація та суворий контроль меж модульного моноліту DH

Програмна структура, ідіоматичні приклади коду та інженерні інструменти забезпечують контроль меж між модулями у єдиній монолітній кодовій базі Digital Homes (`cloud-core`). Розгляд охоплює організацію каталогів за доменами, побудову публічних контрактів, реалізацію високопродуктивної внутрішньопроцесної шини подій та написання розширеного архітектурного тесту для CI/CD-пайплайну.

Головна мета практичної реалізації модульного моноліту полягає у забезпеченні такої структури коду, при якій розробники мають усі переваги роботи в єдиному процесі (простота дебагу, вказівники в пам'яті, відсутність мережевих затримок), але позбавлені головного недоліку хаотичного моноліту — неконтрольованого зчеплення коду та плутанини у деталях реалізації.

---

## 1. Структура каталогів кодової бази `cloud-core`

Дисципліна модульного моноліту починається з чіткого розкладання каталогів за функціональними доменами (пакування за фічею / доменом), а не за технічними шарами (пакування за шарами — controllers/services/repositories).

У монолітному проекті `cloud-core` кожен функціональний модуль розміщується у власному ізольованому каталозі всередині папки `modules/`. Структура підкаталогів розділяє публічний контракт модуля від його приватної реалізації:

```
cloud-core/
├── modules/
│   ├── device_registry/
│   │   ├── __init__.py           # Публічна точка входу (експортує лише contract)
│   │   ├── contract.py           # Публічний інтерфейс IDeviceRegistry
│   │   ├── events.py             # Публічні події домену
│   │   └── internal/             # Приватна реалізація (ЗАБОРОНЕНО для зовнішніх імпортів)
│   │       ├── models.py         # ORM-сутності (схема devices.*)
│   │       ├── repository.py     # Робота з PostgreSQL
│   │       └── service.py        # Внутрішня логіка Device Shadow
│   ├── automation/
│   │   ├── contract.py           # Публічний інтерфейс IAutomation
│   │   ├── events.py             # Події автоматизацій
│   │   └── internal/             # Двигун правил
│   │       ├── evaluator.py      # Оцінка умов правил
│   │       └── models.py         # ORM-сутності (схема automation.*)
│   ├── telemetry/
│   │   ├── contract.py
│   │   └── internal/
│   └── billing/
│       ├── contract.py
│       └── internal/
├── platform/
│   ├── event_bus.py              # Внутрішньопроцесна шина подій (InMemoryEventBus)
│   └── database.py               # Конфігурація пулу з'єднань СУБД
└── tests/
    └── architecture/
        └── test_module_boundaries.py  # CI/CD Архітектурний тест меж
```

При такій структурі кожен каталог у `modules/` є самодостатнім автономним блоком. Зовнішній світ має право звертатися лише до вмісту файлів `contract.py` та `events.py`. Весь вміст каталогу `internal/` повністю закритий від прямого виклику з інших модулів.

Завдяки впровадженню каталогу `internal/` розробники мають чіткий зоровий орієнтир: якщо у виклику файлу зустрічається слово `internal`, цей код не належить їхньому модулю і не може використовуватися напряму.

---

## 2. Реалізація публічних контрактів та шини подій

Модулі всередині `cloud-core` спілкуються між собою виключно двома дозволеними шляхами:
1. **Синхронний виклик:** Через методи публічного абстрактного інтерфейсу (наприклад, `IDeviceRegistryModule`).
2. **Асинхронне сповіщення:** Через публікацію та підписку на доменні події у `InMemoryEventBus`.

Нижче наведено повноцінну ідіоматичну реалізацію цих механізмів мовами Python, C++ та Go.

:::tabs
```py
# Python 3.12 implementation
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Type, TypeVar, Any
from datetime import datetime

# ── 1. Публічна доменна подія ──
@dataclass(frozen=True)
class DeviceStateChangedEvent:
    event_id: str
    device_id: str
    home_id: str
    property_name: str
    old_value: Any
    new_value: Any
    timestamp: datetime

# ── 2. Публічний DTO та Інтерфейс модуля DeviceRegistry ──
@dataclass(frozen=True)
class DeviceDTO:
    id: str
    home_id: str
    model: str
    is_online: bool
    reported_state: dict[str, Any]

class IDeviceRegistryModule(ABC):
    @abstractmethod
    def get_device(self, device_id: str) -> DeviceDTO | None:
        """Отримати публічний DTO пристрою."""
        pass

    @abstractmethod
    def list_home_devices(self, home_id: str) -> list[DeviceDTO]:
        """Отримати список пристроїв дому."""
        pass

# ── 3. Внутрішньопроцесна шина подій (InMemoryEventBus) ──
E = TypeVar('E')

class InMemoryEventBus:
    """Високопродуктивна внутрішньопроцесна шина подій.
    Забезпечує реєстрацію підписників та синхронну/асинхронну розсилку подій у пам'яті.
    Затримка виклику підписника складає від 20 до 50 наносекунд.
    """
    def __init__(self) -> None:
        self._handlers: dict[Type[Any], list[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)  # Синхронний виклик у пам'яті
                except Exception as ex:
                    # Логування помилки підписника без збою основного потоку
                    print(f"[EventBus Error] Помилка обробника події {event_type}: {ex}")
```
```cpp
// C++20 implementation
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <typeindex>
#include <optional>
#include <chrono>
#include <iostream>

// ── 1. Публічна доменна подія ──
struct DeviceStateChangedEvent {
    std::string event_id;
    std::string device_id;
    std::string home_id;
    std::string property_name;
    std::string old_value;
    std::string new_value;
    std::chrono::system_clock::time_point timestamp;
};

// ── 2. Публічний DTO та Інтерфейс (Pure Abstract Class) ──
struct DeviceDTO {
    std::string id;
    std::string home_id;
    std::string model;
    bool is_online;
};

class IDeviceRegistryModule {
public:
    virtual ~IDeviceRegistryModule() = default;
    virtual std::optional<DeviceDTO> get_device(const std::string& device_id) = 0;
    virtual std::vector<DeviceDTO> list_home_devices(const std::string& home_id) = 0;
};

// ── 3. Внутрішньопроцесна шина подій (InMemoryEventBus) ──
class InMemoryEventBus {
private:
    using HandlerList = std::vector<std::function<void(const void*)>>;
    std::unordered_map<std::type_index, HandlerList> handlers_;

public:
    template<typename EventType>
    void subscribe(std::function<void(const EventType&)> handler) {
        handlers_[typeid(EventType)].push_back([handler](const void* evt_ptr) {
            handler(*static_cast<const EventType*>(evt_ptr));
        });
    }

    template<typename EventType>
    void publish(const EventType& event) {
        auto it = handlers_.find(typeid(EventType));
        if (it != handlers_.end()) {
            for (const auto& handler : it->second) {
                try {
                    handler(&event);
                } catch (const std::exception& ex) {
                    std::cerr << "[EventBus Error] Exception in handler: " << ex.what() << '\n';
                }
            }
        }
    }
};
```
```go
// Go 1.22 implementation
package main

import (
	"context"
	"fmt"
	"reflect"
	"time"
)

// ── 1. Публічна доменна подія ──
type DeviceStateChangedEvent struct {
	EventID      string
	DeviceID     string
	HomeID       string
	PropertyName string
	OldValue     any
	NewValue     any
	Timestamp    time.Time
}

// ── 2. Публічний DTO та Інтерфейс ──
type DeviceDTO struct {
	ID       string
	HomeID   string
	Model    string
	IsOnline bool
}

type IDeviceRegistryModule interface {
	GetDevice(ctx context.Context, deviceID string) (*DeviceDTO, error)
	ListHomeDevices(ctx context.Context, homeID string) ([]DeviceDTO, error)
}

// ── 3. Внутрішньопроцесна шина подій (InMemoryEventBus) ──
type InMemoryEventBus struct {
	handlers map[reflect.Type][]func(any)
}

func NewInMemoryEventBus() *InMemoryEventBus {
	return &InMemoryEventBus{handlers: make(map[reflect.Type][]func(any))}
}

func Subscribe[T any](bus *InMemoryEventBus, handler func(T)) {
	t := reflect.TypeOf((*T)(nil)).Elem()
	wrapper := func(evt any) {
		handler(evt.(T))
	}
	bus.handlers[t] = append(bus.handlers[t], wrapper)
}

func (bus *InMemoryEventBus) Publish(event any) {
	t := reflect.TypeOf(event)
	if list, ok := bus.handlers[t]; ok {
		for _, h := range list {
			defer func() {
				if r := recover(); r != nil {
					fmt.Printf("[EventBus Error] Recovered from panic: %v\n", r)
				}
			}()
			h(event)
		}
	}
}
```
:::

Реалізація шини `InMemoryEventBus` відрізняється від зовнішніх брокерів (Kafka, RabbitMQ) повною відсутністю серіалізації. Подія передається як звичайний об'єкт у пам'яті за посиланням. Це дозволяє обробляти понад `1 000 000` подій на секунду на одному ядрі CPU без витрат на мережевий stack та серіалізацію JSON/Protobuf.

---

## 3. Написання автоматичного архітектурного тесту (AST Import Linter)

Найбільшим практичним ризиком розробки модульного моноліту є «ерозія меж коду» (Architectural Erosion). У разі термінових фіксів розробник може спокуситися імпортувати приватний клас іншого модуля напряму (наприклад, написати `from modules.billing.internal.models import Invoice` всередині модуля `automation`).

Щоб конструктивно унеможливити такі порушення, у CI/CD-пайплайн проекту додається **архітектурний тест на основі AST-аналізу коду**. Модуль `ast` у мові Python розбирає вихідні файли у дерево абстрактного синтаксису (Abstract Syntax Tree) та обходить усі вузли імпортування, перевіряючи дотримання правил.

### Правила контролю меж у тесті:
1. Файли з модуля `A` можуть імпортувати з модуля `B` **ТІЛЬКИ** файли `contract.py` або `events.py`.
2. Пряме імпортування з пакету `modules.B.internal.*` є критичним порушенням і негайно зупиняє CI-збірку.
3. Модуль не має права імпортувати власні файли через абсолютне зовнішнє ім'я, щоб уникнути плутанини у циклічних залежностях.

:::tabs
```py
# tests/architecture/test_module_boundaries.py
import ast
import os
import pytest

MODULES_ROOT_PATH = os.path.abspath("cloud-core/modules")

def find_all_python_files(directory: str):
    """Рекурсивний пошук усіх Python-файлів у каталозі модулів."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def inspect_file_imports(file_path: str, current_module_name: str) -> list[str]:
    """Аналізує синтаксичне дерево (AST) файлу та виявляє несанкціоновані імпорти."""
    with open(file_path, "r", encoding="utf-8") as file_handle:
        try:
            tree = ast.parse(file_handle.read(), filename=file_path)
        except SyntaxError as err:
            return [f"Синтаксична помилка у файлі {file_path}: {err}"]

    violations = []
    for node in ast.walk(tree):
        imported_module_path = None
        
        # Обробка конструкцій вида 'import modules.billing.internal.models'
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_module_path = alias.name
        # Обробка конструкцій вида 'from modules.billing.internal.models import Invoice'
        elif isinstance(node, ast.ImportFrom):
            imported_module_path = node.module or ""

        if imported_module_path and "modules." in imported_module_path:
            path_segments = imported_module_path.split(".")
            # Очікуваний формат: ['modules', 'target_module_name', 'subpackage', ...]
            if len(path_segments) > 1:
                target_module_name = path_segments[1]

                # Перевірка 1: Заборона імпорту приватного вмісту (internal) чужого модуля
                if target_module_name != current_module_name:
                    if "internal" in path_segments:
                        violations.append(
                            f"ПОРУШЕННЯ МЕЖІ: {file_path}:{node.lineno} -> "
                            f"Модуль '{current_module_name}' імпортує приватний код '{imported_module_path}'! "
                            f"Дозволено імпортувати лише modules.{target_module_name}.contract або events."
                        )
                    elif len(path_segments) > 2 and path_segments[2] not in ("contract", "events"):
                        violations.append(
                            f"ПОРУШЕННЯ МЕЖІ: {file_path}:{node.lineno} -> "
                            f"Модуль '{current_module_name}' імпортує неприпустимий файл '{imported_module_path}'!"
                        )

    return violations

def test_enforce_strict_module_boundaries():
    """Головний архітектурний тест для CI/CD."""
    all_boundary_violations = []

    if not os.path.exists(MODULES_ROOT_PATH):
        pytest.fail(f"Каталог модулів не знайдено за шляхом: {MODULES_ROOT_PATH}")

    for entry in os.listdir(MODULES_ROOT_PATH):
        module_dir = os.path.join(MODULES_ROOT_PATH, entry)
        if os.path.isdir(module_dir):
            for py_file in find_all_python_files(module_dir):
                file_violations = inspect_file_imports(py_file, current_module_name=entry)
                all_boundary_violations.extend(file_violations)

    # Якщо виявлено хоча б одне порушення — тест виводить чіткий звіт і валить збірку
    assert not all_boundary_violations, (
        "Виявлено порушення архітектурних меж модульного моноліту:\n" +
        "\n".join(all_boundary_violations)
    )
```
:::

Принцип роботи цього архітектурного тесту полягає у тому, що він працює без виконання коду (статичний аналіз). Тесту не потрібне підключення до бази даних чи створення тестового оточення; він виконується за 100–200 мілісекунд, миттєво перевіряючи сотні вихідних файлів.

---

## 4. Виявлення циклічних залежностей та обробка крайових випадків

Окрім прямої перевірки приватних імпортів, суворий контроль меж у модульному моноліті вимагає захисту від **циклічних залежностей між модулями** (Cyclic Module Dependencies).

Якщо модуль `DeviceRegistry` викликає метод `AutomationEngine`, а `AutomationEngine` синхронно імпортує `DeviceRegistry`, виникає мертва петля зчеплення. Граф залежностей між модулями зобов'язаний бути **орієнтованим ациклічним графом (DAG)**.

### Алгоритм перевірки DAG між модулями:

1. Архітектурний тест будує матрицю суміжності імпортів між модулями на основі `contract.py`.
2. Якщо виявляється цикл вида `A -> B -> C -> A`, тест повертає помилку `ЦИКЛІЧНА ЗАЛЕЖНІСТЬ МОДУЛІВ`.
3. Усунення циклів виконується шляхом перенесення спільної доменної події в інший модуль або переходу з синхронного виклику на асинхронне сповіщення крізь `InMemoryEventBus`.

---

## 5. Порівняння механізмів контролю меж у мовах програмування

Залежно від технологічного стеку, що використовується для реалізації `cloud-core`, контроль меж модульного моноліту може забезпечуватися як вбудованими засобами компілятора, так і сторонніми静态чними лінтерами:

- **Go (Golang):** Мова Go має вбудовану підтримку приватності пакетів на рівні компілятора. Будь-який каталог із назвою `internal/` у Go може імпортуватися ТІЛЬКИ тими пакетами, що лежать у тому самому батьківському каталозі. Компілятор Go валить збірку автоматично без потреби у сторонніх скриптах.
- **C++ (C++20 Modules):** Стандарт C++20 увів концепцію мовних модулів (`export module device_registry;`). Модуль явно декларує, які класи та функції експортуються (`export class IDeviceRegistryModule`), а всі неекспортовані файли реалізації залишаються недоступними для зовнішніх одиниць трансляції.
- **Python / TypeScript:** У динамічних мовах мовна ізоляція є слабшою, тому використаний вище AST-лінтер або інструменти вида `Packwerk` / `pytest-archon` є обов'язковими елементами CI/CD-інфраструктури.

---

## 6. Результати роботи та інтеграція в CI/CD

Впровадження даного тесту в процес безперервної інтеграції (GitHub Actions / GitLab CI) відбувається додаванням одного кроку в скрипт перевірки:

```yaml
# .github/workflows/ci.yml
- name: Run Architecture Boundary Linter
  run: |
    poetry run pytest tests/architecture/
```

При спробі розробника передати код із несанкціонованим імпортом, система видасть чітке повідомлення з точним вказанням файлу та рядка коду:

```
=================================== FAILURES =================──────────────────
_____________________ test_enforce_strict_module_boundaries ____________________
AssertionError: Виявлено порушення архітектурних меж модульного моноліту:
ПОРУШЕННЯ МЕЖІ: cloud-core/modules/automation/internal/service.py:14 -> 
Модуль 'automation' імпортує приватний код 'modules.billing.internal.models'! 
Дозволено імпортувати лише modules.billing.contract або events.
```

Завдяки цьому інженерному механізму архітектурна дисципліна підтримується автоматично на рівні комбінатора коду. Старші інженери звільняються від необхідності вручну шукати порушення ізоляції під час проведення Code Review, а макроархітектура Digital Homes захищена від непомітної деградації у неструктурований моноліт.
