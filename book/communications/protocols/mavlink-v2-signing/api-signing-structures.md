# 📋 Інтерфейси та структури підпису MAVLink 2

Програмний шар захисту [MAVLink 2](topic:communications/mavlink-packet) від несанкціонованої підміни даних та атак повторного відтворення інкапсульовано в бібліотеці `c_library_v2` ([mavgen](topic:communications/mavlink-xml-codegen)) у вигляді двійкових структур, бітових масок та функцій зворотного виклику. Нижче наведено розкладку структур пам'яті, призначення кожного байта конфігурації, формат повідомлення `SETUP_SIGNING` (#256), маски помилок розбору та правила узгодження ключів між автопілотом і наземною станцією.

### Конфігураційна структура стану підпису: mavlink_signing_t

Керування криптографічним контекстом окремого каналу зв'язку ([UART](topic:communications/packet-design), UDP чи TCP) здійснюється через екземпляр структури `mavlink_signing_t`. Кожен логічний канал MAVLink (індексується константою `MAVLINK_COMM_0` .. `MAVLINK_COMM_NB_HIGH - 1`) містить посилання на власний екземпляр цієї структури у своєму блоці статусу `mavlink_status_t`.

:::tabs
```c
typedef struct __mavlink_signing {
    uint8_t  flags;                             // Бітові прапорці режиму підпису
    uint8_t  link_id;                           // Ідентифікатор фізичного/логічного лінку (0..255)
    uint64_t timestamp;                         // Поточний локальний монотонний час (48 біт, 10 мкс)
    uint8_t  secret_key[32];                    // 256-бітний спільний секретний ключ
    mavlink_signing_streams_t *streams;         // Вказівник на таблицю відстеження вхідних потоків
    mavlink_accept_unsigned_t  accept_unsigned_callback; // Колбек фільтрації непідписаних пакетів
} mavlink_signing_t;
```
```cpp
struct MavlinkSigningContext {
    uint8_t  flags{0};                          // Бітові прапорці режиму підпису
    uint8_t  link_id{0};                        // Ідентифікатор інтерфейсу (0..255)
    uint64_t timestamp{0};                      // Локальний монотонний час (48 біт, 10 мкс)
    std::array<uint8_t, 32> secret_key{};       // 256-бітний спільний ключ
    mavlink_signing_streams_t* streams{nullptr};// Таблиця стану вхідних потоків
    std::function<bool(const mavlink_status_t*, uint32_t)> accept_unsigned_callback{nullptr};
};
```
:::

Структура розроблена з урахуванням жорстких вимог до вирівнювання пам'яті на 32-бітних процесорах ARM Cortex-M. Поле `timestamp` має тип `uint64_t` і вимагає 8-байтового вирівнювання на багатьох апаратних архітектурах. Якщо екземпляр `mavlink_signing_t` розміщується у статичній або динамічній пам'яті, компілятор автоматично вставляє байти доповнення між полями `link_id` та `timestamp`.

Розглянемо детальне функціональне призначення кожного поля та його вплив на роботу низькорівневого розбірника:

Поле `flags` містить бітову маску поточної конфігурації. У поточній ревізії протоколу визначено єдиний керівний біт `MAVLINK_SIGNING_FLAG_SIGN_OUTGOING` (значення `0x01`). Якщо цей біт встановлено у одиницю, генератор вихідних пакетів бібліотеки автоматично встановлює біт `0x01` у полі заголовка `incompat_flags`, обчислює поточний монотонний таймстемп, формує 13-байтовий трейлер підпису та дописує його безпосередньо після 2-байтового поля контрольної суми CRC. Якщо біт скинуто в нуль, вузол працює в режимі суто пасивної перевірки: він валідує вхідні підписані кадри, проте власні вихідні пакети надсилає без трейлера підпису у стандартному форматі MAVLink 2.

Поле `link_id` задає унікальний числовий ідентифікатор конкретного фізичного інтерфейсу (в діапазоні від 0 до 255). Цей байт копіюється у відповідне поле вихідного трейлера підпису. Призначення поля — розділити простори монотонних таймстемпів для різних середовищ передачі. Наприклад, якщо автопілот надсилає телеметрію одночасно через повільний радіомодем на частоті 433 МГц (`link_id = 0`) та через високошвидкісну шину Ethernet до супутнього комп'ютера (`link_id = 1`), ці канали мають абсолютно різну пропускну здатність і затримки. Завдяки наявності `link_id` приймач розглядає ці канали як два незалежні криптографічні потоки й не блокує повільні пакети радіоканалу через випередження лічильника часу в швидкому каналі.

Поле `timestamp` зберігає поточний локальний час відправника. Для вимірювання використовується спеціальна часова шкала протоколу MAVLink: 48-бітне ціле число без знака, ціна однієї одиниці якого дорівнює рівно 10 мікросекундам (частота 100 кГц). Точкою відліку є північ 1 січня 2015 року GMT (Unix timestamp `1420070400` секунд). Головний інваріант відправника полягає у суворій монотонності: під час відправки кожного наступного кадру значення `timestamp` зобов'язане бути строго більшим за значення у попередньому кадрі на цьому ж лінку. Якщо внутрішній годинник процесора з будь-яких причин повернувся назад (наприклад, через коригування часу за GPS або збій системного таймера) або згенерував кілька пакетів протягом одного 10-мікросекундного інтервалу, бібліотека примусово інкрементує збережене поле `timestamp` щонайменше на одиницю перед формуванням підпису.

Поле `secret_key` є масивом із 32 байтів (256 бітів), який містить спільний секретний ключ автентифікації. Цей масив подається на вхід криптографічної геш-функції SHA-256 як перший блок даних перед байтами заголовка, корисного навантаження та трейлера. Ключ є строго конфіденційним: він має бути узгоджений між сторонами перед початком польоту та ніколи не повинен транслюватися у відкритому вигляді через незахищений радіоефір.

Поле `streams` містить покажчик на структуру `mavlink_signing_streams_t`, у якій приймач зберігає поточний стан усіх активних вхідних сесій зв'язку. Якщо покажчик встановлено у `NULL`, підсистема валідації вважається неактивною, і всі вхідні підписані кадри будуть відхилятися через неможливість перевірки монотонності часу.

Поле `accept_unsigned_callback` містить адресу функції зворотного виклику, яка викликається розбірником під час надходження кадру без підпису (`incompat_flags & 0x01 == 0`). Цей механізм дозволяє реалізувати вибіркові політики довіри, розділяючи критичні команди та інформаційну телеметрію.

### Таблиця відстеження вхідних потоків: mavlink_signing_streams_t

Для надійного захисту від атак повтору приймач зобов'язаний зберігати останній прийнятий валідний таймстемп для кожного активного передавача. Оскільки в одній мережі MAVLink можуть одночасно працювати кілька фізичних апаратів (різні `sysid`), кілька бортових пристроїв (різні `compid`) та кілька інтерфейсів зв'язку (різні `link_id`), стан відстежується окремо для кожного унікального триплета адрес.

:::tabs
```c
#define MAVLINK_MAX_SIGNING_STREAMS 16

typedef struct __mavlink_signing_stream {
    uint8_t  link_id;       // Ідентифікатор лінку відправника (0..255)
    uint8_t  sysid;         // Системний ID апарата відправника (1..255)
    uint8_t  compid;        // ID компонента відправника (1..255)
    uint64_t timestamp;     // Останній прийнятий валідний таймстемп (48 біт)
} mavlink_signing_stream_t;

typedef struct __mavlink_signing_streams {
    uint16_t num_signing_streams; // Поточна кількість зайнятих слотів
    mavlink_signing_stream_t stream[MAVLINK_MAX_SIGNING_STREAMS]; // Масив активних слотів
} mavlink_signing_streams_t;
```
```cpp
struct MavlinkSigningStream {
    uint8_t  link_id{0};    // Ідентифікатор лінку відправника (0..255)
    uint8_t  sysid{0};      // Системний ID апарата відправника (1..255)
    uint8_t  compid{0};     // ID компонента відправника (1..255)
    uint64_t timestamp{0};  // Останній прийнятий валідний таймстемп (48 біт)
};

struct MavlinkSigningStreams {
    static constexpr size_t kMaxStreams = 16;
    uint16_t num_signing_streams{0};
    std::array<MavlinkSigningStream, kMaxStreams> stream{};
};
```
:::

За замовчуванням константа `MAVLINK_MAX_SIGNING_STREAMS` встановлена у значення 16. Це означає, що один вузол може одночасно підтримувати до 16 незалежних безпечних каналів зв'язку без ризику переповнення таблиці.

Під час надходження кожного нового підписаного кадру обробник виконує послідовність дій за чітко визначеним протоколом:

Спершу виконується лінійний перебір масиву `stream` від індексу 0 до `num_signing_streams - 1`. Критерієм точного збігу є рівність усіх трьох адресних полів: ідентифікатора системи `sysid`, ідентифікатора компонента `compid` та ідентифікатора лінії `link_id`.

Якщо відповідний запис знайдено, алгоритм перевіряє умову монотонного зростання: отриманий із трейлера час `incoming_timestamp` має бути строго більшим за збережене значення `stream[i].timestamp`. Якщо вхідний час менший або дорівнює збереженому, пакет негайно відкидається, а статус кадрування встановлюється у `MAVLINK_FRAMING_BAD_SIGNATURE`. Це запобігає будь-яким спробам повторного відтворення старих записів команд.

Якщо запис для даного триплета відсутній, а лічильник `num_signing_streams` менший за граничний розмір `MAVLINK_MAX_SIGNING_STREAMS`, створюється новий запис у першому вільному слоті. До нього копіюються значення `link_id`, `sysid`, `compid` та початковий `timestamp`, а лічильник `num_signing_streams` збільшується на одиницю.

Якщо ж таблиця повністю заповнена (усі 16 слотів зайняті), система застосовує стратегію заміщення найстарішого запису (алгоритм LRU — Least Recently Used). Слот, у який найдовше не надходили нові пакети, очищується та виділяється під нове джерело зв'язку.

### Низькорівневе пакування 48-бітних таймстемпів

Оскільки мова C не має вбудованого примітивного типу розміром 48 бітів, бібліотека MAVLink реалізує пакування та розпакування поля `timestamp` через побайтові макроси `_mav_put_uint48_t` та `_mav_get_uint48_t`. Вони гарантують порядок байтів little-endian (молодший байт за меншою адресою) незалежно від порядку байтів хостового процесора:

:::tabs
```c
// Запис 48-бітного числа в буфер (little-endian)
static inline void _mav_put_uint48_t(uint8_t *buf, uint64_t val) {
    buf[0] = (uint8_t)(val >> 0);
    buf[1] = (uint8_t)(val >> 8);
    buf[2] = (uint8_t)(val >> 16);
    buf[3] = (uint8_t)(val >> 24);
    buf[4] = (uint8_t)(val >> 32);
    buf[5] = (uint8_t)(val >> 40);
}

// Читання 48-бітного числа з буфера (little-endian)
static inline uint64_t _mav_get_uint48_t(const uint8_t *buf) {
    return ((uint64_t)buf[0])       |
           (((uint64_t)buf[1]) << 8)  |
           (((uint64_t)buf[2]) << 16) |
           (((uint64_t)buf[3]) << 24) |
           (((uint64_t)buf[4]) << 32) |
           (((uint64_t)buf[5]) << 40);
}
```
```cpp
// Запис 48-бітного числа в буфер (little-endian)
constexpr void packUint48(std::span<uint8_t, 6> buf, uint64_t val) noexcept {
    for (size_t i = 0; i < 6; ++i) {
        buf[i] = static_cast<uint8_t>((val >> (i * 8)) & 0xFF);
    }
}

// Читання 48-бітного числа з буфера (little-endian)
[[nodiscard]] constexpr uint64_t unpackUint48(std::span<const uint8_t, 6> buf) noexcept {
    uint64_t res = 0;
    for (size_t i = 0; i < 6; ++i) {
        res |= (static_cast<uint64_t>(buf[i]) << (i * 8));
    }
    return res;
}
```
:::

Використання побайтового зсуву виключає проблеми невирівняного доступу (`unaligned memory fault`), які часто виникають при спробах прямого кастування покажчиків типу `*(uint64_t*)buf` на ядрах ARM Cortex-M0/M3.

### Автомат стану розбірника: інтеграція MAVLINK_IFLAG_SIGNED

У процесі потокового розбору ([потоковий розбірник](topic:programming/stream-parser)) байтів функція `mavlink_frame_char_buffer()` проходить через послідовність внутрішніх станів:

1. `MAVLINK_PARSE_STATE_UNINIT` / `IDLE`: очікування стартового байта `0xFD`.
2. `MAVLINK_PARSE_STATE_GOT_STX`: отримання поля `LEN`.
3. `MAVLINK_PARSE_STATE_GOT_LENGTH`: зчитування `incompat_flags`. Якщо біт `0x01` встановлено, розбірник піднімає внутрішній прапорець `status->signing_in_progress = 1`.
4. `MAVLINK_PARSE_STATE_GOT_INCOMPAT_FLAGS` .. `MAVLINK_PARSE_STATE_GOT_PAYLOAD`: накопичення заголовка та корисних даних.
5. `MAVLINK_PARSE_STATE_GOT_CRC1` та `MAVLINK_PARSE_STATE_GOT_CRC2`: перевірка контрольної суми CRC-16.
6. Якщо `status->signing_in_progress == 0`, пакет вважається завершеним. Якщо ж прапорець підпису піднято, автомат переходить у спеціальний стан `MAVLINK_PARSE_STATE_SIGNATURE`, де накопичує рівно 13 додаткових байтів трейлера перед тим, як викликати функцію криптографічної перевірки.

Якщо будь-який байт трейлера не надійшов через обрив зв'язку або таймаут, весь пакет відкидається, а статус кадрування позначається як пошкоджений.

### Повідомлення конфігурації підпису: SETUP_SIGNING (#256)

Для динамічного встановлення або оновлення секретних ключів та узгодження базового часу через сам протокол MAVLink використовується повідомлення `SETUP_SIGNING` (ідентифікатор повідомлення `MSG ID 256`, контрольний байт `CRC_EXTRA = 71`).

Структура корисного навантаження цього повідомлення визначається заголовним файлом діалекту `common.xml`:

:::tabs
```c
typedef struct __mavlink_setup_signing_t {
    uint64_t initial_timestamp; // Початковий базовий час відправника (48 біт, 10 мкс)
    uint8_t  target_system;     // ID цільової системи (0 = широкомовне)
    uint8_t  target_component;  // ID цільового компонента (0 = широкомовне)
    uint8_t  secret_key[32];    // Новий 256-бітний секретний ключ
} mavlink_setup_signing_t;
```
```cpp
struct MavlinkSetupSigning {
    uint64_t initial_timestamp{0};           // 48-бітний час в одиницях 10 мкс
    uint8_t  target_system{0};               // ID цільової системи (0 = broadcast)
    uint8_t  target_component{0};            // ID цільового компонента
    std::array<uint8_t, 32> secret_key{};    // 256-бітний симетричний ключ
};
```
:::

Розташування полів на фізичному рівні підпорядковується правилу спадання розміру типів для запобігання невирівняному доступу до ОЗП:

Перші 8 байтів (зсув `0x00 .. 0x07`) відведено під поле `initial_timestamp` типу `uint64_t` у форматі little-endian. Воно містить поточний системний час наземної станції, переведений у 10-мікросекундну шкалу MAVLink. Отримавши це повідомлення, польотний контролер ініціалізує свій локальний лічильник часу цим значенням, що забезпечує грубу синхронізацію годинників.

Дев'ятий байт (зсув `0x08`) містить `target_system` — номер апарата, якому адресовано команду. Якщо поле дорівнює нулю, повідомлення обробляється всіма пристроями на лінії зв'язку.

Десятий байт (зсув `0x09`) містить `target_component` — номер конкретного вузла (наприклад, 1 для головного автопілота).

Наступні 32 байти (зсув `0x0A .. 0x29`) містять бінарне тіло секретного ключа `secret_key`.

Загальний обсяг корисних даних повідомлення `SETUP_SIGNING` становить рівно 42 байти.

Процедура оновлення ключів вимагає дотримання суворих правил безпеки. Оскільки корисні дані повідомлення `SETUP_SIGNING` передають сам секретний ключ у відкритому вигляді, трансляція цього пакета через незахищений радіоефір повністю нівелює захист, оскільки будь-який пасивний приймач зможе перехопити ключ. Тому специфікація протоколу дозволяє обробляти `SETUP_SIGNING` лише за таких умов:

По-перше, конфігурація через прямий захищений фізичний кабель (USB або прямий UART на сервісному стенді перед зльотом).

По-друге, оновлення ключа через сесію, яка вже є криптографічно захищеною (наприклад, надсилання `SETUP_SIGNING` як підписаного пакета з використанням старого дійсного ключа перед переходом на новий ключ).

Отримавши валідне повідомлення `SETUP_SIGNING`, цільовий вузол копіює масив `secret_key` у свій робочий контекст `mavlink_signing_t`, зберігає ключ у незалежній пам'яті (Flash або FRAM), скидає таблицю потоків `mavlink_signing_streams_t` для запобігання конфліктам старих таймстемпів і встановлює біт `MAVLINK_SIGNING_FLAG_SIGN_OUTGOING`.

### Колбек фільтрації непідписаних пакетів: mavlink_accept_unsigned_t

Для забезпечення гнучкості розгортання протокол підтримує змішаний режим роботи (гібридна безпека). У цьому режимі вузол може одночасно приймати відкриті широкомовні дані та вимагати суворої автентифікації для критичних наказів. Логіка такого розподілу покладається на функцію зворотного виклику типу `mavlink_accept_unsigned_t`:

:::tabs
```c
typedef bool (*mavlink_accept_unsigned_t)(const mavlink_status_t *status, uint32_t msgid);
```
```cpp
using AcceptUnsignedCallback = bool(*)(const mavlink_status_t* status, uint32_t msgid);
```
:::

Функція приймає два аргументи: покажчик на системний статус поточного каналу `status` та числовий ідентифікатор вхідного повідомлення `msgid`.

Якщо функція повертає `true`, розбірник ігнорує відсутність трейлера підпису та передає пакет у польотний стек як валідний.

Якщо функція повертає `false`, непідписаний пакет вважається небезпечним і негайно знищується. При цьому лічильник помилок розбору `status->parse_error` збільшується на одиницю, а статус кадрування позначається як помилковий.

Типова інженерна реалізація колбека будується за принципом «білого списку» (whitelist):

:::tabs
```c
static bool signing_whitelist_filter(const mavlink_status_t *status, uint32_t msgid) {
    (void)status;
    switch (msgid) {
        // Дозволена інформаційна телеметрія:
        case MAVLINK_MSG_ID_HEARTBEAT:            // Серцебиття системи (ID 0)
        case MAVLINK_MSG_ID_SYS_STATUS:           // Стан батареї та сенсорів (ID 1)
        case MAVLINK_MSG_ID_SYSTEM_TIME:          // Час системи (ID 2)
        case MAVLINK_MSG_ID_ATTITUDE:             // Просторова орієнтація (ID 30)
        case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:  // Координати GPS (ID 33)
        case MAVLINK_MSG_ID_VFR_HUD:              // Приладова швидкість і висота (ID 74)
            return true;

        // Заборонено без підпису (усі критичні накази):
        case MAVLINK_MSG_ID_COMMAND_LONG:         // Керуючі команди (ID 76)
        case MAVLINK_MSG_ID_COMMAND_INT:          // Координатні команди (ID 75)
        case MAVLINK_MSG_ID_MISSION_ITEM_INT:     // Точки польотного завдання (ID 73)
        case MAVLINK_MSG_ID_PARAM_SET:            // Зміна параметрів конфігурації (ID 23)
        case MAVLINK_MSG_ID_SET_MODE:             // Зміна режиму польоту (ID 11)
        default:
            return false;
    }
}
```
```cpp
[[nodiscard]] constexpr bool isMessageAllowedUnsigned(uint32_t msgid) noexcept {
    switch (msgid) {
        // Дозволена інформаційна телеметрія:
        case MAVLINK_MSG_ID_HEARTBEAT:            // Серцебиття системи (ID 0)
        case MAVLINK_MSG_ID_SYS_STATUS:           // Стан батареї та сенсорів (ID 1)
        case MAVLINK_MSG_ID_SYSTEM_TIME:          // Час системи (ID 2)
        case MAVLINK_MSG_ID_ATTITUDE:             // Просторова орієнтація (ID 30)
        case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:  // Координати GPS (ID 33)
        case MAVLINK_MSG_ID_VFR_HUD:              // Приладова швидкість і висота (ID 74)
            return true;

        // Заборонено без підпису (усі критичні накази):
        case MAVLINK_MSG_ID_COMMAND_LONG:         // Керуючі команди (ID 76)
        case MAVLINK_MSG_ID_COMMAND_INT:          // Координатні команди (ID 75)
        case MAVLINK_MSG_ID_MISSION_ITEM_INT:     // Точки польотного завдання (ID 73)
        case MAVLINK_MSG_ID_PARAM_SET:            // Зміна параметрів конфігурації (ID 23)
        case MAVLINK_MSG_ID_SET_MODE:             // Зміна режиму польоту (ID 11)
        default:
            return false;
    }
}
```
:::

Такий підхід дозволяє стороннім спостерігачам або допоміжним моніторам бачити координати й телеметрію дрона, повністю блокуючи будь-які спроби несанкціонованого втручання в керування апаратом.

### Маски прапорців, системні константи та коди помилок

Нижче наведено повний перелік констант із заголовного файлу `mavlink_types.h`, які керують криптографічним конвеєром:

Константа `MAVLINK_SIGNING_TRAILER_LEN` визначає фізичний розмір трейлера підпису на дроті й дорівнює рівно 13 байтам (1 байт `link_id` + 6 байтів `timestamp` + 6 байтів `signature`).

Константа `MAVLINK_SIGNING_EPOCH` дорівнює значенню `142007040000000ULL`. Це кількість 10-мікросекундних квантів від початку Unix-епохи (1 січня 1970 року) до початку епохи MAVLink (1 січня 2015 року). Вона використовується у формулах перетворення системного часу `gettimeofday()` або POSIX `clock_gettime()` у формат таймстемпу MAVLink:

```
MAVLink_Timestamp = (Unix_Microseconds - 1420070400000000ULL) / 10
```

Бітова маска `MAVLINK_IFLAG_SIGNED` зі значенням `0x01` встановлюється в першому біті байта `incompat_flags` заголовка кадру MAVLink 2, сповіщаючи приймач про обов'язкову наявність 13-байтового трейлера в кінці пакета.

Статусні коди помилок у полі `status->framing_status` приймають такі значення:

`MAVLINK_FRAMING_OK` (числове значення 0) — кадр успішно розібрано, контрольна сума CRC збіглася, а підпис (якщо був присутній) є цілком валідним.

`MAVLINK_FRAMING_BAD_CRC` (значення 1) — пакет пошкоджено перешкодами в каналі зв'язку, обчислена CRC-16 не відповідає прийнятій.

`MAVLINK_FRAMING_BAD_SIGNATURE` (значення 2) — пакет відкинуто криптографічним фільтром. Причиною може бути розбіжність обчисленого SHA-256 хешу через невірний ключ, спотворення байтів трейлера або порушення монотонності часу (виявлена атака повтору).

### Приклади конфігурації та роботи з інтерфейсом

Нижче наведено робочий приклад повної ініціалізації та конфігурації підсистеми підпису мовами C та ідіоматичною C++:

:::tabs
```c
#include <mavlink.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

static mavlink_signing_t g_signing_channel0;
static mavlink_signing_streams_t g_signing_streams_channel0;

// Функція безпечної конвертації POSIX часу в таймстемп MAVLink
static uint64_t get_system_mavlink_timestamp(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t unix_us = (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)(ts.tv_nsec / 1000);
    uint64_t epoch_us = 1420070400000000ULL; // 2015-01-01 00:00:00 GMT
    
    if (unix_us < epoch_us) {
        return 1; // Захист від некоректного системного годинника
    }
    return (unix_us - epoch_us) / 10ULL;
}

// Колбек фільтрації непідписаного трафіку
static bool signing_filter_cb(const mavlink_status_t *status, uint32_t msgid) {
    (void)status;
    // Дозволяємо без підпису лише відкриту базову телеметрію
    if (msgid == MAVLINK_MSG_ID_HEARTBEAT || 
        msgid == MAVLINK_MSG_ID_ATTITUDE ||
        msgid == MAVLINK_MSG_ID_GLOBAL_POSITION_INT) {
        return true;
    }
    return false; // Усі команди вимагають валідного підпису
}

void setup_mavlink_signing_interface(uint8_t channel, const uint8_t raw_key[32], uint8_t link_id) {
    memset(&g_signing_channel0, 0, sizeof(g_signing_channel0));
    memset(&g_signing_streams_channel0, 0, sizeof(g_signing_streams_channel0));

    g_signing_channel0.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
    g_signing_channel0.link_id = link_id;
    g_signing_channel0.timestamp = get_system_mavlink_timestamp();
    memcpy(g_signing_channel0.secret_key, raw_key, 32);
    g_signing_channel0.streams = &g_signing_streams_channel0;
    g_signing_channel0.accept_unsigned_callback = signing_filter_cb;

    // Прив'язка до внутрішнього стану бібліотеки MAVLink
    mavlink_status_t *status = mavlink_get_channel_status(channel);
    status->signing = &g_signing_channel0;
    status->signing_streams = &g_signing_streams_channel0;
}
```
```cpp
#include <mavlink.h>
#include <array>
#include <span>
#include <chrono>
#include <cstdint>
#include <algorithm>

class MavlinkSigningContext {
public:
    using SecretKey = std::array<uint8_t, 32>;

    MavlinkSigningContext(uint8_t channel_idx, const SecretKey& key, uint8_t link_id)
        : channel_(channel_idx) {
        signing_ = {};
        streams_ = {};

        signing_.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
        signing_.link_id = link_id;
        signing_.timestamp = calculateCurrentMavlinkTimestamp();
        std::copy(key.begin(), key.end(), signing_.secret_key);
        signing_.streams = &streams_;
        signing_.accept_unsigned_callback = &MavlinkSigningContext::onFilterUnsigned;

        auto* status = mavlink_get_channel_status(channel_);
        status->signing = &signing_;
        status->signing_streams = &streams_;
    }

    void stepMonotonicTime() noexcept {
        const uint64_t now_ts = calculateCurrentMavlinkTimestamp();
        if (now_ts > signing_.timestamp) {
            signing_.timestamp = now_ts;
        } else {
            ++signing_.timestamp; // Гарантія суворої монотонності
        }
    }

    [[nodiscard]] uint8_t linkId() const noexcept { return signing_.link_id; }
    [[nodiscard]] uint64_t currentTimestamp() const noexcept { return signing_.timestamp; }

private:
    static bool onFilterUnsigned(const mavlink_status_t*, uint32_t msgid) noexcept {
        switch (msgid) {
            case MAVLINK_MSG_ID_HEARTBEAT:
            case MAVLINK_MSG_ID_ATTITUDE:
            case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
            case MAVLINK_MSG_ID_SYS_STATUS:
                return true;
            default:
                return false;
        }
    }

    static uint64_t calculateCurrentMavlinkTimestamp() noexcept {
        using namespace std::chrono;
        const auto now = system_clock::now();
        const auto us = duration_cast<microseconds>(now.time_since_epoch()).count();
        constexpr int64_t kMavlinkEpochUs = 1420070400000000LL; // 2015-01-01 GMT
        
        if (us <= kMavlinkEpochUs) {
            return 1ULL;
        }
        return static_cast<uint64_t>((us - kMavlinkEpochUs) / 10);
    }

    uint8_t channel_;
    mavlink_signing_t signing_{};
    mavlink_signing_streams_t streams_{};
};
```
:::

### Інтеграція з польотними стеками ArduPilot, PX4 та наземними станціями

У реальних безпілотних комплексах конфігурація підпису розподілена між прошивкою автопілота та програмним забезпеченням оператора:

В автопілотах ArduPilot ключ завантажується з файлу `/APM/signing.key` на карті пам'яті microSD під час завантаження системи. Драйвер телеметрії викликає функцію `mavlink_set_signing_key()`, яка автоматично ініціалізує контексти для всіх послідовних портів UART. Додатковий параметр `BRD_SIGNING_EN` дозволяє повністю заборонити або дозволити криптографічну обробку на апаратному рівні.

У польотному стеку PX4 конфігурація здійснюється через системні параметри `MAV_0_SIGNING` .. `MAV_2_SIGNING`. Якщо параметр встановлено у значення 1, модуль `mavlink` блокує виконання будь-яких непідписаних наказів `MAV_CMD`, переводячи канал у режим суворої авторизації.

У наземних станціях керування (QGroundControl та Mission Planner) налаштування підпису винесено в окремий розділ безпеки зв'язку. Оператор генерує криптографічно стійкий 256-бітний ключ, записує його у захищене сховище ключів ОС (Windows Credential Manager або macOS Keychain) та передає на автопілот через кабель USB за допомогою процедури `SETUP_SIGNING`. Утиліти на базі бібліотеки PyMAVLink активують підпис через виклик `master.setup_signing(key, sign_outgoing=True)`, що автоматично налаштовує відправку 13-байтових трейлерів у скриптах автоматизації.
