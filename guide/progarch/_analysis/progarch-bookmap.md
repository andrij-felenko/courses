# Курс «Program architecture» (progarch) — BOOK-МАПА

Лінза: крило книг під курс. Джерело правди — індекс `book-index-fresh.txt` (2446 тем, зріз 2026-07-05).
Перевірено книги: **programming (362), algorithms (251), communications (285), math (239)**.

Дуга курсу (задано): принципи коду → класичні патерни → архітектура застосунку → дані → паралельність → розподілені системи → високе навантаження → експлуатація. ~250 кроків, 9–12 модулів.

**Зведення цієї мапи:**
- до реюзу ref-ами — **~70 ядрових** наявних тем (+ ~20 запасних), з них basic:done ≈ 45;
- нові атоми — **~230** (з навмисним запасом понад курс): 5 нових галузей programming (~122), розширення 5 наявних галузей programming (~55), algorithms (~43), communications (5), math (6);
- склад курсу орієнтовно: ~70 `[ref]` наявних + ~140 `[nb]` нових атомів + ~40 `[own]` власних кроків ≈ 250.

Ескіз модульної сітки (для прив'язки атомів; фінальна структура — за іншою лінзою):

| M | Модуль | ~кроків |
|---|--------|---------|
| M1 | Принципи здорового коду | 20 |
| M2 | Класичні патерни | 24 |
| M3 | Архітектура застосунку | 22 |
| M4 | Дані і сховища | 24 |
| M5 | Паралельність в одному процесі | 22 |
| M6 | Мережа і API назовні | 20 |
| M7 | Розподілені системи: основи | 22 |
| M8 | Події і черги | 18 |
| M9 | Високе навантаження | 24 |
| M10 | Стійкість і безпека | 18 |
| M11 | Експлуатація | 22 |
| M12 | Синтез: проєктуємо системи (кейси) | 14 |

---

## 1. Наявні теми до реюзу (ref-и)

Статус вказано для `basic` (це те, що читає курс); `pending` = тема заведена в маніфест, стаття ще не написана — ref легальний, стаття напишеться загальною чергою письма.

### 1.1 book/programming

| ref | Назва | basic | Модуль |
|-----|-------|-------|--------|
| programming/software-engineering/abstraction-principle | Принцип абстракції | pending | M1 |
| programming/software-engineering/information-hiding | Приховування інформації | pending | M1 |
| programming/software-engineering/behavioral-subtyping | Поведінкова підтипізація (≈ LSP) | **done** | M1 |
| programming/software-engineering/interface-segregation | Принцип розділення інтерфейсів (ISP) | pending | M1 |
| programming/software-engineering/design-by-contract | Проєктування за контрактом | **done** | M1 |
| programming/software-engineering/defensive-programming | Захисне програмування | **done** | M1 |
| programming/software-engineering/error-handling | Жодна помилка не мовчить | **done** | M1 |
| programming/software-engineering/code-metrics | Метрики якості коду | pending | M1 |
| programming/software-engineering/code-review | Рев'ю коду | **done** | M1/M11 |
| programming/software-engineering/static-analysis | Статичний аналіз | **done** | M1 |
| programming/software-engineering/profiling | Профілювання | **done** | M9 |
| programming/software-engineering/fuzzing | Фаззинг | **done** | M10 (запас) |
| programming/code/version-control | Контроль версій і git | **done** | M1/M11 |
| programming/systems/tasks | Задачі | **done** | M5 |
| programming/systems/scheduler | Планувальник | **done** | M5 |
| programming/systems/context-switch | Перемикання контексту | **done** | M5 |
| programming/systems/atomicity-races | Атомарність і гонки | **done** | M5 |
| programming/systems/task-ipc | Черги й семафори | **done** | M5 |
| programming/systems/priority-inversion | Інверсія пріоритетів | **done** | M5 (запас) |
| programming/systems/coroutines | Корутини | pending | M5 |
| programming/systems/garbage-collection | Збирання сміття | pending | M3/M5 |
| programming/systems/heap-dynamic-memory | Купа | **done** | фон M5 |
| programming/systems/stack-lifo | Стек | **done** | фон |
| programming/systems/stack-overflow | Переповнення стека | **done** | фон |
| programming/systems/memory-ordering-barriers | Упорядкування пам'яті та бар'єри | **done** | M5 (запас) |
| programming/systems/log-structured-storage | Журнальне і log-structured сховище | **done** | M4 |
| programming/languages/raii | RAII | pending | M1/M5 |
| programming/languages/std-atomic | std::atomic і порядок пам'яті | **done** | M5 |
| programming/computer-architecture/cache | Кеш | **done** | M9 (фундамент кешування) |
| programming/computer-architecture/cache-coherence | Когерентність кешів | **done** | M5 (запас) |
| programming/computer-architecture/multicore | Багатоядерні процесори | **done** | M5 |
| programming/computer-architecture/virtual-memory | Віртуальна пам'ять | **done** | фон |
| programming/networking/sockets-tcp-udp | Сокети TCP/UDP | **done** | M6 |
| programming/networking/socket-api | API сокетів | pending | M6 |
| programming/security/buffer-overflow-security | Переповнення буфера як вразливість | pending | M10 |

Запас (реюз за потреби): `languages/rust-ownership` (done), `languages/bytecode-vm` (done), `languages/undefined-behavior` (done), `languages/zero-cost-abstractions` (done), `computer-architecture/branch-prediction` (done), `computer-architecture/ascii-utf8` (done), `software-engineering/heisenbug` (pending), `software-engineering/assert-panic` (done), `software-engineering/covariance-contravariance` (pending), `software-engineering/pair-programming` (pending), `software-engineering/errno` (pending), `systems/function-pointers` (pending), `systems/dynamic-linking` (pending), `systems/persistent-storage` (done), `embedded-systems/graceful-degradation` (done — резильєнтність, M10).

### 1.2 book/algorithms

| ref | Назва | basic | Модуль |
|-----|-------|-------|--------|
| algorithms/data-structures/binary-search | Двійковий пошук | pending | M4 (фон індексів) |
| algorithms/data-structures/queue-fifo | Черга: FIFO і кільцевий буфер | pending | M5/M8 |
| algorithms/data-structures/ring-buffer | Кільцевий буфер | pending | M5 (запас) |
| algorithms/data-structures/priority-queue | Черга з пріоритетом (купа) | pending | M5 (запас) |
| algorithms/data-structures/key-value-store | Сховище «ключ — значення» | pending | M4 |
| algorithms/data-structures/copy-on-write | Copy-on-write | pending | M4/M5 |
| algorithms/data-structures/recursion | Рекурсія | pending | фон |
| algorithms/design-paradigms/backpressure | Протитиск (backpressure) | pending | **M8 — ключовий** |
| algorithms/graph-algorithms/topological-sort | Топологічне сортування | pending | M3 (граф залежностей) |
| algorithms/graph-algorithms/congestion-control | Управління перевантаженням мережі | pending | M6/M9 |
| algorithms/parallel-distributed/monitor-sync | Монітори й умовні змінні | pending | M5 |
| algorithms/data-compression/why-compress | Навіщо стискати | **done** | M6 (запас) |
| algorithms/data-compression/deflate | DEFLATE | **done** | M6 (gzip у HTTP) |
| algorithms/data-compression/adaptive-bitrate | Адаптивний бітрейт | pending | **M9 — кейс YouTube** |

Запас: `data-structures/rolling-hash` (pending — дедуплікація/чанкінг), `data-structures/cache-oblivious` (pending), `data-structures/abstract-syntax-tree` (pending), `graph-algorithms/dijkstra` (done), `graph-algorithms/routing-algorithms` (pending), `string-geometry-streaming/regex-engine` (pending), `data-compression/entropy` (done), `complexity-computability/loop-variant` (pending).

### 1.3 book/communications

| ref | Назва | basic | Модуль |
|-----|-------|-------|--------|
| communications/protocols/tcp-vs-udp | TCP проти UDP | **done** | M6 |
| communications/protocols/quic-protocol | QUIC та HTTP/3 | pending | M6 |
| communications/protocols/mqtt | MQTT | **done** | M8 (pub/sub-прецедент) |
| communications/protocols/flow-control | Керування потоком | **done** | M6/M8 |
| communications/protocols/ntp-sync | NTP: синхронізація часу | pending | **M7 — час у розподілених** |
| communications/networks/mac-ip-arp | MAC, IP і ARP | **done** | фон M6 |
| communications/networks/ip-routing | Маршрутизація | **done** | фон M6 |
| communications/networks/nat | NAT | pending | M6 |
| communications/networks/dhcp-dns | DHCP і DNS | pending | M6/M7 (discovery) |
| communications/networks/latency-reliability | Затримка й надійність | **done** | M6/M9 |
| communications/networks/queue-theory-networks | Черги в мережах: затримка і втрати | pending | **M9** |
| communications/networks/adaptive-bitrate | Адаптивний бітрейт (ABR) | pending | **M9 — кейс YouTube** |
| communications/networks/video-transmission | Передача відео | **done** | M9 (кейс) |
| communications/cryptographic-comm/public-key-crypto | Криптографія з відкритим ключем | pending | M10 (база TLS) |
| communications/synchronization/clock-offset-drift | Дрейф годинників | pending | **M7** |

Запас: `networks/bgp` (pending — anycast/CDN), `networks/cidr` (pending), `networks/jitter` (pending), `networks/bandwidth-loss` (done), `protocols/packet-design` (done — дизайн протоколу), `protocols/reliable-link` (done), `protocols/arq-protocol`, `protocols/sliding-window-arq`, `protocols/sequence-numbering`, `protocols/nat-traversal` (усі pending), `synchronization/timestamps` (pending).

### 1.4 book/math

| ref | Назва | basic | Модуль |
|-----|-------|-------|--------|
| math/probability/poisson-process | Пуассонівський процес | pending | **M9 — модель прибуття запитів** |
| math/probability/heavy-tail-distributions | Розподіли з важкими хвостами | pending | **M9 — хвости латентності** |
| math/probability/gaussian-distribution | Нормальний розподіл | pending | фон |
| math/probability/mean-variance | Середнє й дисперсія | **done** | фон |
| math/number-theory/modular-arithmetic | Модульна арифметика | **done** | M9 (фон хешування) |
| math/combinatorics/graph-theory | Теорія графів | **done** | фон M7 |
| math/logic-foundations/finite-automata | Скінченні автомати | **done** | M2 (патерн State) |

Запас: `statistics/exponential-smoothing` (pending — згладжування метрик, M11), `statistics/median-robust-stats` (pending), `probability/central-limit` (done), `numerical-analysis/ieee754` (done).

---

## 2. Нові галузі book/programming

> Формат атома: `slug` — Назва — (модуль курсу | запас). Вставки — рядком під власником.

### 2.1 `design-patterns` — «Патерни» *(нова галузь)*

**scope:** Повторювані розв'язки в об'єктному дизайні: породжувальні, структурні й поведінкові патерни GoF, їхні сучасні форми, впровадження залежностей та антипатерни.

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | what-is-pattern | Що таке патерн проєктування | M2 |
|   | | вставка hist-gof.md: від мови патернів Крістофера Александера (архітектура будівель) до каталогу «банди чотирьох», 1994 | |
| 2 | singleton | Сінглтон | M2 |
|   | | вставка proj-singleton-threadsafe.md: лінивий потокобезпечний сінглтон і чому DI його витісняє — робочий код | |
| 3 | factory-method | Фабричний метод | M2 |
| 4 | abstract-factory | Абстрактна фабрика | M2 |
| 5 | builder | Будівельник | M2 |
| 6 | prototype | Прототип | запас |
| 7 | object-pool | Пул об'єктів | M2 (місток до пулів з'єднань M9) |
| 8 | adapter | Адаптер | M2 |
| 9 | decorator | Декоратор | M2 |
| 10 | facade | Фасад | M2 |
| 11 | proxy | Проксі | M2 (місток до reverse-proxy M9) |
| 12 | composite | Компонувальник | M2 |
| 13 | bridge | Міст | запас |
| 14 | flyweight | Легковаговик | запас |
| 15 | observer | Спостерігач | M2 (місток до pub/sub M8) |
| 16 | strategy | Стратегія | M2 |
| 17 | command | Команда | M2 (місток до черг задач M8) |
| 18 | state | Стан | M2 (ref: math/logic-foundations/finite-automata) |
| 19 | template-method | Шаблонний метод | M2 |
| 20 | iterator | Ітератор | M2 |
| 21 | chain-of-responsibility | Ланцюжок обов'язків | M2 (місток до middleware M3) |
| 22 | mediator | Посередник | запас |
| 23 | memento | Знімок (Memento) | запас |
| 24 | visitor | Відвідувач | запас |
| 25 | null-object | Null-об'єкт | запас |
| 26 | dependency-injection | Впровадження залежностей (DI) | M2/M3 |
|   | | вставка proj-di-container.md: мінімальний DI-контейнер руками — реєстрація, резолвінг, життєві цикли | |
| 27 | anti-patterns | Антипатерни: god object, spaghetti, golden hammer | M2 |

### 2.2 `software-design` — «Дизайн» *(нова галузь)*

**scope:** Принципи структурування коду й застосунків: зв'язність і зачеплення, SOLID, шари й межі модулів, архітектурні стилі від моноліта до мікросервісів і подієвих систем.

*Примітка розмежування:* принципи, що ВЖЕ живуть в `software-engineering` (abstraction-principle, information-hiding, interface-segregation, behavioral-subtyping), НЕ дублюємо — курс бере їх ref-ами звідти. Можливий пізніший `git mv` у software-design — окрема чистка, не в цьому курсі.

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | coupling-cohesion | Зачеплення і зв'язність | M1 |
| 2 | single-responsibility | Принцип єдиної відповідальності (SRP) | M1 |
| 3 | open-closed | Принцип відкритості-закритості (OCP) | M1 |
| 4 | dependency-inversion | Принцип інверсії залежностей (DIP) | M1 |
| 5 | composition-inheritance | Композиція проти успадкування | M1 |
| 6 | dry-kiss-yagni | DRY, KISS, YAGNI | M1 |
| 7 | law-of-demeter | Закон Деметри | запас |
| 8 | immutability | Незмінність як прийом дизайну | M1 |
| 9 | pure-functions-side-effects | Чисті функції й побічні ефекти | M1 |
| 10 | refactoring | Рефакторинг | M1 |
|    | | вставка hist-refactoring.md: як практика з Smalltalk-спільноти стала книгою Фаулера й кнопкою в IDE | |
| 11 | code-smells | Запахи коду | M1 (запас) |
| 12 | technical-debt | Технічний борг | M1 |
|    | | вставка hist-tech-debt.md: метафора Ворда Каннінгема (1992) і що вона означала насправді | |
| 13 | layered-architecture | Шарова архітектура | M3 |
| 14 | hexagonal-architecture | Гексагональна архітектура (порти й адаптери) | M3 |
| 15 | clean-architecture | Чиста архітектура: правило залежностей | M3 (запас) |
| 16 | mvc-mvp-mvvm | MVC та його родина | M3 |
| 17 | modular-monolith | Модульний моноліт | M3 |
| 18 | microservices | Мікросервіси: межі сервісів, ціна розрізання | M3 |
|    | | вставка hist-amazon-two-pizza.md: мандат Безоса 2002 про сервісні інтерфейси і «команди на дві піци» | |
| 19 | event-driven-architecture | Подієва архітектура | M3/M8 |
| 20 | plugin-architecture | Плагінна архітектура | запас |
| 21 | api-design | Дизайн API: контракти, еволюція, сумісність | M3 |
| 22 | config-design | Конфігурація застосунку: код, середовище, файли | M3 |
| 23 | twelve-factor-app | Дванадцятифакторний застосунок | M3/M11 |
| 24 | domain-driven-design | DDD: обмежені контексти й спільна мова | M3 |
| 25 | cqrs | CQRS: розділення читання й запису | M4/M8 |
| 26 | event-sourcing | Подієвий журнал як джерело правди (event sourcing) | M8 |
| 27 | architecture-decision-records | Записи архітектурних рішень (ADR) | запас |

### 2.3 `distributed-systems` — «Розподілені системи» *(нова галузь)*

**scope:** Системи з багатьох вузлів, з'єднаних ненадійною мережею: моделі узгодженості, реплікація і шардинг, черги повідомлень, координація, стійкість до відмов і доставлення контенту.

*Розмежування з algorithms/parallel-distributed:* там — самі алгоритми з механікою і доведеннями (Raft, Paxos, годинники Лампорта, gossip); тут — системні концепти й практики побудови (що реплікуємо, як шардимо, чим захищаємось).

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | distributed-fallacies | Оманливі припущення розподілених систем | M7 |
|   | | вставка hist-fallacies.md: вісім хиб Пітера Дойча і Sun Microsystems 90-х | |
| 2 | cap-theorem | Теорема CAP | M7 |
|   | | вставка hist-cap-brewer.md: гіпотеза Брюера (2000) → доведення Ґілберт–Лінч (2002) → уточнення «12 років потому» | |
| 3 | consistency-models | Моделі узгодженості: від лінеаризовності до підсумкової | M7 |
| 4 | eventual-consistency | Підсумкова узгодженість і сесійні гарантії | M7 |
| 5 | replication-leader-follower | Реплікація «лідер — послідовники» | M7 |
| 6 | multi-leader-replication | Реплікація з кількома лідерами | M7 (запас) |
| 7 | leaderless-replication | Безлідерна реплікація і кворуми | M7 |
|   | | вставка hist-dynamo.md: Amazon Dynamo (2007) — кошик, який не можна губити, і мода на eventual consistency | |
| 8 | partitioning-sharding | Шардинг: горизонтальне розбиття даних | M9 |
| 9 | rebalancing | Ребалансування шардів | M9 (запас) |
| 10 | distributed-transactions | Розподілені транзакції: чому боляче | M7/M8 |
| 11 | saga-pattern | Сага: довга транзакція як ланцюг компенсацій | M8 |
| 12 | outbox-pattern | Транзакційний outbox | M8 |
| 13 | idempotency | Ідемпотентність операцій | M8 |
| 14 | delivery-guarantees | Гарантії доставлення: at-most-, at-least-, exactly-once | M8 |
| 15 | message-queue | Черга повідомлень: брокер, ack, мертві листи | M8 |
|    | | вставка comp-message-brokers.md: клас систем-брокерів (черги, топіки, роутери) без прив'язки до моделей | |
| 16 | publish-subscribe | Публікація-підписка | M8 |
| 17 | event-log | Журнал подій як шина (модель Kafka) | M8 |
|    | | вставка hist-kafka-linkedin.md: як LinkedIn упирався в ETL-локшину і народив розподілений лог | |
| 18 | service-discovery | Виявлення сервісів | M7 |
| 19 | api-gateway | API-шлюз | M9 |
|    | | вставка comp-api-gateways.md: клас шлюзів — маршрутизація, автентифікація, ліміти на вході | |
| 20 | load-balancing | Балансування навантаження: L4/L7 і алгоритми | M9 |
|    | | вставка comp-load-balancers.md: клас балансерів — апаратні, програмні, DNS-рівень | |
| 21 | reverse-proxy | Зворотний проксі | M9 |
| 22 | cdn | Мережа доставлення контенту (CDN) | **M9 — серце кейсу YouTube** |
|    | | вставка hist-akamai.md: з задачі Тіма Бернерса-Лі в MIT (1995) до Akamai — математики розвантажують веб | |
| 23 | distributed-cache | Розподілений кеш | M9 |
|    | | вставка hist-memcached-facebook.md: як Facebook масштабував memcached (леєзи, регіони) — стаття NSDI'13 | |
| 24 | caching-strategies | Стратегії кешування: cache-aside, write-through/behind | M9 |
|    | | вставка proj-cache-aside.md: cache-aside поверх key-value сховища з TTL — робочий код | |
| 25 | cache-invalidation | Інвалідація кешу і лавина (stampede) | M9 |
| 26 | rate-limiting | Обмеження швидкості: token bucket, ковзне вікно | M9 |
|    | | вставка proj-token-bucket.md: token-bucket-лімітер на ~50 рядків з тестом на сплеск | |
| 27 | circuit-breaker | Запобіжник (circuit breaker) | M10 |
| 28 | retries-backoff | Повтори з експоненційною паузою і джитером | M10 |
| 29 | bulkhead-isolation | Перебірки (bulkhead) й ізоляція відмов | M10 |
| 30 | timeouts-deadlines | Таймаути й бюджети часу | M10 |
| 31 | health-checks | Перевірки живості й готовності | M10/M11 |
| 32 | split-brain | Розщеплення мозку і fencing | M7 (запас) |
| 33 | distributed-locks | Розподілені замки | запас |

### 2.4 `web-backend` — «Веб-бекенд» *(нова галузь)*

**scope:** Серверна частина вебзастосунків: життєвий цикл HTTP-запиту, стилі API, стан і сесії, автентифікація й авторизація, кешування відповідей і робота з файлами.

*Розмежування:* протоколи на дроті (HTTP, TLS, WebSocket) — у communications; тут — що робить із ними застосунок.

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | request-lifecycle | Життєвий цикл HTTP-запиту на сервері | M6 |
| 2 | rest-api | REST: ресурси, дієслова, статуси | M6 |
|   | | вставка hist-fielding-rest.md: дисертація Роя Філдінга (2000) — архітектурний стиль, який усі цитують і мало хто читав | |
| 3 | api-versioning | Версіонування API | M6 |
| 4 | pagination-filtering | Пагінація і фільтрація: offset проти курсора | M6 (місток до стрічок M12) |
| 5 | sessions-state | Сесії і стан: stateful проти stateless | M6 |
| 6 | cookies | Кукі: механіка й атрибути безпеки | M6 |
| 7 | authentication | Автентифікація: паролі, токени, MFA | M10 |
| 8 | jwt-tokens | JWT: сесії без стану | M10 |
|   | | вставка proj-jwt-auth.md: видача і перевірка JWT з ротацією ключів — робочий код | |
| 9 | oauth-oidc | OAuth 2.0 та OpenID Connect | M10 |
| 10 | authorization-models | Авторизація: RBAC і ABAC | M10 |
| 11 | http-caching | HTTP-кешування: Cache-Control, ETag, валідація | M9 |
| 12 | file-uploads | Завантаження файлів: multipart, presigned URL, великі об'єкти | M9 (кейс YouTube: upload) |
| 13 | webhooks | Вебхуки | M8 (запас) |
| 14 | server-sent-events | SSE і довгі з'єднання | запас |
| 15 | graphql | GraphQL | запас |
| 16 | idempotency-keys | Ключі ідемпотентності в API | запас (ref distributed-systems/idempotency) |

### 2.5 `operations` — «Експлуатація» *(нова галузь)*

**scope:** Життя софту в проді: доставлення й розгортання, контейнери та оркестрація, спостережність, надійність (SRE), інциденти й планування потужностей.

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | ci-cd | Неперервна інтеграція і доставлення (CI/CD) | M11 |
| 2 | containers | Контейнери: ізоляція без віртуалки | M11 |
|   | | вставка hist-docker.md: від chroot і Solaris Zones через cgroups Google до вибуху Docker (2013) | |
| 3 | virtualization | Віртуальні машини й гіпервізори | M11 |
| 4 | container-orchestration | Оркестрація контейнерів | M11 |
|   | | вставка comp-orchestrators.md: клас оркестраторів — планувальник, бажаний стан, self-healing (Borg/Kubernetes-модель без версійної конкретики) | |
| 5 | infrastructure-as-code | Інфраструктура як код | M11 |
| 6 | deployment-strategies | Стратегії розгортання: blue-green, канарки, rolling | M11 |
| 7 | feature-flags | Прапорці функцій | M11 |
| 8 | observability | Спостережність: метрики, логи, траси | M11 |
|   | | вставка comp-observability-stacks.md: клас систем спостережності — колектор, сховище часових рядів, дашборди, алерти | |
| 9 | metrics-monitoring | Метрики й моніторинг: RED і USE | M11 |
| 10 | structured-logging | Структуровані логи | M11 |
| 11 | distributed-tracing | Розподілене трасування | M11 |
|    | | вставка hist-dapper.md: Google Dapper (2010) — папір, з якого виросли Zipkin/Jaeger і trace-id у кожному запиті | |
| 12 | slo-sli-sla | SLI, SLO, SLA і бюджет помилок | M11 |
|    | | вставка hist-google-sre.md: як у Google вигадали професію SRE і чому «100% — неправильна ціль» | |
| 13 | alerting | Алерти без шуму | M11 |
| 14 | incident-response | Реагування на інциденти | M11 |
| 15 | postmortems | Постмортеми без пошуку винних | M11 (запас) |
| 16 | capacity-planning | Планування потужностей | M9/M11 |
|    | | вставка hist-twitter-fail-whale.md: «кит невдачі» Twitter 2008–2012 — що ламалось і як переписували | |
| 17 | autoscaling | Автомасштабування | M9/M11 |
| 18 | load-testing | Навантажувальне тестування | M11 |
|    | | вставка proj-load-test.md: сценарій навантаження з профілем прибуття і звітом перцентилів — робочий код | |
| 19 | chaos-engineering | Хаос-інженерія | M11 |
|    | | вставка hist-chaos-monkey.md: Netflix переїжджає в хмару (2010) і випускає мавпу, що вбиває сервери | |
| 20 | availability-nines | Доступність і «дев'ятки» | M11 |
|    | | вставка math-nines.md: послідовні й паралельні відмови, множення доступностей, бюджет простою | |
| 21 | graceful-shutdown | Коректне вимкнення: drain і SIGTERM | M11 |
| 22 | secrets-management | Керування секретами | запас |
| 23 | disaster-recovery | Аварійне відновлення: RPO і RTO | запас |

---

## 3. Розширення наявних галузей book/programming

### 3.1 `databases` (галузь існує, зараз 2 чужі топіки — див. §6)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | relational-model | Реляційна модель | M4 |
|   | | вставка hist-codd.md: Едгар Кодд, IBM і реляційна революція проти ієрархічних БД | |
| 2 | sql-queries | SQL: вибірки, з'єднання, агрегати | M4 |
| 3 | transactions-acid | Транзакції та ACID | M4 |
| 4 | isolation-levels | Рівні ізоляції та аномалії | M4 |
|   | | вставка proj-isolation-demo.md: відтворюємо dirty read / non-repeatable read / phantom двома конкурентними сесіями | |
| 5 | mvcc | MVCC: багатоверсійність | M4 |
| 6 | write-ahead-log | Журнал випереджального запису (WAL) | M4 |
| 7 | database-indexes | Індекси: чому запит прискорюється | M4 (ref b-tree) |
| 8 | query-planner | Планувальник запитів і EXPLAIN | M4 |
| 9 | normalization | Нормалізація | M4 |
| 10 | denormalization | Денормалізація: коли порушувати правила | M4/M9 |
| 11 | orm | ORM: об'єктно-реляційне відображення | M4 |
| 12 | n-plus-one | Проблема N+1 | M4 |
| 13 | connection-pool | Пул з'єднань із базою | M4/M9 |
| 14 | read-replicas | Читальні репліки й розділення читання/запису | M9 |
| 15 | nosql-landscape | Ландшафт NoSQL: чотири родини | M4 |
|    | | вставка comp-nosql-classes.md: документні, ключ-значення, колонкові, графові — клас за класом, без конкретики версій | |
| 16 | document-databases | Документні бази | M4 |
| 17 | wide-column-stores | Широко-колонкові сховища (модель Bigtable) | M4 (запас) |
|    | | вставка hist-bigtable.md: Google Bigtable (2006) — таблиця на петабайт поверх GFS, мати Cassandra і HBase | |
| 18 | time-series-databases | Бази часових рядів | запас |
| 19 | graph-databases | Графові бази | запас |
| 20 | full-text-search | Повнотекстовий пошук | M4 (ref inverted-index) |
|    | | вставка comp-search-engines.md: клас пошукових рушіїв — індексатор, аналізатори, релевантність | |
| 21 | oltp-olap | OLTP і OLAP | M4 |
| 22 | columnar-storage | Колонкове зберігання для аналітики | запас |
| 23 | database-migrations | Міграції схеми | M4/M11 |
| 24 | change-data-capture | Захоплення змін даних (CDC) | запас |

### 3.2 `systems` (розширення — паралельність і IO для бекенду)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | process-vs-thread | Процеси й потоки ОС | M5 (наявний `tasks` — RTOS-кут) |
| 2 | deadlock | Взаємне блокування (deadlock) | M5 |
|   | | вставка hist-dining-philosophers.md: задача Дейкстри про обідніх філософів та умови Коффмана | |
| 3 | livelock-starvation | Лайвлок і голодування | M5 |
| 4 | thread-pool | Пул потоків | M5 |
|   | | вставка proj-thread-pool.md: пул потоків з чергою задач своїми руками — робочий код | |
| 5 | io-multiplexing | Мультиплексування вводу-виводу: select → epoll | M5 |
|   | | вставка hist-c10k.md: проблема C10K (Ден Кегель, 1999) — десять тисяч з'єднань як виклик епохи | |
| 6 | event-loop | Цикл подій | M5 |
|   | | вставка proj-event-loop.md: міні event loop на epoll/kqueue з таймерами — робочий код | |
| 7 | blocking-vs-nonblocking-io | Блокуючий і неблокуючий ввід-вивід | M5 (запас) |
| 8 | async-await | Async/await: кооперативна асинхронність | M5 (ref coroutines) |
| 9 | futures-promises | Ф'ючери й проміси | M5 |
| 10 | actor-model | Модель акторів | M5 |
|    | | вставка hist-erlang.md: Ericsson, комутатор AXD301 і «дев'ять дев'яток» — навіщо телефоністам актори | |
| 11 | csp-channels | Канали і CSP | M5 |
|    | | вставка hist-csp-hoare.md: папір Гоара (1978) і як CSP через 30 років проросло в Go | |
| 12 | green-threads | Зелені потоки і планувальник рантайму | M5 (запас) |
| 13 | zero-copy | Zero-copy: sendfile і splice | M9 (кейс YouTube: віддача файлів) |
| 14 | false-sharing | Хибне розділення кеш-ліній | запас |
| 15 | memory-mapped-files | mmap: файли як пам'ять | запас |

### 3.3 `networking` (розширення)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | rpc | Віддалений виклик процедур: ідея і граблі | M6 |
|   | | вставка hist-rpc.md: від Sun RPC і CORBA до сучасних фреймворків — чому «прозорість» провалилась | |
| 2 | grpc | gRPC: контракти і потоки поверх HTTP/2 | M6 |
| 3 | serialization-formats | Формати серіалізації: JSON, Protobuf, Avro, еволюція схем | M6 |
| 4 | connection-management | Керування з'єднаннями: keep-alive, пули, head-of-line | M6 (запас) |

### 3.4 `security` (розширення — веб-безпека для M10)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | web-vulnerability-classes | Класи веб-вразливостей (мапа OWASP) | M10 |
| 2 | sql-injection | SQL-ін'єкція | M10 |
|   | | вставка proj-sqli-demo.md: вразливий запит → експлойт → параметризація; робочий код до/після | |
| 3 | xss | Міжсайтовий скриптинг (XSS) | M10 |
| 4 | csrf | Підробка міжсайтових запитів (CSRF) | M10 |
| 5 | password-hashing | Зберігання паролів: сіль і повільні хеші | M10 |
| 6 | ddos | DDoS і базовий захист | M9/M10 |
|   | | вставка hist-ddos-cases.md: знакові атаки (Dyn 2016, GitHub 2018) і як їх поглинали | |
| 7 | least-privilege | Принцип найменших привілеїв | запас |
| 8 | supply-chain-security | Безпека ланцюга залежностей | запас |

### 3.5 `software-engineering` (розширення — тести; принципи вже там є)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | unit-testing | Модульні тести | M1 |
| 2 | test-doubles | Тестові двійники: стаби, моки, фейки | M1 |
| 3 | integration-e2e-testing | Інтеграційні та наскрізні тести | M1/M11 |
| 4 | tdd | Розробка через тести (TDD) | запас |
| 5 | property-based-testing | Тести властивостей | запас |
| 6 | contract-testing | Контрактні тести між сервісами | запас (мікросервіси M7) |

---

## 4. Нові теми book/algorithms

### 4.1 `complexity-computability` (розширення)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | big-o-notation | Нотація великого O | M1/фон — **діри зараз нема чим закрити, тема відсутня в книзі!** |
|   | | вставка math-asymptotics.md: формальні означення O/Ω/Θ, границі, ієрархія росту | |
| 2 | amortized-analysis | Амортизована складність | M4 (фон динамічних структур) |
| 3 | space-time-tradeoff | Компроміс пам'ять–час | запас |

### 4.2 `data-structures` (розширення — головний блок для модуля даних)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | linked-list | Зв'язаний список | фон (діра в книзі) |
| 2 | dynamic-array | Динамічний масив і амортизоване подвоєння | фон |
| 3 | hash-table | Хеш-таблиця | M4 — **діра: у книзі немає!** |
|   | | вставка math-birthday-load.md: колізії, парадокс днів народження, load factor | |
|   | | вставка proj-hash-table.md: хеш-таблиця з відкритою адресацією руками — робочий код | |
| 4 | hash-functions | Хеш-функції і колізії (некриптографічні) | M4 |
| 5 | binary-search-tree | Двійкове дерево пошуку | M4 |
| 6 | balanced-trees | Збалансовані дерева: AVL і червоно-чорні | M4 (запас) |
| 7 | b-tree | B-дерево | M4 (серце індексів БД) |
|   | | вставка hist-btree.md: Баєр і Мак-Крейт (Boeing, 1970) — дерево під диски, що пережило пів століття | |
| 8 | lsm-tree | LSM-дерево і компакція | M4 (ref systems/log-structured-storage) |
|   | | вставка hist-lsm.md: від паперу О'Ніла (1996) до LevelDB/RocksDB — чому запис виграв у читання | |
| 9 | skip-list | Список із пропусками | запас |
| 10 | bloom-filter | Фільтр Блума | M4/M9 |
|    | | вставка math-bloom.md: ймовірність хибного спрацювання, оптимальна кількість хешів | |
|    | | вставка proj-bloom-filter.md: фільтр Блума на бітовому масиві — робочий код | |
| 11 | consistent-hashing | Узгоджене хешування | M9 |
|    | | вставка hist-consistent-hashing.md: Каргер і компанія (MIT, 1997) → Akamai → кільце в кожній NoSQL | |
|    | | вставка proj-hash-ring.md: кільце з віртуальними вузлами; демонстрація мінімального переміщення ключів | |
| 12 | merkle-tree | Дерево Меркла | M7 (анти-ентропія, git) |
| 13 | trie | Префіксне дерево (trie) | запас |
| 14 | inverted-index | Інвертований індекс | M4 (пошук) |
| 15 | lru-cache | LRU-кеш і політики витіснення | M9 |
|    | | вставка proj-lru-cache.md: LRU на хеш-таблиці і двозв'язному списку, O(1) на операцію | |
| 16 | quicksort | Швидке сортування | запас |
| 17 | mergesort | Сортування злиттям | запас |
| 18 | external-sort | Зовнішнє сортування | запас (великі дані) |
| 19 | lock-free-queue | Неблокувальна черга | запас (M5) |
| 20 | graph-representations | Подання графів у пам'яті | запас |

### 4.3 `parallel-distributed` (розширення — алгоритмічне ядро M5/M7)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | amdahls-law | Закон Амдала (і Густафсона) | M5 |
|   | | вставка math-amdahl.md: виведення, асимптоти, межі прискорення | |
| 2 | work-stealing | Крадіжка роботи (work stealing) | запас |
| 3 | map-reduce | MapReduce | M7 |
|   | | вставка hist-mapreduce.md: Google 2004 — індексувати веб фермами дешевих машин; народження Hadoop | |
| 4 | lamport-clocks | Логічні годинники Лампорта | M7 |
|   | | вставка hist-lamport-time.md: папір 1978 «Time, Clocks…» — найцитованіший текст розподілених систем | |
| 5 | vector-clocks | Векторні годинники | M7 |
| 6 | consensus-problem | Задача консенсусу і неможливість FLP | M7 |
| 7 | raft | Консенсус Raft | M7 |
|   | | вставка proj-leader-election.md: іграшкові вибори лідера з таймаутами й термами — робочий код | |
| 8 | paxos | Paxos | M7 (запас) |
|   | | вставка hist-part-time-parliament.md: Лампортів «парламент острова Паксос» — жарт, якого ніхто не зрозумів | |
| 9 | leader-election | Вибори лідера | M7 |
| 10 | two-phase-commit | Двофазний коміт (2PC) | M7/M8 |
| 11 | gossip-protocol | Пліткові протоколи | M7 |
| 12 | crdt | CRDT: безконфліктні репліковані типи | запас |
| 13 | distributed-snapshot | Розподілений знімок (Chandy–Lamport) | запас |
| 14 | byzantine-faults | Візантійські відмови | запас |

### 4.4 `string-geometry-streaming` (розширення — потокові лічильники M9)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | hyperloglog | HyperLogLog: лічити унікальних майже без пам'яті | M9 (запас) |
| 2 | count-min-sketch | Count-Min Sketch | запас |
| 3 | reservoir-sampling | Резервуарна вибірка | запас |

### 4.5 `cryptographic-algorithms` (розширення — база для TLS/JWT)

| # | slug | Назва | Курс |
|---|------|-------|------|
| 1 | crypto-hash | Криптографічні хеш-функції | M10 |
| 2 | symmetric-encryption | Симетричне шифрування | M10 (запас) |
| 3 | key-exchange | Обмін ключами Діффі–Геллмана | M10 |
|   | | вставка hist-diffie-hellman.md: 1976, «New Directions in Cryptography» — ключ, яким не обмінювались | |
| 4 | digital-signature | Цифровий підпис | M10 |

---

## 5. Нові теми book/communications і book/math

### 5.1 communications

| # | Галузь/slug | Назва | Курс |
|---|-------------|-------|------|
| 1 | protocols/http | HTTP/1.1: протокол вебу | M6 — **діра: в книзі лише QUIC/HTTP-3!** |
|   | | вставка hist-http.md: від однорядкового GET Бернерса-Лі до keep-alive — як протокол для фізиків з'їв світ | |
| 2 | protocols/http2 | HTTP/2: мультиплексування і head-of-line | M6 |
| 3 | protocols/websocket | WebSocket | M6 |
| 4 | cryptographic-comm/tls | TLS: рукостискання, сертифікати, довіра | M10 (ref public-key-crypto) |
| 5 | networks/anycast | Anycast-маршрутизація | M9 (запас; CDN/DNS) |

### 5.2 math

| # | Галузь/slug | Назва | Курс |
|---|-------------|-------|------|
| 1 | probability/littles-law | Закон Літтла | **M9 — головна формула модуля навантаження** |
|   | | вставка math-littles-proof.md: доведення через усереднення за часом; межі застосовності | |
| 2 | probability/mm1-queue | Черга M/M/1 | M9 |
|   | | вставка math-mm1-derivation.md: рівняння балансу, ρ/(1−ρ), вибух затримки біля насичення | |
| 3 | probability/exponential-distribution | Експоненційний розподіл і безпам'ятність | M9 |
| 4 | probability/zipf-law | Закон Ципфа | M9 (гарячі ключі, кеш-хіти) |
| 5 | probability/birthday-paradox | Парадокс днів народження | запас (колізії хешів) |
| 6 | statistics/percentiles-quantiles | Перцентилі і квантилі (p50/p95/p99) | M9/M11 |

*Дзеркала (легітимно за каноном):* `math/probability/mm1-queue`+`littles-law` (математичний кут) ↔ `communications/networks/queue-theory-networks` (мережевий кут, існує pending); `algorithms/data-structures/lsm-tree` ↔ `programming/systems/log-structured-storage` (done).

---

## 6. Правила розкладки спірного (book / own / вставка)

1. **Патерн, принцип, механізм, структура** — самодостатній атом → **book**. Сінглтон, CAP, шардинг, event loop — усе це читається окремо, отже book (навіть якщо писалось «під курс»).
2. **«Еволюція нашого сервісу»**, наскрізна нитка («ростимо застосунок з моноліта до планетарного масштабу»), синтез кількох атомів, дизайн-сесії («проєктуємо YouTube/чат/стрічку») → **[own:] кроки guide**. Увесь M12 — own.
3. **Кейс компанії**: історія народження рішення → **вставка hist** при атомі-власнику (hist-kafka-linkedin при event-log, hist-dynamo при leaderless-replication); прийом руками → **proj**; великий багатовимірний розбір (YouTube цілком) → **own-крок**, і own-кроки теж можуть мати hist/proj-вставки за схемою.
4. **Алгоритм із механікою/доведенням** (Raft, consistent hashing, Bloom, годинники Лампорта) → **book/algorithms**; **системна практика застосування** (як шардимо, як інвалідуємо кеш, що реплікуємо) → **book/programming/distributed-systems**; «збираємо все в один сервіс» → own.
5. **Протокол на дроті** (HTTP, TLS, WebSocket, QUIC) → **communications** (прецедент: MQTT, QUIC уже там); **програмування поверх протоколу** (REST-дизайн, сесії, автентифікація) → **programming/web-backend**; RPC і серіалізація в коді → **programming/networking** (scope прямо містить RPC).
6. **Математична модель** (M/M/1, Літтл, Ципф, перцентилі, Амдал) → **math** (або algorithms для законів обчислень); інженерний кут тієї ж теми може дзеркалитись у своїй книзі — прецеденти дзеркал у репо є.
7. **Клас систем без конкретики моделей** (брокери, оркестратори, балансери, NoSQL-родини, observability-стеки) → **вставка comp** при атомі; конкретна технологія з власною ідеєю рівня LoRa/FreeRTOS/LLVM (Kafka-модель логу, gRPC, Docker-контейнери) → може бути повноцінним атомом.
8. **Конкуренція**: примітиви й механізми ОС/рантайму (deadlock, пули, epoll, async) → **programming/systems**; паралельні алгоритми і закони (Амдал, work stealing, консенсус) → **algorithms/parallel-distributed**.
9. **Не дублювати наявне** — курс ref-ає, а не переписує: LSP → `behavioral-subtyping` (done), ISP → `interface-segregation`, умовні змінні → `monitor-sync`, черги/семафори → `task-ipc`, async-корені → `coroutines`, кеш-фундамент → `computer-architecture/cache`.

---

## 7. Колізії slug-ів і зауваги до індексу

**Прямих колізій нема:** жодна пропонована пара (галузь, slug) не зайнята. Перевірено grep-ом за повним індексом: deadlock, event-loop, thread-pool, io-multiplexing, async-await, actor-model, hash-table, b-tree, lsm-tree, bloom-filter, consistent-hashing, merkle-tree, trie, inverted-index, lru-cache, big-o-notation, amortized-analysis, raft, paxos, lamport-clocks, vector-clocks, gossip-protocol, crdt, map-reduce, amdahls-law, singleton, factory-method, observer, decorator, strategy, adapter, facade, cap-theorem, sharding (partitioning-sharding), transactions-acid, isolation-levels, mvcc, http, http2, websocket, tls, grpc, rest-api, oauth-oidc, jwt-tokens, sql-injection, xss, csrf, containers, littles-law, mm1-queue, percentiles-quantiles, zipf-law, unit-testing, linked-list, dynamic-array, hyperloglog, refactoring, microservices, graphql, webhooks, anycast — усі відсутні.

**Омоніми в інших книгах** (не конфлікт — шляхи різні, але авторам знати):
- `electronics/components/circuit-breaker` («Автомат захисту», електрика) ↔ наш `programming/distributed-systems/circuit-breaker` — свідомий омонім, термін усталений в обох світах;
- `math/information-theory/singleton-bound` («Межа Сінглтона») ↔ `design-patterns/singleton`;
- `programming/embedded-systems/health-monitor` ↔ наш `distributed-systems/health-checks` — різні речі;
- `programming/embedded-systems/graceful-degradation` (done) ↔ наш `operations/graceful-shutdown` — різні теми; перша сама по собі гарний ref для M10;
- `math/statistics/exponential-smoothing` ↔ наш `math/probability/exponential-distribution` — різні теми.

**Помічені дублі/сироти в наявному індексі** (не чіпати в цьому курсі, кандидати на окрему чистку):
- `math/probability/normal-distribution` і `math/probability/gaussian-distribution` — дубль; курсу ref-ати `gaussian-distribution`;
- `math/probability/central-limit` (done) і `central-limit-theorem` (pending) — дубль; ref-ати done;
- `programming/databases/endianness` і `fat-filesystem` — чужі темі галузі (сліди embedded-скаутів); розширення §3.1 їх не зачіпає;
- пари типу `spi-modes`/`cpol-cpha`, `smbus`/`smbus-protocol` в communications — існуючий стиль книги допускає, на курс не впливає.

---

## 8. Покриття модулів курсу цією мапою (контрольний зріз)

| M | Основні ref (наявні) | Основні nb (нові атоми) | own |
|---|----------------------|--------------------------|-----|
| M1 | design-by-contract, error-handling, defensive-programming, behavioral-subtyping, interface-segregation, abstraction-principle, information-hiding, code-review, static-analysis, version-control | coupling-cohesion, SRP/OCP/DIP, composition-inheritance, dry-kiss-yagni, immutability, pure-functions, refactoring, technical-debt, unit-testing, test-doubles, big-o-notation | 1–2 наскрізні |
| M2 | finite-automata (для State) | what-is-pattern + ~18 патернів GoF + DI + anti-patterns | 2–3 (патерни в живій кодовій базі) |
| M3 | garbage-collection, topological-sort | layered/hexagonal/mvc, modular-monolith, microservices, event-driven, api-design, config-design, twelve-factor, ddd, adr | 3–4 (еволюція застосунку) |
| M4 | key-value-store, log-structured-storage, binary-search, copy-on-write | relational-model…migrations (§3.1), hash-table, b-tree, lsm-tree, bloom-filter, inverted-index, amortized-analysis | 2–3 (вибір сховища) |
| M5 | tasks, scheduler, context-switch, atomicity-races, task-ipc, monitor-sync, coroutines, std-atomic, multicore, priority-inversion | process-vs-thread, deadlock, livelock, thread-pool, io-multiplexing, event-loop, async-await, futures, actor-model, csp-channels, amdahls-law | 2 (архітектури серверів) |
| M6 | sockets-tcp-udp, socket-api, tcp-vs-udp, quic-protocol, mac-ip-arp, ip-routing, nat, dhcp-dns, flow-control, deflate | http, http2, websocket, request-lifecycle, rest-api, api-versioning, pagination, sessions, cookies, rpc, grpc, serialization-formats | 1–2 |
| M7 | ntp-sync, clock-offset-drift, graph-theory, dhcp-dns | distributed-fallacies, cap-theorem, consistency-models, eventual-consistency, реплікації ×3, lamport/vector-clocks, consensus, raft, leader-election, 2pc, gossip, merkle-tree, service-discovery, map-reduce | 2–3 |
| M8 | backpressure, mqtt, flow-control, queue-fifo | message-queue, publish-subscribe, event-log, event-sourcing, cqrs, saga, outbox, idempotency, delivery-guarantees | 2 (проєктуємо конвеєр подій) |
| M9 | queue-theory-networks, adaptive-bitrate ×2, video-transmission, poisson-process, heavy-tail, cache, profiling, congestion-control, modular-arithmetic | littles-law, mm1-queue, exponential-distribution, zipf-law, percentiles, sharding, rebalancing, consistent-hashing, lru-cache, caching-strategies, cache-invalidation, distributed-cache, cdn, load-balancing, reverse-proxy, api-gateway, rate-limiting, http-caching, file-uploads, zero-copy, read-replicas, autoscaling, hyperloglog | 2–3 (**кейс YouTube**) |
| M10 | public-key-crypto, buffer-overflow-security, fuzzing, graceful-degradation | circuit-breaker, retries-backoff, bulkhead, timeouts, health-checks, tls, crypto-hash, key-exchange, digital-signature, authentication, jwt, oauth-oidc, authorization-models, web-vulnerability-classes, sqli/xss/csrf, password-hashing, ddos | 1–2 |
| M11 | version-control, code-review, exponential-smoothing | ci-cd, containers, virtualization, orchestration, iac, deployment-strategies, feature-flags, observability, metrics, logging, tracing, slo, alerting, incident-response, capacity-planning, load-testing, chaos, nines, graceful-shutdown, migrations | 1–2 |
| M12 | (реюз пройденого) | — | ~12–14 own: чат-месенджер, стрічка новин, URL-shortener, платіжка, YouTube-розбір повний, капстоун |

Разом: ~70 ref + ~140 nb + ~40 own ≈ 250 кроків. Книжковий запас понад курс — ~80 атомів (позначені «запас»), лишаються в книгах як pending на загальну чергу письма.
