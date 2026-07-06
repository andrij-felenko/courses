# Лінза «КРИТИЧНІ ВУЗЛИ І ОБХОДИ ПРОБЛЕМ» — progarch v3

**Задача лінзи:** серце уточненої цілі v3 — «як архітектори розв'язують важливі вузли і обходять проблеми». Три каталоги: (1) типові вузли системи, (2) обходи/mitigations, (3) розширення каталогів патернів (cloud/EIP/data/мультирегіон/serverless). Це ЧИСТИЙ репертуар архітектора — жоден крок не є доменним підручником; консенсус трьох критиків («чуже»: ігри/медіа/UI/статистика/протоколи) не зачіпається, а «прогалини» критиків (мультирегіон, serverless, durable workflows, authz-моделі) ця лінза закриває у своїй зоні.

**База:** `_plan.md` v2 (533 кроки, прочитано повністю) · critic-1/2/3 (консенсус) · dh-patterns-full.md (перший прогін каталогів) · book-index-fresh.txt (2446 рядків — усі ref/nb звірено).

**Нотація:** `[ref:…]` — Є в індексі книг (статус вказано) · `[nb:…]` — новий book-атом · `[own:…]` — стаття курсу · **(v2 ✓)** — крок/атом уже в плані v2, лишається · **(v2-запас→курс)** — промот із «запасу» v2 · **NEW** — додає ця лінза. Галузі web-backend/distributed-systems/operations/software-design/databases в індексі ще не існують (створює v2) — усе там [nb].

---

## 0. Зведення лінзи

| Каталог | Нових nb | Промотів запасу v2 | own | Інлайн-розширень наявних атомів |
|---|---|---|---|---|
| §1 Вузли системи (15 вузлів) | 16 | 2 (authorization-models, file-uploads) | 1 інтро + 1 компакт-вибір | 3 |
| §2 Обходи/mitigations | 6 | — | — | 6 |
| §3 Розширення каталогів | 8 | 4 (merkle-tree, materialized-views, multi-leader-replication, cell-based-architecture) | 1 компакт-вибір | 6 |
| §4 Варіантні блоки | — | — | 3 повних (12) + 1 компакт | — |
| **Разом** | **30** | **6** | **16** | **~15** |

Внесок у бюджет ~500: **~52 кроки** (36 nb + 16 own) + ~25 вставок. Головна структурна пропозиція — **новий модуль «Вузли платформи» (~23 кроки, §6)**; решта атомів лягає в наявні модулі v2-дуги точковими вставленнями.

Нова галузь книги НЕ потрібна: вузли природно розширюють scope `programming/web-backend` (пропозиція правки scope — §7.1).

---

## 1. КАТАЛОГ ТИПОВИХ ВУЗЛІВ СИСТЕМИ

Вузол = повторювана підсистема з відомим простором рішень; архітектор її ВПІЗНАЄ, а не винаходить. Кожен вузол: 1–3 атоми + варіанти рішення. Відкриває каталог метод-крок:

- **[own:node-catalog-method] Вузли, які є в кожній системі: впізнати → зібрати → купити** — NEW. Що таке типовий вузол; каталоги готових рішень (cloud-патерни, EIP) як довідники архітектора; рамка build/buy/assemble (луна own:build-vs-buy М21.9 і own:boring-technology М3.29). Місце: відкриття модуля «Вузли платформи» (§6).

### 1.1. Автентифікація і сесії як вузол
- **(v2 ✓)** authentication (М12.18), jwt-tokens (М12.19), oauth-oidc (М12.20), sessions-state (М15.7 — кут «stateless для горизонталі»).
- **[nb:programming/web-backend/session-management] Сесія автентифікації: зберігання, відкликання, ротація** — NEW. Server-side store / stateless-токени / гібрид (короткий access + refresh у сторі); ротація refresh із детекцією крадіжки; «розлогінити всюди» і чорні списки; сесія пристрою ≠ сесія людини (луна М19). Розведення з sessions-state: там — стан і горизонталь, тут — довіра і життєвий цикл. Спирається: authentication, jwt-tokens. · proj-refresh-rotation.md — ротація refresh-токенів з детекцією повторного вжитку.
- **[nb:programming/web-backend/authorization-models] Моделі авторизації: RBAC, ABAC, ReBAC** — **(v2-запас→курс)** — консенсусна діра всіх трьох критиків. «Що тобі можна» як дані: ролі проти атрибутів проти графа стосунків (Zanzibar-клас); де перевіряти (шлюз / сервіс / RLS у БД); кешування рішень авторизації та інвалідація. Спирається: authentication, api-gateway. · comp-authz-models.md — клас систем авторизації: RBAC-движки, policy-engine (OPA-клас), Zanzibar-клас. · hist-zanzibar.md (опц.) — Google Zanzibar (2019): авторизація як глобальний сервіс.
- **[own:session-storage-choice] Компакт-вибір: де живе сесія** — NEW (§4.4).
- Місце: М12.5 «Довіра на межах» (розширення). Якщо структурна лінза перенесе auth у М9 (пропозиція critic-2/3) — вузол їде разом.

### 1.2. Вебхуки (доставка, ретраї, підписи)
- **(v2 ✓)** webhooks (М12.12) — бік СПОЖИВАЧА чужих вебхуків.
- **[nb:programming/web-backend/webhook-provider] Вебхуки як провайдер: роздати подію тисячі чужих серверів** — NEW. Черга відправки окремо від транзакції (outbox-луна); ретраї з backoff і DLQ на адресата; підпис (HMAC) + ротація секрету + timestamp проти реплею (ref §2.3 replay-protection); порядок не гарантуємо — dedup на споживачі (inbox-луна §3.3); вебхук як продукт: дашборд доставки, ручний redeliver. Спирається: webhooks, retries-backoff, dead-letter-queue, outbox-pattern. · proj-webhook-sender.md — відправник з чергою, підписом, ретраями і redeliver.
- Місце: модуль «Вузли», розділ «Вихідна розмова».

### 1.3. Фонові джоби і розподілений cron
- **[nb:programming/web-backend/background-jobs] Черга задач: робота поза запитом** — NEW. Задача як запис (аргументи, стан, спроби); воркери = competing consumers (v2 ✓ М13.5); ідемпотентність задачі, таймаут+heartbeat виконання, retry/DLQ; пріоритети і окремі пули (перебірки!); статус задачі для UI (міст до 1.4). Спирається: message-queue, competing-consumers, idempotency. · proj-db-job-queue.md — черга задач на SQL-таблиці з SELECT … FOR UPDATE SKIP LOCKED. · comp-job-queue-systems.md — клас систем: БД-черги, Redis-черги, брокерні, керовані.
- **[nb:programming/distributed-systems/distributed-cron] Розподілений cron: «одна нічна джоба на кластер»** — NEW. Рівно-один-запуск через лізу/вибори лідера (v2 ✓ leader-election М11.27 — payoff); misfire-політики (пропустити / наздогнати / злити); catch-up після простою; джитер запусків (thundering-herd луна); unique jobs і дедуп запусків. Спирається: leader-election, distributed-locks, clock-skew-practices (§2.5). · proj-cron-lease.md — планувальник на лізі з фенсинг-токеном.
- **[own]-варіантний блок «де живе черга задач» — §4.1 (повний).**
- Місце: модуль «Вузли», розділ «Фонова робота».

### 1.4. Довгі операції (progress, resumability)
- **[nb:programming/web-backend/long-running-operations] Довга операція: async request-reply** — NEW. 202 Accepted + операція-як-ресурс (status endpoint / callback / push); прогрес чесний і брехливий (двофазні операції); скасування як контракт; resumability — чекпоінти й ідемпотентні кроки; зв'язки: черга задач (1.3), durable workflows (§3.5), async-ui-states клієнта (v2 ✓ М5.21). Спирається: rest-api, background-jobs, idempotency. · proj-202-progress.md — операція транскоду: 202 → статус → прогрес → скасування.
- Місце: модуль «Вузли», розділ «Довгі операції і великі байти».

### 1.5. Завантаження файлів
- **[nb:programming/web-backend/file-uploads] Завантаження файлів як конвеєр** — **(v2-запас→курс, розширений)**. Пряме завантаження в object storage за presigned URL (valet key — payoff інлайну М13.12); multipart/resumable (tus-клас) для мобільних мереж; валідація і антивірус як асинхронна стадія (карантинний бакет); деривативи (тумби, транскод) через чергу задач; квоти і ліміти розміру як контракт; життєвий цикл (TTL тимчасових, orphan cleanup). Спирається: object-storage, background-jobs, claim-check. · proj-presigned-upload.md — presigned-аплоад + верифікація + тумба чергою.
- Місце: модуль «Вузли», поруч із 1.4. DH-точково: кліп із камери їде саме так (луна М16 claim-check).

### 1.6. Сповіщення (fan-out, канали, digest, unsubscribe)
- **[nb:programming/web-backend/notification-fanout] Вузол сповіщень** — NEW. Подія → адресати (fan-out on write/read — луна rozbir-twitter М15.25); канали (push/email/SMS/in-app) з різними SLA і цінниками; преференси та unsubscribe як ДАНІ з пріоритетом над кампанією; digest/батчинг «не будити тричі за хвилину» (коалесенція); дедуп і rate limit на адресата; аудит «чому мені це прийшло». Спирається: message-queue, competing-consumers, push-notifications (v2 ✓ М14.26 — клієнтський бік). · proj-digest-batcher.md — коалесенція сповіщень у digest з вікном тиші.
- **(v2 ✓)** own:dh-notifications-queue (М13.6) і own:dh-scenes-fanout (М19.10) лишаються DH-синтезами поверх атома.
- Місце: модуль «Вузли», розділ «Вихідна розмова».

### 1.7. Пошук як підсистема
- **[nb:programming/web-backend/search-subsystem] Пошук як друга правда** — NEW. Індекс — похідна модель читання (CQRS-луна): пайплайн індексації (CDC/події → індексер → інверсний індекс); лаг і консистентність із джерелом (read-your-writes для автора); reindex без даунтайму (blue-green індексів, aliases); релевантність як продуктова петля; фасети й пагінація глибока. Спирається: inverted-index (v2 ✓ nb М18.8 — структурна нотатка §6: перевісити з «логів» на «пошук», логи реферять), change-data-capture, cqrs. · proj-search-indexer.md — CDC→індекс + reindex перемиканням аліаса.
- **[own:search-engine-choice] Компакт-вибір: пошук у основній БД (tsvector/LIKE+trigram) / виділений рушій / SaaS** — NEW. Критерії: обсяг, свіжість, релевантність, команда. (§4.5)
- Місце: модуль «Вузли», розділ «Пошук».

### 1.8. Конфігурація і секрети (розповсюдження, ротація)
- **(v2 ✓)** config-design (М3.22), secrets-management (М18.20 — ротація вже в scope).
- **[nb:programming/operations/config-distribution] Динамічна конфігурація: розповсюдження і відкат** — NEW. Конфіг у рантаймі: push (watch) проти pull (полінг+TTL); версія конфігу як артефакт — «конфіг = деплой» (hist-knight-capital і hist-cloudflare-regex у М18.13 — саме про це, крос-реф); поетапна розкатка конфігів і канарка конфігу; валідація до застосування, безпечний відкат; дрейф між вузлами. Спирається: config-design, feature-flags, deployment-strategies.
- Місце: М18.4 поруч із secrets-management.

### 1.9. Генерація ID (є) + нумерація/лічильники
- **(v2 ✓)** ID-генерація: proj-shard-id-generator при partitioning-sharding (М11.16); UUID/ULID/snowflake — інлайн там (fold-map §5).
- **[nb:programming/databases/sequences-counters] Людські номери і лічильники** — NEW. Монотонна нумерація (інвойс №, тікет #) — точка контеншну і чому «без дірок» буває регуляторною вимогою (передоплата дірки не пробачає); діапазони-блоки на вузол; лічильники читань/лайків: шардовані лічильники, злиття, приблизні лічильники (HyperLogLog-луна М17.18), CRDT-counter-луна (М14.19). Спирається: transactions-acid, partitioning-sharding. · proj-sharded-counter.md — шардований лічильник зі зливанням і оцінкою похибки читання.
- Місце: модуль «Вузли», розділ «Записи, що мають вагу».

### 1.10. Feature flags як вузол (targeting, лавина прапорців)
- **(v2 ✓ РОЗШИРИТИ)** feature-flags (М3.24): додати секції targeting/сегменти (хеш-стабільність — та сама, що в ab-testing), типи прапорців (release/ops/experiment/permission) з різними життєвими циклами, **flag debt** — лавина прапорців: TTL прапорця, прибирання як дисципліна, тестування комбінацій; прапорці як частина config-distribution (1.8). Окремий атом не потрібен — інлайн (fold-map §5).

### 1.11. Мультиарендність (pool/silo/bridge, noisy neighbor, квоти)
- **(v2 ✓)** повний варіантний блок М11.20–22 (спільна схема / база-на-орендаря / гібрид = pool/silo/bridge).
- **[nb:programming/distributed-systems/tenant-isolation] Ізоляція орендаря за межами даних** — NEW. Blast radius конфігурації і деплою (cell-луна §3.1); квоти як політика (API, storage, compute); cost attribution — «скільки коштує цей орендар»; tiering (free/pro/dedicated) як архітектурний параметр; шумний сусід у кеші/черзі/пулі з'єднань (hist-kinesis М7.13 — крос-реф). Спирається: варіантний блок М11.5, fairness-quotas (§1.12). Місце: М11.5 після вибору.

### 1.12. Rate limiting як вузол (є) + fairness
- **(v2 ✓)** rate-limiting (М15.18).
- **[nb:programming/distributed-systems/fairness-quotas] Чесність розподілу: квоти і fair queuing** — NEW. Rate limit захищає СИСТЕМУ, fairness захищає СУСІДІВ: per-client/per-tenant квоти; weighted fair queuing / DRR на чергах; per-key ліміти проти гарячого ключа; голодування дрібних під великими батчами. Розведення: rate-limiting — стеля, fairness — розподіл під стелею; tenant-isolation (1.11) — політика, тут — механіка. Спирається: rate-limiting, message-queue. Місце: М15.4 одразу після rate-limiting.

### 1.13. Платіжний вузол (reconciliation, ledger-думання)
- **(v2 ✓)** idempotency + proj-idempotency-keys (М9.25), сага-платіжка (М13.20–21).
- **[nb:programming/web-backend/payments-integration] Платіжний провайдер: чужа розподілена система з грошима** — NEW. Життєвий цикл платежу як FSM (authorized/captured/refunded/disputed — недопустимий перехід = інцидент); вебхуки статусів приходять пізно, двічі і не по порядку (payoff 1.2, §2.4, §3.3); redirect/3DS-флоу — користувач зник посеред саги; PCI-межа: токенізація, карти не торкаються твоїх серверів; тестові двійники платіжки. Спирається: webhooks, saga-pattern, state (FSM). 
- **[nb:programming/databases/double-entry-ledger] Гросбух: ledger-думання** — NEW. Подвійний запис: рахунок, проводка, інваріант нульової суми; append-only — баланс НЕ зберігається, а виводиться (event-sourcing-луна, але вужче і старше); ніяких UPDATE amount; ідемпотентний запис проводки; знімки балансу для швидкого читання. Спирається: transactions-acid, event-sourcing (контраст). · hist-double-entry.md — Кейс: подвійний запис — практика венеційських купців XIII–XV ст., систематизована Пачолі (1494); чому фінтех перевинаходить гросбух (атрибуцію веб-звірити: Пачолі — систематизатор, НЕ винахідник). · proj-mini-ledger.md — міні-ledger: рахунки, проводки, інваріант, знімки.
- **[nb:programming/distributed-systems/reconciliation] Звірка: дві системи правди сходяться** — NEW. Періодичне порівняння свого стану із зовнішнім (виписка провайдера, інвентар складу, ліцензії); вікна звірки і курсор; розбіжність = задача з власником, компенсаційна проводка ≠ тихе виправлення; звірка як штатний механізм, не аврал (луна anti-entropy §3.2 — та сама ідея всередині системи). Спирається: double-entry-ledger, batch-backfill (v2 ✓ М17.5).
- **[own]-варіантний блок «де живе правда про гроші» — §4.2 (повний).**
- Місце: модуль «Вузли», розділ «Гроші» (фінал модуля — найважчий вузол).

### 1.14. Аудит-лог
- **[nb:programming/web-backend/audit-log] Аудит-лог: журнал з юридичною вагою** — NEW. Відмінності від app-логів: не дропати ніколи (v2 ✓ М18.7 каже «audit — ніколи» — тут пояснення), retention роками, доступ вужчий за розробницький; що писати: хто/що/коли/звідки/чим-було→стало; незмінність: append-only + опц. хеш-ланцюг; аудит як події чи таблиця; PII в аудиті (конфлікт із right-to-delete М17.27 — розв'язки: псевдонімізація, crypto-shredding-луна). Спирається: structured-logging, event-sourcing (контраст: аудит — вимога, ES — архітектура). DH-точково: «хто відкривав замок» (М19.9 аудит — крос-реф).
- Місце: модуль «Вузли», розділ «Записи, що мають вагу».

### 1.15. Soft delete / tombstones
- **[nb:programming/databases/soft-delete-tombstones] М'яке видалення і надгробки** — NEW. deleted_at і його ціна: кожен запит фільтрує, унікальні індекси з умовою, каскади «напіввидаленого»; альтернативи: archive-таблиці, статусна модель життєвого циклу; tombstones у реплікації/синку (v2 ✓ sync-protocols М14.16, CRDT М14.19, компакція лога М13.3 — тут ЗАГАЛЬНИЙ принцип: видалення — це запис); «видалити по-справжньому» — міст до right-to-delete (М17.27). Спирається: database-migrations, sync-protocols.
- Місце: модуль «Вузли», розділ «Записи, що мають вагу».

---

## 2. КАТАЛОГ ОБХОДІВ / MITIGATIONS

Що вже є у v2 — фіксую ✓ і не дублюю; нове — атоми/інлайни.

| Прийом | Статус | Рішення v3 |
|---|---|---|
| hedged requests | **v2 ✓** М15.21 | лишити |
| request coalescing / single-flight | **v2 ✓** інлайн cache-invalidation М15.14 + rozbir-discord М11.19 | лишити |
| поетапна деградація, brownout | **v2 ✓** load-shedding М15.19 (+ ref graceful-degradation embedded, done) | лишити |
| poison message / карантин | **v2 ✓** dead-letter-queue М13.14 | лишити |
| reprocessing / backfill | **v2 ✓** batch-backfill М17.5 + event-log перечитування М13.3 | лишити |
| parallel run / shadow traffic | **v2 ✓** секції dark-launch М18.14 | лишити |
| branch-by-abstraction | **v2 ✓** М21.13 | лишити |
| thundering herd | **v2 ✓** М15.6 | лишити |
| expand–contract | **v2 ✓** live-migration М21.12 | розширити (2.7) |
| lease/фенсинг | **v2 ✓ базово** distributed-locks М11.26 | розширити (2.8) |
| split-brain практики | **v2 ✓ базово** М11.10 | розширити (2.8) |

Нові атоми:

### 2.1. [nb:programming/distributed-systems/adaptive-concurrency] Адаптивні ліміти конкурентності — NEW
Статичний ліміт бреше: справжню місткість шукаємо динамічно — AIMD/gradient за latency (TCP-ідея на рівні застосунку); ліміт у клієнті проти ліміту в сервері; взаємодія з ретраями (посилюють) і чергами (ховають). Спирається: littles-law (v2 ✓ М15.4), rate-limiting, timeouts-deadlines. Місце: М15.4 після rate-limiting. · hist-netflix-concurrency.md — Netflix concurrency-limits (2018): від Hystrix-порогів до градієнтних лімітів. · proj-aimd-limiter.md — AIMD-ліміт робочим кодом під синтетичним навантаженням.

### 2.2. [nb:programming/distributed-systems/admission-control] Admission control: хто заходить під час перевантаження — NEW
Відмовити НА ВХОДІ дешевше, ніж усередині: критичність запиту (health-checks і платежі перед аналітикою), деградований впуск (читання пускаємо, запис — ні), квоти клієнтів у перевантаженні, зв'язок із waiting room (v2 ✓ own:sale-start-waiting-room М15.22 — зала очікування = admission на краю). Розведення: load-shedding — скинути вже прийняте, admission — не прийняти. Спирається: load-shedding, rate-limiting, fairness-quotas. Місце: М15.4 між rate-limiting і load-shedding.

### 2.3. [nb:programming/security/replay-protection] Захист від повтору (replay) — NEW
Ідемпотентність робить повтор БЕЗПЕЧНИМ, replay-захист робить його НЕМОЖЛИВИМ для чужого: nonce+вікно, timestamp у підписі (вебхуки — payoff 1.2), монотонні лічильники команд (замок DH! крос-реф М19.9), одноразові токени (password reset); чому TLS сам по собі не рятує від повтору на рівні застосунку. Спирається: idempotency, public-key-crypto [ref:communications/cryptographic-comm/public-key-crypto — pending]. Місце: М9.6 «Мережа бреше» після idempotency. Це перший внесок у «безпеку як архітектуру» (хендоф security-лінзі — §8).

### 2.4. [nb:programming/distributed-systems/out-of-order-tolerance] Толерантність до безладу — NEW
Порядок дорогий — частіше дешевше ТЕРПІТИ безлад: версія-переможець (LWW з чесними межами), монотонні перевірки (не застосовуй старіше за вже застосоване — луна device-shadow версій М19.5), буфер перевпорядкування з вікном (resequencer з М13.8 — формалізація), комутативні операції (CRDT-луна), watermark і спізнілі події (stream-processing М17.4 — крос-реф). Спирається: delivery-guarantees, vector-clocks, splitter-aggregator. Місце: М13.2 (EIP-розділ, після splitter-aggregator). · proj-out-of-order.md — споживач із вікном перевпорядкування + версійним відкиданням.

### 2.5. [nb:programming/distributed-systems/clock-skew-practices] Обходи розбіжності годинників — NEW
«Не порівнюй чужі таймстемпи»: практики — запас (leeway) у TTL/exp токенів і сертифікатів; monotonic clock для таймаутів, wall clock лише для людей; hybrid logical clocks (HLC) — фізичний час + лампортова гарантія; два часи події (device time / server time — v2 ✓ event-schema-design М17.2 — крос-реф); джитер розкладів. Спирається: clock-offset-drift [ref — pending], ntp-sync [ref — pending], lamport-clocks (v2 ✓). Місце: М11.1 після vector-clocks.

### 2.6. [nb:programming/distributed-systems/cache-tactics] Дрібні тактики кешу, що рятують проди — NEW
Negative caching (кешуй «нема» — інакше промахи довбуть базу); TTL jitter (розсинхронізувати протухання — лавина не збирається); refresh-ahead / stale-while-revalidate на сервері (клієнтський SWR — v2 ✓ М14.6); write-behind coalescing (злити шквал записів одного ключа — луна dh-command-queue злиття М14.17). Спирається: caching-strategies, cache-invalidation. Місце: М15.3 після cache-invalidation.

### 2.7. Розширення live-migration (v2 ✓ М21.12) — інлайн + вставка
Додати секції: онлайн-backfill із тротлінгом (не з'їж прод); подвійне ЧИТАННЯ з порівнянням (shadow reads/verify) — симетрія до dual-write; online DDL (ghost-таблиці, gh-ost/pt-osc-клас). · proj-online-backfill.md — dual-write + тротльований backfill + dual-read verify на живій табличці.

### 2.8. Розширення distributed-locks (М11.26) і split-brain (М11.10) — інлайни
- distributed-locks: цикл поновлення лізи; GC-пауза/зависання як «зомбі з валідним локом» — чому фенсинг-токен обов'язковий. · hist-redlock-debate.md — Кейс: дебати Kleppmann ↔ antirez про Redlock (2016) — коли розподілений лок взагалі коректний.
- split-brain: практики проти зомбі — epoch/generation numbers у кожному записі, STONITH-клас («застрель старого лідера»), кворумний свідок (witness).

---

## 3. РОЗШИРЕННЯ КАТАЛОГІВ

### 3.1. Cloud-патерни, яких нема у v2
| Патерн | Рішення | Де |
|---|---|---|
| BFF | **v2 ✓ атом** bff-pattern М14.7 | — |
| gateway aggregation | **v2 ✓ інлайн** api-gateway М12.7 | — |
| **gateway offloading** | NEW **інлайн** в api-gateway: TLS-термінація, компресія, авторизація на шлюзі — що знімаємо з сервісів і чим платимо | М12.7 |
| valet key | **v2 ✓ інлайн** object-storage М13.12; file-uploads (1.5) робить робочим | — |
| gatekeeper | **v2 ✓ інлайн** authentication М12.18 | — |
| federated identity | **v2 ✓ інлайн** oauth-oidc М12.20 | — |
| competing consumers | **v2 ✓ атом** М13.5 | — |
| priority queue | **v2 ✓ інлайн** message-queue М13.1 (+ref priority-queue, pending) | — |
| **sequential convoy** | NEW **інлайн** у competing-consumers: порядок у межах ключа при паралельності між ключами; партиції event-log і порядок «у межах пристрою» (М14.17) — той самий принцип | М13.5 |
| **scheduler-agent-supervisor** | NEW **інлайн** у durable-workflows (3.5): оркестратор+агенти+ремедіація | — |
| **deployment stamps / cells** | **[nb:programming/distributed-systems/cell-based-architecture]** — **(v2-запас→курс)**: комірка = повний стек на підмножину клієнтів; blast radius, cell-router, гомогенні деплої-штампи; зв'язок із мультиарендністю (1.11) і canary. Спирається: bulkhead-isolation, partitioning-sharding, load-balancing. Місце: М15.2 після load-balancing. · comp-cells-stamps.md — AWS cells / Azure stamps / Slack — осі порівняння | М15.2 |
| geode | **v2 ✓ інлайн** anycast М15.10 | — |

### 3.2. EIP ширше
| Патерн | Рішення |
|---|---|
| routing slip | NEW **інлайн** у message-router (М13.7): маршрут їде З повідомленням; чек-лист стадій обробки зображення/KYC |
| wire tap | NEW **інлайн** у message-router: діагностичний відвід копії потоку — луна shadow-traffic (М18.14) і трейсингу (М18.3) |
| process manager | **v2 ✓ інлайн** saga М13.15 |
| message translator + canonical data model | **v2 ✓ атом** М13.11 |
| idempotent receiver | **v2 ✓ інлайн** idempotency М9.25; inbox-pattern (3.3) дає йому робочу форму |
| resequencer | **v2 ✓ інлайн** splitter-aggregator М13.8; out-of-order-tolerance (2.4) — узагальнення |

### 3.3. Data/consistency глибше
- **CRDT у курсі — v2 ✓** (М14.19, з варіантним блоком конфліктів). Лишити.
- **version vectors** — NEW **інлайн** у vector-clocks (М11.6): версійний вектор трекає ОБ'ЄКТ, векторний годинник — ПРОЦЕСИ; dotted version vectors — рядок-згадка.
- **[nb:programming/distributed-systems/anti-entropy-repair] Анти-ентропія: read repair і hinted handoff** — NEW. Репліки розходяться — три механізми сходження: read repair (лагодь на читанні), hinted handoff (потримай для мертвого), фонова анти-ентропія Merkle-звіркою; звірка як штатний цикл (рима reconciliation 1.13 — там межа систем, тут всередині). Спирається: leaderless-replication (v2 ✓), merkle-tree (нижче). Місце: М11.2 після leaderless-replication. · proj-merkle-sync.md — звірка двох реплік Merkle-деревом: знаходимо розбіжний діапазон за O(log n).
- **[nb:algorithms/data-structures/merkle-tree] Дерево Меркла** — **(v2-запас→курс)**: хеш-дерево, доказ включення, порівняння за корінь; де живе: git (rozbir-git М8.10 — крос-реф), реплікація, блокчейни-згадка. Місце: перед anti-entropy-repair.
- **[nb:programming/distributed-systems/schema-registry] Реєстр схем і еволюція** — NEW. Схема повідомлення = контракт N продюсерів × M споживачів; сумісність BACKWARD/FORWARD/FULL — хто оновлюється перший; реєстр як gate у CI; зв'язки: serialization-formats (М9.16 — еволюція полів), event-schema-design (М17.2 — продуктовий кут), contract-testing (М9.14 — синхронний двійник). Спирається: serialization-formats, event-log. Місце: М13.1 після event-log. · proj-schema-compat.md — перевірка сумісності схеми в CI: ламаємо споживача навмисно.
- **[nb:programming/databases/materialized-views] Матеріалізовані подання** — **(v2-запас/інлайн→курс)**: обчислене заздалегідь читання; refresh-стратегії (повний / інкрементальний / на запис); зв'язок із CQRS-проєкціями (М13.19 — інлайн лишається, атом дає БД-механіку) і cache-tactics (2.6 — кеш без інвалідаційного болю, бо є джерело перерахунку). Місце: М13.4 поруч із cqrs (альтернатива: М4 після індексів — рішення структурній лінзі).
- **[nb:programming/distributed-systems/inbox-pattern] Вхідна скринька: dedup на споживачі** — NEW. Таблиця оброблених message_id + обробка й відмітка в ОДНІЙ транзакції = exactly-once ЕФЕКТ поверх at-least-once; retention скриньки; пара до outbox (М13.16): outbox — не загубити на виході, inbox — не подвоїти на вході. Спирається: outbox-pattern, idempotency, delivery-guarantees. Місце: М13.4 одразу після outbox. · proj-inbox-dedup.md — споживач із inbox-таблицею: дубль і збій посередині.
- **saga: оркестрація vs хореографія — v2 ✓** (М13.15 + вибір М13.20). Розширити вибір 4-м варіантом (3.5).

### 3.4. Мультирегіон — новий кластер (консенсусна діра критиків)
- **[nb:programming/distributed-systems/multi-leader-replication] Мультилідерна реплікація** — **(v2-запас→курс)**: писати можна в кожному регіоні — конфлікти стають нормою; топології (кільце/зірка/all-to-all); git і календарі як побутові мультилідери. Спирається: replication-leader-follower, sync-conflicts (М14.18 — та сама задача в кишені!). Місце: М11.2 після replication-lag.
- **[nb:programming/distributed-systems/multi-region-topologies] Топології мультирегіону** — NEW. Спектр: один регіон + DR (pilot light / warm standby) → active-passive → active-active; RTO/RPO як ПРОЄКТНІ числа топології (disaster-recovery М21.4 — крос-реф); read-local-write-global; вартість крос-регіонального трафіку і лаг реплікації як фізика. Спирається: replication-leader-follower, multi-leader-replication, cap-theorem. · comp-multi-region-dbs.md — клас глобальних БД: Spanner-клас (синхронний кворум) / Dynamo global tables-клас (async+конфлікти) / Cosmos-клас — осі. · hist-netflix-active-active.md — Netflix (2013–2016): active-active і regional evacuation, Chaos Kong (числа веб-звірити).
- **[nb:programming/distributed-systems/data-residency] Резидентність даних** — NEW. «Дані громадян ЄС живуть у ЄС» — регуляторика як шардинг-ключ: region pinning орендаря (луна tenancy М11.5), розщеплення глобального каталогу і регіональних даних, транскордонні потоки (аналітика! бекапи!) як юридична поверхня. Спирається: partitioning-sharding, тенант-блок М11.5, pii-data-classification (М17.24 — крос-реф).
- **[nb:programming/distributed-systems/global-traffic-steering] Кермування глобальним трафіком** — NEW. GeoDNS / anycast (М15.10 — крос-реф чи переїзд, рішення структурній лінзі) / health-based failover; липкість користувача до регіону (сесія! кеші!); евакуація регіону як ШТАТНА операція (кнопка, а не подвиг); split-brain між регіонами. Спирається: anycast, load-balancing, health-checks, multi-region-topologies.
- **[own]-варіантний блок «мультирегіон DH» — §4.3 (повний).**
- Місце кластера: М11, новий розділ 7 «Планета: мультирегіон» (мета: свідомо обрати топологію регіонів) — альтернативи: М15 (після балансування) або М21 (біля DR); рекомендую М11 — це продовження реплікації/консистентності, а «до планети» стоїть у назві курсу.

### 3.5. Serverless і durable workflows — ЯК РІШЕННЯ
- **[nb:programming/operations/serverless-faas] Serverless/FaaS: хто володіє життєвим циклом процесу** — NEW. Функція = обробник без процесу: cold start і його обходи (прогрів, provisioned), стан ЗАВЖДИ зовні (звідси — прив'язка до managed-сервісів), ліміти часу/пам'яті як АРХІТЕКТУРНІ межі, ціна за виклик проти ціни за простій; де FaaS чесно виграє (спорадичні навантаження, glue, вебхук-приймачі — луна 1.2). Спирається: containers, autoscaling (+comp-edge-serverless v2 ✓ М15.20 — крос-реф). Місце: М18.4 після container-orchestration.
- **[own:compute-platform-choice] Компакт-вибір: контейнери/оркестратор — serverless — edge** — NEW (§4.6). Критерії: профіль трафіку, стан, латентність, lock-in, команда. (Критик-3 просив варіантний блок compute — закриваємо компактом.)
- **[nb:programming/distributed-systems/durable-workflows] Durable workflows: оркестратор довгих процесів** — NEW. Клас Temporal/Cadence/Step Functions: воркфлоу-код, що переживає рестарти — історія подій + реплей (event-sourcing у рантаймі!); вимога детермінізму воркфлоу-коду; таймери на тижні, сигнали, людський крок у процесі; версіонування воркфлоу насеред польоту; scheduler-agent-supervisor — інлайн. Межі: коли досить саги руками / черги задач (1.3). Спирається: saga-pattern, event-sourcing, message-queue, background-jobs. Місце: М13.4 після saga-pattern, ПЕРЕД saga-style-choice. · comp-workflow-engines.md — клас рушіїв: Temporal/Cadence, Step Functions-клас, Airflow-межа (batch-DAG ≠ workflow). · hist-uber-cadence.md — Убер: чому народився Cadence (2016) → Temporal; проблема «сага руками в 40 сервісах».
- **(v2 ✓ РОЗШИРИТИ)** own:saga-style-choice (М13.20): додати варіант Г «готовий workflow-рушій» — критерії: скільки довгих процесів, людські кроки, аудит історії, ціна залежності від рушія.

---

## 4. ВАРІАНТНІ БЛОКИ (для найважчих вузлів, стиль v2)

### 4.1. Повний блок: де живе черга задач (модуль «Вузли», розділ «Рішення: черга задач»)
1. [own:jobs-db-variant] Варіант А: черга в основній БД (SKIP LOCKED) — транзакційний enqueue задарма (перегук з outbox), нуль нової інфри, видно SQL-ем; боляче: полінг, база стає брокером, autovacuum/bloat під високим чурном.
2. [own:jobs-broker-variant] Варіант Б: виділений брокер/чергова система — пропускна здатність, ack/DLQ з коробки, ізоляція від OLTP; боляче: друга система правди (потрібен outbox!), дві семантики ретраїв, ops брокера.
3. [own:jobs-managed-variant] Варіант В: керована черга + serverless-воркери — нуль ops, автоскейл до нуля і з нуля; боляче: ліміти платформи (час/пам'ять), cold start на піку, vendor lock-in, локальна розробка.
4. [own:jobs-choice] Вибір: обсяг задач/с, транзакційність із доменними даними, тривалість задач, команда й ops-бюджет; чесний фінал — А до сотень задач/с майже завжди правильний старт (boring-луна), Б коли черга стає продуктом, В для спорадичного.

### 4.2. Повний блок: де живе правда про гроші (модуль «Вузли», розділ «Рішення: правда про гроші»)
1. [own:money-status-variant] Варіант А: статуси в доменних таблицях + періодична звірка з провайдером — швидко, зрозуміло CRUD-команді; боляче: історія губиться (UPDATE стирає), розслідування «звідки це число» без сліду, кожен новий потік грошей = нові статусні поля.
2. [own:money-ledger-variant] Варіант Б: власний гросбух (подвійний запис) + провайдер як канал — повний слід, баланс завжди сходиться, аудит задарма; боляче: планка входу (ledger-думання), кожна фіча проходить крізь проводки, знімки для швидкого читання.
3. [own:money-provider-variant] Варіант В: провайдер як джерело правди (thin wrapper) — мінімум коду, PCI-межа далеко; боляче: рахунок = API-виклики, ліміти і лаг провайдера, мультипровайдерність неможлива, «експорт своїх грошей» — біль.
4. [own:money-choice] Вибір: обсяг і різноманіття потоків (разові/підписки/виплати/повернення), регуляторика і аудит, мультипровайдерність, команда; рамка: В → А → Б — це ЕВОЛЮЦІЯ (переїзд А→Б показати expand-contract-ом — луна М21.12).

### 4.3. Повний блок: мультирегіон (М11, розділ «Рішення: планета»)
1. [own:region-dr-variant] Варіант А: один регіон + DR (pilot light) — простота, консистентність тривіальна; боляче: RTO годинами, DR ніколи не тестять (gitlab-луна М21.4), латентність далеких користувачів.
2. [own:region-ap-variant] Варіант Б: active-passive з гарячою реплікою — RTO хвилинами, читання можна локалізувати; боляче: passive коштує як active а не працює, failover = split-brain-ризик (фенсинг!), реплікаційний лаг = втрачені секунди (RPO>0).
3. [own:region-aa-variant] Варіант В: active-active — латентність локальна всім, евакуація регіону штатна; боляче: конфлікти записів як НОРМА (multi-leader/CRDT/розведення ключів по домівках), подвійна складність кожної фічі, крос-регіональні інваріанти (унікальність!) — найдорожча властивість.
4. [own:region-choice] Вибір: RTO/RPO як гроші, географія користувачів, residency-вимоги (3.4), які інваріанти глобальні; чесний гібрид — актив-актив для stateless-краю і читань + один дім запису на домен даних (home region per tenant — тенансі-луна).

### 4.4. Компакт-вибір: де живе сесія (М12.5)
[own:session-storage-choice] — А: server-side store (простий logout, стор на шляху кожного запиту) / Б: stateless JWT (масштаб задарма, біль відкликання, розмір токена) / В: гібрид access+refresh (галузевий дефолт). Критерії: вимоги відкликання, кількість сервісів-споживачів, латентність стора. Після session-management і jwt-tokens.

### 4.5. Компакт-вибір: пошук (модуль «Вузли»)
[own:search-engine-choice] — А: пошук в основній БД (tsvector/trigram — нуль нової інфри, релевантність базова) / Б: виділений рушій (інверсний індекс, фасети; друга система правди + пайплайн індексації) / В: SaaS-пошук (швидкий старт; ціна на обсязі, дані назовні). Критерії: обсяг, свіжість, релевантність як продукт, приватність.

### 4.6. Компакт-вибір: compute-платформа (М18.4)
[own:compute-platform-choice] — контейнери+оркестратор / serverless / edge-ізоляти (див. 3.5).

---

## 5. FOLD-МАПА ІНЛАЙНІВ ЦІЄЇ ЛІНЗИ (щоб «усі» ≠ «кожному по кроку»)

| Прийом/патерн | Власник (де інлайн) |
|---|---|
| gateway offloading | api-gateway (М12.7) |
| sequential convoy | competing-consumers (М13.5) |
| routing slip, wire tap | message-router (М13.7) |
| scheduler-agent-supervisor | durable-workflows (3.5) |
| version vectors (vs vector clocks) | vector-clocks (М11.6) |
| lease renewal, зомбі-лок після GC-паузи | distributed-locks (М11.26) + hist-redlock-debate |
| epoch/generation, STONITH, witness | split-brain (М11.10) |
| онлайн-backfill, dual-read verify, online DDL | live-migration (М21.12) + proj-online-backfill |
| targeting, типи прапорців, flag debt | feature-flags (М3.24) |
| ротація секретів | secrets-management (М18.20 — вже в scope) |
| ID-генерація (UUID/ULID/snowflake) | partitioning-sharding (М11.16) + proj-shard-id-generator (v2 ✓) |
| idempotency-keys (запас web-backend) | idempotency (М9.25) + proj (v2 ✓) — у курс окремо НЕ тягнути |
| brownout | load-shedding (М15.19, v2 ✓) |
| negative-cache/jitter/refresh-ahead/write-behind coalescing | ВЛАСНИЙ атом cache-tactics (2.6) — НЕ розпорошувати |
| RTO/RPO-словник | disaster-recovery (М21.4) ↔ multi-region-topologies (3.4) — взаємні картки |

---

## 6. РОЗМІЩЕННЯ В ДУЗІ v2 + структурна пропозиція

**Новий модуль «Вузли платформи» [platform-nodes], ~23 кроки** — рекомендоване місце: одразу ПІСЛЯ М13 (події) — все потрібне вже введено (черги, outbox, DLQ, object-storage, ідемпотентність, auth). Розділи (розділ = одна мета):
1. **Метод вузла** (впізнати→зібрати→купити): own:node-catalog-method — 1
2. **Фонова робота** (робота поза запитом надійна): background-jobs, distributed-cron — 2
3. **Рішення: черга задач** (§4.1) — 4
4. **Довгі операції і великі байти** (операція довша за запит, файл більший за пам'ять): long-running-operations, file-uploads — 2
5. **Вихідна розмова** (система сама говорить зі світом): webhook-provider, notification-fanout — 2
6. **Пошук** (індекс — друга правда, що наздоганяє першу): search-subsystem, own:search-engine-choice — 2
7. **Записи, що мають вагу** (номери, аудит, видалення): sequences-counters, audit-log, soft-delete-tombstones — 3
8. **Гроші** (грошовий вузол переживає подвійність світів): payments-integration, double-entry-ledger, reconciliation — 3
9. **Рішення: правда про гроші** (§4.2) — 4

Точкові вставлення в наявні модулі:
- **М9.6:** replay-protection (після idempotency).
- **М11.1:** clock-skew-practices; **М11.2:** multi-leader-replication, merkle-tree, anti-entropy-repair; **М11.5:** tenant-isolation (після тенансі-вибору); **М11 новий розділ 7 «Планета»:** multi-region-topologies, data-residency, global-traffic-steering + блок §4.3 (7 кроків).
- **М12.5:** session-management, authorization-models, own:session-storage-choice (їдуть за auth, якщо той переїде в М9).
- **М13.1:** schema-registry (після event-log); **М13.2:** out-of-order-tolerance (після splitter-aggregator); **М13.4:** inbox-pattern (після outbox), materialized-views (біля cqrs), durable-workflows (перед saga-style-choice; вибір +варіант Г).
- **М15.2:** cell-based-architecture; **М15.3:** cache-tactics; **М15.4:** admission-control, adaptive-concurrency, fairness-quotas (кластер «казати ні» разом із rate-limiting/load-shedding).
- **М18.4:** config-distribution (біля secrets), serverless-faas, own:compute-platform-choice.
- **М21.3:** розширення live-migration (2.7).

Структурні нотатки суміжним лінзам: (а) inverted-index (v2 М18.8) природніше вводити при search-subsystem, логи його реферять; (б) anycast (М15.10) може переїхати в розділ «Планета» М11.7; (в) якщо auth їде в М9 (критики 2/3) — вузол 1.1 їде слідом; (г) модуль «Вузли» частково компенсує вирізані доменні кроки М16/М17 — переносить курс із «доменних підручників» на «репертуар».

---

## 7. Колізії, омоніми, межі (звірено з індексом 2446 рядків і слаг-списками v2)

1. **Колізій з індексом — нуль:** усі нові слаги в галузях, яких в індексі ще нема (web-backend, distributed-systems, operations) або перевірено вручну (databases: там лише fat-filesystem, endianness; security: secure-boot/aes-xts/buffer-overflow-security; data-structures: merkle-tree відсутній ✓).
2. **Колізій зі слагами v2 — нуль** (звірено проти §«Нові галузі book» плану). Промоти (authorization-models, file-uploads, materialized-views, multi-leader-replication, cell-based-architecture, merkle-tree) беруть ІСНУЮЧІ назви запасу — нових сутностей не плодимо.
3. **Розведення пар (рядок-розведення в обох статтях):** session-management ↔ sessions-state (довіра ↔ горизонталь); fairness-quotas ↔ rate-limiting (розподіл під стелею ↔ стеля); admission-control ↔ load-shedding (не прийняти ↔ скинути прийняте); reconciliation ↔ anti-entropy-repair (межа систем ↔ всередині системи); audit-log ↔ event-sourcing (вимога ↔ архітектура); inbox ↔ outbox (вхід ↔ вихід); durable-workflows ↔ saga (рушій ↔ патерн); webhook-provider ↔ webhooks (роздаємо ↔ споживаємо).
4. **Scope-правка галузі:** `programming/web-backend` розширити: «…вебхуки. **Типові вузли бекенд-платформи: сесії, фонові задачі, довгі операції, файли, сповіщення, пошук, платежі, аудит.**» Нова галузь не потрібна.
5. **Історія (AUTHORING §7):** hist-double-entry — Пачолі СИСТЕМАТИЗУВАВ (1494), практика старша (венеційські/флорентійські купці) — не робити одноосібного міфу; hist-netflix-active-active, hist-uber-cadence, hist-netflix-concurrency, hist-redlock-debate, hist-zanzibar — числа і атрибуції веб-звіряти письменнику.

---

## 8. Хендоф іншим лінзам
- **Security-лінза:** replay-protection (2.3) — мій внесок у її зону; audit-log, session-management, authorization-models — її сусіди (trust boundaries, threat modeling — НЕ мої).
- **Структурна лінза:** фінальне місце модуля «Вузли»; мультирегіон М11 vs М15/М21; частка «Вузлів» у скороченні М16/М17; чи давати блоку §4.1 повний формат (можна стиснути до компакту, −3 кроки).
- **Кейсова лінза:** мої hist (~7) — вище; кандидати додатково: Stripe API changelog (schema-registry-сусід), GitHub webhook redeliver (1.2).
- **Клієнтська/доменні лінзи:** notification-fanout ↔ push-notifications (М14.26), long-running-operations ↔ async-ui-states (М5.21) — атоми мої, клієнтські кути їхні.

## 9. Черга письма (усі мої nb — самодостатні, ідеальні для write-batch)
Б-A «вузли-ядро» (10): background-jobs, distributed-cron, long-running-operations, file-uploads, webhook-provider, notification-fanout, search-subsystem, session-management, authorization-models, config-distribution.
Б-B «записи і гроші» (6): sequences-counters, audit-log, soft-delete-tombstones, payments-integration, double-entry-ledger, reconciliation.
Б-C «mitigations» (6): adaptive-concurrency, admission-control, replay-protection, out-of-order-tolerance, clock-skew-practices, cache-tactics.
Б-D «дані/інтеграція» (7): inbox-pattern, schema-registry, materialized-views, merkle-tree, anti-entropy-repair, multi-leader-replication, durable-workflows.
Б-E «планета/compute» (7): multi-region-topologies, data-residency, global-traffic-steering, cell-based-architecture, serverless-faas, tenant-isolation, fairness-quotas.
own-кроки (16) — після book-батчів своїх модулів, строго по дузі.
