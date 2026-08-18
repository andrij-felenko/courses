# 📋 Socket API для SCTP: виклики, структури, мультихоумінг та події

Розширення інтерфейсу Berkeley sockets для протоколу SCTP (*Stream Control Transmission Protocol*, RFC 6458, заголовок `netinet/sctp.h`, системна бібліотека `libsctp`) надають прикладним програмам засоби прямого керування мультистрімінгом, динамічної конфігурації мультихоумінгу, підписки на асинхронні події ядра, налаштування таймерів надійної доставки операторського класу та ввімкнення розширень протоколу (PR-SCTP, динамічна реконфігурація адрес ASCONF, скидання потоків).

---

## 1. Дві моделі сокетів: один-до-одного та один-до-багатьох

Специфікація RFC 6458 стандартизує дві різні парадигми взаємодії прикладного коду зі стеком SCTP у ядрі операційної системи (зокрема реалізації Linux Kernel SCTP — `lksctp`):

| Характеристика | Стиль «Один-до-одного» (*One-to-One*) | Стиль «Один-до-багатьох» (*One-to-Many*) |
| :--- | :--- | :--- |
| **Тип сокета** | `SOCK_STREAM` | `SOCK_SEQPACKET` |
| **Протокол** | `IPPROTO_SCTP` | `IPPROTO_SCTP` |
| **Семантика** | Аналогічна TCP (один дескриптор = одна асоціація) | Аналогічна UDP (один дескриптор = множина асоціацій) |
| **Встановлення зв'язку** | Явний виклик `listen()` та `accept()` на сервері, `connect()` на клієнті | Неявне відкриття при першому виклику `sctp_sendmsg()` або явне через `sctp_connectx()` |
| **Ідентифікація піра** | За файловим дескриптором сокета (`int fd`) | За 32-бітним ідентифікатором асоціації (`sctp_assoc_t assoc_id`) |
| **Керування пам'яттю** | Окремі черги та буфери ядра на кожне з'єднання | Спільний буфер сокета для всіх активних асоціацій |
| **Сфера застосування** | Портування наявних служб TCP; високоінтенсивні сесії | Сервери сигналізації (SIGTRAN, Diameter, MME), робота з тисячами клієнтів в одному потоці |

Для стилю «Один-до-одного» програма використовує стандартний життєвий цикл з'єднання: сокет створюється з типом `SOCK_STREAM`, прив'язується до локальних адрес і переводиться в режим очікування викликом `listen()`. Кожен новий клієнт виділяється в окремий файловий дескриптор через `accept()`.

Для стилю «Один-до-багатьох» сокет створюється з типом `SOCK_SEQPACKET`. Серверний процес викликає `listen()`, але ніколи не викликає `accept()`. Усі вхідні повідомлення від сотень різних клієнтів зчитуються через єдиний дескриптор, а розрізнення відправників здійснюється за полем `sinfo_assoc_id` у метаданих `struct sctp_sndrcvinfo`.

---

## 2. Керування адресами та мультихоумінгом

У традиційних протоколах TCP і UDP сокет прив'язується системним викликом `bind()` виключно до однієї конкретної IP-адреси або до універсального шаблону `INADDR_ANY`. Для реалізації мультихоумінгу в SCTP стандартизовано функції множинної прив'язки та динамічної модифікації списку мережевих інтерфейсів кінцевої точки.

### Системний виклик `sctp_bindx()`

Дозволяє зв'язати сокет із довільним переліком локальних IP-адрес хоста (IPv4 або IPv6), а також додавати чи вилучати окремі адреси під час функціонування програми:

```c
int sctp_bindx(int sd, struct sockaddr *addrs, int addrcnt, int flags);
```

#### Параметри та режими роботи

- **`sd`**: Дескриптор відкритого сокета SCTP.
- **`addrs`**: Вказівник на запакований масив структур адрес (`struct sockaddr_in` для IPv4 або `struct sockaddr_in6` для IPv6), розташованих у безперервному блоці пам'яті одна за одною.
- **`addrcnt`**: Загальна кількість адрес у переданому масиві.
- **`flags`**: Прапорець керування модифікацією:
  - `SCTP_BINDX_ADD_ADDR`: Додати вказані IP-адреси до списку локальних інтерфейсів кінцевої точки. Якщо асоціація вже перебуває в робочому стані й обидва хости підтримують розширення динамічної реконфігурації адрес ASCONF (RFC 5061), ядро автоматично формує та надсилає віддаленому піру чанк `ASCONF` із параметром додавання IP-адреси.
  - `SCTP_BINDX_REM_ADDR`: Вилучити вказані IP-адреси з локального списку. Якщо асоціація активна, ядро сповіщає піра чанком видалення адреси. Спроба видалити останню залишкову адресу сокета завершується помилкою.

#### Коди помилок та діагностика

У разі успішного виконання функція повертає `0`. При помилці повертається `-1`, а системна змінна `errno` встановлюється в одне зі значень:
- `EBADF`: Дескриптор `sd` не є дійсним відкритим файлом.
- `ENOTSOCK`: Дескриптор не вказує на мережевий сокет.
- `EADDRINUSE`: Одна із зазначених адрес або порт уже зайняті іншим сокетом операційної системи.
- `EINVAL`: Неприпустимі прапорці операції, значення `addrcnt <= 0`, або спроба вилучення єдиної активної адреси.
- `EFAULT`: Вказівник `addrs` веде на недоступний адресний простір пам'яті процесу.

---

### Системний виклик `sctp_connectx()`

Ініціює чотириетапне рукостискання з віддаленим сервером, одразу передаючи ядру весь перелік відомих IP-адрес призначення для побудови основного та резервних маршрутів:

```c
int sctp_connectx(int sd, struct sockaddr *addrs, int addrcnt, sctp_assoc_t *assoc_id);
```

Стек протоколу надсилає перший пакет `INIT` на початкову адресу масиву `addrs[0]`. Якщо віддалений вузол не відповідає протягом початкового інтервалу таймауту повторної передачі (`RTO.Initial`), ядро не розриває спробу з'єднання, а автоматично перенаправляє наступний `INIT` на адресу `addrs[1]`, забезпечуючи стійкість навіть на етапі ініціалізації сеансу.

Якщо аргумент `assoc_id` не дорівнює `NULL`, ядро записує туди сформований числовий ідентифікатор асоціації. Це критично для сокетів `SOCK_SEQPACKET`, де один дескриптор використовується для паралельного зв'язку з сотнями вузлів.

---

### Інспекція активних адрес асоціації

Для діагностики поточного стану зв'язку бібліотека `libsctp` надає функції опитування адрес віддаленого партнера та локальних інтерфейсів:

```c
int sctp_getpaddrs(int sd, sctp_assoc_t id, struct sockaddr **addrs);
void sctp_freepaddrs(struct sockaddr *addrs);

int sctp_getladdrs(int sd, sctp_assoc_t id, struct sockaddr **addrs);
void sctp_freeladdrs(struct sockaddr *addrs);
```

- `sctp_getpaddrs()`: Запитує в ядра список усіх дійсних адрес віддаленого піра (*Peer Addresses*) для асоціації `id`. Функція динамічно виділяє пам'ять під масив структур адрес і повертає їхню кількість. Очищення пам'яті здійснюється викликом `sctp_freepaddrs()`.
- `sctp_getladdrs()`: Повертає список локальних адрес (*Local Addresses*), що обслуговують цю асоціацію. Звільнення буфера пам'яті виконується викликом `sctp_freeladdrs()`.

---

## 3. Передача та отримання повідомлень з мультистрімінгом

Оскільки SCTP оперує дискретними записами (повідомленнями), класичні системні виклики `send()` та `recv()` не мають аргументів для вибору номера потоку чи передачі ідентифікатора протоколу PPID. Специфікація RFC 6458 вводить розширені функції `sctp_sendmsg()` та `sctp_recvmsg()`, а також уніфікований векторизований інтерфейс `sctp_sendv()` та `sctp_recvv()`.

### Системний виклик `sctp_sendmsg()`

```c
ssize_t sctp_sendmsg(int sd, const void *msg, size_t len,
                     struct sockaddr *to, socklen_t tolen,
                     uint32_t ppid, uint32_t flags,
                     uint16_t stream_no, uint32_t timetolive,
                     uint32_t context);
```

#### Опис параметрів виклику

- **`msg`**, **`len`**: Вказівник на буфер корисного навантаження повідомлення та його точний розмір у байтах.
- **`to`**, **`tolen`**: Цільова адреса віддаленого вузла. Для підключених сокетів `SOCK_STREAM` передаються `NULL` та `0`. Для непідключених сокетів `SOCK_SEQPACKET` ця адреса визначає цільову асоціацію; якщо асоціація ще не відкрита, ядро автоматично запускає рукостискання й буферизує повідомлення для відправки в першому `COOKIE ECHO` або одразу після `COOKIE ACK`.
- **`ppid`** (*Payload Protocol Identifier*): 32-бітний беззнаковий ідентифікатор типу корисного навантаження, що записується безпосередньо в заголовок кожного чанка `DATA`. На відміну від TCP, де тип вмісту мусить розбиратися на прикладному рівні, SCTP дозволяє комутаторам і брандмауерам фільтрувати та маршрутизувати пакети за цим полем (наприклад, `0x00000003` — M3UA, `0x0000003C` — S1AP у 4G LTE, `0x0000003C` — NGAP у 5G, `0x00000035` — WebRTC DataChannel Binary). Значення передається в мережевому порядку байтів (`htonl()`).
- **`flags`**: Бітова маска спеціальних режимів передачі:
  - `0`: Звичайна надійна впорядкована передача (*Ordered Delivery*).
  - `SCTP_UNORDERED`: Невпорядкована передача (встановлює біт `U=1` у чанку DATA). Повідомлення не отримує порядкового номера `SSN` і доставляється приймальному застосунку миттєво, без очікування попередніх пропущених пакетів потоку.
  - `SCTP_ADDR_OVER`: Примусово надіслати повідомлення на IP-адресу, зазначену в аргументі `to`, ігноруючи поточний вибір основного маршруту (*Primary Path*).
  - `SCTP_ABORT`: Надіслати чанк `ABORT` для негайного аварійного розриву асоціації зі скиданням черг.
  - `SCTP_EOF`: Ініціювати плавне штатно закриття асоціації (*Graceful Shutdown*) після успішної передачі даних цього повідомлення.
- **`stream_no`**: 16-бітний числовий ідентифікатор вихідного потоку (*Stream ID*), у який поміщається повідомлення. Номер має лежати в діапазоні від `0` до `outbound_streams - 1`.
- **`timetolive`**: Час життя повідомлення в мілісекундах. Використовується розширенням часткової надійності PR-SCTP (RFC 3758). Якщо повідомлення затримується у черзі передачі довше зазначеного інтервалу, ядро анулює його передачу та надсилає піру чанк сповіщення `FORWARD TSN`. Значення `0` вимикає таймер (гарантована надійна доставка).
- **`context`**: Довільне 32-бітне число користувача. Якщо повідомлення буде відкинуто через перевищення часу життя чи розрив каналу, ядро поверне це значення в структурі сповіщення `sctp_send_failed` для точної ідентифікації недоставленої команди.

---

### Системний виклик `sctp_recvmsg()`

```c
ssize_t sctp_recvmsg(int sd, void *msg, size_t len,
                     struct sockaddr *from, socklen_t *fromlen,
                     struct sctp_sndrcvinfo *sinfo, int *msg_flags);
```

#### Структура супровідних метаданих `struct sctp_sndrcvinfo`

Якщо на сокеті активовано подію `sctp_data_io_event`, ядро записує в структуру `sinfo` вичерпні атрибути прийнятого пакета:

```c
struct sctp_sndrcvinfo {
    uint16_t     sinfo_stream;     /* Номер потоку, з якого надійшло повідомлення */
    uint16_t     sinfo_ssn;        /* Номер послідовності всередині потоку (SSN) */
    uint16_t     sinfo_flags;      /* Прапорці чанка (SCTP_UNORDERED тощо) */
    uint32_t     sinfo_ppid;       /* Ідентифікатор прикладного протоколу (PPID) */
    uint32_t     sinfo_context;    /* Контекст відправника */
    uint32_t     sinfo_timetolive; /* Залишковий час життя */
    uint32_t     sinfo_tsn;        /* Глобальний порядковий номер передачі (TSN) */
    uint32_t     sinfo_cumtsn;     /* Поточний накопичувальний TSN підтвердження */
    sctp_assoc_t sinfo_assoc_id;   /* Числовий дескриптор асоціації */
};
```

#### Значення вихідного прапорця `msg_flags`

- `MSG_EOR` (*End of Record*): Повідомлення зчитано з черги ядра повністю. Якщо буфер `msg` був замалий для великого фрагментованого повідомлення, виклик повертає стільки байтів, скільки помістилося, а прапорець `MSG_EOR` залишається скинутим. Застосунок продовжує викликати `sctp_recvmsg()` до появи `MSG_EOR`.
- `MSG_NOTIFICATION`: Прочитані байти є не даними користувача, а системним повідомленням ядра про зміну стану сокета чи мережевих маршрутів (`union sctp_notification`).

---

### Векторизований інтерфейс: `sctp_sendv()` та `sctp_recvv()`

Специфікація RFC 6458 вводить системні виклики нового покоління, що дозволяють надсилати дані з кількох несуміжних буферів пам'яті (векторний ввід-вивід *scatter-gather*):

```c
ssize_t sctp_sendv(int sd, const struct iovec *iov, int iovcnt,
                   struct sockaddr *addrs, int addrcnt,
                   void *info, socklen_t infolen,
                   unsigned int infotype, int flags);

ssize_t sctp_recvv(int sd, const struct iovec *iov, int iovcnt,
                   struct sockaddr *from, socklen_t *fromlen,
                   void *info, socklen_t *infolen,
                   unsigned int *infotype, int *flags);
```

Замість окремих скалярних аргументів виклик `sctp_sendv()` приймає структуру `struct sctp_sendv_spa` (*Send Parameters Array*), яка в одному системному виклику об'єднує метадані потоку (`sctp_sndinfo`), параметри часткової надійності (`sctp_prinfo`) та ключі автентифікації (`sctp_authinfo`).

---

## 4. Опції сокета та тонке налаштування параметрів

Керування внутрішніми алгоритмами передачі здійснюється стандартними системними викликами `setsockopt()` та `getsockopt()` з рівнем протоколу `IPPROTO_SCTP`:

```c
int setsockopt(int sd, IPPROTO_SCTP, int optname, const void *optval, socklen_t optlen);
int getsockopt(int sd, IPPROTO_SCTP, int optname, void *optval, socklen_t *optlen);
```

### Основні структури конфігурації опцій

#### 1. `SCTP_INITMSG`: Узгодження ємності потоків та параметрів INIT

Викликається перед переведенням сокета в режим прослуховування (`listen()`) або активного підключення (`connect()`):

```c
struct sctp_initmsg {
    uint16_t sinit_num_ostreams;   /* Бажана кількість вихідних потоків (Outbound) */
    uint16_t sinit_max_instreams;  /* Максимум дозволених вхідних потоків (Inbound) */
    uint16_t sinit_max_attempts;   /* Кількість повторних відправок INIT до помилки */
    uint16_t sinit_max_init_timeo; /* Максимальний таймаут RTO для фази INIT (мс) */
};
```

#### 2. `SCTP_RTOINFO`: Межі таймера повторної передачі

Дозволяє перевизначити параметри обчислення RTO для всієї асоціації або для окремого дескриптора:

```c
struct sctp_rtoinfo {
    sctp_assoc_t srto_assoc_id;
    uint32_t     srto_initial;  /* Початковий RTO (типово 3000 мс) */
    uint32_t     srto_max;      /* Верхня межа RTO (типово 60000 мс) */
    uint32_t     srto_min;      /* Нижня межа RTO (типово 1000 мс) */
};
```

#### 3. `SCTP_PEER_ADDR_PARAMS`: Моніторинг працездатності шляхів (Heartbeat)

Конфігурує параметри фонового зондування та пороги фіксації збоїв для конкретної віддаленої IP-адреси:

```c
struct sctp_paddrparams {
    sctp_assoc_t            spp_assoc_id;
    struct sockaddr_storage spp_address;    /* Конкретна IP-адреса або 0 для всіх адрес */
    uint32_t                spp_hbinterval; /* Інтервал HEARTBEAT (мс), 0 = вимкнути */
    uint16_t                spp_pathmaxrxt; /* Максимум помилок до статусу INACTIVE */
    uint32_t                spp_pathmtu;    /* Фіксований PMTU або 0 для PMTU Discovery */
    uint32_t                spp_flags;      /* SPP_HB_ENABLE, SPP_HB_DISABLE, SPP_PMTUD_ENABLE */
};
```

#### 4. `SCTP_PRIMARY_ADDR`: Явне призначення основного шляху

Вказує стеку протоколу віддалену IP-адресу, яка повинна мати найвищий пріоритет для надсилання нових чанків `DATA`:

```c
struct sctp_setprim {
    sctp_assoc_t            ssp_assoc_id;
    struct sockaddr_storage ssp_addr;
};
```

#### 5. `SCTP_NODELAY`: Вимкнення алгоритму Наґла

Прапорець `int on = 1` вимикає буферизацію малих чанків у ядрі, змушуючи стек негайно відправляти пакет при виклику `sctp_sendmsg()`. Це критично для систем сигналізації реального часу з мінімальною затримкою.

#### 6. `SCTP_EVENTS`: Підписка на події ядра

За замовчуванням більшість внутрішніх повідомлень ядра прихована від прикладного процесу. Програма активує доставку необхідних сповіщень у потік читання через структуру `sctp_event_subscribe`:

```c
struct sctp_event_subscribe {
    uint8_t sctp_data_io_event;          /* Заповнювати sctp_sndrcvinfo при читанні */
    uint8_t sctp_association_event;      /* Сповіщення про відкриття/закриття асоціації */
    uint8_t sctp_address_event;          /* Зміна працездатності IP-адрес піра */
    uint8_t sctp_send_failure_event;     /* Сповіщення про неможливість доставки повідомлення */
    uint8_t sctp_peer_error_event;       /* Отримано чанк ERROR від піра */
    uint8_t sctp_shutdown_event;         /* Пір ініціював процедуру SHUTDOWN */
    uint8_t sctp_partial_delivery_event; /* Переривання часткової доставки */
    uint8_t sctp_adaptation_layer_event; /* Сповіщення про рівень адаптації */
};
```

---

## 5. Обробка системних сповіщень (`sctp_notification`)

Коли функція `sctp_recvmsg()` повертає дані з встановленим прапорцем `MSG_NOTIFICATION`, прийнятий буфер містить структуру об'єднання `union sctp_notification`:

```c
union sctp_notification {
    struct {
        uint16_t sn_type;   /* Тип сповіщення (SCTP_ASSOC_CHANGE, SCTP_PEER_ADDR_CHANGE) */
        uint16_t sn_flags;
        uint32_t sn_length;
    } sn_header;
    struct sctp_assoc_change   sn_assoc_change;
    struct sctp_paddr_change   sn_paddr_change;
    struct sctp_send_failed    sn_send_failed;
    struct sctp_remote_error   sn_remote_error;
    struct sctp_shutdown_event sn_shutdown_event;
};
```

### Події асоціації (`struct sctp_assoc_change`)

Поле `sac_state` відображає життєвий цикл сеансу зв'язку:
- `SCTP_COMM_UP`: Асоціацію успішно встановлено (після 4-way handshake). Поля `sac_outbound_streams` та `sac_inbound_streams` містять узгоджену кількість вихідних і вхідних потоків.
- `SCTP_COMM_LOST`: Асоціацію аварійно розірвано через перевищення ліміту повторів `Association.Max.Retrans` або отримання чанка `ABORT`.
- `SCTP_RESTART`: Віддалений пір перезавантажився під час відкритої сесії та успішно повторив рукостискання з новим початковим TSN.
- `SCTP_SHUTDOWN_COMP`: Асоціацію штатно закрито.
- `SCTP_CANT_STR_ASSOC`: Не вдалося встановити асоціацію у відповідь на вихідний `INIT`.

### Події адреси піра (`struct sctp_paddr_change`)

Поле `spc_state` сповіщає про стан фізичних інтерфейсів віддаленого вузла:
- `SCTP_ADDR_AVAILABLE`: Адреса активна і штатно відповідає на запити зондування `HEARTBEAT`.
- `SCTP_ADDR_UNREACHABLE`: Адреса не відповіла на `Path.Max.Retrans` повторів поспіль і переведена в стан `INACTIVE`. Стек SCTP автоматично перенаправив трафік на альтернативну адресу.
- `SCTP_ADDR_REMOVED`: Віддалений хост надіслав чанк ASCONF про видалення цієї IP-адреси.
- `SCTP_ADDR_ADDED`: До асоціації динамічно додано нову IP-адресу піра.
- `SCTP_ADDR_MADE_PRIM`: Вказана адреса стала новим основним маршрутом (*Primary Path*).

---

## 6. Розширення протоколу: часткова надійність (PR-SCTP) та скидання потоків

Крім базових можливостей RFC 4960, сучасні стеки SCTP надають спеціалізовані розширення для мультимедіа та керування сесіями.

### Часткова надійність (PR-SCTP, RFC 3758)

Розширення PR-SCTP дозволяє відправнику відмовитися від повторної передачі застарілих повідомлень. Замість нескінченних спроб доставки стек надсилає піру чанк `FORWARD TSN`, повідомляючи отримувача про пропуск певного діапазону номерів `TSN` та переміщення вікна прийому вперед без зупинки черги.

У Socket API підтримуються три політики часткової надійності:
1. `SCTP_PR_SCTP_TTL` (Часова політика): повідомлення відкидається, якщо воно не було успішно надіслане за вказану кількість мілісекунд.
2. `SCTP_PR_SCTP_BUF` (Буферна політика): найстаріші повідомлення у черзі відкидаються, якщо сумарний обсяг черги передачі перевищує встановлений ліміт байтів.
3. `SCTP_PR_SCTP_RTX` (Ліміт спроб): повідомлення анулюється, якщо кількість повторних передач перевищила заданий лічильник.

Для моніторингу відкинутих пакетів використовується опція сокета `SCTP_PR_ASSOC_STATUS`:

```c
struct sctp_prstatus {
    sctp_assoc_t sprstat_assoc_id;
    uint16_t     sprstat_policy;       /* Політика PR-SCTP */
    uint64_t     sprstat_abandoned_unsent; /* Відкинуто до першої відправки */
    uint64_t     sprstat_abandoned_sent;   /* Відкинуто під час повторних спроб */
};
```

---

### Скидання номерів послідовності потоків (RFC 6525)

У тривалих сесіях (наприклад, постійних сигнальних лінках між комутаторами) виникає потреба переініціалізувати окремий потік, скинувши його лічильник `SSN` у нуль без розриву всієї асоціації. Для цього застосунок надсилає запит через опцію `SCTP_RESET_STREAMS`:

```c
struct sctp_reset_streams {
    sctp_assoc_t srs_assoc_id;
    uint16_t     srs_flags;        /* SCTP_STREAM_RESET_INCOMING / SCTP_STREAM_RESET_OUTGOING */
    uint16_t     srs_number_streams;
    uint16_t     srs_stream_list[]; /* Масив номерів потоків для скидання */
};
```

---

## 7. Неблокуючий ввід-вивід та мультиплексування з `epoll`

При побудові високопродуктивних серверів сокет SCTP переводиться в неблокуючий режим викликом `fcntl(sd, F_SETFL, O_NONBLOCK)`. Оскільки SCTP орієнтований на повідомлення, взаємодія з системним мультиплексором `epoll` має специфічні особливості:

1. **Обробка часткового читання:** Якщо буфер користувача в `sctp_recvmsg()` менший за розмір надісланого повідомлення, виклик повертає частину байтів без прапорця `MSG_EOR`. Дескриптор залишається готовим до читання в `epoll`, і наступний виклик `sctp_recvmsg()` повертає залишок запису з тим самим номером `sinfo_ssn`.
2. **Поведінка `EAGAIN` / `EWOULDBLOCK`:** При виклику `sctp_sendmsg()` у переповнену чергу сокета функція повертає `-1` з установленням `errno = EAGAIN`. Застосунок повинен дочекатися події `EPOLLOUT` перед повторною спробою відправки.
3. **Політика буферизації сокета (`sctp_rcvbuf_policy`):** За замовчуванням ліміт `SO_RCVBUF` є спільним для всіх асоціацій сокета `SOCK_SEQPACKET`. Встановлення `sysctl net.sctp.rcvbuf_policy = 1` змушує ядро виділяти індивідуальний буфер розміром `SO_RCVBUF` для кожної асоціації окремо.

---

## 8. Завершення асоціації: плавне закриття (Shutdown) проти екстреного розриву (Abort)

Протокол SCTP не підтримує стан напівзакритого з'єднання (*half-closed state*), характерний для TCP (де одна сторона може закрити запис, але нескінченно читати відповіді). Завершення асоціації в SCTP завжди є симетричним і повним:

1. **Плавне закриття (*Graceful Shutdown*):**
   - Викликається закриттям дескриптора сокета `close(sd)` або відправкою спеціального прапорця `sctp_sendmsg(..., flags = SCTP_EOF)`.
   - Сторона, що ініціює закриття, припиняє прийом нових даних від застосунку, але повністю передає всі накопичені в черзі відправки чанки `DATA`. Після підтвердження всіх `DATA` відправляється чанк керування `SHUTDOWN`.
   - Віддалений вузол дочитує залишок черги, завершує передачу власних непідтверджених даних і відповідає чанком `SHUTDOWN ACK`.
   - Ініціатор надсилає `SHUTDOWN COMPLETE`, після чого ресурси асоціації (TCB) остаточно звільняються в ядрі операційної системи.

2. **Екстрений розрив (*Abortive Teardown*):**
   - Викликається викликом `sctp_sendmsg(..., flags = SCTP_ABORT)` або встановленням опції сокета `SO_LINGER` з нульовим таймаутом.
   - Стек негайно очищає всі вхідні та вихідні черги пам'яті, генерує чанк `ABORT` із необов'язковим кодом причини помилки (Error Cause TCB Destroyed) і миттєво знищує асоціацію без очікування підтверджень.

---

## 9. Робочий шаблон ініціалізації сервера та клієнта

Нижче наведено повнофункціональний шаблон налаштування серверного сокета SCTP із прив'язкою двох IP-адрес для мультихоумінгу, конфігурацією кількості потоків та підпискою на всі події керування.

:::tabs
```c
/* Повноцінне налаштування SCTP-сервера з мультихоумінгом мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

int init_sctp_multihome_server(const char *ip1, const char *ip2, uint16_t port) {
    int sd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (sd < 0) {
        perror("Помилка створення сокета SCTP");
        return -1;
    }

    /* 1. Конфігурація кількості потоків */
    struct sctp_initmsg initmsg;
    memset(&initmsg, 0, sizeof(initmsg));
    initmsg.sinit_num_ostreams = 10;
    initmsg.sinit_max_instreams = 10;
    initmsg.sinit_max_attempts = 4;
    initmsg.sinit_max_init_timeo = 5000;
    if (setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
        perror("Помилка setsockopt SCTP_INITMSG");
        close(sd);
        return -1;
    }

    /* 2. Підписка на події ядра */
    struct sctp_event_subscribe events;
    memset(&events, 0, sizeof(events));
    events.sctp_data_io_event = 1;
    events.sctp_association_event = 1;
    events.sctp_address_event = 1;
    events.sctp_shutdown_event = 1;
    if (setsockopt(sd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
        perror("Помилка setsockopt SCTP_EVENTS");
        close(sd);
        return -1;
    }

    /* 3. Прив'язка двох IP-адрес через sctp_bindx */
    struct sockaddr_in bind_addrs[2];
    memset(bind_addrs, 0, sizeof(bind_addrs));

    bind_addrs[0].sin_family = AF_INET;
    bind_addrs[0].sin_port = htons(port);
    if (inet_pton(AF_INET, ip1, &bind_addrs[0].sin_addr) <= 0) {
        close(sd);
        return -1;
    }

    bind_addrs[1].sin_family = AF_INET;
    bind_addrs[1].sin_port = htons(port);
    if (inet_pton(AF_INET, ip2, &bind_addrs[1].sin_addr) <= 0) {
        close(sd);
        return -1;
    }

    if (sctp_bindx(sd, (struct sockaddr *)bind_addrs, 2, SCTP_BINDX_ADD_ADDR) < 0) {
        perror("Помилка sctp_bindx");
        close(sd);
        return -1;
    }

    if (listen(sd, 10) < 0) {
        perror("Помилка listen");
        close(sd);
        return -1;
    }

    return sd;
}
```
```cpp
// Ідіоматичний еквівалент налаштування SCTP-сервера на C++20 (RAII, expected, span)
#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

class SctpServerSocket {
public:
    explicit SctpServerSocket(int fd) noexcept : fd_(fd) {}
    ~SctpServerSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SctpServerSocket(const SctpServerSocket&) = delete;
    SctpServerSocket& operator=(const SctpServerSocket&) = delete;

    SctpServerSocket(SctpServerSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SctpServerSocket& operator=(SctpServerSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    static std::expected<SctpServerSocket, std::error_code> create(
        std::string_view ip1, std::string_view ip2, uint16_t port) 
    {
        int sd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
        if (sd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        SctpServerSocket server(sd);

        // 1. Конфігурація кількості потоків
        sctp_initmsg initmsg{};
        initmsg.sinit_num_ostreams = 10;
        initmsg.sinit_max_instreams = 10;
        initmsg.sinit_max_attempts = 4;
        initmsg.sinit_max_init_timeo = 5000;
        if (::setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 2. Підписка на події ядра
        sctp_event_subscribe events{};
        events.sctp_data_io_event = 1;
        events.sctp_association_event = 1;
        events.sctp_address_event = 1;
        events.sctp_shutdown_event = 1;
        if (::setsockopt(sd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 3. Прив'язка двох IP-адрес для мультихоумінгу
        std::array<sockaddr_in, 2> addrs{};
        addrs[0].sin_family = AF_INET;
        addrs[0].sin_port = htons(port);
        if (::inet_pton(AF_INET, ip1.data(), &addrs[0].sin_addr) <= 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        addrs[1].sin_family = AF_INET;
        addrs[1].sin_port = htons(port);
        if (::inet_pton(AF_INET, ip2.data(), &addrs[1].sin_addr) <= 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::sctp_bindx(sd, reinterpret_cast<sockaddr*>(addrs.data()), 
                         static_cast<int>(addrs.size()), SCTP_BINDX_ADD_ADDR) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(sd, 10) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return server;
    }

private:
    int fd_{-1};
};
```
:::
