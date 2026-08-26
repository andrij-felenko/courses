# Що тримати на пристрої, а що на сервері

<preknowlist>
- [Часові ряди: темп запису, зріджування, строк зберігання](root:sf-data/chasovi-riady) — поведінка незмінних метрик, потокові агрегації та життєвий цикл вимірювань.
- [Спектр консистентності, CAP і PACELC](root:sf-distributed/consistency-models) — узгодженість розподіленого стану при мережевих розривах та асинхронній передачі.
- [Край чи хмара: що рахувати на місці](root:embedded/krai-chy-khmara) — енергетичний та обчислювальний баланс між локальною обробкою та радіопередачею.
- [Черга офлайну](root:embedded/cherha-oflainu) — буферизування телеметрії у локальній енергонезалежній пам'яті під час втрати каналу зв'язку.
- [Журнал попереднього запису (WAL)](root:sf-data/write-ahead-log) — забезпечення атомарності змін та стійкості до раптового знеструмлення.
- [EEPROM та FRAM](root:embedded/eeprom-fram) — фізика комірок енергонезалежної пам'яті, ресурс циклів перезапису та гранулярність доступу.
</preknowlist>

Команда розробників вводить в експлуатацію партію з 500 автономних насосних станцій зрошення з живленням від акумуляторів і сонячних панелей під керуванням мікроконтролера STM32 та модема LTE-M. У першій версії прошивки архітектори вирішили зберігати всю телеметрію (тиск, вібрацію вала, струм двигуна) на сервері, транслюючи щосекундні вимірювання безпосередньо через стільниковий зв'язок, а поточний стан регулятора тримати виключно в базі даних бекенда: пристрій запитував у сервера дозвіл перед кожним перемиканням клапана. Через три доби акумулятори ємністю 10 А·год повністю розрядилися через постійно активний радіомодем, а під час першої ж грози, коли стільникова вежа знеструмилася на дві години, станція не змогла виконати аварійне вимкнення при критичному стрибку тиску понад 25 бар і розірвала магістральний трубопровід.

Спроба «виправити» помилку протилежним крайнощем — записувати щосекундні сирі дані у внутрішню Flash-пам'ять мікроконтролера розміром 1 МБ із сектором стирання 4 КБ — призвела до іншої катастрофи: за чотири місяці ресурс у 100 000 циклів стирання вичерпався, комірки пам'яті деградували, і прошивка втратила здатність зберігати навіть базові калібрувальні коефіцієнти.

Ці дві аварії демонструють фундаментальну проблему архітектури зв'язаних систем (*Connected Embedded Systems*): **розподіл даних та розміщення стану** (*Data Partitioning and State Placement*). Вбудований пристрій і сервер мають принципово різну фізику, вартість і надійність збереження інформації. Помилка у визначенні того, які байти належать кремнію мікроконтролера, а які — хмарним базам даних, руйнує енергетичний бюджет, випалює ресурс кремнію і позбавляє систему автономної безпеки.

![Архітектурний розподіл даних між вбудованим пристроєм та сервером](/root/course/embedded/shcho-trymaty-na-prystroi-a-shcho-na-serveri/img/data-partitioning-architecture.svg)
*Розподіл обов'язків між вбудованим вузлом та сервером: локальний контур зберігає критичний стан, ключі та короткостроковий буфер, тоді як сервер агрегує історію, виконує аналітику парку та веде цифрові двійники.*

---

### Фізика та вартість зберігання: кремній MCU проти хмарних баз даних

Щоб побудувати надійний розподіл даних, необхідно зіставити фізичні характеристики та економіку носіїв на боці пристрою та на боці сервера.

На вбудованому вузлі доступні три основні класи пам'яті:
1. **Оперативна пам'ять (SRAM)**: розмір від 16 до 512 КБ. Час доступу — одиниці наносекунд. Енергія запису нульова (в межах споживання ядра), ресурси перезапису нескінченні. Проте це волатильна пам'ять: будь-яке знеструмлення, спрацювання сторожового таймера (*Watchdog*) або перехід у глибокий сон (*Deep Sleep*) без утримання живлення домену пам'яті повністю знищує її вміст.
2. **Внутрішня та зовнішня Flash-пам'ять (NOR Flash)**: розмір від 64 КБ до 32 МБ. Головне фізичне обмеження — **асиметрія читання та стирання**. Запис окремого байта можливий лише шляхом скидання бітів з `1` в `0`. Щоб повернути біти в стан `1`, необхідно виконати стирання цілого сектора (типово 4 КБ) або блока (32–64 КБ). Стирання сектора вимагає подачі підвищеної напруги на плаваючий затвор (тунелювання Фаулера — Нордгейма), що займає від 20 до 150 мс і споживає струм 15–30 мА. Фізичний ресурс оксидного шару обмежений: після 10 000 – 100 000 циклів стирання сектор перестає утримувати заряд.
3. **Сегнетоелектрична (FRAM) та магніторезистивна (MRAM) пам'ять**: розмір від 8 до 512 КБ. Забезпечує побайтовий енергонезалежний запис зі швидкістю шини SPI/I2C (час доступу ~50 нс), енергією запису близько 1 нДж на байт і ресурсом понад 10¹⁴ циклів (фактично необмежений). Головний недолік — висока питома вартість чипа (від $1.50 за 32 КБ проти $0.30 за 4 МБ SPI Flash).

![Характеристики та компроміси носіїв інформації в IoT-системах](/root/course/embedded/shcho-trymaty-na-prystroi-a-shcho-na-serveri/img/storage-hierarchy-tradeoffs.svg)
*Порівняльна піраміда носіїв: від високошвидкісної, але обмеженої пам'яті мікроконтролера до необмежених, але віддалених серверних сховищ.*

На серверному боці діють інші закони:
- Дискові сховища (NVMe SSD, мережеві блокові пристрої AWS EBS, об'єктні сховища S3) надають практично необмежену ємність (петабайти).
- Спеціалізовані бази даних часових рядів (ClickHouse, TimescaleDB, InfluxDB) використовують колоночне стиснення (алгоритми Gorilla для чисел з рухомою комою, дельта-кодування для міток часу), знижуючи вартість зберігання однієї точки телеметрії до часток цента на рік.
- Реляційні системи (PostgreSQL) гарантують повну транзакційну узгодженість (*ACID*) для складних бізнес-правил та метаданих.

#### Економічний та енергетичний бар'єр передачі

Чому не можна просто передавати всі дані на сервер у реальному часі? Відповідь полягає у фізиці радіоканалу.

Передача 1 КБ даних через енергоефективний стільниковий модуль LTE-M/NB-IoT вимагає пробудження радіотракту, синхронізації з базовою станцією, проходження процедури автентифікації та передачі пакетів TCP/TLS. На цей сеанс витрачається від 100 до 300 мДж енергії (середній струм 150 мА при напрузі 3.6 В протягом 0.5–2 секунд). Для батареї CR123A (номінал 1500 мА·год, енергія близько 16 000 Дж) щосекундна передача вичерпає весь заряд за 2–3 доби. Якщо ж накопичувати вимірювання в локальній Flash-пам'яті й надсилати стиснений пакет 1 раз на 6 годин, та сама батарея забезпечить 5–7 років автономної роботи.

#### Фізика деградації комірок Flash та розрахунок ресурсу

Розглянемо типовий провал проектування: розробник записує структуру конфігурації розміром 64 байти у фіксований сектор Flash-пам'яті (4096 байтів) щоразу, коли змінюється поточний лічильник мотогодин (наприклад, кожні 5 хвилин).

Оскільки Flash-пам'ять не дозволяє перезаписати байти без попереднього стирання сектора, кожен запис 64 байтів змушує драйвер зчитувати 4 КБ в оперативну пам'ять, прати весь фізичний сектор і записувати 4 КБ назад.

```
Стирань на добу = (24 години · 60 хв) / 5 хв = 288 стирань/добу
Ресурс сектора NOR Flash = 100 000 циклів
Термін служби носія = 100 000 / 288 ≈ 347 діб (менше 1 року)
```

Через 11 місяців оксидний діелектрик затворів втрачає здатність ізолювати електрони, виникають бітові помилки, і пристрій не може завантажити власні налаштування.

Щоб запобігти цьому, застосовують дві стратегії:
1. **Апаратна заміна на FRAM/EEPROM**: для лічильників і параметрів, що змінюються щохвилини, встановлюють мікросхему FRAM, де ресурс $10^{14}$ циклів гарантує понад 100 років роботи без деградації.
2. **Лог-структуровані сховища (Log-Structured NVS / LittleFS)**: замість стирання сектора нові 64-байтні записи дописуються послідовно в кінець вільного простору сектора (*Append-only*). Сектор стирається лише тоді, коли всі його 4096 байтів заповнені (через $4096 / 64 = 64$ записи). Це знижує частоту стирань у 64 рази й подовжує життя Flash-пам'яті до 60 років.

> 🔧 **Навіщо це.** Локальна пам'ять пристрою призначена для підтримки безперервного, безпечного й енергоефективного функціонування в умовах відсутності мережі. Серверне сховище призначене для глобального аналізу, ретроспективи, координації парку та взаємодії з користувачами.

---

### Декомпозиція даних: що життєво необхідно тримати на вузлі

На основі фізичних обмежень виділяють чотири категорії даних, які зобов'язані перебувати в локальній пам'яті вбудованого вузла.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   КАТЕГОРІЇ ЛОКАЛЬНИХ ДАНИХ ВУЗЛА                        │
├────────────────────────────────┬─────────────────────────────────────────┤
│ 1. Операційний стан (Runtime)  │ FSM, активні уставки, контури безпеки   │
│ 2. Криптографія та ідентичність│ Приватний ключ, апаратний UID, CA cert  │
│ 3. Калібрувальні матриці       │ Зсув нуля АЦП, термодрейф, коефіцієнти  │
│ 4. Кільцевий буфер подій       │ FIFO-черга на 1–7 днів, краш-дампи WDT  │
└────────────────────────────────┴─────────────────────────────────────────┘
```

#### 1. Поточний операційний стан і локальні уставки (Operational State)
Вбудований вузол керує фізичними процесами: клапанами, нагрівачами, реле, силовими мостами інверторів. Час реакції на аварійний стан (перевантаження за струмом, вихід температури за критичну межу, відсутність потоку рідини) повинен складати від мікросекунд до десятків мілісекунд.

Якщо контур захисту залежить від зв'язку з хмарою, затримка передачі пакета (*RTT — Round Trip Time*) плюс час обробки на сервері (сумарно 100–2000 мс) або мережевий збій приведуть до фізичного руйнування обладнання. Тому **всі активні уставки регуляторів (Setpoints), поточний стан кінцевого автомата (FSM) та аварійні пороги зберігаються локально в NVM** (FRAM або емульованому EEPROM на Flash) і миттєво зчитуються під час завантаження ядра.

#### 2. Криптографічні матеріали та апаратна ідентичність (Security Credentials)
Пристрій повинен однозначно підтверджувати свою автентичність серверу без ризику компрометації всього парку.
- **Приватний асимметричний ключ** (наприклад, ECDSA secp256r1 або Ed25519) генерується на етапі виробництва і записується в захищену апаратну область (*Secure Element* ATECC608, eFuse мікроконтролера або зону ARM TrustZone). Цей ключ **ніколи не передається мережею** і не залишає межі кремнію.
- **Кореневий сертифікат центра сертифікації (Root CA)**: публічний сертифікат, зашитий у прошивку, за допомогою якого клієнт TLS верифікує справжність хмарного сервера при підключенні та перевіряє цифровий підпис бінарних оновлень (*Firmware OTA*).
- **Унікальний серійний номер (Hardware UID)**: зчитується з фабричного регістра мікроконтролера (наприклад, 96-бітний `UID` у STM32 або 48-бітний `MAC` в ESP32).

#### 3. Заводські калібрувальні таблиці (Calibration Parameters)
Жоден аналоговий датчик чи перетворювач не є ідеальним. Технологічний розкид кремнію, похибки резистивних дільників і температурний дрейф створюють індивідуальні зміщення.
- Зсув нуля (*Offset*) і крутизна характеристики (*Gain*) внутрішнього АЦП.
- Матриці компенсації взаємного впливу осей триосьового акселерометра та гіроскопа.
- Таблиці перерахунку опору NTC-термісторів у температуру (поліноми Стейнхарта — Харта).

Ці параметри визначаються індивідуально на тестовому стенді під час виготовлення плати й записуються в захищений сектор Flash/EEPROM. Вузол повинен виконувати перетворення сирих кодів АЦП у фізичні одиниці (вольти, бари, градуси) на місці. Це дозволяє локальній бізнес-логіці ухвалювати коректні рішення без звернення до сервера.

#### 4. Короткостроковий кільцевий буфер подій та «Чорна скринька» (Telemetry Buffer & Crash Log)
Втрата каналу зв'язку — це штатний режим роботи будь-якої бездротової системи. Локальна Flash-пам'ять організовується як кільцевий буфер (*Circular Log Buffer*), який забезпечує збереження телеметрії на період від 1 до 7 діб:
- Під час штатної роботи нові записи додаються в буфер, а фоновий процес передає їх на сервер і зміщує вказівник підтверджених даних (*Tail Pointer*).
- Якщо мережа недоступна, буфер заповнюється. При досягненні 100% ємності вмикається стратегія FIFO-витіснення: найстаріші рутинні вимірювання перезаписуються новими.
- **Аварійні дампи (Crash Dumps)**: стан регістрів процесора під час виникнення `HardFault`, трасування стека (*Stack Unwinding*) та лічильники скидань сторожового таймера записуються в окрему фіксовану зону пам'яті, яка **ніколи не затирається рутинною телеметрією**.

#### Формати серіалізації: накладні витрати JSON проти CBOR та Protobuf

Коли дані передаються між пристроєм і сервером, вибір формату серіалізації прямо впливає на споживання пам'яті та енергетичний бюджет.

```
┌──────────────────────────────────────────────────────────────────────────┐
│             ПОРІВНЯННЯ ФОРМАТІВ СЕРІАЛІЗАЦІЇ ДЛЯ ВУЗЛІВ                  │
├─────────────────┬──────────┬──────────────┬──────────────┬───────────────┤
│ Формат          │ Розмір   │ RAM (Парсер) │ CPU навантаж.│ Схема даних   │
├─────────────────┼──────────┼──────────────┼──────────────┼───────────────┤
│ JSON (текст)    │ 240 Б    │ 2–8 КБ (Купа)│ Високе       │ Неявна        │
│ CBOR (бінарний) │ 68 Б     │ 256–512 Б    │ Середнє      │ Самоописова   │
│ Protocol Buffers│ 22 Б     │ 0 Б (Статика)│ Мінімальне   │ Жорстка (.proto)│
└─────────────────┴──────────┴──────────────┴──────────────┴───────────────┘
```

Розглянемо типовий пакет телеметрії: мітка часу, 3 канали аналогових сенсорів, статус прапорців та заряд батареї:
- **JSON**: вимагає передачі текстових ключів `{"timestamp":1700000000,"temp":23.45,"pressure":101.3,"batt_v":3.82,"status":"OK"}`. Розмір корисного навантаження — близько 90 байтів плюс заголовки. Парсинг вимагає сканування рядків і часто динамічного виділення пам'яті (`malloc`), що на мікроконтролерах із 32 КБ RAM створює ризик фрагментації купи.
- **Protocol Buffers (NanoPB)** або плоска бінарна C-структура: ті самі дані упаковуються у 16–22 байти за допомогою кодування змінної довжини (*Varint*) та упакованих чисел з рухомою комою. Десеріалізація на мікроконтролері зводиться до перевірки розміру та прямого копіювання полів без жодного виділення пам'яті з купи.

Зменшення пакета з 240 байтів до 22 байтів знижує час роботи передавача в ефірі у 10 разів, зберігаючи роки роботи акумулятора для парку з тисяч пристроїв.

---

### Серверні сховища: часові ряди, аналітика та цифрові двійники

Серверна частина системи бере на себе завдання, які неможливо вирішити в межах ресурсів окремого мікроконтролера.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   КАТЕГОРІЇ СЕРВЕРНИХ ДАНИХ                              │
├────────────────────────────────┬─────────────────────────────────────────┤
│ 1. Бази часових рядів          │ ClickHouse/Timescale, роки вимірювань   │
│ 2. Багаторівневе зріджування   │ Raw (14 днів) -> 1 год -> 1 доба (3 р.) │
│ 3. Аналітика парку та ML       │ Предиктивне обслуговування, кореляції   │
│ 4. Метадані та права доступу   │ PostgreSQL, прив'язка до акаунтів, RBAC │
│ 5. Цифровий двійник (Shadow)   │ Стан desired vs reported, черга дельт   │
└────────────────────────────────┴─────────────────────────────────────────┘
```

#### 1. Довгострокова історія та багаторівневе зріджування (Downsampling)
Сервер агрегує потоки даних від тисяч пристроїв за роки експлуатації. Для оптимізації вартості сховища застосовують конвеєри зріджування:
- **Рівень 1 (Hot Storage)**: сирі секундні дані зберігаються протягом 14–30 днів для оперативної діагностики інцидентів.
- **Рівень 2 (Warm Storage)**: фоновий процес щогодини агрегує секундні точки у середні значення, мінімуми, максимуми та перцентилі (p₅₀, p₉₅, p₉₉). Дані зберігаються 90–180 днів.
- **Рівень 3 (Cold Storage)**: добові агрегати зберігаються 3–5 років у колоночних сховищах для побудови річних звітів та аналізу сезонних трендів.

#### 2. Аналітика всього парку (Fleet Intelligence & Predictive Maintenance)
Жоден окремий пристрій не може оцінити загальну картину деградації компонентів. Маючи телеметрію від 100 000 вузлів, серверні алгоритми машинного навчання виявляють системні закономірності:
- Виявлення бракованих партій акумуляторів за швидкістю росту внутрішнього еквівалентного послідовного опору (ESR) при однакових температурних циклах.
- Прогнозування виходу підшипника помпи з ладу шляхом спектрального аналізу вібрацій і зіставлення його з історичними поломками інших станцій (*Predictive Maintenance*).
- Кореляція енергоспоживання з погодними умовами в конкретному географічному регіоні.

#### 3. Метадані користувачів та бізнес-правила
Інформація про те, якому фермерському господарству належить насосна станція, які права доступу має конкретний оператор (рольова модель RBAC), історія платежів за зв'язок та географічні межі дозволеної експлуатації (*Geofencing*) зберігаються виключно в реляційній базі даних сервера. Вбудований мікроконтролер не повинен знати імен користувачів чи тарифних планів.

#### 4. Цифрові двійники (Device Shadows / Digital Twins)
Головний архітектурний шаблон зв'язку між асинхронним вебом і вбудованим вузлом — **цифровий двійник**.

Оскільки кінцевий вузол 99% часу спить або може бути тимчасово недоступний через перешкоди зв'язку, користувач мобільного застосунку не може безпосередньо надсилати синхронні RPC-запити на плату. Замість цього сервер підтримує JSON/CBOR-документ стану, розділений на дві гілки:
- `desired`: бажаний стан, який встановив користувач або бізнес-логіка бекенда (наприклад, увімкнути полив, цільовий тиск 4.5 бар).
- `reported`: фактичний стан, який вузол востаннє підтвердив апаратними вимірюваннями.

Коли пристрій виходить на зв'язок, він отримує різницю (`delta = desired - reported`), застосовує зміни до своїх регістрів і публікує новий `reported`.

---

### Інваріанти узгодженості та проблема джерела правди (Source of Truth)

Найнебезпечніша помилка проектування розподіленої системи — розмивання меж відповідальності за дані (*Data Ownership*). Якщо одне й те саме поле конфігурації можуть одночасно змінювати і сервер, і локальний пристрій без чіткого арбітражу, виникає стан перегонів (*Race Condition*), що веде до розсинхронізації та аварій.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   МАТРИЦЯ ДЖЕРЕЛ ПРАВДИ (SOURCE OF TRUTH)                │
├──────────────────────────────────┬───────────────────────────────────────┤
│ Джерело правди — ПРИСТРІЙ        │ Джерело правди — СЕРВЕР               │
├──────────────────────────────────┼───────────────────────────────────────┤
│ • Фактичний стан реле та моторів │ • Цільові уставки (Target Setpoints)  │
│ • Напруга та температура батареї │ • Розклад роботи та тайм-слоти        │
│ • Фізичні покази сенсорів        │ • Версія цільової прошивки (OTA)      │
│ • Локальний одометр/мотогодини   │ • Геозони та ліміти споживання        │
│ • Апаратні коди аварій (Faults)  │ • Дозволи на активацію функцій        │
└──────────────────────────────────┴───────────────────────────────────────┘
```

#### Правило 1: Фізичні факти належать виключно пристрою
Сервер ніколи не може «призначити» пристрою напругу акумулятора `3.85 В` або змусити його «вважати», що температура підшипника дорівнює `40 °C`. Будь-які дані, що є результатом прямого фізичного вимірювання сенсорами або відображають поточний стан силових ключів (реле увімкнене/вимкнене), мають єдине джерело правди — **вбудований вузол**. Сервер лише фіксує отримані звіти (`reported`).

#### Правило 2: Бізнес-наміри та глобальні уставки належать серверу
Бажані режими роботи, розклади активації, тарифні обмеження та політики оновлення прошивки формуються користувачем чи хмарною платформою. Сервер є єдиним джерелом правди для гілки `desired`.

#### Правило 3: Локальний пріоритет безпеки (Local Safety Precedence)
Якщо сервер надіслав команду встановити оберти помпи на 3000 об/хв (`desired`), але локальний сенсор тиску зафіксував перевищення критичної позначки 30 бар, вбудований вузол **зобов'язаний відхилити серверне налаштування**, вимкнути двигун через локальний аварійний контур і опублікувати у відповідь статус помилки:

```json
{
  "reported": {
    "pump_state": "EMERGENCY_STOP",
    "pressure_bar": 31.2,
    "last_error": "ERR_OVERPRESSURE_LOCKOUT",
    "config_version": 42
  }
}
```

Серверний цифровий двійник, отримавши такий звіт, скидає гілку `desired`, синхронізуючи віртуальний стан із фізичною реальністю.

#### Локальне ручне керування (Manual Override) та арбітраж перегонів

Типовий інженерний випадок: на шафі керування насосною станцією встановлено фізичний перемикач «Ручний пуск / Автомат». Якщо оператор на місці вручну перемикає тумблер у положення «Увімкнено», виникає конфлікт із серверним розкладом.

Архітектурний патерн вирішення конфлікту:
1. **Локальний пріоритет дії**: Вузол негайно виконує команду фізичного тумблера, встановлюючи внутрішній прапорець `manual_override = true`.
2. **Публікація оновленого стану**: Вузол формує звіт `reported: { pump_state: "RUNNING", manual_override: true, version: 105 }`.
3. **Реакція сервера**: Отримавши повідомлення про ручне керування, хмарний сервіс тимчасово блокує автоматичні команди за розкладом і надсилає сповіщення диспетчеру в веб-інтерфейс.
4. **Скидання блокування**: Автоматичне керування відновлюється лише тоді, коли тумблер на місці повертають у режим «Автомат», або після вичерпання апаратного таймауту безпеки.

#### Життєвий цикл трифазної синхронізації з версіонуванням

Для запобігання втраті оновлень та усунення дублювання конфігурація супроводжується монотонним цілочисельним лічильником версій (`config_version`).

![Життєвий цикл узгодження цифрового двійника](/root/course/embedded/shcho-trymaty-na-prystroi-a-shcho-na-serveri/img/device-shadow-sync-flow.svg)
*Послідовність синхронізації: користувач задає бажаний стан у хмарі, вузол отримує дельту, перевіряє її, фіксує в NVM, застосовує до апаратури та звітує про новий стан.*

Кроки протоколу:
1. **Ініціація зміни**: Користувач змінює цільову температуру в додатку. Сервер формує запис у двійнику:
   `desired: { target_temp: 24.0 }, version: 105`.
2. **Формування дельти**: Сервер обчислює різницю між `desired` та `reported` і відправляє у топік `$shadow/delta` лише змінені поля разом із номером версії `105`.
3. **Приймання та валідація на вузлі**:
   - Вузол перевіряє, що отримана версія більша за поточну збережену (`105 > 104`).
   - Виконується перевірка меж (*Sanity Check*): наприклад, `-20.0 <= target_temp <= 80.0`.
4. **Атомарна фіксація в NVM**: Нова структура конфігурації з новою версією `105` і контрольною сумою CRC32 записується в енергонезалежну пам'ять (Flash/FRAM).
5. **Застосування до апаратури**: Нові коефіцієнти передаються у виконавчий контур регулятора.
6. **Звіт про узгодження**: Вузол публікує повідомлення в топік `$shadow/reported`:
   `reported: { target_temp: 24.0, status: "OK" }, version: 105`.
7. **Закриття дельти на сервері**: Сервер фіксує збіг `desired == reported` і очищає активну дельту.

---

### Повний модуль розподіленого керування конфігурацією та станом на C/C++

Нижче наведено промисловий модуль синхронізації конфігурації та стану пристрою (*Device Shadow State Synchronizer*).

Модуль реалізує:
1. Захищене збереження конфігурації в енергонезалежній пам'яті (NVM) з перевіркою магічного числа `0x43464731` ("CFG1"), монотонної версії та контрольної суми CRC-32.
2. Валідацію діапазонів значень для захисту фізичного обладнання.
3. Обробку вхідної дельти від хмари, оновлення апаратного стану та генерацію пакета підтвердження `reported`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CONFIG_MAGIC 0x43464731U /* "CFG1" */
#define MAX_DEVICE_NAME_LEN 32

/* Апаратні обмеження безпеки */
#define MIN_TARGET_TEMP_C   (-20.0f)
#define MAX_TARGET_TEMP_C   (80.0f)
#define MIN_INTERVAL_SEC    (5U)
#define MAX_INTERVAL_SEC    (86400U)

/* Коди результатів синхронізації */
typedef enum {
    SYNC_OK = 0,
    SYNC_ERR_INVALID_MAGIC,
    SYNC_ERR_CRC_MISMATCH,
    SYNC_ERR_STALE_VERSION,
    SYNC_ERR_OUT_OF_RANGE,
    SYNC_ERR_STORAGE_FAIL
} sync_status_t;

/* Структура конфігурації (зберігається в NVM) */
typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t version;
    float    target_temperature_c;
    uint32_t telemetry_interval_sec;
    bool     auto_valve_enabled;
    char     device_alias[MAX_DEVICE_NAME_LEN];
    uint32_t crc32;
} device_nvm_config_t;

/* Структура дельти, що приходить від сервера */
typedef struct {
    uint32_t version;
    bool     has_target_temp;
    float    target_temperature_c;
    bool     has_interval;
    uint32_t telemetry_interval_sec;
    bool     has_auto_valve;
    bool     auto_valve_enabled;
    bool     has_device_alias;
    const char *device_alias;
} shadow_delta_t;

/* Фактичний операційний стан для звітування в хмару */
typedef struct {
    uint32_t applied_version;
    float    current_temperature_c;
    float    active_target_temp_c;
    uint32_t active_interval_sec;
    bool     active_valve_state;
    sync_status_t last_sync_status;
} shadow_reported_state_t;

/* Розрахунок CRC32 (поліном IEEE 802.3 0xEDB88320) */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

/* Імітація низькорівневого інтерфейсу Flash/FRAM (HAL) */
static uint8_t g_simulated_nvm_storage[sizeof(device_nvm_config_t)];

static bool hal_nvm_read(void *dest, size_t size) {
    if (size != sizeof(device_nvm_config_t)) return false;
    memcpy(dest, g_simulated_nvm_storage, size);
    return true;
}

static bool hal_nvm_write(const void *src, size_t size) {
    if (size != sizeof(device_nvm_config_t)) return false;
    memcpy(g_simulated_nvm_storage, src, size);
    return true;
}

/* Модуль синхронізатора */
typedef struct {
    device_nvm_config_t active_config;
    bool is_initialized;
} state_synchronizer_t;

static state_synchronizer_t g_sync_mgr;

/* Завантаження та перевірка цілісності конфігурації з NVM */
sync_status_t state_sync_init(void) {
    device_nvm_config_t loaded_cfg;
    if (!hal_nvm_read(&loaded_cfg, sizeof(loaded_cfg))) {
        return SYNC_ERR_STORAGE_FAIL;
    }

    if (loaded_cfg.magic != CONFIG_MAGIC) {
        /* Перший старт: ініціалізація заводськими значеннями */
        memset(&g_sync_mgr.active_config, 0, sizeof(device_nvm_config_t));
        g_sync_mgr.active_config.magic = CONFIG_MAGIC;
        g_sync_mgr.active_config.version = 1;
        g_sync_mgr.active_config.target_temperature_c = 22.0f;
        g_sync_mgr.active_config.telemetry_interval_sec = 60;
        g_sync_mgr.active_config.auto_valve_enabled = true;
        strncpy(g_sync_mgr.active_config.device_alias, "Node-Default", MAX_DEVICE_NAME_LEN - 1);

        size_t payload_len = sizeof(device_nvm_config_t) - sizeof(uint32_t);
        g_sync_mgr.active_config.crc32 = calculate_crc32((const uint8_t *)&g_sync_mgr.active_config, payload_len);

        if (!hal_nvm_write(&g_sync_mgr.active_config, sizeof(device_nvm_config_t))) {
            return SYNC_ERR_STORAGE_FAIL;
        }
        g_sync_mgr.is_initialized = true;
        return SYNC_OK;
    }

    /* Перевірка контрольної суми */
    size_t payload_len = sizeof(device_nvm_config_t) - sizeof(uint32_t);
    uint32_t expected_crc = calculate_crc32((const uint8_t *)&loaded_cfg, payload_len);
    if (loaded_cfg.crc32 != expected_crc) {
        return SYNC_ERR_CRC_MISMATCH;
    }

    memcpy(&g_sync_mgr.active_config, &loaded_cfg, sizeof(device_nvm_config_t));
    g_sync_mgr.is_initialized = true;
    return SYNC_OK;
}

/* Обробка вхідної дельти конфігурації від сервера */
sync_status_t state_sync_apply_delta(const shadow_delta_t *delta) {
    if (!g_sync_mgr.is_initialized || delta == NULL) {
        return SYNC_ERR_STORAGE_FAIL;
    }

    /* Захист від застарілих або повторних повідомлень */
    if (delta->version <= g_sync_mgr.active_config.version) {
        return SYNC_ERR_STALE_VERSION;
    }

    /* Створення тіньової копії для перевірки меж */
    device_nvm_config_t candidate_cfg = g_sync_mgr.active_config;
    candidate_cfg.version = delta->version;

    if (delta->has_target_temp) {
        if (delta->target_temperature_c < MIN_TARGET_TEMP_C || 
            delta->target_temperature_c > MAX_TARGET_TEMP_C) {
            return SYNC_ERR_OUT_OF_RANGE;
        }
        candidate_cfg.target_temperature_c = delta->target_temperature_c;
    }

    if (delta->has_interval) {
        if (delta->telemetry_interval_sec < MIN_INTERVAL_SEC || 
            delta->telemetry_interval_sec > MAX_INTERVAL_SEC) {
            return SYNC_ERR_OUT_OF_RANGE;
        }
        candidate_cfg.telemetry_interval_sec = delta->telemetry_interval_sec;
    }

    if (delta->has_auto_valve) {
        candidate_cfg.auto_valve_enabled = delta->auto_valve_enabled;
    }

    if (delta->has_device_alias && delta->device_alias != NULL) {
        strncpy(candidate_cfg.device_alias, delta->device_alias, MAX_DEVICE_NAME_LEN - 1);
        candidate_cfg.device_alias[MAX_DEVICE_NAME_LEN - 1] = '\0';
    }

    /* Оновлення CRC та атомарний запис у Flash */
    size_t payload_len = sizeof(device_nvm_config_t) - sizeof(uint32_t);
    candidate_cfg.crc32 = calculate_crc32((const uint8_t *)&candidate_cfg, payload_len);

    if (!hal_nvm_write(&candidate_cfg, sizeof(device_nvm_config_t))) {
        return SYNC_ERR_STORAGE_FAIL;
    }

    /* Зміни успішно зафіксовані */
    g_sync_mgr.active_config = candidate_cfg;
    return SYNC_OK;
}

/* Формування стану Reported для публікації на сервер */
void state_sync_get_reported(float current_sensor_temp, 
                             bool current_valve_pin_state,
                             sync_status_t last_status,
                             shadow_reported_state_t *out_reported) {
    if (out_reported == NULL) return;

    out_reported->applied_version = g_sync_mgr.active_config.version;
    out_reported->current_temperature_c = current_sensor_temp;
    out_reported->active_target_temp_c = g_sync_mgr.active_config.target_temperature_c;
    out_reported->active_interval_sec = g_sync_mgr.active_config.telemetry_interval_sec;
    out_reported->active_valve_state = current_valve_pin_state;
    out_reported->last_sync_status = last_status;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <array>
#include <string_view>
#include <optional>
#include <expected>
#include <span>

namespace embedded::iot {

inline constexpr uint32_t ConfigMagic = 0x43464731U; // "CFG1"
inline constexpr size_t MaxAliasLength = 32;

inline constexpr float MinTargetTempC = -20.0f;
inline constexpr float MaxTargetTempC = 80.0f;
inline constexpr uint32_t MinIntervalSec = 5U;
inline constexpr uint32_t MaxIntervalSec = 86400U;

enum class SyncError : uint8_t {
    InvalidMagic,
    CrcMismatch,
    StaleVersion,
    OutOfRange,
    StorageFailure
};

#pragma pack(push, 1)
struct DeviceNvmPayload {
    uint32_t magic{ConfigMagic};
    uint32_t version{1};
    float targetTemperatureC{22.0f};
    uint32_t telemetryIntervalSec{60};
    bool autoValveEnabled{true};
    char deviceAlias[MaxAliasLength]{"Node-Default"};
};

struct DeviceNvmRecord {
    DeviceNvmPayload payload{};
    uint32_t crc32{0};
};
#pragma pack(pop)

struct ShadowDelta {
    uint32_t version{0};
    std::optional<float> targetTemperatureC{};
    std::optional<uint32_t> telemetryIntervalSec{};
    std::optional<bool> autoValveEnabled{};
    std::optional<std::string_view> deviceAlias{};
};

struct ShadowReportedState {
    uint32_t appliedVersion{};
    float currentSensorTempC{};
    float activeTargetTempC{};
    uint32_t activeIntervalSec{};
    bool activeValveState{};
    std::optional<SyncError> lastError{};
};

class Crc32Calculator {
public:
    static constexpr uint32_t Calculate(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 1U) {
                    crc = (crc >> 1) ^ 0xEDB88320U;
                } else {
                    crc >>= 1;
                }
            }
        }
        return ~crc;
    }
};

// Абстрактний інтерфейс сховища NVM (Flash / FRAM)
class INvmStorage {
public:
    virtual ~INvmStorage() = default;
    virtual bool Read(std::span<uint8_t> destination) = 0;
    virtual bool Write(std::span<const uint8_t> source) = 0;
};

// Симулятор NVM-драйвера в пам'яті
class SimulatedNvmStorage final : public INvmStorage {
public:
    bool Read(std::span<uint8_t> destination) override {
        if (destination.size() != m_storage.size()) return false;
        std::memcpy(destination.data(), m_storage.data(), destination.size());
        return true;
    }

    bool Write(std::span<const uint8_t> source) override {
        if (source.size() != m_storage.size()) return false;
        std::memcpy(m_storage.data(), source.data(), source.size());
        return true;
    }

private:
    std::array<uint8_t, sizeof(DeviceNvmRecord)> m_storage{};
};

class StateSynchronizer {
public:
    explicit StateSynchronizer(INvmStorage& storage) noexcept
        : m_storage(storage) {}

    [[nodiscard]] std::expected<void, SyncError> Initialize() noexcept {
        DeviceNvmRecord record{};
        auto recordSpan = std::span<uint8_t>(reinterpret_cast<uint8_t*>(&record), sizeof(record));

        if (!m_storage.Read(recordSpan)) {
            return std::unexpected(SyncError::StorageFailure);
        }

        if (record.payload.magic != ConfigMagic) {
            return InitializeFactoryDefaults();
        }

        auto payloadSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&record.payload), sizeof(DeviceNvmPayload));
        
        if (record.crc32 != Crc32Calculator::Calculate(payloadSpan)) {
            return std::unexpected(SyncError::CrcMismatch);
        }

        m_activeRecord = record;
        m_isInitialized = true;
        return {};
    }

    [[nodiscard]] std::expected<void, SyncError> ApplyDelta(const ShadowDelta& delta) noexcept {
        if (!m_isInitialized) {
            return std::unexpected(SyncError::StorageFailure);
        }

        if (delta.version <= m_activeRecord.payload.version) {
            return std::unexpected(SyncError::StaleVersion);
        }

        DeviceNvmRecord candidate = m_activeRecord;
        candidate.payload.version = delta.version;

        if (delta.targetTemperatureC) {
            if (*delta.targetTemperatureC < MinTargetTempC || *delta.targetTemperatureC > MaxTargetTempC) {
                return std::unexpected(SyncError::OutOfRange);
            }
            candidate.payload.targetTemperatureC = *delta.targetTemperatureC;
        }

        if (delta.telemetryIntervalSec) {
            if (*delta.telemetryIntervalSec < MinIntervalSec || *delta.telemetryIntervalSec > MaxIntervalSec) {
                return std::unexpected(SyncError::OutOfRange);
            }
            candidate.payload.telemetryIntervalSec = *delta.telemetryIntervalSec;
        }

        if (delta.autoValveEnabled) {
            candidate.payload.autoValveEnabled = *delta.autoValveEnabled;
        }

        if (delta.deviceAlias) {
            const size_t copyLen = std::min(delta.deviceAlias->size(), MaxAliasLength - 1);
            std::memset(candidate.payload.deviceAlias, 0, MaxAliasLength);
            std::memcpy(candidate.payload.deviceAlias, delta.deviceAlias->data(), copyLen);
        }

        auto payloadSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&candidate.payload), sizeof(DeviceNvmPayload));
        candidate.crc32 = Crc32Calculator::Calculate(payloadSpan);

        auto recordSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&candidate), sizeof(candidate));

        if (!m_storage.Write(recordSpan)) {
            return std::unexpected(SyncError::StorageFailure);
        }

        m_activeRecord = candidate;
        return {};
    }

    [[nodiscard]] ShadowReportedState GenerateReport(float currentSensorTemp, 
                                                    bool currentValveState,
                                                    std::optional<SyncError> error = std::nullopt) const noexcept {
        return ShadowReportedState{
            .appliedVersion = m_activeRecord.payload.version,
            .currentSensorTempC = currentSensorTemp,
            .activeTargetTempC = m_activeRecord.payload.targetTemperatureC,
            .activeIntervalSec = m_activeRecord.payload.telemetryIntervalSec,
            .activeValveState = currentValveState,
            .lastError = error
        };
    }

    [[nodiscard]] const DeviceNvmPayload& GetConfig() const noexcept {
        return m_activeRecord.payload;
    }

private:
    std::expected<void, SyncError> InitializeFactoryDefaults() noexcept {
        m_activeRecord = DeviceNvmRecord{};
        m_activeRecord.payload.magic = ConfigMagic;
        m_activeRecord.payload.version = 1;
        m_activeRecord.payload.targetTemperatureC = 22.0f;
        m_activeRecord.payload.telemetryIntervalSec = 60;
        m_activeRecord.payload.autoValveEnabled = true;

        constexpr std::string_view defaultAlias = "Node-Default";
        std::memcpy(m_activeRecord.payload.deviceAlias, defaultAlias.data(), defaultAlias.size());

        auto payloadSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&m_activeRecord.payload), sizeof(DeviceNvmPayload));
        m_activeRecord.crc32 = Crc32Calculator::Calculate(payloadSpan);

        auto recordSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&m_activeRecord), sizeof(m_activeRecord));

        if (!m_storage.Write(recordSpan)) {
            return std::unexpected(SyncError::StorageFailure);
        }

        m_isInitialized = true;
        return {};
    }

    INvmStorage& m_storage;
    DeviceNvmRecord m_activeRecord{};
    bool m_isInitialized{false};
};

} // namespace embedded::iot
```
:::

---

### Підсумок інженерних правил розміщення даних

Чітке розмежування відповідальності між вбудованим вузлом і сервером базується на трьох непорушних інженерних правилах:

1. **Правило автономної безпеки**: Все, що необхідно для запобігання фізичній аварії та підтримки локального контуру регулювання (FSM, калібрування, уставки захисту), живе в енергонезалежній пам'яті мікроконтролера. Пристрій не має права чекати на відповідь сервера, коли тиск або температура перетинають критичну межу.
2. **Правило збереження кремнію та батареї**: Високочастотні сирі вимірювання агрегуються та фільтруються на місці в SRAM. Довгострокова телеметрія пишеться у Flash-буфер лише пакетами, узгодженими з розміром сторінки, а радіоканал активується з мінімально допустимою періодичністю.
3. **Правило цифрового двійника з монотонним версіонуванням**: Будь-яка двостороння зміна параметрів проходить через модель `desired / reported` з інваріантом «фізичні факти належать пристрою, бізнес-наміри — серверу». Відхилення неприпустимих значень та обробка розривів мережі закладаються в код як штатний базовий сценарій.
