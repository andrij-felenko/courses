# progarch v2 — лінза «Типи програмування»: щоб випускник будь-якого профілю впізнав свій світ

Дата: 2026-07-05. Основа: `guide/progarch/_plan.md` (264 кроки, прочитано повністю), звіти `_analysis/*`, індекс книг `book-index-fresh.txt` (2447 тем, усі ref-и нижче звірені зі статусами). У репозиторії нічого не змінено.

## 0. Діагноз базового плану і рецепт

**Діагноз.** М1–М3 базового плану (принципи, патерни, застосунок) — доменно-нейтральні й добрі. Але М4–М10 — фактично «шлях веб-бекендера»: реляційна база → HTTP-API → репліки/шарди → мікросервіси → хайлоад → експлуатація. Це найкраще задокументований шлях індустрії, і він лишається хребтом, — але **геймдев, десктоп, системник, дата-інженер, ML-інженер і embedded-розробник у плані-264 свого світу не бачать**: немає жодного кроку про game loop, undo/redo, демони/IPC/CLI, DAG-пайплайни, сервінг моделей; embedded — лише «містки». Індекс книг це підтверджує: в book/ нуль тем про ігри, GUI-стан, data-engineering, MLOps (при цьому є 34 готові ML-теми, 181 embedded-тема і сильні systems/computer-architecture — їх треба реюзати, а не переписувати).

**Рецепт із трьох ходів** (сумарно ~124 кроки з бюджету +236 до ~500; решта — іншим лінзам: повний каталог патернів, mitigation-прийоми, розширення universal-модулів):

1. **Доменні приклади всередину універсальних тем** — дешево, скрізь (таблиці «вплітання» в кожному розділі нижче).
2. **П'ять профіль-модулів** «як універсальні принципи спеціалізуються»: Реальний час/ігри · Клієнти (веб/мобайл/десктоп) · Системне ПЗ й інструменти · Дата-платформи (+ML-розділ) · IoT/edge (+медіа-розділ). ML і медіа — розділи, не модулі; embedded-знання не дублюємо (є курс embedded) — беремо архітектурний поверх.
3. **Три нові галузі book** (`programming/games`, `programming/clients`, `programming/data-engineering`) + точкові розширення наявних; ~46 нових nb-атомів + ~12 промоцій із «запасу» плану-264 (memento, crdt, map-reduce, oltp-olap, cdc, hyperloglog, graceful-shutdown, flyweight, prototype, mediator…).

## 1. Зведена таблиця

| Домен | У плані-264 | Що додати | Власний модуль/розділ? |
|---|---|---|---|
| Веб-бекенд | ~повний (М4–М10) | нічого нового; лишається хребтом | уже є |
| Ігри й realtime-симуляції | 0 кроків | ~11 nb (галузь games) + 4 own | **ТАК: модуль ~24** |
| Десктоп | лише патерни згадками | ~6 nb + промоція memento/flyweight | розділ у модулі «Клієнти» |
| Клієнти веб/мобайл | websocket, http-caching | ~8 nb (галузь clients) + crdt | **ТАК: модуль ~26 (разом із десктопом)** |
| Системне/інфраструктурне ПЗ + tooling | systems-атоми як ref-и для конкурентності | ~6 nb + 8 pending-ref-ів (AST, regex-engine, dynamic-linking…) | **ТАК: модуль ~24** |
| Data/batch-аналітика | 0 (тільки event-log у М8) | ~9 nb (галузь data-engineering) + промоції | **ТАК: модуль ~28 (з ML-розділом)** |
| ML-у-проді | 0 | ~3 nb (operations) + готові ref-и ML-гілки | розділ 5–6 кроків у дата-модулі |
| Embedded/realtime-обмеження | містки (watchdog, MQTT, priority-inversion) | ~4 nb IoT-рівня; решта — ref-и на готове | **ТАК: профіль-модуль «IoT/edge» ~22 (+медіа-розділ)**; МК-рівень — ref-ами, без дублювання курсу embedded |
| Медіа/відео | М9.5 (YouTube, ABR) — роздача є | +2 nb (webrtc, hls-dash-промоція) — інжест/лайв | розділ у модулі IoT/edge (камери DH) |

---

## 2. Домен «Ігри й realtime-симуляції»

Єдиний великий клас ПЗ, де архітектуру диктує **жорсткий періодичний дедлайн** (кадр) і **безперервний змінний стан світу**. Без нього курс не пояснює половину прийомів роботи з пам'яттю і станом.

### 2.1 Атоми-мусти (нова галузь `programming/games` — «Ігри й симуляції реального часу»)

| Крок | Суть | Статус |
|---|---|---|
| [nb:programming/games/game-loop] | Ігровий цикл: update/render, фіксований крок + акумулятор, «спіраль смерті» | нове |
| [nb:programming/games/frame-budget] | Бюджет кадру 16,6 мс: жорсткий дедлайн, hitch, кадрові хвости | нове |
| [nb:programming/games/ecs] | ECS: сутність–компонент–система — стан світу як таблиці | нове |
| [nb:programming/software-design/data-oriented-design] | Data-oriented design: SoA проти AoS, «пам'ять повільніша за CPU» (універсальний атом; ECS — приклад) | нове |
| [nb:programming/games/scene-graph] | Граф сцени: composite у ділі, трансформації, culling | нове |
| [nb:algorithms/data-structures/spatial-partitioning] | Просторові структури: сітка, quadtree, BVH | нове |
| [nb:programming/games/state-replication] | Реплікація стану: снапшоти, дельти, зона інтересу | нове |
| [nb:programming/games/client-prediction] | Клієнтське передбачення і реконсиляція із сервером | нове |
| [nb:programming/games/lockstep-rollback] | Lockstep і rollback: детермінована симуляція як вимога | нове |
| [nb:programming/games/entity-interpolation] | Інтерполяція/екстраполяція між тіками | нове |
| [nb:programming/games/asset-pipeline] | Конвеєр ассетів: оффлайн-збірка ресурсів (це data/batch геймдеву) | нове |
| [ref:communications/protocols/tcp-vs-udp] | чому netcode живе на UDP | done |
| [ref:communications/networks/latency-reliability] | затримка як фізика | done |
| [ref:programming/computer-architecture/fixed-point] | фіксована кома → детермінізм lockstep | done |
| [ref:algorithms/numerical-algorithms/numerical-ode] | інтегратори фізики (Ейлер/Верле) | pending |
| [ref:math/logic-foundations/finite-automata] | стани AI/анімацій | done |
| [ref:algorithms/data-structures/ring-buffer] | буфер вводу/команд | pending |
| [ref:algorithms/signal-robotics/real-time-systems] | hard/soft realtime рамка | pending |
| [ref:algorithms/signal-robotics/kalman-filter], [ref:…/motion-model] | згладжування/передбачення руху | done |

Запас галузі: behavior-trees, particle-systems, a-star-pathfinding (algorithms/graph-algorithms), game-ai-steering, deterministic-random.

### 2.2 Вплітання в універсальні теми

| Універсальна тема (модуль) | Ігровий приклад |
|---|---|
| Цикл подій (М5) | ігровий цикл — «event loop із дедлайном»: поруч, як брати |
| Кеш/когерентність, false sharing (М5) | SoA проти AoS; чому ECS обходить кеш-проміахи |
| Пул об'єктів (М2) | пул частинок/куль — канонічне застосування |
| Flyweight (промоція із запасу) | спрайти/тайли/гліфи |
| Prototype (промоція) | спавн юнітів із шаблону |
| Таймаути/бюджети (М6), перцентилі (М9) | 16,6 мс як p99-мислення; frame pacing |
| Реконсиляція стану, eventual consistency (М7) | rollback netcode = оптимістичне виконання + реконсиляція — ідеальний місток-приклад |
| Черги/backpressure (М5/М8) | вхідні команди гравців, тікрейт сервера |
| Детермінізм і відтворюваність (М10 інциденти) | replay-файли як «трейсинг» симуляцій |

Кейси/вставки: hist-age-of-empires-lockstep («1500 лучників по модему», 2001), hist-ggpo-rollback (файтинги), hist-eve-time-dilation, hist-gaffer-fixed-timestep; proj-mini-game-loop, proj-rollback-demo.

### 2.3 Вердикт

**Окремий модуль «Реальний час: ігри й симуляції» (~24 кроки, 5 розділів)**, місце — після М6 (мережа), перед М7 (розподілені): netcode потребує UDP/latency, а rollback стає трампліном до реконсиляції М7. Склад: (1) Цикл і час: game-loop, frame-budget, numerical-ode, fixed-point; (2) Стан світу: ecs, data-oriented-design, scene-graph, spatial-partitioning; (3) Мультиплеєр: state-replication, prediction, interpolation, lockstep-rollback; (4) **Варіантний блок**: синхронізація мультиплеєра А/Б/В + вибір (див. §9); (5) Конвеєр ассетів і симуляції поза іграми (digital twin, DH-панель наживо). Digital Homes тут другорядний (живі графіки датчиків = entity interpolation; twin хаба) — головні приклади чесно ігрові.

---

## 3. Домен «Десктоп-застосунки»

Довгоживучий процес із документом, який користувач **редагує, скасовує і зберігає роками** — унікальні сили: undo, автозбереження, файловий формат, плагіни.

### 3.1 Атоми-мусти

| Крок | Суть | Статус |
|---|---|---|
| [nb:programming/clients/document-model] | Документна модель: документ як структура даних + інваріанти (DOM/проєкт DAW) | нове |
| [nb:programming/clients/undo-redo] | Undo/redo: стек команд, злиття правок, межі транзакції користувача | нове |
| [nb:programming/clients/autosave-recovery] | Автозбереження й відновлення після краху: атомарний запис, журнал правок | нове |
| [nb:programming/representation/file-format-design] | Дизайн файлового формату: магічні байти, чанки (PNG/RIFF-клас), версії, сумісність уперед/назад | нове |
| [nb:programming/clients/ui-thread-model] | UI-потік і фонові роботи: чому інтерфейс «замерзає» | нове |
| промоція: memento (design-patterns, запас → курс) | без нього undo не скласти | запас плану |
| [ref:programming/systems/dynamic-linking] | плагіни як динамічне завантаження | pending |
| [ref:algorithms/data-structures/copy-on-write] | снапшоти документа задешево | pending (уже в плані М3) |
| ref-и вже в плані: mvc-mvp-mvvm, plugin-architecture, immutability, finite-automata, command | — | — |

### 3.2 Вплітання в універсальні теми

| Універсальна тема | Десктоп-приклад |
|---|---|
| Command (М2) | undo-стек редактора (не лише «черга задач») |
| Memento + event sourcing (М8) | історія Photoshop; «документ як журнал правок» — event sourcing на клієнті |
| Атомарне перейменування, fsync (М4 files-as-storage) | «Зберегти файл» — той самий патерн, що WAL |
| Граф залежностей, topological-sort (М1/М3) | рушій перерахунку Excel |
| Плагіни (М3) | VS Code: extension host в окремому процесі — ізоляція збоїв = bulkhead на клієнті |
| Мутекси й цикл подій (М5) | правило одного UI-потоку |
| Config/feature flags (М3) | налаштування користувача проти конфігурації системи |

Кейси: hist-photoshop-history, hist-vscode-extension-host, hist-excel-recalc; proj-undo-stack (робочий код).

### 3.3 Вердикт

Окремого модуля не заслуговує — **два розділи в модулі «Клієнти»** (див. §4): «Документ і його історія» + «Розширюваність і довгоживучий стан». Ризик інакше — модуль-«зоопарк» без єдиної мети.

---

## 4. Домен «Клієнти: веб і мобайл» (+ десктоп із §3)

Клієнт — половина кожної системи (і Digital Homes: веб + мобільний + ПК-додаток), а в плані-264 клієнтської архітектури немає взагалі.

### 4.1 Атоми-мусти (нова галузь `programming/clients` — «Клієнтські застосунки»)

| Крок | Суть | Статус |
|---|---|---|
| [nb:programming/clients/ui-state-unidirectional] | Односпрямований потік даних: Flux/Elm-модель, стан → подання | нове |
| [nb:programming/clients/optimistic-ui] | Оптимістичний інтерфейс: показати до підтвердження, відкотити при відмові | нове |
| [nb:programming/clients/offline-first] | Offline-first: локальна база — правда, синхронізація в тлі | нове |
| промоція: [nb:algorithms/parallel-distributed/crdt] (запас → курс) | злиття станів без координатора | запас плану |
| [nb:programming/clients/push-notifications] | Push: розбудити застосунок, якого нема в пам'яті | нове |
| [nb:programming/clients/mobile-constraints] | Мобільні сили: батарея, радіо, флакі-мережа, вбивство процесу ОС | нове |
| [nb:programming/distributed-systems/backend-for-frontend] | BFF: бекенд під форму клієнта | нове |
| [nb:programming/clients/client-release-trains] | Постачання клієнтів: стор-реліз, форс-апдейт, парк старих версій | нове |
| ref-и з плану: websocket, http-caching, api-versioning, sessions-state, oauth-oidc | — | — |

### 4.2 Вплітання в універсальні теми

| Універсальна тема | Клієнтський приклад |
|---|---|
| Retry/backoff/ідемпотентність (М6) | мобільний клієнт у метро — головний споживач цих прийомів |
| Eventual consistency, read-your-writes (М7) | optimistic UI = клієнтська реконсиляція (пара до rollback з §2) |
| api-versioning (М6) | «клієнти не оновлюються місяцями» — сумісність як закон |
| Кеш-ієрархія (М9) | перший ярус — сам клієнт |
| Feature flags (М3/М10) | ремоут-конфіг мобільних застосунків |
| Черги (М8) | локальна черга вихідних повідомлень WhatsApp |

Кейси: hist-figma-multiplayer (CRDT-подібне злиття), hist-whatsapp-offline-queue, hist-linear-sync-engine; proj-optimistic-todo.

### 4.3 Вердикт

**Модуль «Клієнти: веб, мобайл, десктоп» (~26 кроків, 5 розділів)**, після М7/М8 (потрібні eventual consistency і події). Склад: (1) Стан UI і односпрямований потік; (2) Документ і його історія (десктоп §3); (3) Offline-first і синхронізація (crdt, optimistic-ui); (4) Клієнт і мережа (push, mobile-constraints, BFF); (5) Постачання клієнтів + **варіантний блок** «синхронізація мобільного клієнта DH» (§9).

---

## 5. Домен «Системне й інфраструктурне ПЗ + tooling»

Аудиторія системників/DevOps-інструментальників. База в book/ сильна (systems, languages, computer-architecture), бракує «архітектури процесу в ОС» і «CLI як контракту».

### 5.1 Атоми-мусти

| Крок | Суть | Статус |
|---|---|---|
| [nb:programming/systems/daemons-services] | Демон/сервіс ОС: життєвий цикл, супервізія, перезапуск | нове |
| [nb:programming/systems/ipc-mechanisms] | IPC однієї машини: пайпи, unix-сокети, спільна пам'ять, сигнали | нове |
| [nb:programming/systems/signals-graceful-shutdown] | Сигнали і graceful shutdown (SIGTERM→drain→exit); промоція operations/graceful-shutdown із запасу | нове |
| [nb:programming/software-design/cli-design] | CLI як API: аргументи, exit-коди, stdin/stdout-контракти, композиційність | нове |
| [nb:programming/systems/mmap-files] | memory-mapped files (промоція із запасу плану) | запас плану |
| [ref:algorithms/data-structures/abstract-syntax-tree] | AST — серце інструментів коду | pending |
| [ref:algorithms/string-geometry-streaming/regex-engine] | рушій регексів | pending |
| [ref:math/logic-foundations/regular-languages] | чому grep швидкий | pending |
| [ref:algorithms/graph-algorithms/topological-sort] | build-система/DAG залежностей | pending |
| [ref:programming/systems/dynamic-linking] | плагіни/розширення | pending |
| [ref:programming/languages/elf-format], [ref:…/linking] | артефакт як формат | done |
| [ref:programming/systems/garbage-collection], [ref:…/memory-allocator-internals] | рантайм як інфраструктура | pending |
| [ref:programming/computer-architecture/virtual-memory] | процес очима ОС | done |
| [ref:programming/software-engineering/errno], [ref:math/number-theory/octal-system] | POSIX-дрібниці як контракти | pending |

### 5.2 Вплітання в універсальні теми

| Універсальна тема | Системний приклад |
|---|---|
| Pipes-filters (М3, вже є hist-unix-pipes) | розширити robочим прикладом композиції CLI |
| Серіалізація/еволюція схем (М6) | файлові формати: SQLite тримає сумісність 20 років |
| Log-structured storage (М4, done) | git object model як сховище |
| Health checks / self-healing (М8/М10) | супервізор демонів = reconciliation loop у мініатюрі |
| Деплой (М10) | пакетні менеджери й міграції конфігів |
| Спостережність (М10) | syslog/journald — структуровані логи задовго до хмар |

Кейси: hist-sqlite-file-format, hist-git-object-model, hist-systemd-debate, hist-llvm-pipeline; proj-mini-daemon (демон із graceful shutdown), proj-cli-pipeline.

### 5.3 Вердикт

**Модуль «Системне ПЗ та інструменти» (~24 кроки, 5 розділів)**, після М5 (потрібні процеси/потоки). Склад: (1) Процес у ОС: демони, сигнали, життєвий цикл; (2) IPC і композиція процесів (+CLI-дизайн); (3) Файлові формати й сумісність (file-format-design §3 — спільний атом); (4) Інструменти, що читають код: regex→AST→лінтер, build як DAG; (5) Рантайми й розповсюдження: GC/алокатори, лінкування, semver/ABI бібліотек. Tooling окремого модуля не заслуговує — це розділи 2/4/5 тут.

---

## 6. Домен «Data/batch-аналітика»

«Статистика для розробників» Digital Homes — чесний привід, але домен самоцінний: пайплайни — третя велика парадигма виконання (запит/подія/**джоб**).

### 6.1 Атоми-мусти (нова галузь `programming/data-engineering` — «Інженерія даних»)

| Крок | Суть | Статус |
|---|---|---|
| [nb:programming/data-engineering/batch-vs-streaming] | Пакетна проти потокової: свіжість ↔ повнота ↔ вартість | нове |
| [nb:programming/data-engineering/pipeline-dag] | Пайплайн як DAG: оркестрація, залежності, retry (ref: topological-sort) | нове |
| [nb:programming/data-engineering/idempotent-jobs] | Ідемпотентний джоб: перезапуск без страху, партиції за датою | нове |
| [nb:programming/data-engineering/backfill] | Backfill: перерахунок історії, версія логіки поруч із даними | нове |
| [nb:programming/data-engineering/stream-windows] | Вікна й watermark: час події ≠ час обробки, спізнілі дані | нове |
| [nb:programming/data-engineering/stream-state-checkpoints] | Стан у потоці й чекпоінти: «exactly-once» чесно | нове |
| [nb:programming/databases/oltp-olap] (промоція із запасу) | два світи навантажень | запас плану |
| [nb:programming/databases/columnar-storage] | колонкове сховище: чому аналітика читає стовпці | нове |
| [nb:programming/databases/change-data-capture] (промоція) | база → потік подій без подвійного запису | запас плану |
| [nb:algorithms/parallel-distributed/map-reduce] (промоція) | розкидати й зібрати; спадок для Spark-класу | запас плану |
| [nb:algorithms/string-geometry-streaming/hyperloglog] (промоція; + count-min-sketch у запасі) | «скільки унікальних» за копійки — DH-статистика | запас плану |
| ref-и: event-log (М8), backpressure (pending), external-sort (запас) | — | — |

### 6.2 Вплітання в універсальні теми

| Універсальна тема | Data-приклад |
|---|---|
| Ідемпотентність (М6) | джоб поруч із HTTP-запитом — той самий принцип у двох світах |
| Event sourcing / журнал (М8) | backfill = replay журналу; «The Log» Крепса — спільний фундамент |
| Черги/backpressure (М5/М8) | потокова обробка — головний споживач |
| Міграції (М4) | еволюція схем датасетів, expand–contract для таблиць |
| CI/CD (М10) | data-пайплайн — це CI для даних; тести якості даних |
| Шардинг (М7) | партиції за ключем/датою — те саме мислення |

Кейси: hist-mapreduce-google (2004), hist-kappa-vs-lambda (Kreps), hist-uber-data-platform; proj-mini-dag-runner, proj-dh-telemetry-rollup (агрегація телеметрії DH: сира → хвилинна → добова).

### 6.3 Вердикт

**Модуль «Дата-платформи: пайплайни й аналітика» (~28 кроків, 6 розділів)**, після М8 (журнал подій уже є). Склад: (1) OLTP↔OLAP і колонки; (2) Batch: DAG, ідемпотентні джоби, backfill; (3) Stream: вікна, watermark, чекпоінти; (4) Міст: CDC, sketch-структури; (5) **ML-у-проді** (див. §7); (6) **Варіантний блок** «статистика DH» (§9) + розбір реальної платформи.

---

## 7. Домен «ML-у-проді» (оглядово, без навчання ML)

book/ вже має 34 ML-теми (більшість basic:done) — курс НЕ вчить ML, він показує **модель як компонент системи**.

### 7.1 Атоми-мусти

| Крок | Суть | Статус |
|---|---|---|
| [ref:algorithms/machine-learning/train-vs-inference] | навчання ≠ вивід — головний поділ | **done** |
| [ref:algorithms/machine-learning/inference-latency] | латентність інференсу | **done** |
| [ref:algorithms/machine-learning/model-quantization] (+knowledge-distillation done) | стиснути модель під edge | **done** |
| [ref:algorithms/machine-learning/edge-computing] | де рахувати | pending |
| [nb:programming/operations/model-artifact] | Модель як версійований артефакт: код+дані+ваги; реєстр моделей | нове |
| [nb:programming/operations/model-serving] | Сервінг: модель за API, батчинг запитів, прогрів, GPU-пул | нове |
| [nb:programming/operations/model-drift] | Дрейф даних і деградація моделі: моніторинг якості як SLO | нове |
| запас: feature-store, training-serving-skew | — | нове (запас) |

### 7.2 Вплітання

Canary-деплой (М10) — канарка для **моделі**, не лише коду; метрики (М10) — якість передбачень як продукт-метрика; кеш (М9) — кешування інференсу; черги (М8) — батчинг запитів до GPU; автоскейл (М9) — GPU-пули дорогі й повільні на прогрів. Digital Homes — показовий наскрізний приклад: розпізнавання подій на відео камер (людина/тварина/авто), взимку модель «сліпне» (сніг = дрейф), оновлення моделі на парку хабів = fleet-OTA з §8.

### 7.3 Вердикт

**Розділ (5–6 кроків) у дата-модулі §6**, не окремий модуль: артефакт → сервінг → дрейф → варіантний блок «інференс DH: камера/хаб/хмара» (§9). Окремий модуль роздув би огляд у псевдо-курс MLOps.

---

## 8. Домен «Embedded/realtime + IoT/edge»

Особливий випадок: **знання вже є** (курс embedded + 181 атом), тож дублювати заборонено. Але архітектурний поверх IoT — флот пристроїв, розриви зв'язку, edge/cloud-межа — у жодному курсі не жив, а Digital Homes без нього не стоїть.

### 8.1 Атоми-мусти

| Крок | Суть | Статус |
|---|---|---|
| ref-и на готове (усі done): realtime-determinism, watchdog, super-loop, failsafe, bootloader, ota-update, ota-slots, priority-inversion, interrupt-priorities, scheduler, task-ipc, mqtt (detailed:done), video-latency (detailed:done), heap-dynamic-memory | детермінізм/ресурси як сили + механіка МК | **done** |
| pending-ref-и (підняти пріоритет): real-time-systems, edf-scheduling, interrupt-latency, state-machine-embedded, driver-pattern, ota-rollback, ota-image-signing, ring-buffer | realtime-планування і безпечні оновлення | pending |
| [nb:programming/distributed-systems/device-shadow] | Тінь пристрою (shadow/twin): бажаний ↔ фактичний стан, робота при розриві | нове |
| [nb:programming/distributed-systems/fleet-ota] | Оновлення парку: хвилі, health-гейти, A/B-слоти, автовідкат — deployment-strategies для заліза | нове |
| [nb:programming/distributed-systems/edge-cloud-split] | Межа edge/cloud: латентність, приватність, автономність, вартість каналу | нове |
| [nb:communications/protocols/webrtc] | лайв-відео/p2p крізь NAT | нове |
| промоція: hls-dash (запас communications → курс) | сегментоване відео (архів камер) | запас плану |
| ref-и медіа (уже в М9.5): quality-bitrate (done), inter-frame (done), adaptive-bitrate (pending), video-transmission (done) | — | — |

### 8.2 Вплітання в універсальні теми

| Універсальна тема | Embedded/IoT-приклад |
|---|---|
| Пул об'єктів / статична алокація (М2/М5) | «без купи після старту» — крайній випадок пулів |
| Перцентилі/хвости (М9) | GC-пауза й jitter проти жорсткого дедлайну; чому в прошивці немає GC |
| Health checks (М8) → watchdog (done) | самолікування: від МК до оркестратора — один патерн |
| Blue-green (М10) → ota-slots (done) | A/B-розділи прошивки = blue-green до хмар |
| Pub/sub (М8) → mqtt (done) | уже в плані — лишити |
| Backpressure (М8) | датчик 1 кГц → канал 1 кбіт/с: деградація на джерелі |
| Delivery guarantees (М6) | offline-буфер датчика: at-least-once + дедуплікація |

### 8.3 Вердикт

**Профіль-модуль «IoT та edge: від датчика до хмари» (~22 кроки, 5 розділів)** ближче до кінця дуги (після М9): (1) Обмеження як сили: ресурси/детермінізм/енергія (ref-пакет done-атомів); (2) Парк пристроїв: shadow, розриви, offline-буфери; (3) Fleet-операції: OTA хвилями, підпис образів, відкат; (4) **Медіа-розділ**: відео з камер — інжест (webrtc/rtsp-клас), сегменти (hls-dash), архів (object-storage М9), лайв проти запису + **варіантний блок** «відео DH» (§9); (5) Наскрізний розбір Digital Homes знизу догори + місток «далі — курс embedded». Це і є доменний профіль embedded-читача, без дублювання його курсу.

---

## 9. Варіантні блоки від цієї лінзи (2–3 own-«варіанти» + own-«вибір»)

1. **Мультиплеєр-синхронізація** (модуль §2, домен: гра — показовіша за DH): А lockstep · Б снапшоти+інтерполяція · В prediction+rollback → вибір (тікрейт, кількість гравців, чіти, детермінізм).
2. **Відео з камер DH** (модуль §8): А RTSP-релей через сервер · Б HLS-сегменти через CDN · В WebRTC p2p → вибір (латентність ↔ масштаб ↔ NAT/вартість).
3. **Статистика DH для розробників** (модуль §6): А агрегати в OLTP на льоту · Б журнал подій + нічний batch · В потокова агрегація з вікнами → вибір (свіжість ↔ вартість ↔ точність; sketch-и як чит-код).
4. **ML-інференс DH** (розділ §7): А на камері · Б на хабі · В у хмарі → вибір (латентність, приватність, оновлюваність, ціна).
5. **Синхронізація мобільного клієнта DH** (модуль §4): А полінг · Б push+кеш · В offline-first із CRDT → вибір (батарея, консистентність, складність).
6. **Оновлення парку хабів DH** (модуль §8): А всім одразу · Б хвилі з health-гейтами · В A/B-слоти з автовідкатом → вибір (радіус ураження, цегла-ризик, швидкість).
7. **Undo в редакторі сценаріїв DH** (модуль §4, десктоп): А стек команд · Б снапшоти (memento/COW) · В event sourcing документа → вибір (пам'ять, гранулярність, колаборація).

## 10. Нові галузі book і бюджет

**Нові галузі:** `programming/games` (~11 атомів курсу + 5 запас), `programming/clients` (~9 + 4 запас), `programming/data-engineering` (~7 + 3 запас). **Розширення наявних:** programming/systems (+5: daemons, ipc, signals-shutdown, mmap, abi-compat-запас), programming/operations (+3 ML), programming/distributed-systems (+4: device-shadow, fleet-ota, edge-cloud-split, bff), programming/software-design (+2: data-oriented-design, cli-design), programming/clients ← десктоп-атоми, programming/representation (+1 file-format-design), communications/protocols (+1 webrtc; промоція hls-dash), algorithms/data-structures (+1 spatial-partitioning), algorithms (+промоції: crdt, map-reduce, hyperloglog), programming/databases (+2: columnar-storage; промоції oltp-olap, cdc).

**Бюджет лінзи:** 5 модулів ≈ 124 кроки (24+26+24+28+22) ≈ 46 нових nb + ~12 промоцій із запасу + ~30 ref (з них ~20 done — embedded/ML-гілки дають миттєву читабельність) + ~36 own (розбори, варіанти, вибори). 264+124=388; решта ~112 кроків до ~500 — іншим лінзам (повний каталог патернів GoF+поза-GoF, mitigation-прийоми, поглиблення universal-модулів). Порядок дуги з умонтованими модулями: М1–М5 → **Системне ПЗ** → М6 → **Реальний час/ігри** → М7 → М8 → **Дата-платформи+ML** → **Клієнти** → М9 → **IoT/edge+медіа** → М10.

## 11. Тест «випускник впізнає свій світ»

| Профіль | Де впізнає себе |
|---|---|
| Геймдев | модуль §2 цілком; пул/flyweight/prototype у М2; data-oriented у пам'яті; rollback→реконсиляція М7 |
| Десктопник | розділи документа/undo/плагінів §4; atomic save в М4; UI-потік у М5 |
| Системник | модуль §5; log-structured (done) у М4; демон=reconciliation у М10 |
| Дата-інженер | модуль §6; ідемпотентність М6; журнал М8; шардинг М7 |
| ML-інженер | розділ §7 + готова ML-гілка book; canary моделей у М10 |
| Бекендер | хребет М4–М10 як і був |
| Embedded/IoT | модуль §8 + done-ref-и його курсу; ota-slots=blue-green, watchdog=health checks |
| Мобільник/фронтендер | модуль §4; retry в метро М6; версії API М6 |

**Ризики:** (1) профіль-модулі не мають перетворитись на «міні-курси доменів» — тримати фокус «як УНІВЕРСАЛЬНІ принципи спеціалізуються», кожен розділ = одна мета; (2) не дублювати embedded — тільки ref-и та архітектурний поверх; (3) нові галузі book тонкі на старті (7–11 атомів) — це нормально, вони ростимуть запасом; (4) варіантні блоки дорогі в письмі (3–4 own кожен) — сім блоків цієї лінзи покривають вимогу «2–3 варіанти + вибір» для ключових рішень, більше не треба.
