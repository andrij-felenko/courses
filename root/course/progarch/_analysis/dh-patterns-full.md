# Лінза «ПОВНИЙ КАТАЛОГ ПАТЕРНІВ І ПІДХОДІВ» — розширення progarch до ~500 кроків

**Курс:** guide/progarch (перепроєктування, універсальний курс архітектури; Digital Homes — наскрізний приклад, не організуючий принцип; «Квиток» вилучено).
**База:** `guide/progarch/_plan.md` (264 кроки, прочитано повністю) + звіти `_analysis/` + індекс книг `book-index-fresh.txt` (2446 рядків, усі ref-и звірено).
**Задача лінзи:** ВСІ класичні патерни і головні каталоги поза GoF + підходи до проєктування/програмування + принципи-обходи проблем — незалежно від потреб прикладу. Для кожного: `[nb:…]`/`[ref:…]`, місце в дузі, залежності, атом чи прийом.

**Дуга-якір.** Місця вказую за фазами базової дуги (вона зберігається): М1 принципи → М2 патерни → М3 архітектура застосунку → М4 дані → М5 паралельність → М6 мережа/API → М7 розподілені дані → М8 сервіси/події → М9 високе навантаження → М10 експлуатація. У 500-кроковій розкладці фази товстішають і діляться (див. §15), але порядок введення понять — цей.

---

## 1. Зведення лінзи

| Категорія | Нових атомів у курс | З них промоти «запасу» плану | Цілком нові nb | Прийоми/інлайн (без окремого кроку) |
|---|---|---|---|---|
| §2 GoF до 23 (+null-object) | 8 | 7 | 1 (interpreter) | — |
| §3 PoEAA-ядро | 8 | 0 | 8 | 4 (offline locks, front-controller, transaction script, value object→запас) |
| §4 EIP (Хоп/Вульф) | 7 | 0 | 7 | 6 (request-reply, return-address, resequencer, priority-channel, envelope, idempotent-receiver→ref) |
| §5 Конкурентні патерни | 8 | 2 | 6 | 5 (half-sync/half-async, leader-followers, active-object, balking, TLS) |
| §6 Resilience / cloud | 7 (+1 опц.) | 2 | 5 (+1) | 6 (throttling, ambassador, gateway-aggregation, valet-key, gatekeeper, geode) |
| §7 Парадигми | 4 (+1 own) | 1 | 3 | 2 (declarative-vs-imperative, service-locator-контраст) |
| §8 Методики | 4 (+2 ref) | 2 | 2 | 3 (contract-first, architecture-review, trunk-based) |
| §9 Mitigation-прийоми | 5 (+1 опц.) | 2 | 3 (+1) | 8 (kill-switch, shadow traffic, dual-write, backfill, brownout, crash-only, steady-state, N/N+1) |
| **Разом** | **51 (+2 опц.)** | **16** | **35 (+2)** | **34** |

Додатково: 1 own-крок «Парадигми як інструменти» + 8 кластерів варіантних own-статей (§11, ~24–30 кроків-кандидатів) + ~25 вставок (розкидані по секціях). Внесок лінзи в бюджет 500: **~77–82 кроки** (51 атом + 1 own + варіантні кластери), без урахування опційних.

Ключова знахідка: **interpreter відсутній і в курсі, і в «запасі» базового плану** — GoF було 22 з 23 навіть із запасом. З цією лінзою GoF рівно 23 у курсі.

---

## 2. GoF повністю: 23 патерни в курс

Базовий план мав 16 GoF у курсі (4 породжувальні + 5 структурних + 7 поведінкових) і 7 у запасі. Промотуємо 6 GoF-запасних + null-object (не GoF, але в тому ж русі) і додаємо interpreter.

Усі — **атоми** галузі `programming/design-patterns` (нова, колізій зі слагами плану немає).

| Крок | Розмітка | Звідки | Місце в дузі | Спирається на | Приклади доменів |
|---|---|---|---|---|---|
| Прототип: створення копіюванням | [nb:programming/design-patterns/prototype] | запас→курс | М2, розділ «Породжувальні» (після builder) | what-is-pattern; вперед — copy-on-write (ref М3) | ігри: спавн сутностей з еталона; редактори: дублювання фігур; конфіги-шаблони DH-сцен |
| Міст: розвести абстракцію і реалізацію | [nb:programming/design-patterns/bridge] | запас→курс | М2, розділ «Структурні» (після adapter, поруч із decorator) | adapter, composition-inheritance (М1) | GUI-тулкіт × платформи (веб/мобайл/десктоп); драйвер × транспорт у прошивці — луна [ref:programming/software-engineering/hardware-abstraction-layer] (pending) |
| Легковаговик: тисячі об'єктів на спільному стані | [nb:programming/design-patterns/flyweight] | запас→курс | М2, «Структурні» (після composite) | immutability-ідея (формально М3 — дати інтуїцію інлайном), object-pool контрастом | гліфи текстового редактора; частинки/тайли гри; інтернування рядків; типи датчиків DH (один descriptor на тисячі приладів) |
| Посередник: вузол взаємодії замість павутиння | [nb:programming/design-patterns/mediator] | запас→курс | М2, «Поведінкові» (поруч з observer) | observer | діалогові форми UI; авіадиспетчер; хаб DH — буквальний медіатор пристроїв; тизер: медіатор між процесами = брокер (М8) |
| Хранитель: знімок стану для відкату | [nb:programming/design-patterns/memento] | запас→курс | М2, «Поведінкові» (після state) | state | undo в десктоп-редакторі; save-стани емуляторів/ігор; тизер: знімки event sourcing (М8 вже посилається: «знімки — це memento!») |
| Відвідувач: нова операція без зміни класів | [nb:programming/design-patterns/visitor] | запас→курс | М2, «Поведінкові» (розділ «Обхід», після iterator/composite) | composite, iterator | проходи компілятора по AST — луна [ref:algorithms/data-structures/abstract-syntax-tree] (pending); експорт сцени гри; звіти по дереву пристроїв DH |
| Інтерпретатор: мова задачі як об'єктна модель | [nb:programming/design-patterns/interpreter] | **НОВИЙ (діри навіть у запасі)** | М2, «Поведінкові», одразу після visitor | composite, visitor | правила автоматизації DH («якщо рух і ніч — світло») як міні-DSL; формули електронних таблиць; фільтри запитів; луна [ref:algorithms/string-geometry-streaming/regex-engine] (pending) |
| Null Object: відсутність як об'єкт | [nb:programming/design-patterns/null-object] | запас→курс | М2, розділ «Поза каталогом GoF» (перед anti-patterns) | strategy (виродження), error-handling (М1) | no-op логер; заглушка датчика, якого нема в кімнаті; NullRenderer headless-режиму гри |

Вставки: `proj-rules-dsl.md` (interpreter — робочий міні-DSL правил DH), `proj-undo-stack.md` (memento — undo десктоп-клієнта), `proj-particle-flyweight.md` (flyweight — частинки гри до/після, пам'ять у числах), `proj-ast-visitor.md` (visitor — два проходи по AST виразів).
Інлайн у dependency-injection (вже в плані): контраст **service-locator** як анти-двійника DI (Фаулер 2004) — окремий крок не потрібен.

**Разом GoF у курсі: 23 із 23.** Каталог design-patterns у маніфесті книги виростає з 21 до 30 топіків (+PoEAA-частина, §3).

---

## 3. PoEAA-ядро (Фаулер, 2002)

repository та orm уже в плані (М2.23, М4.8). Класти патерни доступу до даних — у `design-patterns` (це каталожні патерни), архітектурні — у `software-design`. Усі — **атоми**.

| Крок | Розмітка | Місце в дузі | Спирається на | Нотатки/приклади |
|---|---|---|---|---|
| Active Record: об'єкт сам себе зберігає | [nb:programming/design-patterns/active-record] | М4, розділ «Реляційна модель», одразу після orm | orm, sql-queries | Rails/Django-модель; чесна ціна: домен зчеплений зі схемою |
| Data Mapper: домен не знає про базу | [nb:programming/design-patterns/data-mapper] | М4, поруч (пара до active-record) | orm, repository (М2), layered (М3) | Hibernate/SQLAlchemy-клас; пара — готовий кластер варіантної статті (§11.2) |
| Unit of Work: ділова транзакція як список змін | [nb:programming/design-patterns/unit-of-work] | М4, після transactions-acid | transactions-acid, data-mapper | сесія ORM; батч-флаш; межа з транзакцією БД |
| Identity Map: один рядок — один об'єкт | [nb:programming/design-patterns/identity-map] | М4, поруч із unit-of-work | data-mapper, hash-table | кеш сесії ≠ кеш застосунку (міст до М4.6 «Перший кеш») |
| Ліниве завантаження: ghost, proxy, value holder | [nb:programming/design-patterns/lazy-loading] | М4, після identity-map | proxy (М2!), orm | джерело N+1 (orm-атом уже обіцяє N+1 — зв'язати); lazy у UI-списках мобайлу — той самий патерн |
| Сервісний шар: операції застосунку як контракт | [nb:programming/software-design/service-layer] | М3, розділ «Шари», після hexagonal | layered-architecture, design-by-contract (ref done) | усередині — контраст transaction script / domain model (прийом, не атом; розгортається у варіантах §11.1) |
| DTO: дані через межу без поведінки | [nb:programming/software-design/dto] | М3, поруч із api-design; активно повертається в М6 (серіалізація) | layered, api-design | межі процесів/потоків; DTO ≠ доменний об'єкт; luna в serialization-formats (М6) |
| Шлюз (Gateway): чужа система за своїм інтерфейсом | [nb:programming/software-design/gateway] | М3, розділ «Межі», перед anti-corruption-layer (§6) | adapter, facade (М2) | обгортка платіжки/вендорського хмарного API датчиків; НЕ плутати з api-gateway (М8, інфраструктура) — розвести явно в обох статтях |

Інлайн (прийоми, без кроків): **optimistic/pessimistic offline lock** — у db-locking + isolation-levels (М4, уже є); **front controller** — усередині mvc-mvp-mvvm (М3); **value object + money** — кандидат запасу `[nb:programming/software-design/value-objects]` (у курс не тягну — DDD-лайт згадає інлайном).
Вставки: `hist-poeaa-rails.md` (як каталог 2002 став лексиконом ORM; Rails зробив Active Record ім'ям) при active-record; `proj-unit-of-work-mini.md` (міні-UoW з identity map поверх SQL — один proj на кластер).

---

## 4. Enterprise Integration Patterns (Хоп/Вульф, 2003)

Гніздо — М8 «Сервіси та події»: після message-queue / publish-subscribe / event-log додається **окремий розділ «Патерни інтеграції: маршрути повідомлень»** (це головне структурне розширення М8, §15). Усі — **атоми** `programming/distributed-systems`.

| Крок | Розмітка | Спирається на | Що поглинає інлайном | Приклади |
|---|---|---|---|---|
| Маршрутизатор повідомлень: хто вирішує, куди далі | [nb:programming/distributed-systems/message-router] | message-queue, publish-subscribe | content-based router, message filter, recipient list, dynamic router | телеметрія DH: події за типом → різні конвеєри; платіжні події за країною |
| Розділювач і збирач: splitter/aggregator | [nb:programming/distributed-systems/splitter-aggregator] | message-queue, correlation-id (сусід) | resequencer, composed message processor | замовлення → рядки → збірка підсумку; кадри відеоаналітики DH; батчі в data-пайплайні |
| Кореляційний ідентифікатор: зшити розмову з повідомлень | [nb:programming/distributed-systems/correlation-id] | message-queue, delivery-guarantees (М6) | request-reply через чергу, return address | той самий id, що вже обіцяний у structured-logging (М10) і трейсингу — ввести ТУТ, М10 лише реферить |
| Квитанція в камері схову (Claim Check): великий вантаж поза шиною | [nb:programming/distributed-systems/claim-check] | message-queue, object-storage (М9 — або дати object-storage раніше інлайн-ідеєю) | envelope wrapper | подія «кліп із камери DH» несе посилання на блоб, не байти; рендер-ферма: сцена в сховищі, задача в черзі |
| Мертва черга: отруйні повідомлення і карантин | [nb:programming/distributed-systems/dead-letter-queue] | message-queue, retries-backoff (М6) | invalid message channel, parking lot | базовий план згадує DLQ рядком у message-queue — промотувати в атом; воркер команд пристроям DH: команда мертвому пристрою |
| Конкурентні споживачі: масштабування воркерів | [nb:programming/distributed-systems/competing-consumers] | message-queue, producer-consumer (М5) | — (consumer groups в event-log лишаються там) | пул обробників знімків; черга транскодування відео; втрата порядку як ціна |
| Транслятор повідомлень і канонічна модель | [nb:programming/distributed-systems/message-translator] | serialization-formats (М6), adapter (М2) | canonical data model, normalizer | зоопарк форматів датчиків (Zigbee/Z-Wave/BLE) → канонічна подія DH; шлюз до legacy-ERP |

Ref-и замість нових атомів: **idempotent receiver** = [ref:programming/distributed-systems/idempotency] (уже в плані М6); **guaranteed delivery/outbox** = outbox-pattern (М8); **priority channel** — інлайн у message-queue з лункою на [ref:algorithms/data-structures/priority-queue] (pending); **process manager** — інлайн у saga-pattern (оркестрація — §11.3).
Вставки: `hist-eip-hohpe.md` (каталог 2003: 65 патернів, мова інтеграції) при message-router; `proj-router-pipeline.md` (роутер+DLQ поверх черги, робочий код); `comp-integration-styles.md` (файл/спільна БД/RPC/повідомлення — класична четвірка Хопа) на відкриття розділу.

---

## 5. Конкурентні патерни

Гніздо — М5 (у 500-кроковій версії М5 напрошується на два модулі: «потоки і пам'ять» / «асинхронність і моделі» — §15). Усі — **атоми** `programming/systems`, крім work-stealing (algorithms).

| Крок | Розмітка | Звідки | Місце | Спирається на | Нотатки |
|---|---|---|---|---|---|
| Reactor і Proactor: готовність проти завершення | [nb:programming/systems/reactor-proactor] | новий | М5.5, після io-multiplexing + event-loop | io-multiplexing, event-loop | epoll/kqueue (reactor) ↔ IOCP/io_uring (proactor); формалізує вже введений цикл подій; comp-вставка `comp-io-models.md` |
| Double-checked locking: ідіома, що була багом | [nb:programming/systems/double-checked-locking] | новий | М5.2–5.3, після memory-ordering-barriers | std-atomic (ref done), memory-ordering (ref done), singleton (М2!) | hist `hist-dcl-broken.md`: декларація «DCL is broken» (Пʼю та ін., 2001), виправлення в моделі пам'яті Java 5; безпечні форми: static init, call_once |
| Guarded suspension: чекати умови під монітором | [nb:programming/systems/guarded-suspension] | новий | М5.3, одразу після monitor-sync (ref) | monitor-sync (ref pending), mutex-critical-section | поглинає **balking** як контраст (не чекати, а відмовити); місток до producer-consumer |
| Readers–writer lock: багато читачів, один письменник | [nb:programming/systems/readers-writer-lock] | новий | М5.3, після mutex | mutex-critical-section | голодування письменників; upgrade-пастка; луна MVCC (М4) — «та сама задача в базі» |
| Future/Promise: значення, якого ще нема | [nb:programming/systems/futures-promises] | запас systems→курс | М5.5, перед async-await | csp-channels або producer-consumer | композиція, all/any, скасування; async/await у плані вже є — future дати ДО нього |
| Work stealing: крадіжка задач із чужих черг | [nb:algorithms/parallel-distributed/work-stealing] | запас algorithms→курс | М5.6, після thread-pool | thread-pool, ring-buffer (ref) | деки, Cilk→ForkJoin→Tokio; hist `hist-cilk.md`; опц. math-вставка про межу Блюмофа–Лейзерсона |
| Thread-per-core: shared-nothing на ядрах | [nb:programming/systems/thread-per-core] | новий | М5.6, після event-loop + cache-coherence (ref done) | event-loop, cache-coherence, партиціювання-ідея | Seastar/ScyllaDB, DPDK; hist `hist-seastar.md`; міст до шардингу М7 («те саме, але між машинами») |
| Дерева нагляду: let it crash | [nb:programming/systems/supervision-trees] | новий | М5.4, одразу після actor-model | actor-model, error-handling (М1) | Erlang/OTP-стратегії рестартів; луна [ref:programming/embedded-systems/watchdog] (done) і k8s-рестартів (М10); proj `proj-supervisor.md` |

Інлайн (прийоми): **half-sync/half-async** і **leader-followers** (POSA2) — секції в reactor-proactor і thread-pool; **active object** — абзац в actor-model; **thread-local storage** — абзац у thread-pool/false-sharing; **monitor object** — це і є monitor-sync (ref). Disruptor/кільце вже покриті (ring-buffer ref + розбір LMAX).

---

## 6. Resilience / cloud-патерни (Azure-каталог, Нігард, k8s-patterns)

| Крок | Розмітка | Звідки | Місце | Спирається на | Нотатки |
|---|---|---|---|---|---|
| Sidecar і Ambassador: помічник поруч із процесом | [nb:programming/distributed-systems/sidecar] | новий (у плані — рядок усередині service-mesh) | М8.2, ПЕРЕД service-mesh | containers-ідея (або процеси М5), api-gateway сусід | ambassador як спеціалізація — інлайн; лог-шипери, OTel-агенти; mesh тепер «sidecar у масштабі» |
| Anti-corruption layer: перекладач на кордоні з чужим світом | [nb:programming/software-design/anti-corruption-layer] | запас software-design→курс | М8.1 (межі сервісів) або М3.4 при DDD — рекомендую М8, коли є чужі системи | domain-driven-design (М3), gateway (§3), message-translator (§4) | інтеграція DH із вендорськими хмарами екосистем (Tuya/Hue-клас); пара до strangler-fig (М10) |
| Вибори лідера як прикладний патерн | [nb:algorithms/parallel-distributed/leader-election] | запас algorithms→курс | М7.5, після distributed-locks | distributed-locks, raft (розвести: тут — лізи/локи ПОВЕРХ готового сервісу координації, не власний консенсус) | «одна нічна джоба на кластер»; singleton-service у k8s; bully/ring — оглядово |
| Scatter-gather: розсипати запит, зібрати відповіді | [nb:programming/distributed-systems/scatter-gather] | новий | М8 (розділ EIP, §4) з луною в М7 (кворум) і М9 (fan-out) | message-router або rpc, timeouts-deadlines | пошук по шардах; опитати всі кімнати DH; **омонім** із algorithms/data-structures/scatter-gather (DMA) — різні галузі, прецедент circuit-breaker уже є (§14) |
| Черга як вирівнювач навантаження | [nb:programming/distributed-systems/queue-load-leveling] | новий (атомізація own:queue-as-shock-absorber М9.17) | М9.4 | message-queue (М8), littles-law (М9) | own-крок М9 лишається як DH-синтез поверх атома; сплеск відеоподій DH → черга → рівний запис |
| Backends for Frontends: свій бекенд кожному клієнту | [nb:programming/distributed-systems/backends-for-frontends] | новий | М8.2, після api-gateway | api-gateway, rest-api, dto (§3) | КЛЮЧОВИЙ для універсального курсу: веб/мобайл/ПК DH мають різні потреби; hist `hist-soundcloud-bff.md`; поглинає gateway-aggregation |
| Хеджовані запити: другий постріл по хвосту | [nb:programming/distributed-systems/hedged-requests] | новий | М9.1–9.2, після percentiles + retries | percentiles-quantiles, retries-backoff, idempotency (!) | Дін і Баррозо «The Tail at Scale» (2013) — hist `hist-tail-at-scale.md`; math-інлайн: P(обидва повільні) = p²; ціна: подвоєний трафік |
| (Опційно) Комірки і штампи: ізоляція відмов масштабом | [nb:programming/distributed-systems/cell-based-architecture] | новий, опційний | М9.4 або М10.4 | bulkhead-isolation, partitioning-sharding, load-balancing | AWS cells / deployment stamps / Slack; якщо бюджет тисне — comp-вставка при bulkhead замість атома |

Інлайн (прийоми): **throttling** (Azure) = rate-limiting + load-shedding (уже в плані; в обох статтях дати слово «throttling» явно); **gatekeeper** — у security-межах М8.6; **valet key** — presigned-розділ object-storage (уже обіцяний); **health endpoint monitoring** = health-checks (є); **compensating transaction** = saga (є); **cache-aside** (є); **static content hosting** = cdn (є); **external configuration store** = config-design (є); **federated identity** = oauth-oidc (є); **geode** — абзац в anycast/cdn; **k8s-патерни** (init container, operator, singleton service) — інлайн у container-orchestration (М10).
Патерни стабільності Нігарда «Release It!»: circuit-breaker/bulkhead/timeouts/handshaking(=backpressure ref)/fail-fast(=assert+defensive, done) — покриті; **steady-state** — абзац у capacity-planning або disaster-recovery (ротація логів, чистка даних); **test harness** — згадка при chaos-engineering.

---

## 7. Підходи: парадигми

| Крок | Розмітка | Звідки | Місце | Спирається на | Нотатки |
|---|---|---|---|---|---|
| Чисті функції і побічні ефекти | [nb:programming/software-design/pure-functions-side-effects] | запас software-design→курс | М1.2 або М3.3 (рекомендую М1, перед тестами: чисте — тестовне) | — (самодостатній) | референтна прозорість; ефекти на краю |
| Функціональне ядро, імперативна оболонка | [nb:programming/software-design/functional-core-imperative-shell] | новий | М3.1–3.3, після hexagonal + immutability | pure-functions, hexagonal-architecture, immutability (є в плані М3.11) | Бернгардт (2012); архітектурний рецепт застосування ФП; ідеал тестовності — рима до testability-as-design (own М3.5) |
| Типи як дизайн: неможливі стани непредставні | [nb:programming/software-design/type-driven-design] | новий | М3.3 (розділ «Стан застосунку», поруч із state-management і FSM) | design-by-contract (ref done), finite-automata (ref done) | ADT/newtype, parse-don't-validate; статуси замовлення без зоопарку прапорців; сильний прийом і для embedded, і для клієнтів |
| Реактивні потоки: дані як потік у часі | [nb:programming/software-design/reactive-programming] | новий | М5.5, після async-await, разом із backpressure | observer + iterator (М2 — push/pull-двоїстість!), async-await, backpressure (ref pending) | Rx-оператори, marble-семантика; UI мобайлу і телеметрія IoT — два природні домени; hist `hist-rx.md` (Мейєр → RxJava/Netflix → Reactive Streams-специфікація) |
| [own:paradigms-toolbox] Парадигми як інструменти: ООП, ФП, реактивність, потоки даних — що коли | own-крок | новий | фінал М3 або М5 (рекомендую М5.6 — коли всі вже показані) | усе вище + actor/csp (М5.4) | синтез-есе з таблицею «задача → парадигма»; варіанти по доменах: гра (ECS-тизер), прошивка (автомати), бекенд (сервіси), аналітика (dataflow) |

Інлайн: **declarative vs imperative** — вступний абзац reactive-programming та infrastructure-as-code (М10); **dataflow/stream processing** як data-домен — територія доменної лінзи (§16), тут лише тизер у pipes-filters.

## 8. Підходи: методики

| Крок | Розмітка | Звідки | Місце | Спирається на | Нотатки |
|---|---|---|---|---|---|
| TDD і BDD: тест попереду коду | [nb:programming/software-engineering/tdd] | запас software-engineering→курс | М1.5, одразу після unit-testing + test-doubles | unit-testing, test-doubles | red-green-refactor; BDD/given-when-then — секція тут же; чесні межі (де TDD не тягне); hist `hist-tdd-beck.md` (Бек: «rediscovery», картки Smalltalk; атрибуцію веб-звірити) |
| Контрактні тести: споживач диктує контракт | [nb:programming/software-engineering/contract-testing] | запас→курс | М6.3, після api-versioning (або М8 при мікросервісах) | rest-api, api-versioning, test-doubles | Pact-клас; consumer-driven contracts; proj `proj-contract-pact.md` — контракт мобайл-DH ↔ хмара-DH |
| Design docs і RFC: проєктування письмом | [nb:programming/software-engineering/design-docs] | новий | М3.6, поруч з architecture-decision-records | architecture-decision-records (сусід; ADR — рішення, design doc — задум) | поглинає **рев'ю архітектури** (процес навколо документа: комітети, легкі рев'ю) — окремий атом не потрібен; hist `hist-rfc-culture.md` (IETF RFC → Google design docs → Rust RFC) |
| Фітнес-функції: архітектурні правила, що самі себе перевіряють | [nb:programming/software-design/fitness-functions] | новий | М3.6 (після design-docs) або М10.2 у CI | layered-architecture (правило залежностей), ci-cd (М10 — тизер) | ArchUnit-клас: «домен не імпортує адаптери» як тест; еволюційна архітектура (Форд/Парсонс); proj `proj-arch-fitness.md` |
| Парне програмування | [ref:programming/software-engineering/pair-programming] — (pending, Є В ІНДЕКСІ) | реюз | М1.5, поруч із code-review (ref done) | — | коротка сходинка культури якості |

Інлайн: **contract-first** (schema-first проти code-first) — розширити api-design (М3.21) і grpc (М6.19; «контракт у файлі» вже там) + варіантна own-стаття §11.5; **trunk-based development і стратегії гілкування** — секція в ci-cd (М10.7); **інспекції Фагана** [ref існує, pending] — згадка в code-review, у курс не тягнути.

## 9. Принципи-обходи проблем (mitigation)

| Крок | Розмітка | Звідки | Місце | Спирається на | Нотатки |
|---|---|---|---|---|---|
| Темний запуск: фіча в проді, якої ніхто не бачить | [nb:programming/operations/dark-launch] | новий | М10.2, після deployment-strategies + feature-flags (М3.20) | feature-flags, deployment-strategies, metrics-monitoring | ОДИН атом на родину: dark launch + **shadow traffic/дзеркалювання** + **parallel run/Scientist** (порівняння результатів) — усе секціями; hist `hist-facebook-dark-launch.md` (чат 2008); proj `proj-parallel-run.md` (harness порівняння старої/нової реалізації на живому трафіку) |
| Жива міграція даних: dual-write, backfill, expand–contract | [nb:programming/distributed-systems/live-migration] | новий | М7.4, після rebalancing (який уже згадує «подвійний запис, зворотне заповнення» — тут це стає предметом) | database-migrations (М4 — сіє expand-contract), rebalancing, feature-flags | фази: expand → dual-write → backfill → verify → switch read → contract; читається і на СХЕМУ (М4), і на СХОВИЩЕ (М7), і на СЕРВІС (М10 strangler); ключовий життєвий навик |
| Branch by abstraction: перебудова без довгих гілок | [nb:programming/software-design/branch-by-abstraction] | новий | М10.6, ПЕРЕД strangler-fig (той самий хід: усередині кодбази ↔ на рівні систем) | refactoring (М1), dependency-inversion (М1), feature-flags | Фаулер/Hammant; пара «BBA — код, стренглер — система» робить фінал курсу симетричним |
| Штатне вимкнення: drain і SIGTERM | [nb:programming/operations/graceful-shutdown] | запас operations→курс | М10.3, поруч із containers/orchestration і rolling-деплоєм | health-checks (М8), deployment-strategies | inflight-запити, черги, з'єднання; ігровий сервер, що доводить матчі; **crash-only** (Кандеа/Фокс 2003) — контраст-секція тут |
| CDC: журнал бази як джерело подій | [nb:programming/databases/change-data-capture] | запас databases→курс | М8.4, одразу після outbox-pattern | write-ahead-log (М4!), outbox-pattern, event-log | альтернатива outbox-у; красиво замикає дугу на WAL із М4; Debezium-клас — інлайн |
| (Опційно) Матеріалізовані подання: обчислене заздалегідь | [nb:programming/databases/materialized-views] | новий, опційний | М4.3 (після індексів) або М8.4 при CQRS-проєкціях | sql-queries, database-indexes | якщо бюджет тисне — секція в cqrs |

Інлайн (прийоми, БЕЗ окремих кроків — розписати по атомах-власниках):
- **kill-switch** → секція в feature-flags (М3.20): ops-прапорці, аварійний рубильник; луна hist-facebook-bgp «аварійний контур поза системою».
- **graceful degradation** → уже покрито load-shedding (М9.19 «плавна деградація») + крос-домен ref [ref:programming/embedded-systems/graceful-degradation] (basic:done!) — у load-shedding дати картку-міст на embedded-статтю; **brownout** (серверний) — абзац там само з луною на embedded brownout (done).
- **dual-write / backfill** → секції атома live-migration (вище).
- **expand–contract** → фаза live-migration + уже обіцяний у database-migrations (М4.9).
- **N/N+1-сумісність** → уже в deployment-strategies (М10.8).
- **shadow traffic / parallel run** → секції dark-launch (вище).
- **steady-state** → абзац у capacity-planning/disaster-recovery (М10).
- **request coalescing / single-flight** → уже в cache-invalidation (М9.14).
- **жорсткі перезапуски як стратегія** → supervision-trees (§5) + watchdog-ref.

Крос-доменні ref-луни embedded (усі done, реюз без нового письма; для універсального курсу — цінні містки «та сама ідея в залізі»): watchdog (при health-checks/supervision), safe-mode + failsafe (при load-shedding/incident-response), redundancy (при replication М7.2), brownout (при load-shedding), graceful-degradation (вище), ota-slots/ota-rollback (при deployment-strategies: blue-green у прошивці — два банки флешу!).

---

## 10. Fold-мапа: названі патерни, покриті інлайном (контроль, що «всі» ≠ «кожному по кроку»)

| Названий патерн/прийом | Де живе (власник) |
|---|---|
| Service Locator | dependency-injection (М2) — контраст-секція |
| Content-Based Router, Message Filter, Recipient List | message-router (§4) |
| Request-Reply, Return Address | correlation-id (§4) |
| Resequencer | splitter-aggregator (§4) |
| Envelope Wrapper | claim-check / message-translator (§4) |
| Priority Channel | message-queue + ref priority-queue |
| Process Manager (оркестратор) | saga-pattern (М8) + варіанти §11.3 |
| Idempotent Receiver | idempotency (М6, є) |
| Half-Sync/Half-Async, Leader-Followers | reactor-proactor, thread-pool (§5) |
| Active Object | actor-model (М5) |
| Balking | guarded-suspension (§5) |
| Monitor Object | monitor-sync (ref, М5) |
| Ambassador | sidecar (§6) |
| Gateway Aggregation | api-gateway/BFF (§6) |
| Throttling (Azure) | rate-limiting + load-shedding (М9) |
| Valet Key | object-storage/presigned (М9) |
| Gatekeeper | межі довіри М8.6 |
| Geode | anycast/cdn (М9) |
| Compensating Transaction | saga (М8) |
| Steady State, Test Harness, Fail Fast (Нігард) | capacity/DR, chaos-engineering, assert-panic (є) |
| Transaction Script / Domain Model / Table Module | service-layer (§3) + варіанти §11.1 |
| Optimistic/Pessimistic Offline Lock | isolation-levels/db-locking (М4) |
| Front Controller | mvc-mvp-mvvm (М3) |
| Init Container, Operator, Singleton Service (k8s) | container-orchestration (М10) + leader-election (§6) |
| Crash-Only | graceful-shutdown (§9) |
| Blackboard (POSA) | згадка в pipes-filters або anti-patterns — одним абзацом |
| Broker (POSA) | message-queue/брокери (М8, comp уже є) |
| Microkernel (POSA) | plugin-architecture (М3, є) |

## 11. Кластери варіантних own-статей (нова вимога: «варіант А/Б/В + вибір»)

Пропозиція для структурної лінзи; кожен кластер = 3–4 own-кроки (варіанти + стаття-вибір). Мої атоми — їхня сировина.

1. **Організація бізнес-логіки** (М3): transaction script / domain model / table module — на движку правил-автоматизацій Digital Homes. Спирається: service-layer, ddd.
2. **Доступ до даних** (М4): active record / data mapper / чистий SQL+repository — реєстр пристроїв DH. Спирається: §3-кластер.
3. **Сага: оркестрація / хореографія / без саги (моноліт-транзакція)** (М8): сценарій «активація сцени DH» або платіжка. Спирається: saga, event-log, message-router.
4. **API для трьох клієнтів** (М8): один REST / BFF на клієнта / GraphQL — веб+мобайл+ПК Digital Homes. Спирається: rest-api, backends-for-frontends, api-gateway. (GraphQL — у запасі web-backend; для варіанта Б/В підняти в курс або лишити hist-рівнем.)
5. **Контракт API: code-first / contract-first / consumer-driven** (М6): API хаба DH. Спирається: api-design, grpc, contract-testing.
6. **Рантайм конкурентності** (М5): потоки+локи / event loop / актори — відеосервер DH проти ігрового сервера (де показовіше — гра). Спирається: весь М5.
7. **Стійкість у виклику: бібліотека / sidecar-mesh / шлюз** (М8): куди класти retry+CB+mTLS. Спирається: circuit-breaker, sidecar, api-gateway, service-mesh.
8. **Міграція живої системи: big bang / strangler / branch-by-abstraction (+live-migration даних)** (М10): DH-хмара v1→v2. Спирається: §9.

## 12. Дé вводиться — зведена мапа по дузі (усі 51+3)

- **М1:** pure-functions-side-effects · tdd · pair-programming(ref) — розділ «Страхувальні сітки» товстішає на методики.
- **М2 (патерни ×2 модулі):** prototype, bridge, flyweight (породж./структ.) · mediator, memento, visitor, interpreter (поведінк.) · null-object (поза GoF). GoF = 23/23.
- **М3:** service-layer, dto, gateway · functional-core-imperative-shell, type-driven-design · design-docs, fitness-functions (+ contract-first інлайн в api-design; kill-switch інлайн у feature-flags).
- **М4:** active-record, data-mapper, unit-of-work, identity-map, lazy-loading · (опц.) materialized-views.
- **М5:** double-checked-locking, guarded-suspension, readers-writer-lock · supervision-trees · futures-promises, reactor-proactor, reactive-programming · work-stealing, thread-per-core · own:paradigms-toolbox.
- **М6:** contract-testing (після api-versioning).
- **М7:** leader-election · live-migration (після rebalancing).
- **М8:** sidecar (перед mesh) · anti-corruption-layer · backends-for-frontends · РОЗДІЛ EIP: message-router, splitter-aggregator, correlation-id, claim-check, dead-letter-queue, competing-consumers, message-translator, scatter-gather · change-data-capture (після outbox).
- **М9:** queue-load-leveling · hedged-requests · (опц.) cell-based-architecture.
- **М10:** dark-launch · graceful-shutdown · branch-by-abstraction (перед strangler-fig).

Кумулятивність перевірено: жоден новий атом не вживає невведеного (усі «спирається на» — раніше по дузі або ref:done; єдина натяжка — claim-check хоче object-storage (М9): дати ідею блоб-сховища інлайном або пересунути object-storage раніше — рішення за структурною лінзою).

## 13. Контроль повноти за каталогами

- **GoF (1994):** 23/23 ✔ (16 було + 7 цією лінзою; interpreter — знайдена діра).
- **PoEAA (2002):** ядро 8/8 ✔ + repository/orm уже були; решта каталогу — інлайн/запас (§3, §10).
- **EIP (2003):** усі магістральні ✔ (7 атомів + 6 інлайн + 4 уже в плані: queue, pub/sub, event-log, outbox).
- **POSA1/POSA2:** layers/pipes-filters/microkernel/broker були; reactor-proactor, half-sync, leader-followers, monitor — ✔ (§5).
- **Нігард «Release It!»:** усі стабілізаційні ✔ (§6, §10).
- **Azure Cloud Design Patterns:** покрито все, крім свідомо відкинутих як згадки (geode, gatekeeper — інлайн) ✔.
- **Підходи:** ФП-прийоми ✔, реактивність ✔, TDD/BDD ✔, contract-first ✔, RFC/design docs ✔, рев'ю архітектури ✔ (в design-docs), mitigation-набір ✔ (§9).

## 14. Омоніми, колізії, межі (перевірено за індексом 2446 рядків)

1. Нових галузей у індексі ще нема (design-patterns, software-design, distributed-systems, web-backend, operations) — колізій НУЛЬ; усередині галузей мої слаги не перетинаються зі списками плану (звірено проти §«Нові галузі book» плану).
2. **scatter-gather:** омонім із `algorithms/data-structures/scatter-gather` (DMA, pending) — різні галузі, прецедент узаконений (circuit-breaker в electronics/components). У статті — рядок-розведення.
3. **gateway (software-design) vs api-gateway (distributed-systems):** різні поняття (об'єктна обгортка vs інфраструктурні двері) — у ОБОХ статтях взаємні картки-розведення.
4. **leader-election vs raft:** розвести кути — raft: власний консенсус усередині; leader-election: прикладний патерн поверх готової координації (лізи/локи). У плані proj-leader-election висить на raft — можна перевісити на новий атом.
5. **graceful-degradation:** існує embedded-версія (done). НЕ створювати дубль у distributed-systems; реюз ref-ом + серверні кути в load-shedding.
6. **reactive-programming** кладу в software-design (підхід/стиль), не в systems (там механіка виконання) — межа галузей за планом.
7. Відомий дубль adaptive-bitrate (2 галузі) — не мій, уже зафіксований у плані як окрема чистка.

## 15. Вплив на структуру курсу (при перекладці на ~500 кроків)

- **Патерни: 1 модуль → 2** («творення і структура» ~24, «поведінка і поза-GoF» ~24) — architect-лінза вже так різала; мої +8 GoF лягають рівно туди.
- **М8 → 2 модулі:** «сервіси» (межі, комунікація, довіра) і «інтеграція та події» (черги/лог/EIP-розділ/сага/outbox/CDC) — EIP-розділ (+8 атомів) інакше не влазить.
- **М5 → 2 модулі:** «потоки і пам'ять» (+DCL, guarded, rw-lock) і «асинхронність і моделі» (+futures, reactor-proactor, reactive, supervision, work-stealing, thread-per-core).
- **М1/М3 отримують розділ методик** (tdd, design-docs, fitness-functions, contract-first) — або окремий модуль «Процес і культура проєктування» ближче до середини курсу.
- Варіантні кластери §11 — по своїх модулях як фінальні розділи «Рішення» (розділ = одна мета: «ухвалити рішення X»).
- **Черга письма:** мої атоми — однотипні самодостатні (ідеальні для write-batch); порядок: (Б-патерни: 8 GoF+PoEAA-5) → (Б-методики/парадигми: 8) → (Б-конкурентність: 8) → (Б-EIP+resilience: 15) → (Б-mitigation/ops: 7). Промоти запасу (16) — просто перемкнути статуси pending при заведенні маніфесту.

## 16. Хендоф іншим лінзам (щоб не було дір і дублів)

- **Доменна лінза (ігри/клієнти/data/embedded):** ECS і data-oriented design, game loop / update method / double buffer / dirty flag / spatial partition (Nystrom), offline-first і синхронізація мобайлу, redux/MVI-однонапрямний потік (клієнтська луна CQRS — зв'язати з моїм cqrs/event-sourcing!), stream processing (вікна/watermark), MapReduce (у запасі algorithms). Мої атоми observer/command/state/flyweight/memento — їхня сировина, дублювати не треба.
- **Структурна лінза:** розміщення варіантних кластерів §11; рішення по claim-check↔object-storage порядку; чи промотувати GraphQL у курс (кластер §11.4).
- **Кейсова лінза:** мої hist-пропозиції (~12) — dcl-broken, tail-at-scale, facebook-dark-launch, rfc-culture, tdd-beck, rx, cilk, seastar, soundcloud-bff, poeaa-rails, eip-hohpe (+ наявні); усі числа/атрибуції веб-звіряти за AUTHORING §7 (особливо «Бек перевідкрив TDD» і історію Rx).
