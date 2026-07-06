# Курс «Архітектура програм» (guide/progarch) — проєкт, лінза «хайлоад-інженер»

Проєкт нового курсу з нуля. Нічого в репозиторії не змінено — це план для маніфесту `guide/progarch/manifest.js`.

## Параметри (як задано)

- **Обсяг:** 258 кроків (ціль 250 ±10% → 225–275 ✓).
- **10 модулів** по 22–30 кроків; у кожному 5–6 розділів, розділ = одна чітка мета.
- **Дуга:** принципи коду → патерни → архітектура застосунку → дані → паралельність → розподілені системи → високе навантаження → експлуатація. Друга половина — з хайлоад-глибиною: кожен механізм пояснюється через «що ламається без нього на N користувачів», і це видно з назв розділів.
- **Аудиторія:** вміє писати код (пререквізит — модуль «Вхід у програмування» курсу embedded або еквівалент). Синтаксису не вчимо.
- **Мова:** назви — жива українська (патерн, кеш, шардинг — як усталено); slug-и — латиниця kebab-case.

## Легенда кроків

- `[ref:книга/галузь/slug]` — тема ВЖЕ у book-маніфесті (статус звірено з індексом: done / pending).
- `[nb:книга/галузь/slug]` — НОВИЙ book-атом (самодостатня стаття; галузь наявна або нова — див. нижче).
- `[own:slug]` — власна кумулятивна стаття курсу (спирається на пройдене; синтези, кейси, наскрізна нитка).
- Вставки — рядком під кроком-власником: `hist-*` (як народилось; кейси компаній), `proj-*` (робочий код), `math-*` (математика), `comp-*` (клас систем без конкретики моделей).

## Наскрізна нитка курсу

Через усі own-кроки іде **один сервіс — скорочувач посилань** (робоча назва «Лінк»). Він народжується в М3 як застосунок в одному процесі, у М4 отримує базу, у М5 впирається в C10K, у М6 — репліки й шарди, у М7 — черги і розріз на сервіси, у М8 — кеш-ієрархію та CDN, у М9 переживає пік, у М10 живе в проді. Скорочувач обраний навмисно: він досить простий, щоб не заступати механізми, і досить справжній, щоб на ньому чесно ламалося все, що має ламатися (класична задача system design). Великі чужі кейси (WhatsApp, Twitter, YouTube, AWS, Netflix, Google) ідуть окремими own-кроками та hist/proj-вставками там, де вони канонічні.

## Нові галузі book/ (пропозиція)

Курс породжує багато самодостатніх атомів — за залізним правилом вони йдуть у book/, не в guide/. Наявних галузей не вистачає, пропоную **4 нові секції в `book/programming/`**:

| Нова галузь | Що містить | К-сть nb тут |
|---|---|---|
| `programming/design-patterns` | класичні патерни (сінглтон, фабрика, спостерігач…) — кожен патерн = атом | 20 |
| `programming/architecture` | архітектурні стилі та патерни рівня застосунку/сервісу (шари, MVC, DI-архітектура, CQRS, кеш-патерни, деградація, комірки…) | 33 |
| `programming/distributed` | механізми розподілених систем (реплікація, шардинг, CAP, кворум, сага, консенсус, service discovery…) | 31 |
| `programming/operations` | експлуатація/SRE (логи, метрики, трейси, SLO, деплої, інциденти, хаос) | 22 |

Решта nb лягає в наявні галузі: `programming/databases` (17), `programming/systems` (8), `programming/software-engineering` (11), `programming/networking` (5), `programming/languages` (3), `programming/security` (1), `algorithms/data-structures` (4), `algorithms/design-paradigms` (2), `communications/protocols` (5), `communications/networks` (2), `communications/cryptographic-comm` (1).

Межа між `architecture` і `distributed`: architecture = форма одного застосунку/сервісу та патерни його поведінки; distributed = механізми, що існують лише між кількома вузлами.

---

# Модуль 1. Принципи: чому код гниє і що його тримає — 23 кроки, 5 розділів

Стисло, але повно: словник якості коду, на який далі спиратиметься все.

### 1.1 Складність — головний ворог (мета: назвати ворога і навчитись його міряти)
1. [own:why-architecture] Навіщо архітектура: від скрипта до системи, де все залежить від усього (вступ; дуга курсу)
   вставка hist-big-ball-of-mud.md: Фут і Йодер про «велику грудку бруду» — найпоширенішу архітектуру світу
2. [nb:programming/software-engineering/essential-accidental-complexity] Суттєва і привнесена складність (Брукс: срібної кулі немає)
3. [nb:programming/software-engineering/coupling-cohesion] Зчеплення і зв'язність (coupling/cohesion)
4. [ref:programming/software-engineering/code-metrics] (pending) Метрики якості коду

### 1.2 Абстракція ховає деталі (мета: інтерфейс проти реалізації)
5. [ref:programming/software-engineering/abstraction-principle] (pending) Принцип абстракції
6. [ref:programming/software-engineering/information-hiding] (pending) Приховування інформації
7. [nb:programming/software-engineering/leaky-abstractions] Діряві абстракції: чому деталі просочуються (закон Спольскі)
8. [ref:programming/embedded-systems/module-model] (done) Модель модуля: інтерфейс і реалізація

### 1.3 SOLID без карго-культу (мета: п'ять принципів керування залежностями)
9. [nb:programming/software-engineering/single-responsibility] SRP: одна причина змінюватися
10. [nb:programming/software-engineering/open-closed] OCP: відкритий для розширення, закритий для змін
11. [ref:programming/software-engineering/behavioral-subtyping] (done) Поведінкова підтипізація (LSP)
12. [ref:programming/software-engineering/interface-segregation] (pending) Принцип розділення інтерфейсів (ISP)
13. [nb:programming/software-engineering/dependency-inversion] DIP: залежати від абстракцій, не від деталей
14. [own:solid-in-practice] SOLID разом: один рефакторинг, п'ять принципів парами (кумулятивний синтез 1.1–1.3)
    вставка proj-solid-refactor.md: беремо god-object і розводимо за принципами — робочий код «до/після»

### 1.4 Контракти й чесні помилки (мета: інтерфейс, що не бреше)
15. [ref:programming/software-engineering/design-by-contract] (done) Проєктування за контрактом
16. [ref:programming/software-engineering/error-handling] (done) Жодна помилка не мовчить
17. [nb:programming/languages/exceptions-vs-error-codes] Винятки проти кодів повернення (і Result-типи)
18. [ref:programming/languages/raii] (pending) RAII: ресурс прив'язаний до часу життя
19. [ref:programming/software-engineering/defensive-programming] (done) Захисне програмування

### 1.5 Код живе роками (мета: еволюція без страху)
20. [ref:programming/code/version-control] (done) Контроль версій і git
21. [nb:programming/software-engineering/refactoring] Рефакторинг: змінити структуру, не змінивши поведінку
22. [nb:programming/software-engineering/technical-debt] Технічний борг
    вставка hist-tech-debt.md: як Ворд Каннінгем вигадав метафору боргу, пояснюючи фінансистам ітеративність
23. [ref:programming/software-engineering/code-review] (done) Рев'ю коду

---

# Модуль 2. Класичні патерни: словник готових рішень — 26 кроків, 5 розділів

Кожен патерн — самодостатній book-атом у новій галузі `programming/design-patterns`; курсові кроки-власники зв'язують їх у словник і перекидають місток до серверних патернів другої половини.

### 2.1 Що таке патерн (мета: проблема→контекст→рішення, і коли патерн шкодить)
1. [nb:programming/design-patterns/what-is-pattern] Що таке патерн проєктування (і що таке антипатерн)
   вставка hist-gof-alexander.md: від патернів архітектора Крістофера Александера до «банди чотирьох» (GoF, 1994)
2. [own:patterns-as-vocabulary] Патерни як мова команди: називаємо рішення з М1 їхніми іменами (кумулятивно)

### 2.2 Породжувальні: хто і як створює об'єкти (мета: забрати `new` з логіки)
3. [nb:programming/design-patterns/singleton] Сінглтон — і чому його ненавидять
4. [nb:programming/design-patterns/factory-method] Фабричний метод
5. [nb:programming/design-patterns/abstract-factory] Абстрактна фабрика
6. [nb:programming/design-patterns/builder] Будівельник
7. [nb:programming/design-patterns/object-pool] Пул об'єктів (далі виросте в пули з'єднань)
8. [nb:programming/design-patterns/dependency-injection] Впровадження залежностей (DI): фабрики, доведені до кінця
   вставка proj-di-container.md: мінімальний DI-контейнер руками — робочий код

### 2.3 Структурні: як складати ціле з частин (мета: змінювати композицію, не класи)
9. [nb:programming/design-patterns/adapter] Адаптер
10. [nb:programming/design-patterns/facade] Фасад
11. [nb:programming/design-patterns/decorator] Декоратор
12. [nb:programming/design-patterns/composite] Компонувальник
13. [nb:programming/design-patterns/proxy] Проксі (далі виросте у reverse proxy і service mesh)
14. [nb:programming/design-patterns/flyweight] Легковаговик: мільйони об'єктів у скінченній пам'яті

### 2.4 Поведінкові: хто кому каже, що робити (мета: розчепити відправника й виконавця)
15. [nb:programming/design-patterns/observer] Спостерігач (далі виросте в pub/sub)
16. [nb:programming/design-patterns/strategy] Стратегія
17. [nb:programming/design-patterns/command] Команда (далі виросте в чергу задач)
18. [nb:programming/design-patterns/state] Стан
19. [ref:programming/embedded-systems/state-machine] (pending) Машина станів
20. [nb:programming/design-patterns/template-method] Шаблонний метод
21. [nb:programming/design-patterns/chain-of-responsibility] Ланцюжок відповідальності (далі — middleware)
22. [nb:programming/design-patterns/iterator] Ітератор і лінива послідовність

### 2.5 Патерни під капотом мови (мета: побачити, чим патерн є в машині)
23. [ref:programming/embedded-systems/virtual-dispatch-cpp] (pending) Таблиця віртуальних методів
24. [ref:programming/systems/function-pointers] (pending) Покажчики на функції
25. [nb:programming/languages/closures] Замикання: об'єкт з однієї функції
26. [own:patterns-scale-up] Патерни, що переживуть процес: proxy→балансувальник, observer→брокер, command→черга повідомлень (місток до М6–М8, кумулятивно)

---

# Модуль 3. Архітектура застосунку: шари, межі, стан — 22 кроки, 6 розділів

### 3.1 Шари і правило залежностей (мета: бізнес-логіка не знає про базу)
1. [nb:programming/architecture/layered-architecture] Шарувата архітектура
2. [nb:programming/architecture/hexagonal-architecture] Порти й адаптери (гексагональна архітектура)
3. [own:dependency-rule] Правило залежностей: DIP з М1 на рівні цілої системи (кумулятивно)
4. [ref:programming/embedded-systems/ardupilot-layers] (done) Шари ArduPilot — живий приклад шарів у великій кодовій базі

### 3.2 Стан і потік даних (мета: де живе стан і хто його міняє)
5. [nb:programming/architecture/mvc-mvvm] MVC і MVVM: відділити подання від моделі
6. [nb:programming/architecture/unidirectional-data-flow] Односпрямований потік даних (flux/redux-стиль)
7. [nb:programming/architecture/event-driven-architecture] Подієва архітектура всередині застосунку
8. [ref:programming/embedded-systems/data-serialization] (done) Серіалізація даних

### 3.3 API: контракт назовні (мета: межа процесу, яку можна тримати роками)
9. [nb:communications/protocols/http-protocol] HTTP: протокол, на якому стоїть веб
10. [nb:programming/architecture/rest-api] REST: ресурси, дієслова, статуси
11. [nb:programming/architecture/rpc-grpc] RPC і gRPC: виклик функції через мережу
12. [nb:programming/architecture/api-contract] Контракт API: схема, OpenAPI, зворотна сумісність
13. [nb:programming/architecture/api-versioning] Версіонування API: змінитися і нікого не зламати

### 3.4 Один код — багато середовищ (мета: відв'язати збірку від конфігурації)
14. [nb:programming/architecture/twelve-factor] Дванадцять факторів: код, конфіг, залежності, порти
15. [nb:programming/operations/feature-flags] Прапорці функцій (feature flags)
16. [ref:programming/embedded-systems/vendor-lock-in] (pending) Прив'язка до платформи (vendor lock-in)

### 3.5 Тестованість як лакмус архітектури (мета: не тестується — погано розрізано)
17. [nb:programming/software-engineering/unit-testing] Юніт-тести
18. [nb:programming/software-engineering/test-doubles] Тестові двійники: моки, стаби, фейки
19. [nb:programming/software-engineering/integration-testing] Інтеграційні та наскрізні тести: піраміда тестування
20. [own:testability-as-design] Тестованість = розв'язаність: порти з 3.1 у дії (кумулятивно)
    вставка proj-hexagon-test.md: гексагональний застосунок з тестами портів — робочий код

### 3.6 Модульний моноліт — стартова форма (мета: правильний перший цільний застосунок)
21. [nb:programming/architecture/modular-monolith] Модульний моноліт
22. [own:app-architecture-capstone] Капстоун модуля: проєктуємо скорочувач посилань «Лінк» — шари, API, тести (старт наскрізної нитки)
    вставка proj-url-shortener.md: скорочувач URL цілком в одному процесі — робочий код, який масштабуватимемо до кінця курсу

---

# Модуль 4. Дані: правда живе в базі — 24 кроки, 6 розділів

### 4.1 Навіщо СУБД (мета: чому не просто файли)
1. [own:why-database] «Лінк» пише у файл: конкурентний доступ, збій посеред запису, пошук — три причини взяти СУБД (кумулятивно)
2. [nb:programming/databases/acid-transactions] Транзакція та ACID
3. [nb:programming/databases/write-ahead-log] Журнал попереднього запису (WAL): чому база переживає вимкнення світла

### 4.2 Реляційна модель (мета: схема, запити, індекси)
4. [nb:programming/databases/relational-model-sql] Реляційна модель і SQL
   вставка hist-codd-relational.md: Кодд проти ієрархічних БД: як таблиці перемогли (IBM System R, Ingres)
5. [nb:programming/databases/normalization] Нормалізація: одна правда — одне місце
6. [nb:programming/databases/db-indexes] Індекси: чому пошук швидкий, а вставка повільніша
7. [nb:algorithms/data-structures/b-tree] B-дерево
8. [nb:programming/databases/query-planner] Планувальник запитів: EXPLAIN і чому база вирішує сама

### 4.3 Багато письменників — одна правда (мета: конкурентний доступ без загублених оновлень)
9. [nb:programming/databases/isolation-levels] Рівні ізоляції: від read uncommitted до serializable
10. [nb:programming/databases/mvcc] MVCC: читачі не блокують письменників
11. [nb:programming/databases/db-locks-deadlocks] Блокування і дедлоки в БД
12. [own:lost-update-in-service] Загублене оновлення в «Лінку»: лічильник кліків з'їдає кліки (кумулятивно)
    вставка proj-isolation-demo.md: відтворюємо аномалії ізоляції на живій СУБД — робочий код

### 4.4 Модель даних під модель доступу (мета: не все — таблиці)
13. [ref:algorithms/data-structures/key-value-store] (pending) Сховище «ключ — значення»
14. [nb:programming/databases/document-databases] Документні БД
15. [nb:programming/databases/column-wide-stores] Колонкові й широкостовпцеві сховища: OLTP проти OLAP
16. [ref:programming/systems/log-structured-storage] (done) Журнальне і log-structured сховище
17. [nb:programming/databases/lsm-tree] LSM-дерево: писати швидко, читати сходинками

### 4.5 Схема живе і міняється (мета: еволюція даних без страху)
18. [nb:programming/databases/schema-migrations] Міграції схеми
19. [nb:programming/databases/orm-pattern] ORM: міст об'єкти↔таблиці та його ціна
20. [own:data-model-capstone] Модель даних «Лінка»: сутності → схема → індекси (кумулятивно)
    вставка proj-slug-schema.md: схема, індекси й міграції скорочувача — робочий код

### 4.6 Перший кеш (мета: не ходити в базу за тим самим; підготовка до М8)
21. [ref:programming/computer-architecture/cache] (done) Кеш — принцип локальності на прикладі CPU
22. [nb:programming/architecture/cache-aside] Патерн cache-aside: прочитай — поклади
23. [nb:algorithms/data-structures/lru-cache] LRU і політики витіснення
24. [own:cache-first-touch] Кеш у «Лінку»: гарячі посилання — і перший баг застарілих даних (тизер М8, кумулятивно)

---

# Модуль 5. Паралельність: один сервер, десять тисяч з'єднань — 29 кроків, 5 розділів

Звідси починається хайлоад-глибина: кожен розділ — «що ламається на N».

### 5.1 Хто виконує код (мета: процеси, потоки і чому їх не буває безкоштовно багато)
1. [nb:programming/systems/process-vs-thread] Процес і потік: що спільне, що окреме
2. [ref:programming/systems/context-switch] (done) Перемикання контексту
3. [ref:programming/systems/smp-scheduling] (pending) SMP-планування
4. [ref:programming/computer-architecture/multicore] (done) Багатоядерні процесори
5. [own:server-v1-thread-per-conn] «Лінк»-сервер v1: потік на з'єднання — і стеля вже на тисячах (кумулятивно)
   вставка proj-thread-per-conn.md: thread-per-connection сервер + вимір, скільки з'єднань він реально тягне

### 5.2 Спільна пам'ять: гонки і замки (мета: коректність, коли потоки ділять стан)
6. [ref:programming/systems/atomicity-races] (done) Атомарність і гонки
7. [nb:programming/systems/mutex-critical-section] М'ютекс і критична секція
8. [ref:algorithms/parallel-distributed/monitor-sync] (pending) Монітори й умовні змінні
9. [nb:programming/systems/deadlock] Взаємне блокування: чотири умови Коффмана і як їх ламати
10. [ref:programming/languages/std-atomic] (done) std::atomic і порядок пам'яті
11. [ref:programming/systems/memory-ordering-barriers] (done) Упорядкування пам'яті та бар'єри
12. [ref:programming/computer-architecture/cache-coherence] (done) Когерентність кешів (і false sharing)
13. [nb:programming/systems/lock-free-basics] Без замків: CAS, проблема ABA — оглядово

### 5.3 Не ділити пам'ять, а передавати повідомлення (мета: моделі, де гонок немає за побудовою)
14. [ref:programming/systems/task-ipc] (done) Черги й семафори
15. [ref:algorithms/data-structures/ring-buffer] (pending) Кільцевий буфер
16. [nb:programming/architecture/actor-model] Модель акторів: стан замкнено в акторі
    вставка hist-erlang-whatsapp.md: Erlang — від телефонних станцій Ericsson до WhatsApp із 2 млн з'єднань на сервер
17. [nb:programming/architecture/csp-channels] CSP і канали (Go-стиль): спілкуйся, а не діли
18. [ref:algorithms/data-structures/copy-on-write] (pending) Copy-on-write: незмінні копії
19. [nb:programming/systems/thread-pool] Пул потоків: не створюй — позичай

### 5.4 Event loop: тисячі з'єднань одним потоком (мета: прибрати потік як одиницю з'єднання)
20. [nb:programming/systems/blocking-vs-nonblocking-io] Блокуючий і неблокуючий В/В
21. [nb:programming/systems/io-multiplexing-epoll] Мультиплексування В/В: select → poll → epoll/kqueue
22. [nb:programming/systems/event-loop] Event loop: один потік, тисячі справ — і чому його не можна блокувати
    вставка comp-event-loop-runtimes.md: клас рушіїв на циклі подій: nginx, Node.js, Redis — одна ідея, різні задачі
23. [nb:programming/languages/async-await] Callbacks → проміси → async/await
24. [ref:programming/systems/coroutines] (pending) Корутини
25. [own:server-v2-event-loop] «Лінк»-сервер v2: event loop замість тисячі потоків (кумулятивно)
    вставка proj-epoll-server.md: мінімальний epoll-сервер; порівняння v1 і v2 під навантаженням — робочий код

### 5.5 C10K→C10M: куди тікають ресурси (мета: що ламається на 10 тис. і що — на 10 млн з'єднань)
26. [own:c10k-problem] Проблема C10K: чому «потік на з'єднання» помирає, і як її розв'язали (синтез 5.1–5.4)
    вставка hist-c10k-kegel.md: маніфест Дена Кегеля (1999) і як nginx обійшов Apache
27. [nb:programming/networking/connection-pool] Пул з'єднань: TCP-рукостискання і сесія БД не безкоштовні
28. [ref:algorithms/design-paradigms/backpressure] (pending) Протитиск (backpressure): скажи джерелу «повільніше»
29. [own:overload-single-server] Перевантаження одного сервера: черга росте — латентність вибухає; межі вертикального росту (місток до М6)
    вставка math-littles-law.md: закон Літтла L=λW і коліно кривої утилізації

---

# Модуль 6. Розподілені системи I: мережа бреше — 28 кроків, 5 розділів

### 6.1 Фізика запиту (мета: скільки насправді коштує «сходити по мережі»)
1. [ref:programming/networking/sockets-tcp-udp] (done) Сокети TCP/UDP
2. [ref:communications/protocols/tcp-vs-udp] (done) TCP проти UDP
3. [nb:communications/protocols/tcp-handshake-slowstart] TCP зсередини: рукостискання, slow start, head-of-line blocking
4. [ref:communications/networks/dhcp-dns] (pending) DHCP і DNS
5. [nb:communications/cryptographic-comm/tls-handshake] TLS: рукостискання, сертифікати, ціна першого байта
6. [ref:communications/protocols/quic-protocol] (pending) QUIC та HTTP/3
7. [nb:communications/protocols/websocket-sse] WebSocket і SSE: сервер говорить першим

### 6.2 Відмова — це норма (мета: без таймаутів, повторів та ідемпотентності перший же збій = подвійне списання)
8. [own:fallacies-distributed] Вісім хиб розподілених обчислень: мережа не надійна, затримка не нуль (кумулятивно)
   вставка hist-deutsch-fallacies.md: як у Sun Microsystems сформулювали «хиби» — Дойч, Гослінг
9. [nb:programming/distributed/timeouts-retries] Таймаути і повтори: скільки чекати і коли здатися
10. [nb:programming/distributed/idempotency] Ідемпотентність: повтор без подвійного ефекту (ключі ідемпотентності)
11. [nb:programming/distributed/exactly-once-myth] «Рівно раз» — міф: at-least-once, at-most-once, дедуплікація
12. [nb:programming/distributed/failure-detection] Виявлення відмов: heartbeat, підозра замість вироку
13. [own:retry-storm] Шторм повторів: як ретраї добивають систему, що вже лежить (кумулятивно)
    вставка proj-backoff-jitter.md: експоненційний бекоф із джитером — симуляція шторму, робочий код

### 6.3 Реплікація: пережити смерть сервера (мета: без реплік одна відмова диска = втрата всього)
14. [nb:programming/distributed/replication-leader-follower] Реплікація лідер-послідовники: синхронно чи асинхронно
15. [nb:programming/distributed/replication-lag] Відставання репліки: читаєш — а там минуле
16. [nb:programming/distributed/failover-split-brain] Failover і розщеплення мозку: два лідери — гірше, ніж жодного
17. [nb:programming/distributed/multi-leader-conflicts] Кілька лідерів і конфлікти записів (LWW, злиття, CRDT оглядово)
18. [own:read-replicas-in-service] «Лінк»: розводимо читання на репліки — і ловимо «щойно створив, а лінк не працює» (кумулятивно)

### 6.4 Шардинг: коли дані не влазять в одну машину (мета: різати так, щоб потім не збирати)
19. [nb:programming/distributed/sharding-partitioning] Шардинг: за діапазоном і за хешем
20. [nb:algorithms/data-structures/consistent-hashing] Консистентне хешування: додали вузол — переїхала 1/N ключів
    вставка hist-karger-akamai.md: як консистентний хеш придумали для веб-кешів (Каргер, 1997) і він породив Akamai
    вставка proj-hash-ring.md: кільце консистентного хешу з віртуальними вузлами — робочий код
21. [nb:programming/distributed/resharding] Решардинг: перевезти дані, не зупиняючи світ
22. [nb:programming/distributed/hot-partitions] Гарячі шарди: селебриті-проблема і перекіс ключів
23. [own:shard-our-db] Шардимо лічильники «Лінка»: вибір ключа шардингу і чому «за датою» — пастка (кумулятивно)

### 6.5 Яку правду бачить читач (мета: свідомий вибір консистентності, а не випадковий)
24. [nb:programming/distributed/cap-theorem] CAP: що обираєш під час розриву мережі
    вставка hist-cap-brewer.md: гіпотеза Брюера (2000) → доведення → критика «двох із трьох»
25. [nb:programming/distributed/consistency-models] Моделі консистентності: від лінеаризовності до eventual
26. [nb:programming/distributed/session-guarantees] Сесійні гарантії: read-your-writes, monotonic reads
27. [nb:programming/distributed/quorum-rw] Кворумні читання й записи: W+R>N
    вставка math-quorum-intersection.md: чому W+R>N гарантує перетин — проста комбінаторика
28. [own:choose-consistency] Обираємо для «Лінка»: лічильники — eventual, білінг — строго (кумулятивний синтез)
    вставка hist-dynamo-cassandra.md: Amazon Dynamo: кошик, який не можна губити, і родовід Cassandra/Riak

---

# Модуль 7. Координація і сервіси: багато частин — одна система — 26 кроків, 5 розділів

### 7.1 Черги повідомлень: розчепити в часі (мета: продюсер і консюмер живуть у різному темпі — без буфера падають обидва)
1. [nb:programming/distributed/message-queue] Черга повідомлень: буфер між сервісами
2. [nb:programming/distributed/pubsub-broker] Pub/sub і брокер: спостерігач з М2 — тепер між процесами
3. [ref:communications/protocols/mqtt] (done, detailed done) MQTT
4. [nb:programming/distributed/log-based-broker] Лог-брокер (Kafka-стиль): черга, яку можна перечитати
   вставка hist-kafka-linkedin.md: LinkedIn: чому «труби» подій переросли БД і народився Kafka
5. [nb:programming/distributed/delivery-semantics] Семантика доставки і порядок: офсети, партиції, dead letter queue
6. [own:queue-decouple-service] «Лінк»: клік → черга → лічильник; запис більше не тримає редирект (кумулятивно)
   вставка proj-click-queue.md: продюсер/консюмер з повторами й дедуплікацією — робочий код

### 7.2 Довгі операції без спільної транзакції (мета: узгодженість між сервісами, де ACID не дістає)
7. [nb:programming/distributed/two-phase-commit] Двофазний коміт — і чому його уникають
8. [nb:programming/distributed/saga-pattern] Сага: довга операція як ланцюг компенсацій
9. [nb:programming/distributed/outbox-pattern] Outbox: запис у базу і подія — атомарно
10. [nb:programming/architecture/event-sourcing] Event sourcing: стан як журнал подій
11. [nb:programming/architecture/cqrs] CQRS: читання й запис різними шляхами

### 7.3 Консенсус: одна істина на кластер (мета: хто лідер, коли всі рівні — оглядово)
12. [nb:programming/distributed/consensus-problem] Задача консенсусу і чому вона важка (FLP оглядово)
13. [nb:programming/distributed/raft-overview] Raft оглядово: вибори лідера, реплікація логу, терми
    вставка hist-paxos-raft.md: від Paxos Лампорта до Raft, «зрозумілого за задумом»
    вставка comp-coordination-services.md: клас сервісів координації: ZooKeeper, etcd, Consul — що вони насправді дають
14. [nb:programming/distributed/distributed-locks-leases] Розподілені замки і лізи: чому замок із таймаутом бреше (fencing tokens)
15. [nb:programming/distributed/logical-clocks] Логічні годинники: Лампорт і векторні
16. [ref:communications/protocols/ntp-sync] (pending) NTP: скільки бреше фізичний годинник

### 7.4 Мікросервіси: різати чи ні (мета: межі сервісів і чесна ціна розрізу)
17. [nb:programming/architecture/monolith-vs-microservices] Моноліт проти мікросервісів: що купуєш, чим платиш
    вставка hist-amazon-two-pizza.md: Amazon: мандат Безоса «все через API» і команди на дві піци
18. [nb:programming/architecture/bounded-context] Обмежені контексти: різати по швах домену (DDD-lite)
19. [nb:programming/distributed/service-discovery] Service discovery: як сервіси знаходять одне одного, коли адреси плинні
20. [nb:programming/architecture/api-gateway] API-шлюз: одні двері для всіх клієнтів
21. [nb:programming/distributed/circuit-breaker] Запобіжник (circuit breaker): не дзвони мерцю
    вставка proj-circuit-breaker.md: circuit breaker зі станами closed/open/half-open — робочий код
22. [nb:programming/architecture/service-mesh] Service mesh оглядово: винести мережеву обв'язку з коду
23. [own:cut-service-or-not] Різати «Лінк»? Аналітика кліків — окремо, редирект — нізащо (кумулятивне рішення)

### 7.5 Як НЕ треба: розподілений моноліт (мета: антипатерни розподілу — і математика, чому це боляче)
24. [own:distributed-monolith] Розподілений моноліт: мікросервіси, що ходять строєм (синтез)
25. [own:sync-vs-async-boundaries] Синхронний ланцюг сервісів = множення відмов і додавання затримок (кумулятивно)
    вставка math-availability-chain.md: множення дев'яток: доступність послідовного ланцюга проти паралельних реплік
26. [own:distributed-capstone] Капстоун: платіжний потік «Лінк Pro» — сага + outbox + ідемпотентність (синтез М6–М7)

---

# Модуль 8. Високе навантаження I: віддати мільйонам — 30 кроків, 6 розділів

### 8.1 Мова масштабу: числа і хвости (мета: рахувати до того, як будувати; без перцентилів ти не знаєш, що у тебе повільно)
1. [own:back-of-envelope] Прикидка на серветці: RPS, байти, диски й мережа для «Лінка» на 100 млн користувачів (кумулятивно)
   вставка math-latency-numbers.md: «числа, які має знати кожен» (за Діном): наносекунди кешу — мілісекунди міжконтинентального RTT
2. [ref:math/probability/order-statistics] (pending) Порядкові статистики — що таке p50/p99
3. [ref:math/probability/heavy-tail-distributions] (pending) Розподіли з важкими хвостами
4. [own:tail-latency] Хвіст затримки: чому p99 важливіший за середнє і як фан-аут його множить (кумулятивно)
   вставка math-tail-amplification.md: ймовірність зачепити повільний сервер при фан-ауті на N: 1−(0.99)^N
5. [ref:communications/networks/queue-theory-networks] (pending) Черги в мережах: затримка і втрати (M/M/1, коліно утилізації)

### 8.2 Балансування: щоб жоден сервер не помирав сам (мета: без LB перший же сервер, на який показує DNS, лягає)
6. [nb:programming/networking/load-balancing-l4-l7] Балансування L4 і L7: пакети проти запитів
7. [nb:programming/networking/lb-algorithms] Алгоритми балансування: round-robin, least-connections, power of two choices
   вставка math-power-of-two.md: сила двох виборів: чому два випадкові кращі за один — і майже як повне знання
8. [nb:programming/networking/health-checks] Health checks: виведення з ротації швидше, ніж скарги користувачів
9. [nb:programming/networking/sticky-sessions-stateless] Липкі сесії проти stateless: де жити сесії, коли серверів багато
10. [nb:programming/security/session-auth-jwt] Сесії і токени (JWT): автентифікація без спільної пам'яті
11. [nb:communications/networks/anycast-gslb] Anycast і глобальне балансування DNS: найближчий дата-центр
12. [own:lb-our-service] Ставимо балансувальник перед «Лінком»: що з довгими WebSocket і деплоєм (кумулятивно)

### 8.3 Кеш-ієрархія: браузер → CDN → edge → застосунок → БД (мета: не ходити далеко за тим самим — інакше origin горить)
13. [nb:communications/protocols/http-caching] HTTP-кешування: Cache-Control, ETag, 304
14. [nb:communications/networks/cdn] CDN: контент поруч із користувачем
    вставка hist-akamai-cdn.md: від колапсів сайтів 90-х до Akamai: народження індустрії CDN
    вставка comp-cdn-pop.md: клас: точка присутності (PoP) — що всередині, від пірингу до SSD-кешів
15. [nb:programming/architecture/cache-write-strategies] Стратегії запису: write-through, write-back, write-around
16. [nb:programming/architecture/cache-invalidation] Інвалідація: «найважча задача інформатики» — TTL, версії ключів, події
17. [own:cache-hierarchy-request-path] Шлях запиту «Лінка» крізь усі яруси кешу: рахуємо hit-rate і трафік до origin (кумулятивний синтез)
    вставка math-hit-rate-stack.md: множення hit-rate по ярусах: скільки насправді доходить до бази

### 8.4 Кеш-патології: коли кеш вбиває (мета: що ламається — стемпід, гарячі ключі, пробиття)
18. [nb:programming/architecture/cache-stampede] Кеш-стемпід: тисяча запитів по один протухлий ключ
    вставка proj-stampede-lock.md: захист: request coalescing і м'який TTL — робочий код
19. [nb:programming/distributed/hot-keys] Гарячі ключі: коли один ключ палить цілий кеш-шард
20. [nb:algorithms/data-structures/bloom-filter] Фільтр Блума
21. [nb:programming/architecture/negative-caching] Негативний кеш і пробиття (penetration): фільтр Блума на вході
22. [own:celebrity-tweet] Кейс: твіт селебриті — гарячий ключ, стемпід і фан-аут таймлайнів разом (синтез)
    вставка hist-twitter-timeline.md: Twitter: від запиту в базу до попередньо зібраних таймлайнів (fan-out on write) і гібриду для селебриті

### 8.5 Кейс: мільйони дивляться відео (мета: зібрати модуль на YouTube-класі задач)
23. [ref:algorithms/data-compression/quality-bitrate] (done) Якість і бітрейт
24. [nb:communications/protocols/hls-dash] Стрімінг сегментами: HLS/DASH — плейлист і шматки по кілька секунд
25. [ref:communications/networks/adaptive-bitrate] (pending) Адаптивний бітрейт (ABR)
26. [nb:programming/architecture/object-storage] Об'єктне сховище: блоби без файлової системи
27. [own:youtube-case] Кейс YouTube: завантаження → транскодування чергою → сегменти в CDN → ABR у плеєрі — як мільйони дивляться і сервери не рвуться (великий синтез М4–М8)
    вставка hist-youtube-growth.md: 2005–2007: як YouTube пережив вибуховий ріст — Python, шардинг MySQL і «хитрощі, які соромно показувати»

### 8.6 Читання на масштабі (мета: розвантажити базу, коли читань у тисячі разів більше, ніж записів)
28. [nb:programming/databases/denormalization-materialized-views] Денормалізація і матеріалізовані подання: платити записом за читання
29. [nb:programming/databases/search-index-inverted] Пошуковий (інвертований) індекс
30. [own:read-path-capstone] Читальний шлях «Лінка» під ×1000: кеш + репліки + денормалізація разом (кумулятивний капстоун)

---

# Модуль 9. Високе навантаження II: вижити під піком — 24 кроки, 6 розділів

### 9.1 Впустити не всіх: rate limiting (мета: без лімітів один клієнт-цикл кладе API для всіх)
1. [nb:algorithms/design-paradigms/token-bucket] Token bucket і leaky bucket
   вставка proj-token-bucket.md: token bucket + ковзне вікно — робочий код
2. [nb:algorithms/design-paradigms/rate-limiting-distributed] Розподілений rate limiting: центральні лічильники проти локальних квот
3. [nb:programming/architecture/admission-control] Admission control: пріоритет запитів — кого пускати, коли місця нема
4. [own:limits-for-api] Ліміти API «Лінка»: по ключу, по IP, по тарифу (кумулятивно)

### 9.2 Скинути баласт, лишити ядро (мета: без деградації перевантаження = колапс, з нею = повільніше, але живе)
5. [nb:programming/architecture/graceful-degradation] Плавна деградація: вимкнути рюші, лишити ядро
6. [nb:programming/architecture/load-shedding] Скидання навантаження: швидке 503 рятує решту
7. [nb:programming/architecture/queue-limits-timeouts] Обмежені черги і дедлайн запиту: нескінченна черга = нескінченна латентність
8. [nb:programming/architecture/retry-budget] Бюджет повторів і поширення дедлайнів: ретраї під піком — підпал
9. [own:metastable-failures] Метастабільні відмови: система, що не встає після піку, бо кеш холодний і всі повторюють (синтез)
   вставка hist-metastable-outages.md: як великі компанії описали метастабільні збої — від папера Bronson et al. до реальних розборів

### 9.3 Потужність слідом за попитом: автоскейл (мета: без нього — або платиш за повітря, або лежиш у пік)
10. [nb:programming/operations/autoscaling] Автоскейлінг: за якими метриками і з яким лагом
11. [nb:programming/operations/stateless-scaling] Stateless як передумова: куди подіти сесії і файли
12. [nb:programming/operations/cold-start-warmup] Холодний старт і прогрів: кеш порожній, JIT спить, пули не зібрані
13. [nb:programming/architecture/serverless] Serverless/FaaS оглядово: масштаб до нуля і його ціна
14. [own:flash-crowd] Флеш-крауд для «Лінка»: реліз, розсилка, Суперкубок — план заздалегідь (кумулятивно)
    вставка hist-slashdot-superbowl.md: від «слешдот-ефекту» до реклами в Суперкубку: класика флеш-краудів

### 9.4 Ізолювати вибух: комірки і перегородки (мета: відмова частини ≠ відмова всього)
15. [nb:programming/architecture/bulkhead] Перегородки (bulkhead): окремі пули на окремі залежності
16. [nb:programming/architecture/cell-based-architecture] Комірчаста архітектура: багато маленьких копій системи замість однієї великої
    вставка hist-aws-cells.md: як AWS будує сервіси з комірок і чому падає одна AZ, а не регіон
17. [nb:programming/distributed/shuffle-sharding] Shuffle sharding: кожному клієнту — своя випадкова пара серверів
    вставка math-shuffle-sharding.md: комбінаторика: ймовірність повністю розділити долю з «шумним сусідом» ≈ 1/C(n,k)
18. [nb:programming/distributed/multi-region] Мультирегіон: активний-активний чи активний-пасивний
19. [own:isolate-our-service] Комірки для «Лінка»: чи варто, з якого розміру, по чому різати (кумулятивне рішення)

### 9.5 Гроші: масштаб має бюджет (мета: архітектура без цінника — фантазія)
20. [nb:programming/operations/capacity-cost] Вартість потужності: залізо, хмара, трафік, ліцензії
21. [nb:programming/operations/overprovisioning-headroom] Запас (headroom): чому 60% утилізації — це вже «повно»
22. [own:cost-per-request] Ціна одного редиректу «Лінка»: рахуємо і ріжемо (кумулятивно)
    вставка math-cost-model.md: модель $/1000 запитів: CPU + трафік + сторедж + люди

### 9.6 Анатомія великого падіння (мета: синтез модуля на реальних каскадах)
23. [own:outage-anatomy] Анатомія каскадної відмови: таймлайн типового великого інциденту — від тригера до метастабільності (синтез М9)
    вставка hist-big-outages.md: класичні каскади: S3 2017 (одна команда оператора), Cloudflare 2019 (regex), Facebook 2021 (BGP)
24. [own:overload-checklist] Чеклист живучості під піком: від лімітів до комірок (кумулятивний підсумок)

---

# Модуль 10. Експлуатація: система живе в проді — 26 кроків, 6 розділів

### 10.1 Бачити систему: логи, метрики, трейси (мета: без спостережності дебаг проду = ворожіння)
1. [nb:programming/operations/structured-logging] Структуровані логи: не текст, а події
2. [nb:programming/operations/metrics-timeseries] Метрики: лічильники, ґейджи, гістограми — і чому перцентилі не усереднюють
3. [nb:programming/operations/distributed-tracing] Розподілений трейсинг: шлях одного запиту крізь двадцять сервісів
   вставка hist-google-dapper.md: Dapper: як Google навчився бачити запит наскрізь
4. [ref:programming/software-engineering/profiling] (done) Профілювання
5. [own:three-pillars-service] Обвішуємо «Лінк»: кореляційний ID від браузера до БД (кумулятивно)
   вставка proj-observability-stack.md: логи+метрики+трейси на нашому сервісі — робочий код

### 10.2 Скільки дев'яток треба: SLO і бюджет помилок (мета: надійність — число, а не відчуття)
6. [nb:programming/operations/sli-slo] SLI і SLO: обіцянка, яку можна виміряти
7. [nb:programming/operations/error-budget] Бюджет помилок: ліцензія на ризик і мир між dev і ops
   вставка hist-google-sre.md: Google SRE: як error budget помирив розробку з експлуатацією
8. [nb:programming/operations/alerting] Алерти на симптоми, а не причини: пейджер, який не бреше
9. [own:slo-our-service] SLO «Лінка»: 99.9% редиректів швидші за 100 мс — і що з цього випливає (кумулятивно)
   вставка math-nines-budget.md: дев'ятки в хвилини: скільки можна лежати на місяць за 99.9%

### 10.3 Деплой без зупинки світу (мета: зміни — головне джерело збоїв; викочувати треба вміти)
10. [nb:programming/operations/ci-cd-pipeline] CI/CD: конвеєр від коміту до проду
11. [nb:programming/operations/blue-green-deploy] Blue-green: два світи і рубильник
12. [nb:programming/operations/canary-release] Канарейка: 1% користувачів першими
13. [nb:programming/operations/rolling-update-compat] Поступовий викат і сумісність: версії N і N+1 живуть поруч
14. [nb:programming/databases/online-schema-migration] Міграції схеми без даунтайму: expand–contract
15. [own:deploy-our-service] Викочуємо «Лінк»: канарейка + прапорці з М3 + автовідкат (кумулятивно)

### 10.4 Коли все ж упало: інциденти (мета: мінімізувати шкоду і справді навчитися)
16. [nb:programming/operations/oncall-runbooks] Чергування і ранбуки
17. [nb:programming/operations/incident-response] Керування інцидентом: ролі, комунікація, таймлайн
18. [nb:programming/operations/blameless-postmortem] Постмортем без винних
    вставка hist-postmortem-culture.md: від авіації та АЕС до IT: звідки культура розборів без покарань
19. [own:incident-drill] Розбираємо падіння «Лінка»: від пейджа о 3:00 до постмортему (кумулятивний сценарій)

### 10.5 Ламати навмисно: хаос і навантаження (мета: знайти слабке раніше за користувачів)
20. [nb:programming/operations/load-testing] Навантажувальне тестування: профіль трафіку, а не «жми сильніше»
    вставка proj-load-test.md: навантажувальний тест «Лінка»: знаходимо коліно — робочий код
21. [nb:programming/operations/chaos-engineering] Хаос-інженерія: гіпотеза → вибух → висновок
    вставка hist-chaos-monkey.md: Netflix: мавпа, що вимикає сервери в проді, і чому це подіяло
22. [nb:programming/operations/capacity-planning] Планування місткості: прогноз росту проти строків закупівель
23. [own:game-day] Game day «Лінка»: вбиваємо репліку, кеш і цілий регіон — за планом (кумулятивно)

### 10.6 Фінал: уся дуга разом (мета: синтез курсу)
24. [own:request-journey-final] Життя одного запиту: від DNS і TLS через LB, кеші, шарди — до трейса і дашборда (наскрізний розбір усіх шарів курсу)
25. [own:course-capstone-design] Капстоун: проєктуємо відеоплатформу на мільйон одночасних глядачів — повний system design з обґрунтуванням кожного вибору
26. [own:architect-checklist] Чеклист архітектора: питання, які треба поставити будь-якій системі (закриття курсу)

---

# Зведення

## Числа

| Показник | Значення |
|---|---|
| Кроків усього | **258** (ціль 250 ±10% ✓) |
| Модулів | 10 (22–30 кроків) |
| Розділів | 55 (5–6 на модуль, кожен = одна мета) |
| `[ref]` на наявні book-теми | **46** (з них done: 23; pending: 23 — вже стоять у чергах book-маніфестів) |
| `[nb]` нових book-атомів | **165** |
| `[own]` власних статей курсу | **47** |
| Вставок | **53**: hist 24 · proj 16 · math 10 · comp 3 |

## Нові nb за галузями

- `programming/design-patterns` (нова) — 20; `programming/architecture` (нова) — 33; `programming/distributed` (нова) — 31; `programming/operations` (нова) — 22.
- Наявні: `programming/databases` 17, `programming/software-engineering` 11, `programming/systems` 8, `programming/networking` 5, `programming/languages` 3, `programming/security` 1; `algorithms/data-structures` 4, `algorithms/design-paradigms` 2; `communications/protocols` 5, `communications/networks` 2, `communications/cryptographic-comm` 1.

## Головні кейси компаній (де живуть)

- WhatsApp/Erlang — hist при 5.3 (актори); nginx проти Apache — hist при 5.5 (C10K); Amazon Dynamo — hist при 6.5; Akamai — hist при 6.4 (consistent hashing) і 8.3 (CDN); Kafka/LinkedIn — hist при 7.1; Amazon «дві піци» — hist при 7.4; Twitter timeline fan-out — hist при 8.4; **YouTube — окремий own-крок 8.5.27 + hist**; AWS cells — hist при 9.4; S3/Cloudflare/Facebook-BGP каскади — hist при 9.6; Google Dapper і SRE — hist при 10.1/10.2; Netflix Chaos Monkey — hist при 10.5.

## Примітки для реалізації

1. **Дублікат в індексі:** «Адаптивний бітрейт» існує двічі — `communications/networks/adaptive-bitrate` і `algorithms/data-compression/adaptive-bitrate` (обидва pending). Курс реферить communications-версію; при письмі варто злити або розвести кути.
2. **Машини станів:** в індексі три близькі теми (`state-machine`, `state-machine-embedded`, `mode-state-machine`); курс реферить загальну `programming/embedded-systems/state-machine` (pending) — писати її треба без embedded-ухилу.
3. **Повторних ref немає:** кожна тема реферована рівно один раз; де потрібне повернення (backpressure у 9.2, feature flags у 10.3) — зв'язка йде інлайн-`book:`-лінком у прозі own-кроку.
4. **Pending-рефи (23)** — уже в чергах book-письма; для проходження курсу їх треба підняти пріоритетом (особливо: backpressure, queue-theory-networks, order-statistics, heavy-tail-distributions, dhcp-dns, quic-protocol, ntp-sync, adaptive-bitrate).
5. **Порядок письма курсу:** спершу М1–М3 (незалежні від хайлоад-ланцюга), паралельно можна писати book-атоми патернів (М2 — 20 однотипних атомів, зручний батч для write-batch.js); далі М4→М10 строго послідовно — own-кроки кумулятивні, нитка «Лінка» наскрізна.
6. **v6:** кожна нова стаття починається `<preknowlist>`; для guide-кроків — лише непройдене по курсу (напр., у 8.2 JWT-крок посилається на tls-handshake з 6.1 як пройдене, а на криптографію з відкритим ключем — як передумову з book).
