# Шлюз і локальна автономія (детально)

<preknowlist>
- [Ролі: вузол, шлюз, брокер, служба, сховище, клієнт](root:embedded/roli-vuzol-shliuz-broker-sluzhba-skhovyshche-kliient) — призначення та місце шлюзу в загальній ієрархії IoT-системи.
- [Вузол розумного дому: давач + MQTT + автономна логіка](root:embedded/smart-home-node) — базова автономія кінцевого пристрою та архітектура розділених петель.
- [Шлюз: міст між протоколами й межа автономії](root:embedded/shliuz-mist-mizh-protokolamy-i-mezha-avtonomii) — поняття мостового з'єднання та фізична ізоляція шин.
- [MQTT](root:com-protocol/mqtt) — механіка публікації/підписки (Pub/Sub), рівні якості доставки (QoS 0/1/2) та прапорець утримання (retain).
- [Modbus RTU](root:com-protocol/modbus) — кадрова структура, інтервали t1.5/t3.5, коди функцій та регістрова модель польової шини.
- [LoRaWAN](root:com-transport/lorawan) — радіоінтерфейс великого радіуса дії, структура кадрів, FPort і часовий бюджет ефіру.
</preknowlist>

Коли на теплопункті багатоповерхового будинку або в автономному агрокомплексі одночасно працюють двадцять ультразвукових лічильників тепла на дротовій шині RS-485 Modbus, десяток бездротових давачів витоку газу на радіомодулях LoRaWAN і кілька сервоприводів змішувальних контурів, система щосекунди генерує щільний потік різнорідних сигналів. Якщо екскаватор перебиває магістральне оптоволокно провайдера або знеструмлюється найближча базова станція стільникового зв'язку LTE, цей локальний світ не має права зупинитися. Тиск у паровому котлі не повинен піднятися до критичної межі через те, що хмарний сервер перестав надсилати команди регулювання; циркуляційні насоси не мають згоріти на сухому ході; а терабайти показників комерційного обліку енергії за три доби блекауту не сміють безслідно зникнути.

Кінцевий мікроконтролер окремого сенсорного вузла фізично не здатен взяти на себе координацію цілого об'єкта: йому бракує оперативної пам'яті для тривалої буферизації мегабайтів вимірювань, він не має стійкої до раптових вимкнень файлової системи та не вміє одночасно обслуговувати важкий криптографічний стек mTLS поруч із низькорівневим тактуванням кількох польових трансиверів. Цю межу тримає **локальний IoT-шлюз** (*Edge Gateway*). Він бере на себе дві взаємопов'язані ролі: виступає **мостом трансляції протоколів та агрегації даних**, який перетворює сирі бінарні кадри польових шин на стандартизовані повідомлення IP/MQTT, і функціонує як **автономний центр керування**, що за повної відсутності зв'язку з хмарою самостійно ухвалює захисні рішення та надійно зберігає хронологію подій у локальному енергонезалежному сховищі.

![Архітектура автономного індустріального IoT-шлюзу](/root/course/embedded/shliuz-i-lokalna-avtonomiia/img/gateway-architecture.svg)
*Архітектура автономного IoT-шлюзу: розділення низхідного польового периметра (Southbound) від висхідного (Northbound), конвеєр первинної фільтрації, локальний аварійний рушій правил та відмовостійка черга Store-and-Forward на базі SQLite WAL.*

---

## Межа двох світів: чому польовий сегмент вимагає шлюзу

Неможливість підключити польові контролери безпосередньо до хмарного брокера або бази даних часових рядів зумовлена трьома фундаментальними бар'єрами: фізично-електричним, обчислювально-криптографічним та парадигмальним.

```
+-------------------------------------------------------------------------------+
|                       ХМАРНИЙ БРОКЕР ТА SCADA (WAN)                           |
|       Стек: TCP/IP · TLS 1.3 (mTLS) · MQTT v5.0 / HTTPS · JSON/Protobuf       |
+-------------------------------------------------------------------------------+
                                      ▲
                                      │ Висхідний канал (Ethernet / 4G / LTE)
                                      ▼
+-------------------------------------------------------------------------------+
|                           ЛОКАЛЬНИЙ ШЛЮЗ (GATEWAY)                            |
|  · Гальванічна розв'язка 2.5 кВ            · SQLite WAL (Store-and-Forward)   |
|  · Апаратний RTC (NTP / GPS Timestamping)  · Fast-Path Rule Engine (< 1 мс)   |
|  · Планувальник опитування Modbus          · Концентратор LoRaWAN (SX1302)    |
+-------------------------------------------------------------------------------+
         ▲                            ▲                            ▲
         │ RS-485 (Диференційна пара) │ SPI / Радіоефір 868 МГц    │ UART / BLE
         ▼                            ▼                            ▼
+--------------------+      +--------------------+      +--------------------+
| Лічильник тепла    |      | Сенсор газу LoRa   |      | Кліматичний датчик |
| Modbus RTU (Slave) |      | Батарейне живлення |      | BLE GATT Сервер    |
+--------------------+      +--------------------+      +--------------------+
```

### 1. Фізичний та електричний бар'єр
Польові пристрої використовують промислові та бездротові інтерфейси, позбавлені адресації IP та концепції мережевих маршрутизаторів:
* **RS-485 (Modbus RTU)** передає сигнал диференційною парою напівдуплексних ліній `A` та `B`. Лінії зв'язку довжиною до 1200 метрів проходять поруч із потужними силовими кабелями двигунів і частотних перетворювачів. Різниця потенціалів між «землями» в різних точках споруди досягає десятків вольтів. Пряме з'єднання мікроконтролера з такою лінією без апаратної гальванічної розв'язки на 2.5–5 кВ (наприклад, оптичних або магнітних ізоляторів `ADuM1411` чи `ISO1410`) та каскадів супресорів (TVS-діодів) неминуче призведе до вигоряння кристала від першої синфазної завади або утворення земляної петлі (*Ground Loop*).
* **LoRaWAN** оперує радіомодуляцією з розширенням спектра (Chirp Spread Spectrum) на неліцензованих частотах 868/915 МГц. Батарейний сенсор передає короткий пакет тривалістю кілька десятків мілісекунд раз на 10 хвилин, щоб зберегти заряд джерела живлення на 5–10 років. Він не підтримує протокол TCP з його трикроковим рукостисканням (SYN-ACK) та повторними передачами, оскільки це миттєво спустошило б батарею.

### 2. Ресурсний та криптографічний бар'єр
Сучасні стандарти кібербезпеки вимагають обов'язкового взаємного шифрування транспортного рівня (TLS 1.3 / mTLS з алгоритмами ECDSA та ChaCha20-Poly1305 або AES-GCM). Щоб провести криптографічне рукостискання, верифікувати ланцюжок сертифікатів X.509 і тримати в пам'яті сесійні ключі та буфери фрагментації TCP, пристрою потрібно щонайменше 50–120 КБ виділеної оперативної пам'яті (RAM).

Польовий датчик температури на базі 8-бітного ядра або ощадливого мікроконтролера ARM Cortex-M0+ має усього 8–16 КБ усієї пам'яті SRAM. Він не здатний виконати TLS-рукостискання ані за обсягом пам'яті, ані за обчислювальною швидкодією. Шлюз бере цю криптографічну роботу на себе: він підтримує захищену TLS-сесію з хмарою, виступаючи єдиною довіреною точкою виходу об'єкта у зовнішній світ.

### 3. Парадигмальний бар'єр
Польові протоколи здебільшого синхронні та циклічні: майстер на шині Modbus послідовно запитує регістри підлеглих пристроїв за жорстким розкладом. Хмарні платформи та системи диспетчеризації працюють за асинхронною моделлю публікації/підписки (MQTT) або подієво-орієнтованою моделлю (REST/Webhooks). Шлюз транслює синхронний цикл опитування у потік асинхронних семантичних подій.

> 🔧 **Навіщо це.** Шлюз — це не просто кабельний перехідник і не «німа труба» (*dumb pipe*), яка пересилає байти з одного сокета в інший. Шлюз є локальним хазяїном об'єкта. Він володіє знанням про структуру підключених приладів, правила їх опитування, одиниці вимірювання та фізичні межі безпеки.

---

## Конвеєр вхідних даних: мостове перетворення, фільтрація й агрегація

Трансляція протоколів у шлюзі вимагає суворого детермінізму. Розгляньмо послідовний шлях обробки вимірювань від фізичного порту до готового до відправки MQTT-пакета.

![Механіка трансляції бінарних польових протоколів у семантичні MQTT JSON повідомлення](/root/course/embedded/shliuz-i-lokalna-avtonomiia/img/protocol-translation-flow.svg)
*Трансляція моделей: перетворення синхронного кадру Modbus RTU та бінарного пакета LoRaWAN Cayenne LPP у стандартизовані асинхронні повідомлення MQTT із збереженням апаратних міток часу.*

### 1. Низхідний прийом (Southbound Ingestion) та контроль таймінгів

#### Modbus RTU (RS-485)
Шлюз працює як `Modbus Master`. Планувальник опитування активує запити до підлеглих вузлів (`Slave ID: 1..247`) згідно з конфігураційними дескрипторами. 

Приймання кадру вимагає апаратного контролю інтервалів тиші на шині:
* Інтервал між байтами всередині кадру не повинен перевищувати `t1.5` (1.5 символу).
* Інтервал між окремими кадрами повинен бути не меншим за `t3.5` (3.5 символу). При швидкості 9600 біт/с час одного байта (11 бітів) дорівнює 1.145 мс, отже пауза `t3.5` становить 4.01 мс.

Драйвер UART шлюзу використовує апаратні таймери бездіяльності (наприклад, функцію *Receiver Timeout* у мікроконтролерах STM32/ESP32) або переривання DMA, щоб зафіксувати кінець кадру без навантаження центрального процесора. Після прийому шлюз розраховує та перевіряє 16-бітну контрольну суму `CRC-16/MODBUS` (поліном `0xA001`). Якщо контрольна сума зійшлася, сирі байти надходять у транслятор.

#### LoRaWAN Concentrator
Шлюз на базі мікросхеми концентратора (наприклад, Semtech SX1302/SX1303) одночасно прослуховує 8 радіоканалів і кілька коефіцієнтів розширення спектра (SF7–SF12). Демодульований радіопакет передається в процесор шлюзу через шину SPI. 

Шлюз витягує заголовок `FHDR`:
* Перевіряє адресу пристрою `DevAddr` (32 біти).
* Перевіряє лічильник кадрів `FCnt` для захисту від атак повторного відтворення (Replay Attacks).
* Валідує код автентичності повідомлення `MIC` (Message Integrity Code) за допомогою ключа `NwkSKey` (алгоритм AES-CMAC-128).
* Розшифровує корисне навантаження `FRMPayload` ключем `AppSKey` (алгоритм AES-CTR-128).

### 2. Розбір байтового порядку (Endianness) та бітових полів

Польові протоколи пакують дані в компактні бінарні структури. Для їх перетворення на дійсні інженерні величини шлюз використовує карту регістрів:

* **Modbus Word Swapping:** Стандарт Modbus не регламентує порядок слів у 32-бітних числах з рухомою комою (IEEE 754 Float). Якщо теплолічильник повертає два 16-бітні регістри `0x4288` та `0x0000`, шлюз має знати конфігурацію пристрою:
  * *Big-Endian (ABCD):* `0x42880000` = `68.0`
  * *Little-Endian Word Swap (CDAB):* `0x00004288` = `0.0000000000...` (сміття)
* **LoRaWAN Cayenne LPP / Packed Binary:** Формати кодування пакують тип сенсора, номер каналу та масштабоване ціле число. Наприклад, байти `0x01 0x67 0x01 0x1A` означають:
  * `0x01` — Канал 1
  * `0x67` — Тип: Давач температури (роздільна здатність 0.1 °C, знакове int16)
  * `0x011A` = `282` → `282 × 0.1` = `28.2 °C`

### 3. Апаратне мічення часу (Hardware Timestamping)

Критична помилка недосвідчених систем — ставити мітку часу в хмарі в момент отримання повідомлення. Якщо висхідний канал упаде на дві доби, хмарний сервер після відновлення зв'язку отримає 100 000 накопичених точок і запише їх під однією поточною секундою, перетворивши часовий ряд на вертикальну стіну некоректних даних.

Шлюз має власний апаратний годинник реального часу (RTC), який періодично синхронізується через NTP або GPS. Мітка часу `sampled_at` (UNIX Timestamp у мікросекундах або мілісекундах) формується шлюзом у момент фізичного переривання UART або SPI прийому пакета і назавжди вшивається в структуру вимірювання.

### 4. Апертурна фільтрація (Deadband) та фільтрація викидів

Якщо давач температури теплоносія опитується раз на секунду, але температура змінюється повільно, надсилати 86 400 ідентичних повідомлень на добу через платний стільниковий трафік 4G — марнотратство.

Шлюз застосовує **апертурну фільтрацію** (*Report-by-Exception / Deadband*):

```
Поточне значення: v
Останнє передане: v_last
Поріг апертури:   Δv
Максимальний час тиші: T_heartbeat

Умова відправки:
(|v - v_last| ≥ Δv)  АБО  (now - t_last_sent ≥ T_heartbeat)
```

1. Якщо зміна величини перевищує дельту `Δv` (наприклад, `|T - T_last| ≥ 0.2 °C`), подія негайно генерується та передається далі.
2. Якщо величина не змінюється, шлюз мовчить, але не довше за `T_heartbeat` (наприклад, 15 хвилин). Примусове повідомлення серцебиття підтверджує, що датчик і шлюз живі, а канал зв'язку справний.

Паралельно працює **фільтрація викидів** (*Sanity Check*):
* Якщо давач тиску води в побутовій системі повертає значення `999.9 bar` або `-50.0 bar`, це апаратний обрив струмової петлі або помилка АЦП.
* Шлюз відкидає такі точки з потоку телеметрії, але генерує діагностичну подію `SENSOR_HARDWARE_FAULT` у локальний журнал.

### 5. Віконна агрегація (Time-Window Aggregation)

Для високочастотних сигналів (наприклад, вимірювання вібрації підшипника насоса на частоті 1 кГц або струму двигуна на 50 Гц) передача сирих відліків у хмару неможлива через обмеження пропускної здатності.

Шлюз накопичує ковзне вікно відліків тривалістю `W` (наприклад, 10 секунд) і розраховує статистичний вектор:
* `avg` (середнє арифметичне значення)
* `rms` (середнє квадратичне значення для оцінки діючого струму / потужності)
* `min` та `max` (екстремуми напруги або тиску)
* `variance` / `std_dev` (дисперсія як індикатор механічного зносу)

У висхідний канал вирушає один компактний агрегований запис раз на 10 секунд замість 10 000 сирих чисел.

---

## Механізм автономії (Store-and-Forward): надійність на дні блекауту

Головний виклик для автономного шлюзу — поведінка під час тривалого обриву висхідного каналу (*WAN Outage*). Обрив може тривати від кількох секунд (короткочасний збій базової станції) до кількох діб (пошкодження оптоволоконної лінії внаслідок аварії).

![Життєвий цикл повідомлення у черзі Store-and-Forward та автомат станів зв'язку](/root/course/embedded/shliuz-i-lokalna-avtonomiia/img/store-forward-lifecycle.svg)
*Скінченний автомат синхронізації: перемикання між прямою трансляцією, збереженням у SQLite WAL під час блекауту та транзакційним порційним зливом без перевантаження висхідного каналу зв'язку.*

### Чому буферизація в RAM непридатна

Якщо система генерує 10 повідомлень на секунду розміром 200 байтів кожне, за годину блекауту обсяг даних становить:

```
10 пов/с × 200 байт × 3600 с = 7.2 МБ / год
За добу: 7.2 МБ × 24 = 172.8 МБ
```

Для вбудованого контролера з 16–32 МБ оперативної пам'яті вичерпання RAM настане вже за кілька годин. Крім того, будь-яке раптове перезавантаження шлюзу через стрибок живлення миттєво знищить увесь накопичений у RAM буфер. Дані мусять зберігатися в енергонезалежній пам'яті (Flash / eMMC / microSD).

### Архітектура локального сховища на SQLite у режимі WAL

Класичні реляційні бази даних на вбудованих Linux-системах за замовчуванням використовують режим відкатного журналу (*Rollback Journal*). У цьому режимі кожен запис викликає блокування файлу бази, скидання сторінок на диск через `fsync()` і подвійний перезапис блоків флеш-пам'яті, що викликає катастрофічне зношення флешу (*Flash Wear-Out*) і гальмує систему.

Стандартом промислових IoT-шлюзів є вбудована база **SQLite у режимі журналу випереджального запису (Write-Ahead Log, WAL)**.

Переваги режиму WAL для вбудованих систем:
1. **Паралельне читання та запис:** Читачі черги (потік синхронізації з хмарою) не блокують запис нових вимірювань від польових шин. Запис здійснюється послідовним додаванням в кінець файлу `*-wal`.
2. **Стійкість до збоїв живлення (Power-Cut Safety):** Якщо живлення зникає посеред запису транзакції, неповний кадр у WAL просто ігнорується під час наступного старту. Основний файл бази даних `gateway.db` ніколи не пошкоджується.
3. **Оптимальна взаємодія з Flash-пам'яттю:** Завдяки послідовному запису сторінок і відсутності частих хаотичних перезаписів контролер eMMC/Flash ефективно виконує вирівнювання зносу (*Wear Leveling*).

Налаштування SQLite для автономного шлюзу:

```sql
PRAGMA journal_mode = WAL;          -- Вмикаємо режим Write-Ahead Log
PRAGMA synchronous = NORMAL;         -- Баланс між надійністю та швидкістю fsync
PRAGMA temp_store = MEMORY;          -- Тимчасові таблиці тримаємо в RAM
PRAGMA wal_autocheckpoint = 1000;    -- Скидання журналу у файл кожні 1000 сторінок
PRAGMA mmap_size = 67108864;         -- 64 МБ Memory-Mapped I/O для швидкого читання
```

### Схема таблиці черги Store-and-Forward

```sql
CREATE TABLE IF NOT EXISTS outbound_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  INTEGER NOT NULL,     -- Мітка часу зняття вимірювання (UNIX ms)
    priority    INTEGER NOT NULL,     -- 0: Телеметрія, 1: Стан/Події, 2: Аварії (Alarms)
    topic       TEXT NOT NULL,        -- Цільовий MQTT-топік
    payload     BLOB NOT NULL,        -- Бінарний payload (JSON / CBOR / Protobuf)
    status      INTEGER DEFAULT 0     -- 0: PENDING, 1: IN_FLIGHT
);

CREATE INDEX IF NOT EXISTS idx_queue_drain 
ON outbound_queue (status, priority DESC, id ASC);
```

### Політика витіснення при переповненні накопичувача (Eviction Strategy)

Якщо блекаут триває тижнями, а обсяг виділеного розділу Flash (наприклад, 2 ГБ) заповнюється на 85%, шлюз застосовує політику **пріоритетного витіснення**:

1. **Аварійні події (Priority 2 - Alarms) та аудит-логи** зберігаються безстроково і ніколи не видаляються автоматично.
2. **Високочастотна телеметрія (Priority 0)** витісняється за принципом FIFO: найстаріші регулярні точки видаляються пакетами по 1000 штук, щоб звільнити місце для свіжих вимірювань та аварійних подій.
3. Шлюз фіксує факт втрати точок і формує діагностичний прапорець `DATA_EVICTION_OCCURRED`, який буде відправлено в хмару першим повідомленням після відновлення зв'язку.

```sql
-- Видалення найстаріших 500 записів низького пріоритету при досягненні ліміту диска
DELETE FROM outbound_queue 
WHERE id IN (
    SELECT id FROM outbound_queue 
    WHERE priority = 0 AND status = 0 
    ORDER BY id ASC 
    LIMIT 500
);
```

### Автомат станів відновлення зв'язку та порційний злив (Batch Drain)

Коли інтернет-канал відновлюється, наївна спроба «вивалити» всі накопичені 500 000 повідомлень одночасно призведе до колапсу: переповниться черга модему, брокер розірве з'єднання через перевищення ліміту частоти повідомлень (*Rate Limit*), а процесор шлюзу зависне в блокувальних мережевих викликах.

Синхронізація виконується через чотиристадійний автомат:

```
[1. ONLINE_STREAMING] ────(Втрата WAN)────► [2. OFFLINE_BUFFERING]
        ▲                                            │
        │                                            │ (Відновлення лінка)
 (Черга порожня)                                     ▼
        │                                   [3. WAN_RECOVERING]
        │                                            │
        │                                   (TLS/MQTT підключено)
        │                                            ▼
[4. DRAINING_SYNC] ◄─────────────────────────────────┘
```

1. **ONLINE_STREAMING:** Канал активний, черга на диску порожня. Свіжі дані після фільтрації публікуються в MQTT напряму (затримка < 5 мс).
2. **OFFLINE_BUFFERING:** Фіксація обриву (провал MQTT Keep-Alive / TCP RST). Усі повідомлення записуються виключно в SQLite WAL.
3. **WAN_RECOVERING:** Відновлення інтерфейсу WAN (отримання IP по DHCP / підняття LTE сесії). Виконання TLS-рукостискання та підключення до MQTT-брокера.
4. **DRAINING_SYNC (Порційний злив):**
   * Шлюз вибирає з бази транзакційну пачку `BATCH_SIZE = 50` записів найвищого пріоритету:
     ```sql
     SELECT id, topic, payload FROM outbound_queue 
     WHERE status = 0 
     ORDER BY priority DESC, id ASC 
     LIMIT 50;
     ```
   * Переводить їх у статус `IN_FLIGHT` (`status = 1`).
   * Публікує пачку в MQTT з рівнем якості **QoS 1**.
   * Тільки після отримання від брокера пакетів підтвердження `PUBACK` на всі повідомлення пачки виконується атомарне видалення:
     ```sql
     DELETE FROM outbound_queue WHERE id IN (101, 102, ... 150);
     ```
   * Між пачками встановлюється регульована пауза (наприклад, 50 мс), що обмежує висхідний потік на рівні безпечних 100–200 кбіт/с.
   * Коли черга стає порожньою (`SELECT COUNT(*) FROM outbound_queue == 0`), шлюз повертається в стан `ONLINE_STREAMING`.

---

## Локальне аварійне реагування (Local Rule Engine)

Головна відмінність промислового шлюзу від простого ретранслятора — наявність вбудованого **рушія локальних правил** (*Edge Rule Engine*).

![Розділення локального аварійного контуру та висхідного моніторингу](/root/course/embedded/shliuz-i-lokalna-avtonomiia/img/emergency-rule-pipeline.svg)
*Швидкий локальний аварійний шлях (Fast-Path) виконується за частки мілісекунди безпосередньо в оперативній пам'яті шлюзу, повністю ізолюючи захисну автоматику від затримок та збоїв глобальної мережі.*

### Бюджет часу аварійного реагування

У технологічних процесах критичні аварії розвиваються за лічені частки секунди:
* Кавітація та сухий хід насоса руйнують крильчатку за 1–2 секунди.
* Гідроудар при різкому закритті магістрального клапана поширюється зі швидкістю звуку у воді (1400 м/с).
* Перегрів літієвого акумулятора (Thermal Runaway) переходить у некероване займання за секунди.

Час проходження сигналу через хмару складається з неконтрольованих затримок:

```
T_реакції_хмари = T_модем + T_стільниковий_канал + T_інтернет_маршрутизація + 
                  T_хмарна_черга + T_обробка_сервером + T_зворотний_шлях
```

Навіть в ідеальних умовах 4G/LTE цей час становить 150–500 мс, а за нестабільного сигналу чи повторних передач TCP — 5–30 секунд. Під час обриву зв'язку час реакції хмари дорівнює **нескінченності**.

Локальний рушій правил шлюзу працює за детермінованим **швидким шляхом (Fast-Path)**:
```
T_локальної_реакції = T_прийом_кадру (DMA) + T_перевірка_правил (RAM) + T_GPIO_вихід
                     = 200 мкс + 50 мкс + 5 мкс ≈ 0.255 мс
```

Реакція менше ніж за 1 мілісекунду виконується локально і не залежить від стану глобальної мережі.

### Архітектура Fast-Path Rule Engine

1. **Таблиця стану об'єкта в пам'яті (Shared State Table):** Шлюз тримає в пам'яті атомарну таблицю останніх валідних значень усіх фізичних величин:

:::tabs
```c
typedef struct {
    float value;
    uint64_t timestamp_ms;
    bool is_valid;
    bool is_alarm;
} MetricState;
```
```cpp
struct MetricState {
    float value{0.0f};
    std::chrono::milliseconds timestamp{0};
    bool is_valid{false};
    bool is_alarm{false};
};
```
:::

2. **Конфігурація правил:** Правило описується декларативно або у вигляді автомата станів:
   * *Умова спрацьовування:* `IF (boiler_pressure > 6.0 bar) AND (valve_feedback == CLOSED)`
   * *Захисна дія:* `ACTION: gpio_set_emergency_relay(HIGH); modbus_write_coil(PUMP_RELAY_ADDR, 0);`
   * *Діагностичне сповіщення:* Сформувати подію найвищого пріоритету (`priority = 2`) в чергу SQLite.
3. **Гістерезис та антибрязкіт аварій (Debounce / Hysteresis):** Щоб виключити багаторазове клацання потужного силового контактора при коливаннях тиску навколо порогового значення (наприклад, 6.01 -> 5.99 -> 6.02 bar), правило містить гістерезис (поріг скидання 5.5 bar) і таймер затримки повернення (*Hold-off Timer*).
4. **Конфлікт пріоритетів (Локальний захист проти хмарних команд):** Якщо оператор із мобільного застосунку через хмару надсилає команду `FORCE_START_HEATER`, але локальний шлюз фіксує тиск `6.5 bar` (аварія), шлюз **блокує виконання дистанційної команди**, повертаючи статус `CMD_REJECTED_LOCAL_SAFETY_OVERRIDE`. Локальна безпека завжди має вищий пріоритет над віддаленими командами.
5. **Сторожовий таймер зв'язку з периферією (Node Watchdog):** Якщо підлеглий польовий давач перестав відповідати на опитування довше за тайм-аут `T_sensor_timeout` (наприклад, обрив дроту термопари), шлюз не має права тримати останнє старе значення — він негайно переводить контур у безпечний стан (*Fail-Safe Default*): зупиняє нагрів і активує аварійну сигналізацію.

---

## Модуль надійного шлюзу на C та C++

Розгляньмо повну реалізацію ядра автономного шлюзу: мостове перетворення, виконання аварійних правил, локальна черга повідомлень із пріоритетами та автомат порційного зливу Store-and-Forward.

:::tabs
```c
// gateway_core.h - Ядро автономного шлюзу на чистому C (C99/C11)
#ifndef GATEWAY_CORE_H
#define GATEWAY_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_METRICS         64
#define MAX_TOPIC_LEN       64
#define MAX_PAYLOAD_LEN     256
#define MAX_QUEUE_DEPTH     512
#define BATCH_DRAIN_LIMIT   16

// Рівні пріоритету повідомлень
typedef enum {
    PRIO_TELEMETRY = 0,     // Регулярні точки (витісняються першими)
    PRIO_EVENT     = 1,     // Зміна стану / Команди
    PRIO_ALARM     = 2      // Критичні аварії (не видаляються ніколи)
} MessagePriority;

// Стани висхідного каналу WAN
typedef enum {
    WAN_ONLINE_STREAMING,   // Пряма публікація в MQTT
    WAN_OFFLINE_BUFFERING,  // Збереження у чергу на диску
    WAN_DRAINING_SYNC       // Порційна передача накопиченої черги
} WanState;

// Запис черги Store-and-Forward
typedef struct {
    uint32_t id;
    uint64_t timestamp_ms;
    MessagePriority priority;
    char topic[MAX_TOPIC_LEN];
    char payload[MAX_PAYLOAD_LEN];
    bool in_flight;
} QueueRecord;

// Стан фізичної величини в пам'яті
typedef struct {
    uint16_t metric_id;
    float current_val;
    float last_sent_val;
    uint64_t last_sampled_time_ms;
    uint64_t last_sent_time_ms;
    float deadband;
    uint64_t max_interval_ms;
    bool is_valid;
} MetricEntry;

// Контекст шлюзу
typedef struct {
    MetricEntry metrics[MAX_METRICS];
    size_t metric_count;
    
    QueueRecord queue[MAX_QUEUE_DEPTH];
    size_t queue_count;
    uint32_t next_record_id;
    
    WanState wan_state;
    bool emergency_shutdown_latched;
    float pressure_threshold_bar;
} GatewayContext;

// Публічний API
void gateway_init(GatewayContext *ctx, float pressure_threshold);
void gateway_ingest_modbus_point(GatewayContext *ctx, uint16_t metric_id, 
                                 float value, uint64_t now_ms);
void gateway_process_lorawan_frame(GatewayContext *ctx, uint32_t dev_addr, 
                                   const uint8_t *payload, size_t len, uint64_t now_ms);
void gateway_set_wan_online(GatewayContext *ctx, bool is_online);
void gateway_poll(GatewayContext *ctx, uint64_t now_ms);

#endif // GATEWAY_CORE_H
```
```cpp
// gateway_core.hpp - Ідіоматичне ядро шлюзу на сучасному C++ (C++20)
#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <deque>
#include <unordered_map>
#include <optional>
#include <chrono>
#include <functional>
#include <memory>
#include <span>

namespace edge {

enum class Priority : uint8_t {
    Telemetry = 0,
    Event     = 1,
    Alarm     = 2
};

enum class WanState {
    OnlineStreaming,
    OfflineBuffering,
    DrainingSync
};

struct QueueRecord {
    uint32_t id;
    std::chrono::milliseconds timestamp;
    Priority priority;
    std::string topic;
    std::string payload;
    bool in_flight{false};
};

struct MetricConfig {
    float deadband{0.2f};
    std::chrono::milliseconds max_heartbeat_interval{std::chrono::seconds(300)};
};

struct MetricState {
    float current_value{0.0f};
    float last_sent_value{0.0f};
    std::chrono::milliseconds last_sampled_time{0};
    std::chrono::milliseconds last_sent_time{0};
    bool is_valid{false};
};

class Gateway {
public:
    using OutputPublisher = std::function<bool(std::string_view topic, 
                                               std::string_view payload, 
                                               Priority prio)>;
    using EmergencyActuator = std::function<void(bool activate)>;

    explicit Gateway(float pressure_limit_bar,
                     OutputPublisher publisher,
                     EmergencyActuator actuator,
                     size_t max_queue_capacity = 10000);

    void register_metric(uint16_t metric_id, MetricConfig config);
    void ingest_modbus_reading(uint16_t metric_id, float value, 
                               std::chrono::milliseconds now);
    void ingest_lorawan_packet(uint32_t dev_addr, std::span<const uint8_t> payload, 
                               std::chrono::milliseconds now);

    void set_wan_connected(bool connected);
    void tick(std::chrono::milliseconds now);

    [[nodiscard]] size_t queue_size() const noexcept { return queue_.size(); }
    [[nodiscard]] WanState wan_state() const noexcept { return wan_state_; }
    [[nodiscard]] bool is_emergency_latched() const noexcept { return emergency_latched_; }

private:
    void enqueue_message(Priority prio, std::string topic, std::string payload, 
                         std::chrono::milliseconds now);
    void evaluate_fast_path_rules(uint16_t metric_id, float value, 
                                  std::chrono::milliseconds now);
    void drain_queue_batch();

    float pressure_limit_bar_;
    OutputPublisher publisher_;
    EmergencyActuator emergency_actuator_;
    size_t max_queue_capacity_;

    WanState wan_state_{WanState::OfflineBuffering};
    bool emergency_latched_{false};
    uint32_t next_id_{1};

    std::unordered_map<uint16_t, MetricConfig> metric_configs_;
    std::unordered_map<uint16_t, MetricState> metric_states_;
    std::deque<QueueRecord> queue_;
};

} // namespace edge
```
:::

Тепер реалізуємо логіку обробки:

:::tabs
```c
// gateway_core.c - Реалізація ядра шлюзу
#include "gateway_core.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

// Локальний апаратний виклик (симуляція відсікання аварійного реле)
static void hardware_set_emergency_interlock(bool trigger) {
    // У реальному коді: запис у GPIO або відправка Modbus команди зупинки
    (void)trigger;
}

// Пряма відправка в мережевий стек MQTT (повертає true при успішній публікації)
static bool network_mqtt_publish(const char *topic, const char *payload, MessagePriority prio) {
    (void)topic;
    (void)payload;
    (void)prio;
    // У реальному коді: виклик mg_mqtt_pub() або esp_mqtt_client_publish()
    return true;
}

void gateway_init(GatewayContext *ctx, float pressure_threshold) {
    memset(ctx, 0, sizeof(GatewayContext));
    ctx->pressure_threshold_bar = pressure_threshold;
    ctx->wan_state = WAN_OFFLINE_BUFFERING;
    ctx->next_record_id = 1;
}

// Додавання повідомлення в чергу Store-and-Forward із захистом від переповнення
static void enqueue_record(GatewayContext *ctx, MessagePriority prio, 
                           const char *topic, const char *payload, uint64_t now_ms) {
    // Якщо черга заповнена, витісняємо найстаріший запис низького пріоритету
    if (ctx->queue_count >= MAX_QUEUE_DEPTH) {
        size_t evict_idx = MAX_QUEUE_DEPTH;
        for (size_t i = 0; i < ctx->queue_count; ++i) {
            if (ctx->queue[i].priority == PRIO_TELEMETRY) {
                evict_idx = i;
                break;
            }
        }
        if (evict_idx == MAX_QUEUE_DEPTH) {
            // Якщо немає телеметрії, шукаємо звичайні події
            for (size_t i = 0; i < ctx->queue_count; ++i) {
                if (ctx->queue[i].priority == PRIO_EVENT) {
                    evict_idx = i;
                    break;
                }
            }
        }
        
        // Зсуваємо чергу, якщо знайшли кандидата на видалення
        if (evict_idx < MAX_QUEUE_DEPTH) {
            memmove(&ctx->queue[evict_idx], &ctx->queue[evict_idx + 1], 
                    (ctx->queue_count - evict_idx - 1) * sizeof(QueueRecord));
            ctx->queue_count--;
        } else {
            // Черга забита виключно аваріями - не можемо записати
            return;
        }
    }

    QueueRecord *rec = &ctx->queue[ctx->queue_count++];
    rec->id = ctx->next_record_id++;
    rec->timestamp_ms = now_ms;
    rec->priority = prio;
    rec->in_flight = false;
    snprintf(rec->topic, sizeof(rec->topic), "%s", topic);
    snprintf(rec->payload, sizeof(rec->payload), "%s", payload);
}

// Локальний швидкий шлях (Fast-Path Rule Engine)
static void evaluate_fast_path_rules(GatewayContext *ctx, uint16_t metric_id, 
                                     float value, uint64_t now_ms) {
    // Правило аварії: Тиск у паровому котлі (Metric ID 100)
    if (metric_id == 100) {
        if (value >= ctx->pressure_threshold_bar) {
            if (!ctx->emergency_shutdown_latched) {
                ctx->emergency_shutdown_latched = true;
                hardware_set_emergency_interlock(true);

                char alarm_payload[MAX_PAYLOAD_LEN];
                snprintf(alarm_payload, sizeof(alarm_payload), 
                         "{\"event\":\"CRITICAL_OVERPRESSURE\",\"val\":%.2f,\"ts\":%llu}", 
                         value, (unsigned long long)now_ms);
                
                enqueue_record(ctx, PRIO_ALARM, "plant/boiler/alarm", alarm_payload, now_ms);
            }
        } else if (value < (ctx->pressure_threshold_bar - 0.5f)) {
            // Гістерезис 0.5 bar для скидання аварійного прапорця
            if (ctx->emergency_shutdown_latched) {
                ctx->emergency_shutdown_latched = false;
                hardware_set_emergency_interlock(false);
            }
        }
    }
}

// Обробка показань Modbus RTU
void gateway_ingest_modbus_point(GatewayContext *ctx, uint16_t metric_id, 
                                 float value, uint64_t now_ms) {
    MetricEntry *entry = NULL;
    for (size_t i = 0; i < ctx->metric_count; ++i) {
        if (ctx->metrics[i].metric_id == metric_id) {
            entry = &ctx->metrics[i];
            break;
        }
    }

    if (!entry) {
        if (ctx->metric_count >= MAX_METRICS) return;
        entry = &ctx->metrics[ctx->metric_count++];
        entry->metric_id = metric_id;
        entry->deadband = 0.2f;
        entry->max_interval_ms = 300000; // 5 хв
        entry->is_valid = false;
    }

    entry->current_val = value;
    entry->last_sampled_time_ms = now_ms;

    // 1. Негайне виконання правил захисту (< 1 мс)
    evaluate_fast_path_rules(ctx, metric_id, value, now_ms);

    // 2. Апертурна фільтрація (Deadband)
    bool should_send = false;
    if (!entry->is_valid) {
        should_send = true;
        entry->is_valid = true;
    } else {
        float delta = fabsf(value - entry->last_sent_val);
        if (delta >= entry->deadband) {
            should_send = true;
        } else if ((now_ms - entry->last_sent_time_ms) >= entry->max_interval_ms) {
            should_send = true; // Серцебиття
        }
    }

    if (should_send) {
        entry->last_sent_val = value;
        entry->last_sent_time_ms = now_ms;

        char topic[MAX_TOPIC_LEN];
        char payload[MAX_PAYLOAD_LEN];
        snprintf(topic, sizeof(topic), "plant/sensor/%u/telemetry", metric_id);
        snprintf(payload, sizeof(payload), "{\"val\":%.2f,\"ts\":%llu}", 
                 value, (unsigned long long)now_ms);

        if (ctx->wan_state == WAN_ONLINE_STREAMING && ctx->queue_count == 0) {
            // Канал вільний - публікуємо напряму
            if (!network_mqtt_publish(topic, payload, PRIO_TELEMETRY)) {
                // При невдачі перемикаємося в офлайн і кладемо в чергу
                ctx->wan_state = WAN_OFFLINE_BUFFERING;
                enqueue_record(ctx, PRIO_TELEMETRY, topic, payload, now_ms);
            }
        } else {
            // Канал офлайн або йде злив черги - зберігаємо у Store-and-Forward
            enqueue_record(ctx, PRIO_TELEMETRY, topic, payload, now_ms);
        }
    }
}

// Декодування пакета LoRaWAN Cayenne LPP
void gateway_process_lorawan_frame(GatewayContext *ctx, uint32_t dev_addr, 
                                   const uint8_t *payload, size_t len, uint64_t now_ms) {
    if (len < 4) return; // Мінімум 1 канал: Channel(1) + Type(1) + Val(2)

    size_t offset = 0;
    while (offset + 2 <= len) {
        uint8_t channel = payload[offset++];
        uint8_t type = payload[offset++];

        if (type == 0x67 && (offset + 2 <= len)) { // Температура (0.1 °C знакове)
            int16_t raw_temp = (int16_t)((payload[offset] << 8) | payload[offset + 1]);
            offset += 2;
            float temperature = raw_temp * 0.1f;
            uint16_t synthetic_id = (uint16_t)((dev_addr & 0xFF) * 100 + channel);
            gateway_ingest_modbus_point(ctx, synthetic_id, temperature, now_ms);
        } else {
            break; // Невідомий тип для стислості
        }
    }
}

void gateway_set_wan_online(GatewayContext *ctx, bool is_online) {
    if (is_online) {
        if (ctx->wan_state == WAN_OFFLINE_BUFFERING) {
            ctx->wan_state = (ctx->queue_count > 0) ? WAN_DRAINING_SYNC : WAN_ONLINE_STREAMING;
        }
    } else {
        ctx->wan_state = WAN_OFFLINE_BUFFERING;
    }
}

// Періодичний виклик зливу черги
void gateway_poll(GatewayContext *ctx, uint64_t now_ms) {
    (void)now_ms;
    if (ctx->wan_state != WAN_DRAINING_SYNC) return;

    if (ctx->queue_count == 0) {
        ctx->wan_state = WAN_ONLINE_STREAMING;
        return;
    }

    size_t batch_size = (ctx->queue_count < BATCH_DRAIN_LIMIT) ? ctx->queue_count : BATCH_DRAIN_LIMIT;
    size_t acked_count = 0;

    for (size_t i = 0; i < batch_size; ++i) {
        QueueRecord *rec = &ctx->queue[i];
        if (network_mqtt_publish(rec->topic, rec->payload, rec->priority)) {
            acked_count++;
        } else {
            // Збій висхідного каналу під час зливу
            ctx->wan_state = WAN_OFFLINE_BUFFERING;
            break;
        }
    }

    // Видаляємо успішно відправлені записи
    if (acked_count > 0) {
        memmove(&ctx->queue[0], &ctx->queue[acked_count], 
                (ctx->queue_count - acked_count) * sizeof(QueueRecord));
        ctx->queue_count -= acked_count;
    }
}
```
```cpp
// gateway_core.cpp - Реалізація ядра шлюзу на C++20
#include "gateway_core.hpp"
#include <cmath>
#include <format>
#include <algorithm>

namespace edge {

Gateway::Gateway(float pressure_limit_bar,
                 OutputPublisher publisher,
                 EmergencyActuator actuator,
                 size_t max_queue_capacity)
    : pressure_limit_bar_(pressure_limit_bar),
      publisher_(std::move(publisher)),
      emergency_actuator_(std::move(actuator)),
      max_queue_capacity_(max_queue_capacity) {}

void Gateway::register_metric(uint16_t metric_id, MetricConfig config) {
    metric_configs_[metric_id] = config;
    metric_states_[metric_id] = MetricState{};
}

void Gateway::enqueue_message(Priority prio, std::string topic, std::string payload, 
                              std::chrono::milliseconds now) {
    if (queue_.size() >= max_queue_capacity_) {
        // Витісняємо найстарішу телеметрію
        auto it = std::find_if(queue_.begin(), queue_.end(), [](const QueueRecord& r) {
            return r.priority == Priority::Telemetry;
        });

        if (it != queue_.end()) {
            queue_.erase(it);
        } else {
            // Якщо немає телеметрії, видаляємо звичайну подію
            auto it_ev = std::find_if(queue_.begin(), queue_.end(), [](const QueueRecord& r) {
                return r.priority == Priority::Event;
            });
            if (it_ev != queue_.end()) {
                queue_.erase(it_ev);
            } else {
                return; // Черга заповнена критичними аваріями
            }
        }
    }

    queue_.push_back(QueueRecord{
        .id = next_id_++,
        .timestamp = now,
        .priority = prio,
        .topic = std::move(topic),
        .payload = std::move(payload),
        .in_flight = false
    });
}

void Gateway::evaluate_fast_path_rules(uint16_t metric_id, float value, 
                                       std::chrono::milliseconds now) {
    // Контур контролю критичного тиску парового котла (ID 100)
    if (metric_id == 100) {
        if (value >= pressure_limit_bar_) {
            if (!emergency_latched_) {
                emergency_latched_ = true;
                if (emergency_actuator_) {
                    emergency_actuator_(true); // Негайне апаратне відсікання
                }

                std::string alarm_json = std::format(
                    "{{\"event\":\"CRITICAL_OVERPRESSURE\",\"val\":{:.2f},\"ts\":{}}}",
                    value, now.count()
                );
                enqueue_message(Priority::Alarm, "plant/boiler/alarm", std::move(alarm_json), now);
            }
        } else if (value < (pressure_limit_bar_ - 0.5f)) {
            // Гістерезис відновлення 0.5 bar
            if (emergency_latched_) {
                emergency_latched_ = false;
                if (emergency_actuator_) {
                    emergency_actuator_(false);
                }
            }
        }
    }
}

void Gateway::ingest_modbus_reading(uint16_t metric_id, float value, 
                                    std::chrono::milliseconds now) {
    auto& cfg = metric_configs_[metric_id];
    auto& state = metric_states_[metric_id];

    state.current_value = value;
    state.last_sampled_time = now;

    // 1. Виконання швидкого аварійного контуру (< 1 мс)
    evaluate_fast_path_rules(metric_id, value, now);

    // 2. Апертурна фільтрація
    bool should_send = false;
    if (!state.is_valid) {
        should_send = true;
        state.is_valid = true;
    } else {
        float delta = std::abs(value - state.last_sent_value);
        if (delta >= cfg.deadband) {
            should_send = true;
        } else if ((now - state.last_sent_time) >= cfg.max_heartbeat_interval) {
            should_send = true;
        }
    }

    if (should_send) {
        state.last_sent_value = value;
        state.last_sent_time = now;

        std::string topic = std::format("plant/sensor/{}/telemetry", metric_id);
        std::string payload = std::format("{{\"val\":{:.2f},\"ts\":{}}}", value, now.count());

        if (wan_state_ == WanState::OnlineStreaming && queue_.empty()) {
            if (!publisher_(topic, payload, Priority::Telemetry)) {
                wan_state_ = WanState::OfflineBuffering;
                enqueue_message(Priority::Telemetry, std::move(topic), std::move(payload), now);
            }
        } else {
            enqueue_message(Priority::Telemetry, std::move(topic), std::move(payload), now);
        }
    }
}

void Gateway::ingest_lorawan_packet(uint32_t dev_addr, std::span<const uint8_t> payload, 
                                    std::chrono::milliseconds now) {
    if (payload.size() < 4) return;

    size_t offset = 0;
    while (offset + 2 <= payload.size()) {
        uint8_t channel = payload[offset++];
        uint8_t type = payload[offset++];

        if (type == 0x67 && (offset + 2 <= payload.size())) { // Cayenne LPP Температура
            int16_t raw = static_cast<int16_t>((payload[offset] << 8) | payload[offset + 1]);
            offset += 2;
            float temp = raw * 0.1f;
            uint16_t synthetic_id = static_cast<uint16_t>((dev_addr & 0xFF) * 100 + channel);
            ingest_modbus_reading(synthetic_id, temp, now);
        } else {
            break;
        }
    }
}

void Gateway::set_wan_connected(bool connected) {
    if (connected) {
        if (wan_state_ == WanState::OfflineBuffering) {
            wan_state_ = queue_.empty() ? WanState::OnlineStreaming : WanState::DrainingSync;
        }
    } else {
        wan_state_ = WanState::OfflineBuffering;
    }
}

void Gateway::drain_queue_batch() {
    if (queue_.empty()) {
        wan_state_ = WanState::OnlineStreaming;
        return;
    }

    constexpr size_t BatchLimit = 16;
    size_t processed = 0;

    while (!queue_.empty() && processed < BatchLimit) {
        const auto& rec = queue_.front();
        if (publisher_(rec.topic, rec.payload, rec.priority)) {
            queue_.pop_front();
            processed++;
        } else {
            wan_state_ = WanState::OfflineBuffering;
            break;
        }
    }
}

void Gateway::tick(std::chrono::milliseconds now) {
    (void)now;
    if (wan_state_ == WanState::DrainingSync) {
        drain_queue_batch();
    }
}

} // namespace edge
```
:::

---

## Інженерні крайові випадки, ресурс флешу та вартість відмов

У польових умовах надійність шлюзу перевіряється не в штатному режимі, а в моменти збігів кількох несприятливих факторів.

### 1. Збій живлення під час запису черги (Power Cut during Flash Write)
Раптове відключення живлення під час скидання сторінки на флеш-накопичувач eMMC/SD — головна причина перетворення файлових систем на нечитабельний стан (*RAW/Corrupted*).

* **Апаратний захист:** Промислові шлюзи обладнуються блоком резервного живлення на іоністорах (суперконденсаторах), які утримують напругу живлення 3.3/5 В протягом 200–500 мс після зникнення входу. Сигнал `POWER_FAIL` надходить на лінію переривання мікроконтролера, який негайно завершує відкриті транзакції SQLite та переводить флеш-контролер у стан сну.
* **Програмний захист:** Режим SQLite WAL із `PRAGMA synchronous = NORMAL` гарантує, що навіть у разі раптового знеструмлення без суперконденсаторів цілісність бази даних не порушується: під час наступного завантаження шлюз просто ігнорує пошкоджений хвостовий сектор журналу WAL.

### 2. Стрибок годинника після тривалого блекауту (Clock Jump / Drift)
Якщо шлюз перезавантажився під час повного блекауту за відсутності батарейки RTC, його внутрішній системний годинник стартує з дефолтної епохи (`1970-01-01 00:00:00`). Протягом двох діб автономної роботи він записує в базу 50 000 вимірювань із відносним часом від старту.

Коли зв'язок відновлюється і шлюз отримує точний час від NTP-сервера, годинник стрибає вперед на 56 років:
* **Неприпустимо:** Залишити в базі старі точки з датою 1970 року (вони загубляться на початку часового ряду в хмарі).
* **Неприпустимо:** Переписати всі старі точки поточним моментом NTP (хронологія стиснеться в одну точку).
* **Правильне рішення:** Шлюз обчислює дельту коригування:
  ```
  Δt_зсуву = t_NTP_синхронізований - t_монотонний_на_момент_синхронізації
  ```
  Перед початком зливу черги шлюз виконує одноразовий SQL-запит коригування відносного часу:
  ```sql
  UPDATE outbound_queue 
  SET created_at = created_at + :delta_offset 
  WHERE created_at < 1000000000;
  ```
  Це зміщує всю накопичену хронологію на реальну вісь часу з точністю до мілісекунди.

### 3. Розрахунок ресурсу та зносу флеш-пам'яті (Flash Endurance)

Розрахуймо знос промислової карти microSD / eMMC ємністю 16 ГБ на базі пам'яті 3D TLC (ресурс ~3000 циклів перезапису P/E).

```
Обсяг одного запису в чергу:      256 байтів
Кількість вимірювань:             10 точок/сек = 864 000 точок/добу
Сирий обсяг даних на добу:        864 000 × 256 Б ≈ 221 МБ/добу
Коефіцієнт підсилення запису (WA): ≈ 3 (з урахуванням сторінок файлової системи)
Реальний запис на флеш:           221 МБ × 3 ≈ 663 МБ/добу

Річний обсяг запису:              663 МБ × 365 ≈ 242 ГБ/рік
Сумарний ресурс накопичувача:     16 ГБ × 3000 циклів = 48 000 ГБ (48 ТБ TBW)
Розрахунковий термін служби:      48 000 ГБ ÷ 242 ГБ/рік ≈ 198 років
```

Завдяки пакетуванню в SQLite WAL та апертурній фільтрації (яка зменшує потік точок на 80–90%), знос флеш-пам'яті становить менше 1% ресурсу за 10 років експлуатації.

### 4. Захист від стільникових штормів під час перепідключень
Коли стільникова мережа LTE працює нестабільно, модем може рвати й відновлювати з'єднання кожні кілька секунд. Якщо шлюз намагатиметься миттєво підключатися до MQTT-брокера після кожного підняття інтерфейсу, оператор мобільного зв'язку заблокує SIM-картку за флуд сигнальними повідомленнями в мережі (Signaling Storm).

Шлюз застосовує алгоритм **експоненційного відкату з випадковим джитером** (*Exponential Backoff with Full Jitter*):

```
T_backoff = min(T_max, T_base × 2ⁿ)
T_затримки = Uniform(0, T_backoff)
```

Де `T_base = 2 с`, `T_max = 300 с`, `n` — номер невдалої спроби підключення. Джитер запобігає одночасному штурму хмарного сервера тисячами шлюзів після відновлення живлення на цілій підстанції.

---

## Підсумок: архітектурний баланс автономного шлюзу

Автономний шлюз забезпечує цілісність розподіленої системи шляхом чіткого розмежування обов'язків:
1. **Низхідний контур (Southbound)** бере на себе всю складність фізичних інтерфейсів (гальванічна ізоляція, жорсткі таймінги RS-485, демодуляція LoRaWAN).
2. **Внутрішній конвеєр (Ingestion & Rules)** усуває надлишковий трафік через апертурну фільтрацію та забезпечує миттєву безпеку об'єкта (< 1 мс) незалежно від стану глобальної мережі.
3. **Енергонезалежне сховище (Store-and-Forward)** гарантує збереження хронології подій під час блекаутів будь-якої тривалості завдяки транзакційній природі SQLite WAL.
4. **Висхідний контур (Northbound)** синхронізує накопичені дані порціями з обмеженням швидкості, зберігаючи точні первинні мітки часу вимірювань для хмарної аналітики.
