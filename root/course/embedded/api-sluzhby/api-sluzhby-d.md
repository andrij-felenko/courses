# API служби: ресурси, версії, депрекація

<preknowlist>
- [Ролі: вузол, шлюз, брокер, служба, сховище, клієнт](root:embedded/roli-vuzol-shliuz-broker-sluzhba-skhovyshche-kliient) — розподіл обов'язків між компонентами зв'язаної IoT-системи.
- [REST](root:com-protocol/rest-api) — принципи побудови інтерфейсів на основі ресурсів і стандартних методів HTTP.
- [MQTT](root:com-protocol/mqtt) — модель публікації-підписки для асинхронного обміну з пристроями.
- [Версія повідомлення й сумісність](root:embedded/versiia-povidomlennia-i-sumisnist-v-obydva-boky) — пряма та зворотна сумісність схем даних.
- [Ідемпотентність](root:sf-distributed/idempotency) — безпечне повторення мережевих операцій без дублювання дій.
</preknowlist>

У 2021 році комунальне підприємство розгорнуло в приватному секторі 50 000 розумних лічильників електроенергії. Прилади підключалися через стільникові 2G/NB-IoT модеми раз на добу, передавали пакунок показів методом `POST /api/telemetry` у форматі JSON із полями `{"id": "m_102", "v": 231.4, "a": 4.8, "ts": 1614556800}` і засинали на наступні двадцять чотири години. Через п'ять років бекенд-команда вирішила модернізувати хмарну платформу: переписала сервіси на мікросервісну архітектуру, перейшла на стандартизовані імена полів (`voltage_mv`, `current_ma`), додала обов'язкову автентифікацію через Bearer-токени в заголовках і розгорнула новий інтерфейс замість старого. 

Наступного ранку 38 000 лічильників не змогли передати покази. Отримавши у відповідь `HTTP 404 Not Found` та `401 Unauthorized` із розлогими HTML-сторінками помилок від веб-сервера, прошивка приладів сприйняла це як збій зв'язку. Мікроконтролери перейшли в агресивний режим повторних спроб: вмикали стільниковий радіомодем щохвилини, вичерпали місячний ліміт SIM-карт за півдня, розрядили резервні літієві елементи живлення й заблокували базові станції оператора тисячами одночасних запитів. Оскільки лічильники стояли в опломбованих щитках на електроопорах, дистанційно оновити прошивку без робочого зв'язку було вже неможливо, а виїзд бригад монтерів коштував дорожче за річний бюджет усього проєкту.

Ця катастрофа ілюструє головну відмінність хмарних служб Інтернету речей від звичайного вебу. У класичному вебі випуск нової версії бекенду супроводжується миттєвим перезавантаженням клієнтського JavaScript у браузері користувача. В апаратних системах програмний інтерфейс служби (англ. *Application Programming Interface*, API — «інтерфейс прикладного програмування») фізично прив'язаний до заліза, що роками працює в полі без фізичного доступу. Будь-яка зміна кінцевої точки або формату даних на сервері стає випробуванням надійності для всього парку пристроїв. Розберімо, як проєктувати ресурси служби, керувати версіями контракту та безпечно виводити застарілі інтерфейси, не ламаючи жодного працюючого контролера.

---

### Подвійна площина зв'язку: Північ проти Півдня

Служба Інтернету речей одночасно живе у двох принципово різних світах, вимоги яких суперечать одна одній на кожному рівні мережевого стека.

З одного боку до служби звертаються люди та корпоративні системи: мобільні додатки користувачів, веб-панелі операторів, аналітичні конвеєри, білінгові сервери та системи класу ERP чи SCADA. Цей напрямок називають **північним інтерфейсом** (англ. *Northbound API*). Тут домінує синхронна модель «запит–відповідь» (англ. *request–response pull*): клієнт надсилає запит по HTTP/1.1 або HTTP/2, очікує структурованої відповіді у форматі JSON або gRPC, вимагає суворої перевірки прав через OAuth2 чи JWT-токени, фільтрації, сортування та пагінації великих масивів даних. Клієнти на півночі мають необмежене живлення, стабільні гігабітні канали зв'язку й здатні миттєво адаптуватися до змін контракту після оновлення програми з App Store або перезавантаження вкладки браузера.

З іншого боку до служби підключаються апаратні мікроконтролери, польові датчики, виконавчі реле та промислові шлюзи. Це **південний інтерфейс** (англ. *Southbound API*). Тут взаємодія будується на асинхронній, керованій подіями моделі (англ. *event-driven push*): пристрої прокидаються за внутрішнім таймером або апаратним перериванням, надсилають виміряні дані компактними пакетами через MQTT, CoAP чи сирі UDP/TCP сокети й негайно повертаються в глибокий сон задля збереження батареї. Контролери перебувають за суворими трансляторами адрес операторів (Carrier-Grade NAT) або фаєрволами мобільних мереж, тому сервер **не може** відкрити пряме TCP-з'єднання до сплячого приладу, коли мобільний додаток користувача хоче змінити налаштування.

![Діаграма подвійної площини зв'язку: Північний інтерфейс REST/gRPC згори, Ядро служби з L7-шлюзом, роутером та тінню пристрою посередині, Південний інтерфейс MQTT/CoAP зі сплячими вузлами знизу](/root/course/embedded/api-sluzhby/img/api-iot-dual-plane.svg)
*Подвійна площина взаємодії IoT-служби. Північний інтерфейс обслуговує синхронні запити веб-панелей та мобільних додатків через REST та gRPC. Південний інтерфейс приймає асинхронну телеметрію від польових мікроконтролерів через брокери MQTT, CoAP-шлюзи та черги завдань. Центральне ядро служби узгоджує ці світи за допомогою цифрового двійника (Device Shadow) та асинхронного життєвого циклу команд.*

Спроба об'єднати обидва світи в єдиний монолітний HTTP REST API зазнає краху з двох причин. По-перше, повноцінний HTTP-запит із TLS-рукостисканням, заголовками `User-Agent`, `Authorization`, `Content-Type` та JSON-обгорткою важить від 800 до 2000 байтів, що у 50 разів перевищує корисне навантаження 4-байтового відліку температури й спустошує бюджет енергії та трафіку датчика. По-друге, синхронний виклик «увімкнути реле» з мобільного додатка не може дочекатися фізичного спрацьовування заліза, якщо контролер спатиме ще сорок хвилин.

Головне завдання серверної служби — бути **трансформатором площин**. Вона приймає асинхронні події від заліза, зберігає часові ряди в базі даних, оновлює поточний стан цифрового двійника (англ. *Device Shadow*) і надає північним клієнтам елегантний, швидкий та передбачуваний REST-інтерфейс.

> 🔧 **Навіщо це.** Розділення північної та південної площин дозволяє оптимізувати кожен канал під власні обмеження: для приладів залишається мінімалістичний бінарний чи компактний JSON-транспорт із тривалим утриманням сесії або швидким UDP-пушем, а для зовнішніх розробників та вебу відкривається повнофункціональний OpenAPI/Swagger інтерфейс зі стандартними статус-кодами помилок та документацією.

---

### Ресурсна модель пристрою в REST API

У парадигмі REST (англ. *Representational State Transfer* — «передача стану представлення») усе взаємодіє через ресурси, що мають унікальні ідентифікатори (URI) та стандартні дієслова протоколу HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).

Для Інтернету речей ресурсна модель вибудовується навколо ідентифікатора пристрою (`device_id`). Ієрархія кінцевих точок повинна чітко розмежовувати статичні метадані, динамічний потік часових рядів телеметрії, конфігурацію параметрів та виконання дій.

| Кінцева точка | Метод | Призначення та семантика |
| :--- | :--- | :--- |
| `/v1/devices` | `GET` | Отримання списку пристроїв із пагінацією (`?page=1&limit=50`) та фільтрацією за статусом, типом чи групою. |
| `/v1/devices` | `POST` | Реєстрація нового апарата в системі (ініціалізація серійного номера, сертифіката чи відбитка відкритого ключа). |
| `/v1/devices/{id}` | `GET` | Отримання паспортних даних пристрою: модель, ревізія заліза, версія поточної прошивки, статус зв'язку (`online`/`offline`), час останнього контакту. |
| `/v1/devices/{id}` | `DELETE` | Виведення пристрою з експлуатації (дереєстрація, відкликання сертифікатів доступу). |
| `/v1/devices/{id}/telemetry` | `GET` | Запит історичних часових рядів за діапазоном часу (`?from=2026-03-01T00:00:00Z&to=2026-03-02T00:00:00Z&metric=voltage&downsample=1h`). Тільки читання. |
| `/v1/devices/{id}/config` | `GET` | Читання поточної конфігурації (інтервали вимірювань, пороги спрацьовування аварій, адреси серверів). |
| `/v1/devices/{id}/config` | `PATCH` | Часткове оновлення конфігурації. Змінює бажаний стан (Desired State) у системі. |
| `/v1/devices/{id}/shadow` | `GET` | Отримання повного цифрового двійника: порівняння бажаного (`desired`) та фактично звітованого (`reported`) станів пристрою. |
| `/v1/devices/{id}/commands` | `POST` | Створення нового асинхронного завдання на виконання дії на пристрої (перезавантаження, увімкнення контактора, калібрування). |
| `/v1/devices/{id}/commands/{cmd_id}`| `GET` | Перевірка поточного стану виконання раніше створеної команди (`PENDING`, `DELIVERED`, `EXECUTED`, `FAILED`, `EXPIRED`). |

#### Пастка синхронного виклику та асинхронний життєвий цикл команд

Найпоширеніша помилка розробників, які приходять у IoT із класичного вебу, — проєктування прямих синхронних дій над пристроями. Створюється ендпоінт виду `POST /v1/devices/{id}/relay/toggle`. Коли користувач тисне кнопку в мобільному додатку, бекенд намагається відкрити сокет до приладу, надіслати байт команди, дочекатися фізичного клацання реле й тільки після цього повернути `HTTP 200 OK`.

Цей підхід ламається в реальних умовах:
1. **Сплячі вузли:** якщо пристрій спить і виходить на зв'язок раз на годину, HTTP-з'єднання від мобільного клієнта чекатиме годину й завершиться помилкою `504 Gateway Timeout` через 30–60 секунд.
2. **Вичерпання пулу потоків:** сотня одночасних команд до вузлів із нестабільним зв'язком блокує всі робочі потоки сервера (HTTP workers), паралізуючи роботу всієї системи.
3. **Втрата ідемпотентності:** мобільний додаток після таймауту повторює запит. Якщо перша команда таки дійшла до приладу із запізненням, повторний запит виконається вдруге (наприклад, відкриє ворота двічі або повторно спише лічильник).

Єдине надійне архітектурне рішення — **моделювання команд як окремих асинхронних ресурсів**.

![Асинхронний життєвий цикл команди: клієнт створює команду через POST, отримує 202 Accepted з Location, пристрій забирає завдання після сну через MQTT, виконує дію, звітує статус, клієнт опитує статус через GET](/root/course/embedded/api-sluzhby/img/rest-device-resource-model.svg)
*Асинхронний життєвий цикл виконання команд у REST API. Сервер ніколи не блокує HTTP-з'єднання в очікуванні відповіді від заліза. Запит негайно фіксується в базі даних та черзі, клієнт отримує статус 202 Accepted і посилання на створену команду, а пристрій виконує завдання асинхронно при першому контакті.*

Послідовність роботи асинхронного контуру складається з чотирьох кроків:

1. **Створення ресурсу команди:** Клієнт надсилає `POST /v1/devices/dev-42/commands` із зазначенням типу дії, параметрів, допустимого строку життя команди (англ. *Time to Live*, TTL) та обов'язкового клієнтського ключа ідемпотентності в заголовку:
   ```http
   POST /v1/devices/dev-42/commands HTTP/1.1
   Host: api.iot-system.com
   Authorization: Bearer eyJhbGciOi...
   Idempotency-Key: 9f8a3c2e-44d1-42ab-b3c1-098812af1120
   Content-Type: application/json

   {
     "action": "SET_RELAY_STATE",
     "params": { "relay_index": 0, "state": true },
     "ttl_seconds": 3600
   }
   ```
2. **Миттєва фіксація та статус 202 Accepted:** Сервер у межах однієї транзакції записує команду в таблицю БД зі статусом `PENDING`, публікує повідомлення в чергу завдань (MQTT топік `devices/dev-42/cmd` або брокер Kafka/RabbitMQ) і **негайно** повертає клієнту статус `202 Accepted` із заголовком `Location`:
   ```http
   HTTP/1.1 202 Accepted
   Location: /v1/devices/dev-42/commands/cmd_7719ab2
   Content-Type: application/json

   {
     "id": "cmd_7719ab2",
     "device_id": "dev-42",
     "status": "PENDING",
     "created_at": "2026-08-26T19:30:00Z",
     "expires_at": "2026-08-26T20:30:00Z"
   }
   ```
3. **Асинхронне виконання на пристрої:** Коли контролер виходить на зв'язок, він вичитує команду з брокера, перевіряє, чи не минув `expires_at`, виконує фізичну дію на піні GPIO і шле назад звіт: `{"cmd_id": "cmd_7719ab2", "status": "EXECUTED", "result": {"voltage_after": 229.8}}`. Сервер оновлює стан ресурсу в БД.
4. **Контроль завершення клієнтом:** Мобільний додаток періодично опитує `GET /v1/devices/dev-42/commands/cmd_7719ab2` (або отримує миттєве сповіщення через Server-Sent Events чи WebSocket):
   ```http
   HTTP/1.1 200 OK
   Content-Type: application/json

   {
     "id": "cmd_7719ab2",
     "status": "EXECUTED",
     "executed_at": "2026-08-26T19:34:12Z",
     "duration_ms": 185
   }
   ```

Якщо через нестабільний інтернет клієнтський додаток втратив зв'язок після кроку 1 і повторив свій `POST` запит із тим самим `Idempotency-Key`, сервер знаходить уже створений запис `cmd_7719ab2` і повертає його без створення дублюючої команди. Реле гарантовано спрацює рівно один раз.

---

### Стратегії версіонування API для довговічних апаратних систем

Апаратний пристрій, змонтований у трансформаторній підстанції, ліфтовій шахті чи на даху будівлі, розраховується на експлуатаційний строк у 10–15 років. За цей час стек бекенду встигає змінитися тричі. Контракт між сервером та приладами зобов'язаний еволюціонувати так, щоб жоден старий клієнт не втратив сумісності.

У світовій інженерній практиці виділяють три основні рівні керування версіями інтерфейсів.

![Три стратегії версіонування API: версія в шляху URL для кардинальних змін, версія в заголовках для чистого вебу та версія в схемі навантаження для MQTT та CoAP](/root/course/embedded/api-sluzhby/img/api-versioning-strategies.svg)
*Порівняння трьох стратегій версіонування в архітектурі IoT. Версія в URL path забезпечує максимальну прозорість та легку маршрутизацію на рівні зворотних проксі-серверів. Версія в заголовках зберігає чистоту адрес ресурсів. Версія в корисній схемі є єдиним дієвим рішенням для асинхронних брокерів повідомлень (MQTT, CoAP, Kafka).*

#### 1. Версія в шляху URL (URI Path Versioning)

Номер мажорної версії фіксується як перший сегмент шляху після доменного імені:
- `https://api.iot-system.com/v1/devices/{id}/telemetry`
- `https://api.iot-system.com/v2/devices/{id}/telemetry`

**Як це працює:** Мережевий балансувальник або L7-маршрутизатор (NGINX, Envoy, Traefik, AWS ALB) аналізує префікс URI й миттєво перенаправляє трафік: запити з префіксом `/v1/` ідуть на пул застарілих контейнерів або сервіс-адаптер, а запити `/v2/` спрямовуються до нового сервісу.

**Переваги:**
- Найвища наочність: у логах доступу веб-сервера, дашбордах моніторингу та інструментах трасування (OpenTelemetry, Grafana Tempo) версія контракту очевидна з першого погляду.
- Тривіальне кешування: проміжні проксі-сервери й CDN використовують повний URL як ключ кешування без потреби аналізувати заголовки.
- Не потребує складного розбору заголовків на простих мікроконтролерах із сирими HTTP-клієнтами на C.

**Недоліки:**
- Повний злам простору імен URI: ресурс пристрою концептуально не змінюється, але отримує дві різні адреси.
- Складно версіонувати окремі ресурси: зміна схеми одного лише ендпоінта телеметрії формально змушує дублювати під префіксом `/v2/` усі супутні маршрути (`/config`, `/shadow`, `/commands`), навіть якщо вони не зазнали змін.

#### 2. Версія в HTTP-заголовках (Header Versioning / Content Negotiation)

URL залишається незмінним (`/devices/{id}/telemetry`), а версія передається через спеціалізований заголовок або стандарт узгодження вмісту:
- Користувацький заголовок: `X-API-Version: 2026-03-01` або `X-API-Version: 2`
- Заголовок Accept: `Accept: application/vnd.iot-system.v2+json`

**Як це працює:** Диспетчер сервера зчитує вхідні заголовки запиту й передає потік виконання контролеру відповідної версії. Якщо заголовок відсутній, запит обслуговується базовою версією за замовчуванням (Default API Version).

**Переваги:**
- Чистота та стабільність адрес ресурсів (ідеальне дотримання канонів REST).
- Можливість гнучкого датованого версіонування (англ. *Date-based API Versioning*, популяризованого сервісами Stripe і Twilio): нова версія оголошується датою релізу, а клієнт вказує дату тієї специфікації, під яку він був скомпільований.

**Недоліки:**
- Складність для простих вбудованих пристроїв: багато легких прошивок формують HTTP-запити через статичні рядкові шаблони й не вміють динамічно керувати заголовками контенту.
- Ускладнене кешування: вимагає обов'язкового додавання заголовка `Vary: X-API-Version, Accept` до всіх відповідей сервера, інакше CDN поверне старому приладу кешовану відповідь від нової версії.

#### 3. Версія в схемі корисного навантаження (Payload Schema Versioning)

Номер схеми структурується безпосередньо всередині тіла повідомлення:
```json
{
  "schema_version": 2,
  "device_id": "m_102",
  "readings": {
    "voltage_mv": 231400,
    "current_ma": 4800
  },
  "timestamp_us": 1773446400000000
}
```

**Як це працює:** Це єдиний надійний метод для транспортних протоколів без розвинених HTTP-заголовків: MQTT, CoAP, LoRaWAN, Kafka або сирих UDP-датаграм. Брокер повідомлень спрямовує всі пакети в єдиний топік телеметрії (наприклад, `devices/+/telemetry`), а обробник на сервері зчитує поле `schema_version` і передає бінарний чи JSON буфер відповідному десеріалізатору зі сховища схем (англ. *Schema Registry*).

**Порівняльна оцінка стратегій версіонування:**

| Критерій оцінки | URI Path (`/v1/...`) | Headers (`X-API-Version`) | Payload Schema (`schema_version`) |
| :--- | :--- | :--- | :--- |
| **Сумісність із протоколами** | Тільки HTTP / REST | Тільки HTTP / gRPC metadata | Усі (MQTT, CoAP, LoRaWAN, HTTP) |
| **Маршрутизація на L7 проксі** | Тривіальна (шлях URL) | Потребує аналізу заголовків | Неможлива без парсингу тіла |
| **Оверхед пам'яті на МК** | Мінімальний (статичний рядок) | Додаткові байти заголовків | 2–4 байти в тілі кадру |
| **Кешування на CDN** | Працює з коробки | Вимагає заголовка `Vary` | Не застосовується до CDN |
| **Ідеальна сфера застосування** | Кардинальні зміни REST API | Еволюція веб-сервісів і додатків | Телеметрія та події всього парку заліза |

> 🔧 **Навіщо це.** У зрілих IoT-платформах застосовують гібридний підхід: зовнішній REST API для веб-панелей та інтеграцій версіонується через **URI Path** (`/v1/`, `/v2/`), що спрощує документацію та підтримку SDK, а внутрішній обмін телеметрією через MQTT і черги використовує **Payload Schema Versioning**, захищаючи брокер від перевантаження зайвими топіками.

---

### Життєвий цикл депрекації та безпечне виведення застарілих версій

Депрекація (англ. *deprecation* — «оголошення застарілим») в Інтернеті речей — це не одномоментне видалення коду, а контрольований інженерний процес, що триває від 6 до 24 місяців. Головна мета — вивести застарілі та небезпечні алгоритми з експлуатації, не перетворивши жоден фізичний пристрій у полі на «цеглину» (англ. *bricked device*).

![Життєвий цикл депрекації: Фаза 1 Активна версія -> Фаза 2 Оголошення застарілості з заголовками Deprecation і Sunset -> Фаза 3 Вікна блекауту Brownout -> Фаза 4 Остаточне виведення з 410 Gone або L7-адаптером](/root/course/embedded/api-sluzhby/img/deprecation-sunset-lifecycle.svg)
*Чотири фази життєвого циклу депрекації API. Від активного розвитку версія переходить до оголошення застарілості за стандартом RFC 8594. Перед остаточним закриттям проводяться тестові відключення (Brownout), що виявляють непереведені пристрої до настання дати Sunset.*

#### Стандартизовані HTTP-заголовки депрекації (RFC 8594)

Коли версія оголошується застарілою, сервер зобов'язаний інформувати про це всіх клієнтів у кожній відповіді. Інженерна група IETF стандартизувала для цього спеціальні службові заголовки:

1. **Заголовок `Deprecation` (draft-ietf-httpapi-deprecation-header):** сигналізує про факт оголошення ресурсу застарілим. Може містити значення `true` або точну дату/час початку депрекації за стандартом Unix timestamp з префіксом `@`:
   ```http
   Deprecation: @1773446400
   ```
2. **Заголовок `Sunset` (RFC 8594):** визначає безумовну дату та час, коли кінцева точка буде остаточно вимкнена, видалена або переведена в режим повернення фатальної помилки:
   ```http
   Sunset: Sun, 15 Nov 2026 00:00:00 GMT
   ```
3. **Заголовок `Link` (RFC 8288):** надає машинозчитуване посилання на документацію з міграції на нову версію API:
   ```http
   Link: <https://api.iot-system.com/docs/migrations/v1-to-v2>; rel="deprecation"; type="text/html"
   ```

Повний вигляд відповіді застарілого ендпоінта:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Deprecation: @1773446400
Sunset: Sun, 15 Nov 2026 00:00:00 GMT
Link: <https://api.iot-system.com/docs/v2-migration>; rel="deprecation"

{
  "device_id": "m_102",
  "status": "online"
}
```

Автоматизовані шлюзи, інтеграційні скрипти та мобільні додатки парсять заголовок `Sunset`, автоматично генеруючи попередження в інженерні журнали та системи моніторингу задовго до того, як API припинить відповідати.

#### Телеметрія звернень та сегментація когорт

Неможливо безпечно вимкнути версію, якщо ви не знаєте поіменно кожного клієнта, який продовжує її викликати. На рівні API Gateway або проміжного програмного забезпечення (middleware) налаштовується детальний збір метрик для систем Prometheus та Grafana.

Кожен вхідний запит індексується за чотирма обов'язковими мітками:
- `api_version`: версія запитаного інтерфейсу (`v1`, `v2`).
- `endpoint`: назва кінцевої точки (`/telemetry`, `/commands`).
- `firmware_version`: версія прошивки пристрою, витягнута з заголовка `User-Agent` (наприклад, `WaterMeter/1.0.4 (STM32L476; NB-IoT)`).
- `client_type`: категорія клієнта (`device`, `mobile_app`, `enterprise_backend`).

У системі Prometheus створюється лічильник:
```prometheus
iot_api_requests_total{api_version="v1", endpoint="/telemetry", firmware="1.0.4", client_type="device"} 142050
```

Це дозволяє будувати графіки спадання трафіку старої версії й бачити точний перелік серійних номерів приладів, які зависли на старих прошивках і потребують спрямованого оновлення через [OTA-сервер](root:embedded/ota-server).

#### Практика контрольованого блекауту (Brownout Testing)

Часто навіть після офіційного оголошення Sunset 5–10% клієнтів продовжують надсилати трафік на старий ендпоінт просто тому, що розробники інтеграцій проігнорували листи з попередженнями. Якщо просто вимкнути сервіс у день дедлайну, служба підтримки захлинеться від аварійних інцидентів.

Для запобігання раптовому колапсу застосовують методику **планових навчальних відключень** (англ. *Brownout Testing*):

1. **Фаза мікровідключення (за 2 місяці до Sunset):** у час найменшої активності (наприклад, щовівторка о 03:00 ночі) старий ендпоінт штучно вимикається на **5 хвилин**. Замість успішної відповіді сервер повертає `HTTP 410 Gone` або `429 Too Many Requests` із детальним поясненням. Інженери відстежують реакцію систем моніторингу та звернення чергових служб.
2. **Фаза попереджувального відключення (за 2 тижні до Sunset):** штучне відключення подовжується до **1 години** у робочий час. Усі інтегратори, які досі не перейшли на v2, стикаються зі збоєм і змушені терміново оновити програмне забезпечення.
3. **Остаточний вихід (Sunset):** ендпоінт вимикається назавжди або переводиться на адаптер сумісності.

#### Шлюзові адаптери сумісності (Compatibility Adapters)

Що робити, коли в полі залишилося 2 000 старих датчиків першого покоління, які апаратно не мають достатньо пам'яті для підтримки нового криптографічного протоколу v2 або функціоналу OTA?

Замість збереження всього застарілого бекенд-стека на рівні L7 API Gateway розгортається легкий **транслюючий адаптер** (англ. *Compatibility Adapter / Transpiler*). Адаптер перехоплює вхідний запит старого формату v1, на льоту розгортає застарілі скорочені поля у нову повнорозмірну модель даних v2, передає запит сучасному мікросервісу, а повернуту відповідь v2 згортає назад у формат v1. Старе залізо продовжує функціонувати роками, а основна кодова база сервера залишається чистою від легасі-коду.

---

### Реалізація API-маршрутизатора з версіонуванням та депрекацією

Розгляньмо повну реалізацію виробничого API-маршрутизатора, що підтримує:
1. Автоматичний вибір версії з префікса URL або заголовка `X-API-Version`.
2. Автоматичну інжекцію заголовків `Deprecation`, `Sunset` та `Link` для застарілих версій.
3. Облік метрик звернень для моніторингу застарілих клієнтів.
4. Асинхронну модель створення команд із генерацією статусу `202 Accepted` та заголовка `Location`.

:::tabs
```py
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI(title="IoT Service API Gateway")

# Конфігурація життєвого циклу версій API
@dataclass
class VersionMeta:
    deprecated: bool
    sunset_date: Optional[str] = None  # HTTP-date формат RFC 8594
    migration_url: Optional[str] = None

VERSION_REGISTRY: Dict[str, VersionMeta] = {
    "v1": VersionMeta(
        deprecated=True,
        sunset_date="Sun, 15 Nov 2026 00:00:00 GMT",
        migration_url="https://api.iot-corp.com/docs/v1-to-v2"
    ),
    "v2": VersionMeta(
        deprecated=False
    )
}

# Внутрішнє сховище метрик звернень за версіями та пристроями
metrics_request_counter: Dict[str, int] = {}

@app.middleware("http")
async def versioning_and_deprecation_middleware(request: Request, call_next):
    path = request.url.path
    api_version = None

    # 1. Визначення версії: спочатку з URL, якщо немає — із заголовка
    if path.startswith("/v1/"):
        api_version = "v1"
    elif path.startswith("/v2/"):
        api_version = "v2"
    else:
        api_version = request.headers.get("X-API-Version", "v2")

    # Збір метрики звернення
    user_agent = request.headers.get("User-Agent", "Unknown-Device")
    metric_key = f"{api_version}:{request.method}:{path}:{user_agent}"
    metrics_request_counter[metric_key] = metrics_request_counter.get(metric_key, 0) + 1

    # Виконання запиту обробником
    response: Response = await call_next(request)

    # 2. Інжекція стандартних заголовків депрекації за стандартом RFC 8594
    v_meta = VERSION_REGISTRY.get(api_version)
    if v_meta and v_meta.deprecated:
        response.headers["Deprecation"] = "true"
        if v_meta.sunset_date:
            response.headers["Sunset"] = v_meta.sunset_date
        if v_meta.migration_url:
            response.headers["Link"] = f'<{v_meta.migration_url}>; rel="deprecation"; type="text/html"'

    return response

# База даних стану пристроїв та черги команд (імітація)
device_storage: Dict[str, Dict[str, Any]] = {
    "dev-101": {"id": "dev-101", "type": "energy_meter", "firmware": "1.0.4", "status": "online"}
}
command_queue: Dict[str, Dict[str, Any]] = {}

# v1 Телеметрія (Застарілий контракт зі скороченими полями)
@app.get("/v1/devices/{device_id}/telemetry")
async def get_telemetry_v1(device_id: str):
    if device_id not in device_storage:
        raise HTTPException(status_code=404, detail="Device not found")
    # v1 формат: скорочені імена
    return {"id": device_id, "v": 230.2, "a": 5.1, "ts": int(time.time())}

# v2 Телеметрія (Сучасний стандартизований контракт)
@app.get("/v2/devices/{device_id}/telemetry")
async def get_telemetry_v2(device_id: str):
    if device_id not in device_storage:
        raise HTTPException(status_code=404, detail="Device not found")
    # v2 формат: точні інженерні одиниці в мілівольтах та міліамперах
    return {
        "device_id": device_id,
        "metrics": {
            "voltage_mv": 230200,
            "current_ma": 5100
        },
        "timestamp_iso": datetime.now(timezone.utc).isoformat()
    }

# Асинхронне створення команди (єдине для v1 та v2)
@app.post("/v2/devices/{device_id}/commands", status_code=status.HTTP_202_ACCEPTED)
async def create_command(device_id: str, payload: Dict[str, Any], response: Response):
    if device_id not in device_storage:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd_id = f"cmd_{int(time.time() * 1000)}"
    command_record = {
        "id": cmd_id,
        "device_id": device_id,
        "action": payload.get("action", "NOOP"),
        "params": payload.get("params", {}),
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    command_queue[cmd_id] = command_record

    # Встановлення обов'язкового заголовка Location на створений ресурс
    location_url = f"/v2/devices/{device_id}/commands/{cmd_id}"
    response.headers["Location"] = location_url
    return command_record

# Опитування статусу команди
@app.get("/v2/devices/{device_id}/commands/{cmd_id}")
async def get_command_status(device_id: str, cmd_id: str):
    cmd = command_queue.get(cmd_id)
    if not cmd or cmd["device_id"] != device_id:
        raise HTTPException(status_code=404, detail="Command not found")
    return cmd
```
```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"
)

// VersionMeta описує стан депрекації версії API
type VersionMeta struct {
	Deprecated   bool
	SunsetDate   string
	MigrationURL string
}

var versionRegistry = map[string]VersionMeta{
	"v1": {
		Deprecated:   true,
		SunsetDate:   "Sun, 15 Nov 2026 00:00:00 GMT",
		MigrationURL: "https://api.iot-corp.com/docs/v1-to-v2",
	},
	"v2": {
		Deprecated: false,
	},
}

// MetricsStorage потокобезпечно збирає виклики старих версій
type MetricsStorage struct {
	mu     sync.Mutex
	counts map[string]int64
}

var metrics = &MetricsStorage{counts: make(map[string]int64)}

func (m *MetricsStorage) Inc(key string) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.counts[key]++
}

// DeprecationMiddleware впроваджує заголовки RFC 8594 та збирає телеметрію
func DeprecationMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		apiVersion := "v2"
		if strings.HasPrefix(r.URL.Path, "/v1/") {
			apiVersion = "v1"
		} else if strings.HasPrefix(r.URL.Path, "/v2/") {
			apiVersion = "v2"
		} else if v := r.Header.Get("X-API-Version"); v != "" {
			apiVersion = v
		}

		// Фіксація метрики звернення
		ua := r.UserAgent()
		if ua == "" {
			ua = "unknown-device"
		}
		metrics.Inc(fmt.Sprintf("%s:%s:%s", apiVersion, r.Method, ua))

		// Додавання заголовків депрекації
		if meta, exists := versionRegistry[apiVersion]; exists && meta.Deprecated {
			w.Header().Set("Deprecation", "true")
			if meta.SunsetDate != "" {
				w.Header().Set("Sunset", meta.SunsetDate)
			}
			if meta.MigrationURL != "" {
				w.Header().Set("Link", fmt.Sprintf("<%s>; rel=\"deprecation\"; type=\"text/html\"", meta.MigrationURL))
			}
		}

		next.ServeHTTP(w, r)
	})
}

// Обробник v1 телеметрії
func handleTelemetryV1(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := map[string]interface{}{
		"id": "dev-101",
		"v":  230.2,
		"a":  5.1,
		"ts": time.Now().Unix(),
	}
	json.NewEncoder(w).Encode(resp)
}

// Обробник v2 телеметрії
func handleTelemetryV2(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := map[string]interface{}{
		"device_id": "dev-101",
		"metrics": map[string]int{
			"voltage_mv": 230200,
			"current_ma": 5100,
		},
		"timestamp_iso": time.Now().UTC().Format(time.RFC3339),
	}
	json.NewEncoder(w).Encode(resp)
}

// Обробник асинхронного створення команд
func handleCreateCommandV2(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	cmdID := fmt.Sprintf("cmd_%d", time.Now().UnixNano()/1e6)
	location := fmt.Sprintf("/v2/devices/dev-101/commands/%s", cmdID)

	w.Header().Set("Location", location)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted) // 202 Accepted

	resp := map[string]interface{}{
		"id":         cmdID,
		"device_id":  "dev-101",
		"status":     "PENDING",
		"created_at": time.Now().UTC().Format(time.RFC3339),
	}
	json.NewEncoder(w).Encode(resp)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/v1/devices/dev-101/telemetry", handleTelemetryV1)
	mux.HandleFunc("/v2/devices/dev-101/telemetry", handleTelemetryV2)
	mux.HandleFunc("/v2/devices/dev-101/commands", handleCreateCommandV2)

	server := &http.Server{
		Addr:         ":8080",
		Handler:      DeprecationMiddleware(mux),
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	log.Println("IoT API Gateway запущено на порту :8080")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Помилка сервера: %v", err)
	}
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <format>
#include <optional>

// Метадані депрекації версії API
struct VersionConfig {
    bool deprecated{false};
    std::string sunset_http_date;
    std::string migration_guide_url;
};

// HTTP відповідь
struct HttpResponse {
    int status_code{200};
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

// HTTP запит
struct HttpRequest {
    std::string method;
    std::string path;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

// Високопродуктивний маршрутизатор API з підтримкою життєвого циклу версій
class ApiRouter {
public:
    ApiRouter() {
        // Реєстрація політик версіонування
        versions_["v1"] = VersionConfig{
            .deprecated = true,
            .sunset_http_date = "Sun, 15 Nov 2026 00:00:00 GMT",
            .migration_guide_url = "https://api.iot-corp.com/docs/v1-to-v2"
        };
        versions_["v2"] = VersionConfig{
            .deprecated = false,
            .sunset_http_date = "",
            .migration_guide_url = ""
        };
    }

    HttpResponse dispatch(const HttpRequest& req) {
        std::string_view version = extract_version(req);
        HttpResponse resp;

        // Збір аналітики викликів
        record_metric(version, req.method, req.path);

        // Маршрутизація за шляхами
        if (req.path == "/v1/devices/dev-101/telemetry" && req.method == "GET") {
            resp.status_code = 200;
            resp.body = R"({"id":"dev-101","v":230.2,"a":5.1,"ts":1773446400})";
            resp.headers["Content-Type"] = "application/json";
        } else if (req.path == "/v2/devices/dev-101/telemetry" && req.method == "GET") {
            resp.status_code = 200;
            resp.body = R"({"device_id":"dev-101","metrics":{"voltage_mv":230200,"current_ma":5100},"ts_us":1773446400000000})";
            resp.headers["Content-Type"] = "application/json";
        } else if (req.path == "/v2/devices/dev-101/commands" && req.method == "POST") {
            // Асинхронний прийом команди: повертаємо 202 Accepted
            resp.status_code = 202;
            std::string cmd_id = "cmd_98214";
            resp.headers["Location"] = "/v2/devices/dev-101/commands/" + cmd_id;
            resp.headers["Content-Type"] = "application/json";
            resp.body = R"({"id":")" + cmd_id + R"(","status":"PENDING","device_id":"dev-101"})";
        } else {
            resp.status_code = 404;
            resp.body = R"({"error":"Endpoint not found"})";
            resp.headers["Content-Type"] = "application/json";
        }

        // Інжекція заголовків депрекації за стандартом RFC 8594
        auto it = versions_.find(std::string(version));
        if (it != versions_.end() && it->second.deprecated) {
            resp.headers["Deprecation"] = "true";
            if (!it->second.sunset_http_date.empty()) {
                resp.headers["Sunset"] = it->second.sunset_http_date;
            }
            if (!it->second.migration_guide_url.empty()) {
                resp.headers["Link"] = "<" + it->second.migration_guide_url + ">; rel=\"deprecation\"; type=\"text/html\"";
            }
        }

        return resp;
    }

private:
    std::unordered_map<std::string, VersionConfig> versions_;
    std::unordered_map<std::string, uint64_t> metrics_counter_;

    std::string_view extract_version(const HttpRequest& req) const {
        if (req.path.starts_with("/v1/")) return "v1";
        if (req.path.starts_with("/v2/")) return "v2";
        auto it = req.headers.find("X-API-Version");
        if (it != req.headers.end()) return it->second;
        return "v2"; // Версія за замовчуванням
    }

    void record_metric(std::string_view version, std::string_view method, std::string_view path) {
        std::string key = std::string(version) + ":" + std::string(method) + ":" + std::string(path);
        metrics_counter_[key]++;
    }
};
```
:::

Кожна реалізація гарантує виконання трьох інваріантів:
1. Жоден застарілий виклик не залишається без стандартизованого попередження `Sunset`.
2. Жодна виконавча дія над фізичним пристроєм не блокує HTTP-потік сервера — відповідь `202 Accepted` віддається за лічені мікросекунди.
3. Усі звернення фіксуються в лічильниках моніторингу для контролю графіка міграції парку приладів.

---

### Інженерний чекліст: шість правил надійного API служби

Підсумуймо закономірності проєктування серверних інтерфейсів для вбудованих систем:

1. **Ніколи не блокуйте HTTP на фізичну дію.** Виконання дій на залізі завжди асинхронне. Кінцева точка команди зобов'язана негайно повертати `HTTP 202 Accepted` із заголовком `Location` на створене завдання.
2. **Вимагайте ключ ідемпотентності на всі мутуючі операції.** Заголовок `Idempotency-Key` у комбінації з унікальним `cmd_id` запобігає катастрофічним повторним спрацьовуванням реле чи клапанів під час збоїв та ретраїв мобільної мережі.
3. **Відокремлюйте REST від черг подій.** Використовуйте версіонування в URL (`/v1/`, `/v2/`) для зовнішніх клієнтів і версіонування в схемі корисного навантаження (`schema_version`) для потоку телеметрії по MQTT та CoAP.
4. **Не робіть мовчазних депрекацій.** Кожен застарілий ендпоінт повинен супроводжуватися заголовками `Deprecation`, `Sunset` (RFC 8594) та посиланням на інструкцію з міграції.
5. **Тестуйте блекаути до настання дедлайну.** Проводьте контрольовані 5-хвилинні та 1-годинні вікна вимкнення (Brownout testing) за кілька тижнів до вимкнення старого API, щоб змусити сторонніх інтеграторів оновити свої шлюзи.
6. **Захищайте «вічні» пристрої адаптерами.** Якщо фізичні прилади на об'єктах неможливо перепрошити, реалізуйте трансляцію схем v1→v2 на рівні L7-шлюзу, зберігаючи базові сервіси чистими від застарілого коду.
