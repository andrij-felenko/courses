# ⚙️ Автоматизований контролер синьо-зеленого розгортання: динамічна маршрутизація, прогрів та атомарний відкат

Надійне синьо-зелене розгортання вимагає суворого дотримання послідовності стадій: виділення цільового середовища, синтетичний прогрів кешів та пулів з'єднань, атомарне перемикання ваг або маршрутів на балансувальнику, моніторинг показників надійності протягом періоду вистоювання (англ. *soak period*) та миттєвий відкат, якщо частота помилок або час обробки запитів перевищують допустимі порогові значення.

Головна перевага синьо-зеленої схеми над іншими підходами полягає у винесенні всіх ризиків запуску нового коду за межі активного користувацького трафіку. Поки стара версія стабільно обслуговує запити, нова версія проходить повний цикл ініціалізації в ізольованому контурі. Проте автоматизація цього процесу потребує координації багатьох мережевих та системних компонентів: зондів працездатності, динамічних таблиць маршрутизації, черг завдань та аналізаторів телеметрії.

Нижче наведено повноцінну реалізацію асинхронного інженерного контролера синьо-зеленого розгортання на мові Python. Контролер керує динамічним L7-балансувальником, виконує синтетичні смоук-тести, контролює процес дренажу з'єднань і в режимі реального часу відстежує стан системи за допомогою метрик Prometheus.

## Архітектура та інтерфейс стану контролера

Контролер оперує двома середовищами: `blue` (синє) та `green` (зелене). Кожне середовище складається з групи бекенд-вузлів зі своїми мережевими адресами, статусом готовності та поточною версією артефакту.

Процес розгортання моделюється як строгий скінченний автомат. Перехід між фазами відбувається лише за умови виконання всіх критеріїв якості попереднього етапу:

```text
  [ IDLE ] ──> [ PROVISIONING ] ──> [ WARMING_UP ] ──> [ SMOKE_TESTING ]
                                                              │
                                                        (Тести пройдено)
                                                              ▼
  [ PROMOTED ] <── [ SOAK_MONITORING ] <── [ CUTOVER (Світч L7) ]
        ▲                  │
        │           (Збій метрик?)
  [ Знищення Blue ]        ▼
                   [ ROLLING_BACK (O(1) відкат) ] ──> [ FAILED ]
```

1. `IDLE` — базовий спокійний стан кластера, коли одне із середовищ обслуговує 100% живого трафіку, а інше вимкнене або перебуває в режимі очікування.
2. `PROVISIONING` — створення нової інфраструктури або оновлення контейнерів у пасивному середовищі.
3. `WARMING_UP` — синтетичний прогрів пам'яті, структур даних, JIT-компіляторів та пулів підключень до бази даних.
4. `SMOKE_TESTING` — виконання функціональних перевірок наскрізних бізнес-сценаріїв через внутрішній прев'ю-маршрут.
5. `CUTOVER` — атомарна зміна конфігурації L7-проксі для миттєвого переведення 100% клієнтських запитів на нове середовище.
6. `SOAK_MONITORING` — період вистоювання під реальним навантаженням із безперервною перевіркою частоти помилок та затримок.
7. `PROMOTED` — фіксація успішного релізу, переведення старого середовища в режим резерву або його масштабування до нуля.
8. `ROLLING_BACK` — екстрене повернення трафіку на попередню стабільну версію за час `O(1)` у разі виявлення деградації метрик.

```python
"""
Blue-Green Deployment Controller
Керує життєвим циклом двох середовищ, взаємодіє з L7-проксі
та автоматично ухвалює рішення про просування або відкат.
"""

from __future__ import annotations
import asyncio
import dataclasses
import enum
import logging
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("BlueGreenController")


class EnvironmentRole(str, enum.Enum):
    BLUE = "blue"
    GREEN = "green"


class DeploymentPhase(str, enum.Enum):
    IDLE = "IDLE"
    PROVISIONING = "PROVISIONING"
    WARMING_UP = "WARMING_UP"
    SMOKE_TESTING = "SMOKE_TESTING"
    CUTOVER = "CUTOVER"
    SOAK_MONITORING = "SOAK_MONITORING"
    PROMOTED = "PROMOTED"
    ROLLING_BACK = "ROLLING_BACK"
    FAILED = "FAILED"


@dataclasses.dataclass(frozen=True)
class Endpoint:
    host: str
    port: int
    version: str

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


@dataclasses.dataclass
class EnvironmentState:
    role: EnvironmentRole
    version: str
    endpoints: List[Endpoint]
    is_active: bool = False
    is_warm: bool = False
    error_rate_percent: float = 0.0
    p99_latency_ms: float = 0.0


@dataclasses.dataclass(frozen=True)
class DeploymentConfig:
    app_name: str
    target_version: str
    warmup_requests_count: int = 50
    smoke_test_concurrency: int = 5
    soak_duration_seconds: float = 10.0
    max_allowed_error_rate: float = 1.0       # Максимум 1% помилок 5xx
    max_allowed_p99_latency_ms: float = 120.0  # Максимум 120 мс
    drain_timeout_seconds: float = 5.0
```

## Рівень динамічного L7-маршрутизатора та дренаж з'єднань

Для перемикання трафіку без перезапуску та без розриву активних TCP-сесій контролер взаємодіє з балансувальником (наприклад, через сокет керування HAProxy або REST/gRPC API Envoy). У цій реалізації шар проксі інкапсульовано в інтерфейсі `L7TrafficRouter`, який підтримує атомарну зміну активного пулу, спрямування прев'ю-трафіку та коректний дренаж з'єднань.

Механізм перемикання спирається на три мережеві інваріанти:

1. **Атомарність зміни вказівника:** новий вхідний запит у момент `t` направляється на старий пул, а вже в момент `t + 1 мс` — на новий пул без проміжного стану відсутності бекендів.
2. **Ізоляція прев'ю-маршрутів:** тестовий трафік надсилається за спеціальним службовим заголовком або портом безпосередньо на цільовий пул, не змішуючись із публічними запитами.
3. **Дренаж активних з'єднань (Connection Draining):** старий пул перестає приймати нові з'єднання, проте відкриті TCP-сокети отримують фіксований час на завершення поточних операцій. Для протоколу HTTP/2 балансувальник генерує кадр `GOAWAY` із зазначенням останнього обробленого ідентифікатора потоку (`StreamID`), спонукаючи клієнтів відкривати нові мультиплексовані з'єднання вже до нового пулу.

Взаємодія з проксі-сервером не потребує перезавантаження конфігураційних файлів процесу (англ. *zero-reload re-routing*). У випадку HAProxy контролер надсилає команди `set server backend_blue/srv1 state maint` та `set server backend_green/srv1 state ready` через локальний UNIX-доменний сокет. У випадку Envoy контролер публікує оновлений маніфест кластерів через протокол динамічної конфігурації xDS (Endpoints Discovery Service, EDS), що гарантує зміну маршрутизації за лічені мікросекунди без скидання з'єднань.

Також проксі підтримує роботу з клієнтськими куками сесійної прив'язки (англ. *sticky sessions*). При синьо-зеленому переході проксі може або скидати куку, змушуючи користувача негайно потрапити на Green, або дозволяти користувачам із активною сесією допрацювати на Blue до закінчення вікна дренажу, після чого плавно перевести їх на Green.

```python
class L7TrafficRouter:
    """
    Інкапсулює керування L7-маршрутизатором (Envoy, NGINX Upstream API, HAProxy Socket).
    Забезпечує атомарне перемикання бекенд-пулів за O(1) час.
    """

    def __init__(self) -> None:
        self._active_role: EnvironmentRole = EnvironmentRole.BLUE
        self._preview_role: Optional[EnvironmentRole] = None
        self._drain_in_progress: Dict[EnvironmentRole, bool] = {
            EnvironmentRole.BLUE: False,
            EnvironmentRole.GREEN: False,
        }

    @property
    def active_role(self) -> EnvironmentRole:
        return self._active_role

    async def switch_active_target(self, target_role: EnvironmentRole) -> None:
        """Атомарно перемикає 100% публічного трафіку на обраний пул."""
        old_role = self._active_role
        if old_role == target_role:
            logger.warning("Цільовий пул %s вже є активним.", target_role.value)
            return

        logger.info("=== [L7 ROUTER] ПЕРЕМИКАННЯ ТРАФІКУ: %s -> %s ===",
                    old_role.value.upper(), target_role.value.upper())
        
        # Симуляція запису команди в сокет керування балансувальника (O(1) операція)
        await asyncio.sleep(0.05)
        self._active_role = target_role
        self._drain_in_progress[old_role] = True
        logger.info("[L7 ROUTER] Публічний трафік успішно переведено на %s. Пул %s переведено в режим дренажу.",
                    target_role.value, old_role.value)

    async def execute_drain(self, role: EnvironmentRole, timeout: float) -> None:
        """Очікує завершення обробки активних відкритих з'єднань на старому пулі."""
        logger.info("[L7 ROUTER] Початок дренажу відкритих з'єднань для %s (таймаут %.1f с)...",
                    role.value, timeout)
        # Балансувальник надсилає заголовок 'Connection: close' або кадр GOAWAY в HTTP/2
        await asyncio.sleep(timeout)
        self._drain_in_progress[role] = False
        logger.info("[L7 ROUTER] Дренаж пулу %s успішно завершено. Пул перебуває в режимі Standby.",
                    role.value)

    async def route_preview_request(self, role: EnvironmentRole, path: str) -> Tuple[int, float]:
        """Спрямовує службовий запит безпосередньо на тестований пул в обхід публічного трафіку."""
        start_time = time.monotonic()
        # Симуляція виконання мережевого HTTP-запиту до тестованого бекенду
        await asyncio.sleep(0.01)
        elapsed_ms = (time.monotonic() - start_time) * 1000.0
        return 200, elapsed_ms
```

## Реалізація асинхронного контролера: покроковий розбір фаз

Клас `BlueGreenDeploymentEngine` втілює логіку оркестрації. Він виконує сувору перевірку інваріантів перед кожним наступним кроком.

### Фаза 1: Виділення ресурсів та розгортання артефакту (Provisioning)

На цьому етапі контролер визначає, який саме контур є неактивним. Якщо в продакшені зараз працює `blue`, цільовим призначається `green`. Контролер запускає нові екземпляри застосунку з новим версійним тегом. На відміну від rolling-розгортання, де процеси замінюються по черзі, у синьо-зеленій схемі нове середовище розгортається одразу в повному обсязі (100% розрахункової потужності кластера), що дозволяє перевірити конфігурацію системи під реальним навантаженням ще до пуску публічного трафіку.

Перед запуском нових процесів контролер також викликає хуки міграції бази даних. Оскільки стара версія `blue` продовжує активно записувати дані, будь-яка міграція на цій фазі має бути строго адитивною (створення нових таблиць, додавання опціональних стовпців без обмеження `NOT NULL`), щоб не порушити роботу живого продакшну.

### Фаза 2: Синтетичний прогрів пам'яті та кешів (Warmup)

Свіжозапущений процес зазвичай страждає від проблеми «холодного старту»: пули з'єднань із базою даних порожні, внутрішні кеші не заповнені, а середовища виконання з динамічною компіляцією (JVM C2 JIT, V8, PyPy) ще не оптимізували гарячі ділянки байткоду в нативні інструкції процесора. Якщо спрямувати 50 000 запитів на секунду на «холодний» вузол, черги переповняться, а затримка відповіді підскочить у сотні разів. Контролер генерує контрольований потік синтетичних запитів до внутрішніх ендпоінтів, примусово розігріваючи структуры даних без ризику для користувачів.

Прогрів триває доти, доки середній час обробки тестових запитів не стабілізується на очікуваному рівні базової лінії (англ. *baseline latency*).

### Фаза 3: Димове тестування бізнес-контрактів (Smoke Testing)

Контролер виконує набір критичних інтеграційних запитів (перевірка каталогу, валідація токенів аутентифікації, читання профілів). Якщо хоча б один маршрут повертає помилку `HTTP 5xx` або неочікуване тіло відповіді, процес негайно зупиняється, а цільове середовище маркується як несправне. Живий трафік на старому середовищі лишається абсолютно неушкодженим.

### Фаза 4: Атомарне перемикання трафіку (Cutover)

Отримавши підтвердження повної готовності нового коду, контролер викликає метод `switch_active_target()`. Балансувальник миттєво перенаправляє вхідний потік на новий пул. Одночасно стартує фоновий процес дренажу старого середовища.

Мережеві пакети нових TCP-з'єднань негайно потрапляють на вузли `green`. Ті запити, які вже виконувалися на вузлах `blue` у момент перемикання, спокійно добігають кінця в межах виділеного часового вікна дренажу `drain_timeout_seconds`.

### Фаза 5: Моніторинг вистоювання (Soak Monitoring) та верифікація SLI

Після перемикання настає найкритичніший період — вистоювання. Реальний трафік користувачів відрізняється від синтетичного: він несе непередбачувані комбінації параметрів, специфічні навантаження та крайові випадки. Контролер щосекунди опитує систему моніторингу, порівнюючи поточні показники частоти помилок та перцентиль затримок `p99` із допустимими межами, зафіксованими в конфігурації `DeploymentConfig`.

Аналізатор метрик обчислює ковзне середнє значення частоти помилок та затримок:

```text
Частота_помилок(%) = ( Сума(Rate(помилки_5xx[1m])) / Сума(Rate(всі_запити[1m])) ) · 100
```

Якщо це значення перевищує допустимий поріг (наприклад, 1.0%), або якщо час обробки 99% запитів перевищує 120 мілісекунд, контролер негайно фіксує порушення умов експлуатаційної придатності.

### Фаза 6: Аварійний відкат (Emergency Rollback) або затвердження (Promote)

Якщо протягом періоду вистоювання моніторинг фіксує сплеск помилок або зростання затримок, контролер негайно активує процедуру аварійного відкату `_trigger_emergency_rollback()`. Оскільки старе синє середовище не було знищене, а лише переведено в режим очікування з уже прогрітими кешами та відкритими сокетами, балансувальник повертає трафік назад за соті частки секунди `O(1)`. Якщо ж період вистоювання пройшов без зауважень, реліз офіційно затверджується, а старе середовище переводиться в статус очікування наступного циклу.

```python
class BlueGreenDeploymentEngine:
    """
    Головний механізм координації синьо-зеленого розгортання.
    """

    def __init__(self, config: DeploymentConfig, router: L7TrafficRouter) -> None:
        self.config = config
        self.router = router
        self.phase = DeploymentPhase.IDLE

        # Початковий стан: Blue активний з версією v1.0.0
        self.environments: Dict[EnvironmentRole, EnvironmentState] = {
            EnvironmentRole.BLUE: EnvironmentState(
                role=EnvironmentRole.BLUE,
                version="v1.0.0",
                endpoints=[
                    Endpoint("10.0.1.11", 8080, "v1.0.0"),
                    Endpoint("10.0.1.12", 8080, "v1.0.0"),
                ],
                is_active=True,
                is_warm=True,
            ),
            EnvironmentRole.GREEN: EnvironmentState(
                role=EnvironmentRole.GREEN,
                version="v1.0.0",
                endpoints=[],
                is_active=False,
                is_warm=False,
            ),
        }

    def _get_target_role(self) -> EnvironmentRole:
        """Повертає роль неактивного середовища (куди розгортається реліз)."""
        return (EnvironmentRole.GREEN 
                if self.router.active_role == EnvironmentRole.BLUE 
                else EnvironmentRole.BLUE)

    def _get_active_role(self) -> EnvironmentRole:
        """Повертає роль поточного активного продакшн-середовища."""
        return self.router.active_role

    async def execute_deployment(self) -> bool:
        """
        Головна точка входу для запуску синьо-зеленого циклу розгортання.
        Повертає True, якщо оновлення успішне, або False, якщо стався відкат.
        """
        target_role = self._get_target_role()
        active_role = self._get_active_role()

        logger.info("=== ЗАПУСК СИНЬО-ЗЕЛЕНОГО ДЕПЛОЮ ДЛЯ %s ===", self.config.app_name)
        logger.info("Активне середовище: %s (%s) | Цільове середовище: %s (нова версія: %s)",
                    active_role.value, self.environments[active_role].version,
                    target_role.value, self.config.target_version)

        try:
            # 1. Фаза виділення ресурсів (Provisioning)
            self.phase = DeploymentPhase.PROVISIONING
            await self._phase_provision(target_role)

            # 2. Фаза синтетичного прогріву (Warmup)
            self.phase = DeploymentPhase.WARMING_UP
            await self._phase_warmup(target_role)

            # 3. Фаза димового тестування (Smoke Testing)
            self.phase = DeploymentPhase.SMOKE_TESTING
            if not await self._phase_smoke_test(target_role):
                raise RuntimeError("Димові тести на цільовому середовищі провалено!")

            # 4. Фаза атомарного перемикання трафіку (Cutover)
            self.phase = DeploymentPhase.CUTOVER
            await self._phase_cutover(target_role, active_role)

            # 5. Фаза моніторингу вистоювання (Soak Monitoring)
            self.phase = DeploymentPhase.SOAK_MONITORING
            soak_passed = await self._phase_soak_monitor(target_role)

            if not soak_passed:
                logger.error("Критичні метрики якості деградували під час вистоювання!")
                await self._trigger_emergency_rollback(active_role, target_role)
                self.phase = DeploymentPhase.FAILED
                return False

            # 6. Успішне завершення (Promoted)
            self.phase = DeploymentPhase.PROMOTED
            await self._phase_promote(target_role, active_role)
            logger.info("=== СИНЬО-ЗЕЛЕНИЙ ДЕПЛОЙ УСПІШНО ЗАВЕРШЕНО ===")
            return True

        except Exception as exc:
            logger.exception("Аварійна ситуація під час деплою: %s", str(exc))
            if self.phase in (DeploymentPhase.CUTOVER, DeploymentPhase.SOAK_MONITORING):
                await self._trigger_emergency_rollback(active_role, target_role)
            self.phase = DeploymentPhase.FAILED
            return False

    async def _phase_provision(self, target_role: EnvironmentRole) -> None:
        """Створює нові вузли з новим артефактом у цільовому середовищі."""
        logger.info("[ФАЗА 1/6: PROVISIONING] Розгортання версії %s у середовищі %s...",
                    self.config.target_version, target_role.value)
        await asyncio.sleep(0.5)

        # Реєстрація нових IP-адрес
        new_endpoints = [
            Endpoint("10.0.2.21", 8080, self.config.target_version),
            Endpoint("10.0.2.22", 8080, self.config.target_version),
        ]
        self.environments[target_role] = EnvironmentState(
            role=target_role,
            version=self.config.target_version,
            endpoints=new_endpoints,
            is_active=False,
            is_warm=False,
        )
        logger.info("[PROVISIONING] Створено %d нових вузлів для %s.",
                    len(new_endpoints), target_role.value)

    async def _phase_warmup(self, target_role: EnvironmentRole) -> None:
        """Виконує синтетичні запити для заповнення локальних кешів та прогріву пулів."""
        logger.info("[ФАЗА 2/6: WARMUP] Прогрів кешів та ініціалізація пулів з'єднань (%d запитів)...",
                    self.config.warmup_requests_count)
        
        # Симуляція паралельного потоку запитів
        tasks = [
            self.router.route_preview_request(target_role, "/warmup/prime-cache")
            for _ in range(self.config.warmup_requests_count)
        ]
        results = await asyncio.gather(*tasks)
        avg_lat = sum(r[1] for r in results) / len(results)
        self.environments[target_role].is_warm = True
        logger.info("[WARMUP] Середовище %s прогріто. Середній час відповіді під час прогріву: %.2f мс.",
                    target_role.value, avg_lat)

    async def _phase_smoke_test(self, target_role: EnvironmentRole) -> bool:
        """Перевіряє критичні бізнес-маршрути перед відкриттям публічного доступу."""
        logger.info("[ФАЗА 3/6: SMOKE TEST] Валідація бізнес-контрактів та зондів працездатності...")
        test_routes = ["/healthz", "/api/v1/catalog", "/api/v1/auth/validate"]

        for route in test_routes:
            status_code, lat = await self.router.route_preview_request(target_role, route)
            if status_code != 200:
                logger.error("[SMOKE TEST] Маршрут %s повернув статус %d на %s!",
                             route, status_code, target_role.value)
                return False
            logger.info("[SMOKE TEST] Маршрут %s: HTTP 200 OK (%.2f мс)", route, lat)
        return True

    async def _phase_cutover(self, target_role: EnvironmentRole, old_role: EnvironmentRole) -> None:
        """Виконує миттєве перемикання L7-роутера та запускає дренаж старого середовища."""
        logger.info("[ФАЗА 4/6: CUTOVER] Атомарне перемикання трафіку на %s...", target_role.value)
        await self.router.switch_active_target(target_role)
        self.environments[target_role].is_active = True
        self.environments[old_role].is_active = False

        # Запуск асинхронного дренажу з'єднань у фоні
        asyncio.create_task(self.router.execute_drain(old_role, self.config.drain_timeout_seconds))

    async def _phase_soak_monitor(self, target_role: EnvironmentRole) -> bool:
        """
        Спостерігає за станом нового середовища протягом soak_duration_seconds.
        Перевіряє частоту помилок та затримки p99 кожну секунду.
        """
        logger.info("[ФАЗА 5/6: SOAK MONITORING] Спостереження за живим трафіком протягом %.1f с...",
                    self.config.soak_duration_seconds)
        
        start = time.monotonic()
        while time.monotonic() - start < self.config.soak_duration_seconds:
            await asyncio.sleep(1.0)
            
            # Симуляція отримання метрик із Prometheus
            current_err_rate, current_p99 = await self._fetch_live_metrics(target_role)
            self.environments[target_role].error_rate_percent = current_err_rate
            self.environments[target_role].p99_latency_ms = current_p99

            logger.info("[SOAK METRICS] %s -> Помилки: %.2f%% (ліміт: %.1f%%) | p99: %.1f мс (ліміт: %.1f мс)",
                        target_role.value, current_err_rate, self.config.max_allowed_error_rate,
                        current_p99, self.config.max_allowed_p99_latency_ms)

            if current_err_rate > self.config.max_allowed_error_rate:
                logger.error("[SOAK VIOLATION] Перевищено ліміт частоти помилок!")
                return False

            if current_p99 > self.config.max_allowed_p99_latency_ms:
                logger.error("[SOAK VIOLATION] Перевищено ліміт затримки p99!")
                return False

        return True

    async def _trigger_emergency_rollback(self, safe_role: EnvironmentRole, failed_role: EnvironmentRole) -> None:
        """
        АВАРІЙНИЙ ВІДКАТ ЗА O(1) ЧАС.
        Миттєво перемикає роутер назад на безпечне середовище, яке збереглося в пам'яті.
        """
        self.phase = DeploymentPhase.ROLLING_BACK
        logger.critical("!!! АВАРІЙНИЙ ВІДКАТ: МИТТЄВЕ ПЕРЕМИКАННЯ ТРАФІКУ НАЗАД НА %s !!!",
                        safe_role.value.upper())
        await self.router.switch_active_target(safe_role)
        self.environments[safe_role].is_active = True
        self.environments[failed_role].is_active = False
        logger.info("[ROLLBACK] Трафік повернуто на %s. Пошкоджене середовище %s ізольовано для аналізу.",
                    safe_role.value, failed_role.value)

    async def _phase_promote(self, target_role: EnvironmentRole, old_role: EnvironmentRole) -> None:
        """Остаточне закріплення релізу та переведення старого середовища в режим очікування."""
        logger.info("[ФАЗА 6/6: PROMOTE] Реліз версії %s у середовищі %s офіційно затверджено.",
                    self.config.target_version, target_role.value)
        logger.info("[PROMOTE] Старе середовище %s переведено у статус Standby для наступного релізу.",
                    old_role.value)

    async def _fetch_live_metrics(self, role: EnvironmentRole) -> Tuple[float, float]:
        """Симуляція збору метрик реального часу з системи спостережуваності."""
        # У нормальному стані: 0.05% помилок, 45 мс p99
        return 0.05, 45.0
```

## Демонстрація виконання та сценарій аварійного відкату

Протестуємо роботу контролера у двох режимах: нормальному успішному оновленні та аварійному сценарії, коли новий реліз починає повертати HTTP 500 після перемикання.

У першому тесті система демонструє штатні переходи: успішний прогрів, проходження димових тестів, атомарне перемикання та успішне завершення періоду вистоювання зі збереженням нормальних метрик затримок.

У другому тесті контролер симулює критичний виробничий збій: новий реліз v1.2.0 містить прихований дефект витоку пам'яті або блокування бази даних, через що частота помилок підстрибує до 8.5%, а час відповіді сягає 450 мс. Контролер виявляє порушення контрактів надійності вже на першій секунді вистоювання, блокує промоушн та за соті частки секунди повертає L7-маршрутизатор на стабільне середовище Green v1.1.0, запобігаючи масовому колапсу користувацьких сесій.

```python
async def run_demonstration():
    # 1. Успішний сценарій
    router = L7TrafficRouter()
    config_ok = DeploymentConfig(
        app_name="BillingGateway",
        target_version="v1.1.0",
        warmup_requests_count=10,
        soak_duration_seconds=3.0,
        max_allowed_error_rate=1.0,
        drain_timeout_seconds=2.0
    )
    engine = BlueGreenDeploymentEngine(config_ok, router)
    logger.info("================ ТЕСТ 1: УСПІШНИЙ РЕЛІЗ ================")
    success = await engine.execute_deployment()
    assert success is True
    assert router.active_role == EnvironmentRole.GREEN

    # 2. Сценарій відкату через деградацію SLI
    logger.info("\n================ ТЕСТ 2: АВАРІЙНИЙ ВІДКАТ ================")
    config_fail = DeploymentConfig(
        app_name="BillingGateway",
        target_version="v1.2.0-broken",
        warmup_requests_count=5,
        soak_duration_seconds=3.0,
        max_allowed_error_rate=1.0,
        drain_timeout_seconds=2.0
    )
    engine_fail = BlueGreenDeploymentEngine(config_fail, router)

    # Підміна збору метрик для симуляції збою під навантаженням
    async def broken_metrics(role: EnvironmentRole) -> Tuple[float, float]:
        return 8.5, 450.0  # 8.5% помилок і 450 мс затримка
    engine_fail._fetch_live_metrics = broken_metrics

    success_fail = await engine_fail.execute_deployment()
    assert success_fail is False
    # Перевірка, що роутер миттєво повернувся на стабільний Green v1.1.0
    assert router.active_role == EnvironmentRole.GREEN
    logger.info("Тести завершено. Контролер продемонстрував нульовий простій та миттєвий відкат.")


if __name__ == "__main__":
    asyncio.run(run_demonstration())
```

## Інженерні пастки при розробці та експлуатації контролера

При впровадженні систем автоматизованого синьо-зеленого керування в реальну експлуатацію слід враховувати шість фундаментальних пасток:

### 1. Недостатній тайм-аут дренажу (Drain Timeout Underflow)
Якщо контролер примусово зупиняє процеси старого середовища раніше, ніж завершиться найдовший активний клієнтський запит (наприклад, генерація складного PDF-звіту або завантаження файлу), операційна система відправить клієнту TCP-пакет `RST`. Клієнт отримає фатальну помилку `Connection reset by peer`. Тривалість вікна дренажу повинна завжди перевищувати системний ліміт виконання HTTP-запитів (`request_timeout`) із додаванням запасу на затримку поширення таблиць маршрутизації в сервісній сітці.

При розрахунку тайм-ауту дренажу інженери застосовують правило подвійного запасу:
```text
Таймаут_дренажу = Максимальний_час_виконання_запиту + Затримка_поширення_маршрутів + 5с_буфер
```
Якщо в системі існують фонові операції тривалістю понад 60 секунд, їх слід виносити в асинхронні черги завдань, щоб не блокувати регулярний цикл оновлення бекендів.

### 2. Незворотні деструктивні зміни бази даних
Якщо новий реліз у процесі роботи встиг записати дані в зміненому форматі, який несумісний зі старим кодом, або виконав блокуючу операцію `DROP COLUMN`, швидке повернення маршрутизатора на старе середовище не врятує систему: старий код почне масово аварійно завершуватися при читанні пошкоджених записів. Синьо-зелене перемикання гарантує безпеку лише в тому разі, якщо схема даних мігрується за патерном *Expand-Contract* із підтримкою обох версій.

Будь-які міграції повинні розбиватися на окремі кроки: спочатку розгортається код, здатний читати як старі, так і нові структури, і лише в наступному релізі старі поля фізично видаляються з таблиць.

### 3. Кешування DNS та некерованість клієнтських резолверів
Спроба реалізувати синьо-зелене перемикання шляхом зміни DNS-записів (A або CNAME) приречена на невдачу в системах реального часу. Проміжні DNS-сервери інтернет-провайдерів та корпоративні резолвери кешують IP-адреси на години, повністю ігноруючи значення параметра `TTL`. У результаті частина користувачів надсилатиме трафік на старе середовище навіть через добу після релізу, а екстрений відкат розтягнеться на неконтрольований час. Керування синьо-зеленим перемиканням повинно виконуватися виключно на рівні L7-балансувальників або сервісних сіток.

### 4. Розрив довгоживучих з'єднань WebSockets та gRPC-стрімів
Якщо додаток використовує постійні WebSockets або двонаправлені gRPC-потоки, перемикання балансувальника за замовчуванням не торкнеться вже встановлених TCP-сесій. Клієнти залишатимуться підключеними до старого середовища годинами. Щоб коректно перевести таких клієнтів, контролер повинен надіслати старим вузлам команду на плавне завершення сесій, що спонукає клієнтські бібліотеки виконати повторне підключення з випадковою експоненційною затримкою (англ. *jittered exponential backoff*), розподіляючи навантаження на нові вузли.

### 5. Конкурентна обробка асинхронних черг (Worker Competition)
Якщо бекенд містить фонові воркери (наприклад, обробники черг Celery, RabbitMQ або споживачі Kafka), одночасний запуск `blue` та `green` контурів означає, що воркери обох версій одночасно вичитуватимуть завдання з одних і тих самих топіків. Якщо формат повідомлення змінився у версії v2, старий воркер v1 при читанні нового повідомлення впаде з помилкою десеріалізації або відправить його в чергу мертвих листів (Dead Letter Queue, DLQ). Для запобігання цьому воркери повинні використовувати версійовані топіки або окремі групи споживачів (англ. *consumer groups*), перемикання яких синхронізується з контролером.

### 6. Лавиноподібне перевантаження кешів (Cache Stampede / Thundering Herd)
Коли 100% трафіку миттєво перемикається на свіже зелене середовище, тисячі одночасних запитів можуть звернутися за даними, яких ще немає в локальному оперативному кеші нових вузлів. Усі ці запити одночасно пробивають кеш і звертаються до центральної реляційної СУБД, створюючи лавиноподібне перевантаження (шторм запитів). Саме тому фаза синтетичного прогріву `WARMING_UP` є критично обов'язковою: контролер зобов'язаний завантажити гарячі ключі в кеш до моменту перемикання публічного маршрутизатора.

### 7. Синхронізація сесій користувачів та розподілене сховище
При використанні синьо-зеленого розгортання в додатках, що зберігають стан сесії в оперативній пам'яті сервера (англ. *in-memory session state*), перемикання балансувальника призведе до миттєвої втрати авторизації всіма користувачами (скидання сесій). Для усунення цієї проблеми стан сесій повинен зберігатися виключно в зовнішньому розподіленому сховищі (наприклад, Redis Cluster або Memcached) або кодуватися у криптографічно підписаних токенах JWT, що передаються у заголовках запиту. Це дозволяє будь-якому вузлу як синього, так і зеленого середовища безшовно обробляти запити одного й того самого користувача.

### 8. Розрив розподіленого трейсингу та контексту спанів
Під час одночасної присутності двох активних версій системи в логах та трейсах (OpenTelemetry / Jaeger / Zipkin) виникає плутанина, якщо кожен запит не промаркований атрибутом версії. Контролер повинен гарантувати, що кожен вузол автоматично інжектує теги `service.version=v2.4.0` та `deployment.environment=green` у кореневий контекст розподіленого трейсингу. Це дозволяє команді спостережуваності миттєво фільтрувати спани нового релізу, відокремлюючи затримки нового коду від фонового шуму старого середовища.
