# 📋 Внутрішньопроцесний контракт модулів Digital Homes

Цей довідник визначає публічний інтерфейсний контракт, структуру DTO, специфікацію доменних подій та правила логічної ізоляції схем бази даних для всіх модулів у межах монолітної кодової бази `cloud-core` системи Digital Homes.

Внутрішньопроцесний контракт є головним інструментом збереження архітектурної дисципліни модульного моноліту. Він гарантує, що модулі залишаються слабко зчепленими і можуть спілкуватися лише через явно визначені інтерфейсні двері або асинхронні доменні події, не торкаючись приватних деталей реалізації чи внутрішніх таблиць бази даних один одного.

```
                  ┌─────────────────────────────────────────┐
                  │          cloud-core (Monolith)          │
                  │                                         │
                  │  ┌───────────────────┐                  │
                  │  │ DeviceRegistry    │                  │
                  │  └─────────┬─────────┘                  │
                  │            │ Public Contract API        │
                  │            ▼                            │
                  │  ┌───────────────────┐                  │
                  │  │ AutomationEngine  │                  │
                  │  └─────────┬─────────┘                  │
                  │            │ In-Memory Events           │
                  │            ▼                            │
                  │  ┌───────────────────┐                  │
                  │  │ Notifications     │                  │
                  │  └───────────────────┘                  │
                  └─────────────────────────────────────────┘
```

---

## 1. Загальні принципи контрактування модулів

Усі модулі в межах кодової бази `cloud-core` підпорядковуються чотирьом суворим інтерфейсним правилам, які запобігають ерозії меж та підготовлюють кодову базу до безболісного виділення окремих мікросервісів у майбутньому:

1. **Єдина точка входу (Single Entry Point):** Публічна поверхня модуля експортується виключно через пакет `contract` (`modules.<module_name>.contract`). Усі інші пакети та каталоги (зокрема `internal/`, `repository/`, `models/`) вважаються приватними. Пряме звернення до приватної поверхні з інших модулів заборонене і блокується автоматичним архітектурним тестом на етапі комбінації коду.
2. **Незмінність DTO (Immutability):** Обмін даними між модулями виконується виключно через заморожені об'єкти передачі даних (Data Transfer Objects — DTO). Модуль-отримувач не має права змінювати стан отриманого DTO; будь-які модифікації створюють новий екземпляр об'єкта.
3. **Обробка помилок та винятків:** Модуль не має права пропускати назовні внутрішні винятки драйверів СУБД (наприклад, `psycopg2.OperationalError` або `sqlite3.OperationalError`). Усі інфраструктурні помилки трансуються у доменні винятки контракту (`DeviceNotFoundError`, `ModuleUnavailableError`, `ValidationError`).
4. **Потокобезпечність (Thread Safety):** Реалізації контрактів повинні гарантувати безпечний виклик методів із паралельних потоків обробки HTTP-запитів без додаткового зовнішнього блокування.

---

## 2. Контракт модуля DeviceRegistry (`modules.device_registry.contract`)

Модуль `DeviceRegistry` є єдиним інституційним джерелом правди у системі щодо реєстру фізичних пристроїв, їхнього стану в реальному часі (Device Shadow) та конфігураційних параметрів підключення.

### 2.1. Публічний інтерфейс `IDeviceRegistryModule`

Інтерфейс надає синхронні методи читання та маніпуляції станом пристроїв для суміжних модулів (`AutomationEngine`, `UserIdentity`, `Notifications`).

```py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from datetime import datetime

class IDeviceRegistryModule(ABC):
    @abstractmethod
    def get_device(self, device_id: str) -> DeviceDTO | None:
        """Повертає знімок стану пристрою за його унікальним ідентифікатором.
        
        Параметри:
          - device_id: Унікальний GUID пристрою у форматі рядка (36 символів).
        Повертає:
          - DeviceDTO: Заморожений знімок стану пристрою.
          - None: Якщо пристрій з таким ідентифікатором відсутній у реєстрі.
        Винятки:
          - DeviceRegistryError: При виникненні внутрішньої помилки доступу до даних.
        """
        pass

    @abstractmethod
    def list_home_devices(self, home_id: str, device_type: str | None = None) -> list[DeviceDTO]:
        """Повертає перелік усіх пристроїв, прикріплених до конкретного дому.
        
        Параметри:
          - home_id: Унікальний GUID дому.
          - device_type: (Опціонально) Рядковий фільтр за типом пристрою 
                         ('sensor', 'actuator', 'hub', 'camera').
        Повертає:
          - Список об'єктів DeviceDTO. Якщо пристроїв немає — повертає порожній список [].
        """
        pass

    @abstractmethod
    def update_desired_state(self, device_id: str, desired_payload: dict[str, Any], updated_by_user_id: str) -> bool:
        """Оновлює бажаний стан пристрою (Desired State) у Device Shadow.
        
        Цей метод використовується модулем автоматизації або API-контролерами для відправки 
        команд пристрою (наприклад, увімкнути реле, змінити цільову температуру).
        
        Параметри:
          - device_id: GUID пристрою.
          - desired_payload: Словник ключ-значення з новими цільовими параметрами.
          - updated_by_user_id: GUID користувача або ідентифікатор 'system_automation'.
        Повертає:
          - True, якщо бажаний стан успішно оновлено та згенеровано дельта-подію.
        Винятки:
          - DeviceNotFoundError: Якщо пристрій відсутній у базі.
          - InvalidStatePayloadError: Якщо параметри payload не відповідають схемі пристрою.
        """
        pass
```

### 2.2. Об'єкт передачі даних `DeviceDTO`

```py
@dataclass(frozen=True)
class DeviceDTO:
    id: str
    home_id: str
    serial_number: str
    model_name: str
    device_type: str            # 'sensor' | 'actuator' | 'hub' | 'camera'
    is_online: bool
    firmware_version: str
    reported_state: dict[str, Any]  # Фактичний стан, отриманий від фізичного пристрою
    desired_state: dict[str, Any]   # Бажаний стан, встановлений користувачем або правилом
    last_seen_at: datetime
```

Поля `reported_state` та `desired_state` містять ключ-значення параметрів. Наприклад, для розумного термостата: `reported_state = {"current_temp": 21.5, "target_temp": 22.0, "relay_on": True}`.

---

## 3. Контракт модуля AutomationEngine (`modules.automation.contract`)

Модуль `AutomationEngine` відповідає за збереження, оцінку та виконання автоматичних правил користувача (автосценаріїв).

### 3.1. Публічний інтерфейс `IAutomationModule`

```py
class IAutomationModule(ABC):
    @abstractmethod
    def create_rule(self, home_id: str, rule_name: str, trigger_conditions: list[dict[str, Any]], actions: list[dict[str, Any]]) -> RuleDTO:
        """Створює нове правило автоматизації для дому.
        
        Параметри:
          - home_id: GUID дому, якому належить правило.
          - rule_name: Описова назва правила (наприклад, 'Нічне опалення вітальні').
          - trigger_conditions: Список тригерів (наприклад, [{'device_id': 'sensor_1', 'property': 'temp', 'op': '<', 'val': 18}]).
          - actions: Список дій (наприклад, [{'device_id': 'heater_1', 'property': 'power', 'val': 'ON'}]).
        Повертає:
          - Створений об'єкт RuleDTO з присвоєним rule_id.
        """
        pass

    @abstractmethod
    def evaluate_triggers_for_device(self, device_id: str, property_name: str, new_value: Any) -> list[str]:
        """Синхронно оцінює всі правила, прив'язані до зміни властивості пристрою,
        та повертає список ідентифікаторів виконаних правил.
        
        Параметри:
          - device_id: GUID пристрою, стан якого змінився.
          - property_name: Назва властивості, що зазнала змін.
          - new_value: Нове фактичне значення властивості.
        Повертає:
          - Список rule_id рядків, які спрацювали у результаті оцінки.
        """
        pass
```

### 3.2. Об'єкт передачі даних `RuleDTO`

```py
@dataclass(frozen=True)
class RuleDTO:
    rule_id: str
    home_id: str
    name: str
    is_enabled: bool
    trigger_conditions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    created_at: datetime
    last_triggered_at: datetime | None
```

---

## 4. Контракт модуля UserIdentity (`modules.user_identity.contract`)

Модуль `UserIdentity` керує обліковими записами користувачів, їхніми правами доступу до конкретних домогосподарств та рольовими політикам (адміністратор дому, мешканець, гість, тимчасовий орендар).

### 4.1. Публічний інтерфейс `IUserIdentityModule`

Взаємодія із суміжними модулями вимагає швидкої перевірки авторизаційних прав перед виконанням дій над пристроями чи конфігурацією автоматизацій.

```py
class IUserIdentityModule(ABC):
    @abstractmethod
    def check_user_permission(self, user_id: str, home_id: str, required_permission: str) -> bool:
        """Перевіряє наявність права користувача на виконання дії у конкретному домі.
        
        Параметри:
          - user_id: GUID користувача.
          - home_id: GUID дому.
          - required_permission: Рядковий код права ('control_devices', 'manage_rules', 'view_telemetry').
        Повертає:
          - True, якщо користувач має активне право доступу.
        """
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> UserProfileDTO | None:
        """Отримує профіль користувача з його налаштуваннями сповіщень та мовою."""
        pass
```

---

## 5. Контракт модуля Notifications (`modules.notifications.contract`)

Модуль `Notifications` відповідає за формування, маршрутизацію та надсилання системних сповіщень через зовнішні канали (Apple Push Notification service APNs, Firebase Cloud Messaging FCM, SMS-шлюзи та e-mail провайдери).

### 5.1. Публічний інтерфейс `INotificationsModule`

```py
class INotificationsModule(ABC):
    @abstractmethod
    def send_critical_alert(self, home_id: str, title: str, message: str, payload: dict[str, Any]) -> str:
        """Надсилає термінове сповіщення високого пріоритету всім мешканцям дому.
        
        Параметри:
          - home_id: GUID дому.
          - title: Короткий заголовок сповіщення (наприклад, 'УВАГА: Виявлено протікання води!').
          - message: Текст сповіщення.
          - payload: Додаткові дані для відкриття конкретного екрана у мобільному застосунку.
        Повертає:
          - notification_id відправленого сповіщення.
        """
        pass
```

---

## 6. Специфікація внутрішньопроцесних доменних подій (`Domain Events`)

Асинхронний зв'язок між модулями виконується через публікацію об'єктів доменних подій у внутрішньопроцесну шину `InMemoryEventBus`. Усі події реалізують базовий контракт замороженої структури з унікальним ідентифікатором та часовою міткою UTC.

Доменні події дають змогу повністю розчепити продюсера (який публікує подію та не знає про споживачів) від підписників, які обробляють подію асинхронно у пам'яті.

### 6.1. Подія `DeviceStateChangedEvent`

Подія генерується модулем `DeviceRegistry` щоразу, коли від фізичного пристрою або хаба надходить підтверджене оновлення фактичного стану (Reported State).

```py
@dataclass(frozen=True)
class DeviceStateChangedEvent:
    event_id: str              # Унікальний GUID події для дедуплікації
    device_id: str             # GUID пристрою
    home_id: str               # GUID дому
    property_name: str         # Назва атрибута: 'temperature', 'motion_detected', 'leakage'
    old_value: Any             # Попереднє значення
    new_value: Any             # Нове значення
    timestamp: datetime        # Час фіксації зміни у форматі UTC
```

Передбачені споживачі події (Subscribers):
1. `AutomationEngine` — оцінює, чи не викликає ця зміна спрацювання автоматичних правил.
2. `TelemetryIngest` — додає запис виміру до часового ряду бази даних.

### 6.2. Подія `AutomationTriggeredEvent`

Подія генерується модулем `AutomationEngine` після успішного обчислення та виконання дій автоматичного правила.

```py
@dataclass(frozen=True)
class AutomationTriggeredEvent:
    event_id: str
    rule_id: str
    home_id: str
    rule_name: str
    executed_actions_count: int
    timestamp: datetime
```

Передбачені споживачі події:
1. `Notifications` — надсилає push-сповіщення на смартфони мешканців дому.
2. `AuditLog` — фіксує подію в журналі аудіту дій системи.

### 6.3. Подія `UserAccessRevokedEvent`

Подія генерується модулем `UserIdentity`, коли користувач втрачає доступ до дому (наприклад, видалення мешканця або скасування орендного доступу).

```py
@dataclass(frozen=True)
class UserAccessRevokedEvent:
    event_id: str
    user_id: str
    home_id: str
    timestamp: datetime
```

Передбачені споживачі події:
1. `DeviceRegistry` — анулює активні сесії та токени локального доступу користувача крізь хаб.
2. `Notifications` — відправляє підтвердження про скасування прав.

### 6.4. Подія `TelemetryBatchIngestedEvent`

Подія генерується модулем `TelemetryIngest` при завершенні накопичення пачки вимірів.

```py
@dataclass(frozen=True)
class TelemetryBatchIngestedEvent:
    event_id: str
    home_id: str
    records_count: int
    timestamp: datetime
```

---

## 7. Контракт логічної ізоляції схем бази даних PostgreSQL

Для забезпечення повної готовності модульного моноліту `cloud-core` до можливого майбутнього розпилу (якщо виникне потреба виділення окремих мікросервісів), у базі даних PostgreSQL впроваджено **сувору логічну ізоляцію схем**.

Система використовує єдину фізичну базу даних `cloud_dh_db`, розділену на чотири ізольовані SQL-схеми:

```
PostgreSQL Database: cloud_dh_db
├── Schema: devices
│   ├── devices.device_records
│   ├── devices.device_shadows
│   └── devices.hub_connections
├── Schema: automation
│   ├── automation.rules
│   ├── automation.triggers
│   └── automation.execution_logs
├── Schema: telemetry
│   └── telemetry.time_series_metrics
└── Schema: billing
    ├── billing.user_subscriptions
    └── billing.payment_invoices
```

### 7.1. Детальна специфікація таблиць та меж схем

Таблиці кожної SQL-схеми створюються окремими міграційними файлами Alembic або Flyway. Кожна схема ізолює сутності свого домену.

#### Схема `devices`:
- **`devices.device_records`**: Зберігає паспортні дані пристроїв (ID, home_id, serial_number, model, device_type, created_at). Первинний ключ: `id (UUID)`.
- **`devices.device_shadows`**: Зберігає поточний стан Device Shadow у форматі JSONB (`reported_state`, `desired_state`, `version`, `updated_at`). Первинний ключ: `device_id (UUID)`.

#### Схема `automation`:
- **`automation.rules`**: Зберігає конфігурацію правил автоматизації (rule_id, home_id, name, is_enabled, trigger_json, actions_json). Первинний ключ: `rule_id (UUID)`.
- **`automation.execution_logs`**: Журнал виконань правил (log_id, rule_id, status, error_message, executed_at). Первинний ключ: `log_id (UUID)`.

#### Схема `telemetry`:
- **`telemetry.time_series_metrics`**: Сховище вимірів давачів (time, device_id, metric_name, numeric_value, string_value). Сквозна таблиця з секціонуванням (partitioning) за місяцями.

#### Схема `billing`:
- **`billing.user_subscriptions`**: Зберігає стан та планові тарифи користувачів (user_id, plan_type, status, expires_at). Первинний ключ: `user_id (UUID)`.

### 7.2. Декларативні правила бази даних (Database Boundary Constraints)

Дотримання логічної ізоляції бази даних гарантується трьома незмінними правилами розробки:

1. **Заборона міжсхемних JOIN (No Cross-Schema JOINs):**  
   SQL-запит у коді модуля `automation` не має права містити оператор `JOIN devices.device_records`. Якщо модулю автоматизації потрібні дані про пристрій, він зобов'язаний звернутися до `IDeviceRegistryModule.get_device()` у коді додатка.

2. **Заборона міжсхемних зовнішніх ключів (No Cross-Schema Foreign Keys):**  
   Між таблицями різних схем заборонено створювати обмеження `FOREIGN KEY`. Посилання на об'єкти інших схем (наприклад, `home_id` або `device_id` у таблиці `automation.rules`) зберігаються як звичайні UUID-рядки. Це дає змогу в будь-який момент перенести схему `telemetry` або `billing` на окремий фізичний сервер СУБД без розриву зв'язку.

3. **Розділення прав користувачів СУБД (Role-Based Access Control):**  
   Під час автоматизованого тестування ізоляції для кожного модуля створюється окрема роль PostgreSQL:
   - `dh_devices_role` має доступ `GRANT ALL` ТІЛЬКИ до схеми `devices`.
   - `dh_automation_role` має доступ `GRANT ALL` ТІЛЬКИ до схеми `automation`.

Спроба модуля використати прямий SQL-запит до чужої схеми викликає помилку доступу `permission denied for schema`, що гарантує 100% збереження доменних меж.
