# 📋 Програмний інтерфейс RFCOMM у Linux BlueZ

У стек протоколів ядра Linux (підсистема BlueZ) протокол RFCOMM інтегровано як повноцінне сімейство мережевих сокетів Берклі. Це дозволяє розробникам системного та прикладного програмного забезпечення взаємодіяти з віртуальними послідовними каналами Bluetooth двома різними шляхами: через стандартний сокетний інтерфейс (`AF_BLUETOOTH` із протоколом `BTPROTO_RFCOMM`) або через створення файлів символьних пристроїв у просторі користувача (`/dev/rfcomm0`..`/dev/rfcomm30`) за допомогою керуючих викликів `ioctl`.

### Архітектура сокетного рівня RFCOMM у ядрі

Сокетний інтерфейс RFCOMM є обгорткою над канальним рівнем L2CAP, яка приховує від користувацького простору кадрування, мультиплексування DLCI, облік кредитів CBFC та передачу сигналів стану ліній.

Коли прикладний процес викликає системний виклик `socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)`, підсистема мережевого стека ядра виділяє структуру сокета `struct rfcomm_sock`, яка зв'язується з внутрішнім мультиплексором сесії `struct rfcomm_session`. Якщо фізичне з'єднання L2CAP із цільовим пристроєм ще не існує, ядро автоматично ініціює підключення до PSM `0x0003`, створює службовий канал `DLCI = 0`, виконує узгодження параметрів `PN` і лише після цього надсилає запит `SABM` для відкриття конкретного каналу даних `DLCI = k`.

### Сокетні структури даних

Для адресації та ідентифікації кінцевих точок каналу RFCOMM використовується структура `sockaddr_rc`, визначена в системному заголовному файлі `<bluetooth/rfcomm.h>`.

| Поле структури | Тип даних | Призначення та діапазон значень |
| :--- | :--- | :--- |
| `rc_family` | `sa_family_t` | Сімейство адрес: обов'язково константа `AF_BLUETOOTH` (числове значення `31`). |
| `rc_bdaddr` | `bdaddr_t` | 6-байтна апаратна MAC-адреса пристрою Bluetooth у порядку байтів *little-endian*. |
| `rc_channel` | `uint8_t` | Номер серверного каналу RFCOMM (від `1` до `30`). Значення `0` призначене для динамічного виділення порту ядром під час виклику `bind()`. |

Апаратна адреса пристрою зберігається у спеціальному типі `bdaddr_t` (цитата з системного заголовка `<bluetooth/bluetooth.h>`):

```c
typedef struct {
    uint8_t b[6];
} __attribute__((packed)) bdaddr_t;
```

Оскільки порядок байтів Bluetooth-адреси є зворотним до загальноприйнятого мережевого формату (молодший байт зберігається першим за індексом `b[0]`), пряме копіювання рядків через `memcpy()` призводить до перевертання адреси. Для коректної роботи бібліотека BlueZ надає набір спеціалізованих функцій:

- `str2ba(const char *str, bdaddr_t *ba)`: парсить текстовий рядок формату `"01:23:45:67:89:AB"` у двійкову структуру `bdaddr_t` із реверсом байтів. Повертає `0` при успіху або `-1` при некоректному форматі.
- `ba2str(const bdaddr_t *ba, char *str)`: форматує двійкову адресу у 18-символьний нуль-термінований рядок формату `"XX:XX:XX:XX:XX:XX"`. Буфер призначення повинен мати розмір не менше `18` байтів.
- `bacmp(const bdaddr_t *ba1, const bdaddr_t *ba2)`: виконує побайтове порівняння двох адрес. Повертає `0`, якщо адреси повністю ідентичні (аналог `memcmp`).
- `bacpy(bdaddr_t *dst, const bdaddr_t *src)`: безпечно копіює адресу джерела в буфер призначення.
- `BDADDR_ANY` (`00:00:00:00:00:00`): спеціальний макрос нульової адреси. Використовується сервером під час прив'язки, дозволяючи приймати вхідні з'єднання на будь-якому локальному радіоадаптері (`hci0`, `hci1` тощо).
- `BDADDR_LOCAL` (`00:00:00:FF:FF:FF`): константа для перенаправлення трафіку на локальний адаптер петлі (loopback).

### Системні виклики та життєвий цикл сокета

Створення потокового сокета RFCOMM здійснюється викликом `socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)`. Семантика роботи з сокетом відповідає стандарту POSIX для потокових сокетів TCP:

#### 1. Серверний життєвий цикл

- **Прив'язка (`bind`)**: реєструє локальну адресу та номер Server Channel. Якщо вказати `rc_channel = 0`, ядро автоматично знайде перший вільний серверний канал у діапазоні `1..30` і закріпить його за сокетом. Дізнатися виділений номер можна за допомогою виклику `getsockname()`.
- **Переведення в стан очікування (`listen`)**: готує чергу вхідних з'єднань. Параметр `backlog` визначає максимальну кількість непідтверджених запитів на підключення (зазвичай `1` або `2`, оскільки Bluetooth-адаптер рідко обслуговує понад декілька одночасних клієнтів на одному каналі).
- **Прийом клієнта (`accept`)**: блокує потік виконання доти, доки віддалений клієнт не надішле кадр `SABM` на зареєстрований DLCI. Функція повертає новий файловий дескриптор підключеного клієнта і заповнює структуру `sockaddr_rc` його MAC-адресою.

#### 2. Клієнтський життєвий цикл

- **Встановлення зв'язку (`connect`)**: ініціює повний ланцюжок процедур: пейджинг віддаленого Bluetooth-пристрою, відкриття L2CAP-каналу, надсилання SABM на DLCI 0, узгодження PN і надсилання SABM на цільовий Server Channel. Якщо віддалений порт відкритий і служба запущена, виклик завершується успішно (`0`). Якщо порт закритий, ядро отримує кадр `DM` (Disconnected Mode) і повертає помилку `ECONNREFUSED`.

#### 3. Передача та прийом даних (`write` / `read` / `send` / `recv`)

Операції читання та запису є потоковими: ядро автоматично розбиває буфер прикладного застосунку на блоки, що не перевищують узгоджений розмір кадру MTU, додає заголовки RFCOMM, витрачає кредити CBFC та надсилає кадри в чергу L2CAP. 

Якщо лічильник кредитів передавача досягає нуля, системний виклик `write()` у блокуючому режимі переходить у стан сну доти, доки від приймача не надійде кадр поповнення кредитів `UIH` із прапорцем `P/F = 1`. У неблокуючому режимі (`O_NONBLOCK`) виклик негайно повертає помилку `EAGAIN` або `EWOULDBLOCK`.

### Неблокуючий ввід-вивід та мультиплексування подій (`epoll` / `select`)

Для побудови реактивних мережевих служб сокети RFCOMM підтримують роботу в неблокуючому режимі:

:::tabs
```c
#include <fcntl.h>
#include <unistd.h>

int set_socket_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <expected>
#include <system_error>

std::expected<void, std::error_code> set_socket_nonblocking(int fd) {
    int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

Особливості поведінки подій у системному виклику `epoll`:

- **Подія `EPOLLOUT`**: сигналізує, що сокет готовий до запису даних. Для RFCOMM це означає дві речі одночасно: наявність вільного місця в системному буфері сокета `SO_SNDBUF` та **наявність хоча б одного доступного кредиту CBFC**. Якщо кредити вичерпано, подія `EPOLLOUT` не виникатиме доти, доки віддалений пристрій не надішле кадр поповнення кредитів.
- **Подія `EPOLLIN`**: виникає, коли в чергу прийому надійшов хоча б один кадр даних `UIH`. Читання через `read()` повертає розпаковані корисні байти без заголовків RFCOMM.
- **Події `EPOLLRDHUP` та `EPOLLHUP`**: сигналізують про закриття каналу. `EPOLLRDHUP` виникає при отриманні кадру `DISC` від віддаленої сторони (напівзакрите з'єднання), а `EPOLLHUP` — при розриві базового з'єднання L2CAP або зникненні радіозв'язку (Link Loss).

### Налаштування параметрів сокета (`getsockopt` / `setsockopt`)

Для маніпуляції специфічними параметрами RFCOMM системні виклики використовують рівень протоколу `SOL_RFCOMM`:

```c
int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);
```

Специфікація BlueZ визначає такі ключові параметри:

#### `RFCOMM_CONNINFO` (лише читання)

Повертає службову інформацію про активне низькорівневе з'єднання контролера Bluetooth через структуру `struct rfcomm_conninfo` (цитата з `<bluetooth/rfcomm.h>`):

```c
struct rfcomm_conninfo {
    uint16_t hci_handle;  /* Дескриптор логічного з'єднання HCI ACL */
    uint8_t  dev_class[3];/* Клас віддаленого пристрою (Class of Device) */
};
```

Цей параметр дозволяє прикладному процесу дізнатися числовий індекс з'єднання HCI для подальшого опитування рівня радіосигналу RSSI (англ. *Received Signal Strength Indicator*) або статистики якості каналу зв'язку.

#### `RFCOMM_LM` (Link Mode — читання та запис)

Налаштовує політику безпеки та вимоги до автентифікації радіоканалу до початку передачі прикладних даних. Параметр приймає бітову маску цілочисельного типу:

- `RFCOMM_LM_AUTH` (`0x0002`): вимагати обов'язкової автентифікації пристроїв (перевірка зв'язування / PIN-коду / SSP). Якщо пристрої не спарені, ядро ініціює процедуру безпеки.
- `RFCOMM_LM_ENCRYPT` (`0x0004`): вимагати обов'язкового апаратного шифрування радіоканалу алгоритмом AES-CCM або E0. З'єднання без шифрування буде розірвано.
- `RFCOMM_LM_SECURE` (`0x0020`): вимагати максимального рівня безпеки (Secure Connections) із захистом від атак посередника (MITM) та довжиною ключа не менше 128 бітів.
- `RFCOMM_LM_MASTER` (`0x0001`): вимагати перемикання ролі в стан Master (ведучий пікомережі piconet).
- `RFCOMM_LM_RELIABLE` (`0x0010`): увімкнути режим підвищеної надійності каналу L2CAP.

### Керування буферами та розрахунок кредитів ядра

Підсистема ядра Linux динамічно узгоджує баланс кредитів CBFC на основі розміру прийомного буфера сокета `SO_RCVBUF` та максимального розміру блоку MTU:

```
Початкові кредити = Буфер прийому (SO_RCVBUF) / Узгоджений розмір кадру (MTU)
```

За замовчуванням ядро виділяє буфер розміром від 64 до 128 Кбайт, що при типовому MTU 1012 байтів забезпечує стартовий баланс у 60–120 кредитів. Якщо прикладний процес не встигає зчитувати дані з сокета, черга заповнюється, і ядро припиняє надсилання кадру поповнення кредитів (UIH з `P/F = 1`), автоматично призупиняючи віддаленого передавача.

Збільшення розміру буфера через `setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size))` дозволяє підвищити пропускну здатність каналу при високих мережевих затримках (RTT).

### Інтерфейс емуляції TTY-пристроїв (`/dev/rfcomm`)

Для програм, які працюють виключно з термінальними портами POSIX (наприклад, утиліти `minicom`, демони GPS `gpsd`, модемні служби PPP `pppd`), підсистема ядра надає керівний файл символьного пристрою `/dev/rfcomm` (major-номер 216, minor-номер 0).

За допомогою системного виклику `ioctl` до цього файлу користувацький простір може динамічно створювати повноцінні віртуальні порти `/dev/rfcomm0`..`/dev/rfcomm30`. Драйвер ядра зв'язує такий порт із підсистемою TTY line discipline, перетворюючи кожен виклик `write()` на відправку кадру RFCOMM, а отримані кадри — на символи вхідної черги термінала.

Структура запиту створення пристрою (цитата з `<bluetooth/rfcomm.h>`):

```c
struct rfcomm_dev_req {
    int16_t   dev_id;    /* Номер TTY-порту: 0 для /dev/rfcomm0, або -1 для автовибору */
    uint32_t  flags;     /* Бітова маска прапорців поведінки пристрою */
    bdaddr_t  src;       /* Локальна адреса адаптера (або BDADDR_ANY) */
    bdaddr_t  dst;       /* MAC-адреса віддаленого цільового пристрою */
    uint8_t   channel;   /* Номер Server Channel RFCOMM (від 1 до 30) */
};
```

Прапорці конфігурації `flags`:
- `RFCOMM_REUSE_DLC` (`0x0001`): дозволяє повторно використовувати вже відкрите з'єднання DLCI, якщо воно існує в мультиплексорі сесії.
- `RFCOMM_RELEASE_ONHUP` (`0x0002`): автоматично звільняти та видаляти TTY-пристрій із файлової системи, коли віддалена сторона розриває зв'язок (надсилає `DISC`) або застосунок закриває файловий дескриптор.
- `RFCOMM_HANGUP_NOW` (`0x0004`): негайно ініціювати відключення при отриманні команди розриву.

Керуючі коди `ioctl`:
- `RFCOMMCREATEDEV` (`_IOW('R', 200, int)`): реєструє новий пристрій `/dev/rfcommN` і починає підключення до віддаленої MAC-адреси.
- `RFCOMMRELEASEDEV` (`_IOW('R', 201, int)`): примусово розриває з'єднання та видаляє TTY-ноду.
- `RFCOMMGETDEVLIST` (`_IOR('R', 210, int)`): повертає буфер зі списком усіх наразі активних віртуальних портів RFCOMM та їхніх параметрів.
- `RFCOMMGETDEVINFO` (`_IOR('R', 211, int)`): повертає детальну діагностичну інформацію про конкретний числовий ідентифікатор пристрою.

Приклад створення TTY-порту через системний виклик `ioctl`:

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

int create_rfcomm_tty(const char *dest_mac, uint8_t channel) {
    int ctl_fd = open("/dev/rfcomm", O_RDWR);
    if (ctl_fd < 0) return -1;

    struct rfcomm_dev_req req;
    memset(&req, 0, sizeof(req));
    req.dev_id = -1; // Автоматично призначити перший вільний індекс (/dev/rfcomm0)
    req.flags = (1 << RFCOMM_RELEASE_ONHUP);
    req.channel = channel;
    str2ba(dest_mac, &req.dst);

    int dev_id = ioctl(ctl_fd, RFCOMMCREATEDEV, &req);
    close(ctl_fd);
    return dev_id;
}
```
```cpp
#include <string_view>
#include <expected>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

std::expected<int, std::error_code> create_rfcomm_tty(std::string_view dest_mac, uint8_t channel) {
    int ctl_fd = ::open("/dev/rfcomm", O_RDWR);
    if (ctl_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    struct rfcomm_dev_req req{};
    req.dev_id = -1; // Автоматичний вибір /dev/rfcommN
    req.flags = (1 << RFCOMM_RELEASE_ONHUP);
    req.channel = channel;
    
    std::string mac_str(dest_mac);
    if (str2ba(mac_str.c_str(), &req.dst) < 0) {
        ::close(ctl_fd);
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    int dev_id = ::ioctl(ctl_fd, RFCOMMCREATEDEV, &req);
    ::close(ctl_fd);
    
    if (dev_id < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return dev_id;
}
```
:::

### Налаштування параметрів TTY через `termios`

Коли віртуальний порт `/dev/rfcomm0` відкрито, керування його поведінкою здійснюється стандартною структурою `struct termios`:

- **Прапорець `CRTSCTS`**: вмикає апаратне квітування. Підсистема BlueZ транслює стан апаратних ліній у кадри `MSC`: зміна бітів RTS/CTS на боці Linux генерує відповідні оновлення поля `RTR` у сесії RFCOMM.
- **Прапорець `CLOCAL`**: якщо прапорець скинуто, закриття віддаленим модемом лінії Carrier Detect (`DV = 0` у кадрі MSC) надсилає процесу сигнал розриву зв'язку `SIGHUP`.
- **Швидкість (`cfsetispeed` / `cfsetospeed`)**: зміна бодрейту (наприклад, `B115200`) призводить до генерації кадру `RPN` на каналі керування DLCI 0, що інформує віддалений апаратний модуль про необхідність перемикання частоти UART.

### Програмна реєстрація служби в SDP через C API

Клієнтський пристрій не може знати заздалегідь, на якому саме номері Server Channel (від 1 до 30) сервер запустив свій порт SPP чи PBAP. Тому сервер після успішного виклику `bind()` та `listen()` реєструє запис служби в локальному демоні `sdpd` / `bluetoothd` за допомогою бібліотеки `libbluetooth`:

:::tabs
```c
#include <bluetooth/bluetooth.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>

sdp_session_t *register_spp_service(uint8_t channel, const char *service_name) {
    uuid_t root_uuid, l2cap_uuid, rfcomm_uuid, svc_uuid;
    sdp_list_t *root_list = 0, *l2cap_list = 0, *rfcomm_list = 0, *proto_list = 0, *access_proto_list = 0;
    sdp_data_t *channel_data = 0;

    sdp_record_t *record = sdp_record_alloc();

    // 1. Встановлення класу служби: Serial Port Profile (0x1101)
    sdp_uuid16_create(&svc_uuid, SERIAL_PORT_SVCLASS_ID);
    sdp_set_service_classes(record, sdp_list_append(0, &svc_uuid));

    // 2. Встановлення ідентифікатора кореневої групи (Public Browse Group: 0x1002)
    sdp_uuid16_create(&root_uuid, PUBLIC_BROWSE_GROUP);
    root_list = sdp_list_append(0, &root_uuid);
    sdp_set_browse_groups(record, root_list);

    // 3. Формування стека протоколів: L2CAP (0x0100) -> RFCOMM (0x0003, канал K)
    sdp_uuid16_create(&l2cap_uuid, L2CAP_UUID);
    l2cap_list = sdp_list_append(0, &l2cap_uuid);
    proto_list = sdp_list_append(0, l2cap_list);

    sdp_uuid16_create(&rfcomm_uuid, RFCOMM_UUID);
    channel_data = sdp_data_alloc(SDP_UINT8, &channel);
    rfcomm_list = sdp_list_append(0, &rfcomm_uuid);
    sdp_list_append(rfcomm_list, channel_data);
    sdp_list_append(proto_list, rfcomm_list);

    access_proto_list = sdp_list_append(0, proto_list);
    sdp_set_access_protos(record, access_proto_list);

    // 4. Текстова назва служби
    sdp_set_info_attr(record, service_name, "Provider", "SPP Service Description");

    // 5. Підключення до локального демона SDP та збереження запису
    sdp_session_t *session = sdp_connect(BDADDR_ANY, BDADDR_LOCAL, SDP_RETRY_IF_BUSY);
    sdp_record_register(session, record, 0);

    // Очищення виділених списків структури
    sdp_data_free(channel_data);
    sdp_list_free(l2cap_list, 0);
    sdp_list_free(rfcomm_list, 0);
    sdp_list_free(root_list, 0);
    sdp_list_free(proto_list, 0);
    sdp_list_free(access_proto_list, 0);

    return session; // Зберігати дескриптор сесії відкритим, поки служба працює
}
```
```cpp
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <bluetooth/bluetooth.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>

namespace bt {

struct SdpSessionDeleter {
    void operator()(sdp_session_t* s) const noexcept {
        if (s) sdp_close(s);
    }
};

using UniqueSdpSession = std::unique_ptr<sdp_session_t, SdpSessionDeleter>;

std::expected<UniqueSdpSession, std::error_code> register_spp_service(uint8_t channel, std::string_view name) {
    uuid_t root_uuid{}, l2cap_uuid{}, rfcomm_uuid{}, svc_uuid{};
    sdp_record_t* record = sdp_record_alloc();

    sdp_uuid16_create(&svc_uuid, SERIAL_PORT_SVCLASS_ID);
    sdp_set_service_classes(record, sdp_list_append(nullptr, &svc_uuid));

    sdp_uuid16_create(&root_uuid, PUBLIC_BROWSE_GROUP);
    sdp_list_t* root_list = sdp_list_append(nullptr, &root_uuid);
    sdp_set_browse_groups(record, root_list);

    sdp_uuid16_create(&l2cap_uuid, L2CAP_UUID);
    sdp_list_t* l2cap_list = sdp_list_append(nullptr, &l2cap_uuid);
    sdp_list_t* proto_list = sdp_list_append(nullptr, l2cap_list);

    sdp_uuid16_create(&rfcomm_uuid, RFCOMM_UUID);
    sdp_data_t* channel_data = sdp_data_alloc(SDP_UINT8, &channel);
    sdp_list_t* rfcomm_list = sdp_list_append(nullptr, &rfcomm_uuid);
    sdp_list_append(rfcomm_list, channel_data);
    sdp_list_append(proto_list, rfcomm_list);

    sdp_list_t* access_proto_list = sdp_list_append(nullptr, proto_list);
    sdp_set_access_protos(record, access_proto_list);

    std::string name_str(name);
    sdp_set_info_attr(record, name_str.c_str(), "Provider", "SPP Service Description");

    sdp_session_t* raw_session = sdp_connect(BDADDR_ANY, BDADDR_LOCAL, SDP_RETRY_IF_BUSY);
    if (!raw_session) {
        sdp_record_free(record);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    sdp_record_register(raw_session, record, 0);

    sdp_data_free(channel_data);
    sdp_list_free(l2cap_list, nullptr);
    sdp_list_free(rfcomm_list, nullptr);
    sdp_list_free(root_list, nullptr);
    sdp_list_free(proto_list, nullptr);
    sdp_list_free(access_proto_list, nullptr);

    return UniqueSdpSession(raw_session);
}

} // namespace bt
```
:::

### Пошук номера каналу на стороні клієнта через SDP

Клієнтський застосунок під час роботи виконує зворотну процедуру: підключається до SDP-сервера на віддаленому пристрої та запитує атрибути служби за її UUID:

1. Клієнт відкриває SDP-сесію до віддаленої MAC-адреси за допомогою виклику `sdp_connect(BDADDR_ANY, &remote_mac, SDP_RETRY_IF_BUSY)`.
2. За допомогою функції `sdp_service_search_attr_req()` формується запит пошуку служби з UUID `0x1101` (Serial Port Profile).
3. З отриманого списку атрибутів витягується послідовність `SDP_ATTR_PROTO_DESC_LIST` (список дескрипторів протоколів).
4. Програма ітерує за списком рівнів протоколу: перевіряє наявність `RFCOMM_UUID` і зчитує вкладений 8-бітний параметр, який і є потрібним номером Server Channel.
5. SDP-сесія закривається функцією `sdp_close()`, а отримане число підставляється в поле `rc_channel` клієнтського сокета перед викликом `connect()`.

### Системні права доступу та безпека в Linux

Робота з низькорівневими Bluetooth-сокетами в сучасних версіях Linux підпадає під обмеження системних привілеїв (capabilities):

- **Створення звичайного сокета RFCOMM (`AF_BLUETOOTH`)**: дозволено непривілейованим користувачам за умови, що Bluetooth-адаптер активовано (`hciconfig hci0 up` або через `rfkill unblock bluetooth`).
- **Створення нод `/dev/rfcomm` через `ioctl`**: вимагає членства користувача в системній групі `dialout` або наявності привілею `CAP_SYS_ADMIN` для запису в керівний файл `/dev/rfcomm`.
- **Реєстрація записів SDP**: вимагає взаємодії з системною шиною D-Bus або прав запису у сокет демона `sdpd` (`/var/run/sdp`), що типово потребує привілею `CAP_NET_BIND_SERVICE` або належності до групи `bluetooth`.

### Діагностика збоїв і типові пастки розробки

Під час практичної розробки мережевих служб на базі RFCOMM розробники найчастіше стикаються з трьома специфічними проблемами:

1. **Зависання `write()` при раптовому знеструмленні клієнта**: якщо віддалений пристрій раптово вимкнувся без надсилання кадру `DISC`, локальний сокет не дізнається про це миттєво. Дані успішно записуються в буфери L2CAP та контролера HCI, а системний виклик `write()` не повертає помилки доти, доки в радіомодемі не спливе тайм-аут нагляду зв'язку Link Supervision Timeout (LST, зазвичай від 5 до 20 секунд). Лише після цього ядро генерує помилку `ECONNRESET` або надсилає сигнал `SIGPIPE`. Для швидкого виявлення обривів прикладний протокол повинен реалізовувати періодичні контрольні повідомлення (heartbeat / ping).
2. **Конфлікт ролей Master/Slave у пікомережі (Piconet Role Switch)**: деякі Bluetooth-чипи (зокрема старі модулі гарнітур та промислові модеми) жорстко вимагають бути ведучим (Master) або веденим (Slave) у радіомережі. Якщо локальний адаптер не дозволяє зміну ролі, виклик `connect()` завершується помилкою `ECONNREFUSED`. Встановлення прапорця `RFCOMM_LM_MASTER` у параметрах `RFCOMM_LM` дозволяє форсувати бажану топологію радіозв'язку.
3. **Вичерпання кредитів при однопотоковому блокуючому читанні**: якщо клієнтський застосунок надсилає великий файл через `write()`, але не запускає паралельний потік для вичитування вхідних даних через `read()`, вхідний буфер заповнюється. Ядро припиняє видачу кредитів серверу, сервер зупиняє передачу, і програма потрапляє в стан взаємного блокування (deadlock). Розділення операцій прийому та відправки у незалежні потоки або перехід на подієвий неблокуючий цикл `epoll` є обов'язковим для двостороннього обміну.

### Діагностика та трасування за допомогою `btmon`

Для низькорівневого аналізу сесій RFCOMM у середовищі Linux використовується вбудована системна утиліта `btmon` (англ. *Bluetooth Monitor*). Вона перехоплює необроблені пакети HCI безпосередньо з ядра:

```bash
sudo btmon
```

Під час встановлення з'єднання `btmon` у реальному часі відображає двійковий дампи та декодовану структуру кадрів:
- перехід кадрів `SABM` та `UA` для каналу `DLCI 0`;
- вміст кадрів узгодження параметрів `PN` (значення MTU та біт увімкнення кредитів);
- повідомлення `MSC` із масками сигналів RTS/CTS/DTR;
- потокові кадри `UIH` із відображенням витрати та поповнення кредитів (Credits) у заголовку.

Для швидкої перевірки та зв'язування пристроїв у командному рядку використовується стандартна утиліта `rfcomm`:

```bash
# Зв'язати /dev/rfcomm0 з віддаленим сервером на каналі 1
sudo rfcomm bind 0 00:11:22:33:44:55 1

# Підключитися та запустити термінал
sudo rfcomm connect 0 00:11:22:33:44:55 1

# Звільнити віртуальний порт
sudo rfcomm release 0
```

### Коди помилок та діагностика

Системні виклики сокетів RFCOMM повертають стандартні числові коди помилок у змінній `errno`:

| Номер помилки | Константа errno | Опис та механізм виникнення в протоколі RFCOMM |
| :--- | :--- | :--- |
| `98` | `EADDRINUSE` | Серверний порт (1..30) уже зайнятий іншим активним сокетом або сервером на локальній машині. |
| `111` | `ECONNREFUSED` | Віддалений пристрій відхилив запит на підключення: надіслано кадр `DM` у відповідь на `SABM` (служба не запущена або порт закритий). |
| `110` | `ETIMEDOUT` | Вичерпано таймаут пейджингу радіоканалу Baseband або таймаут узгодження з'єднання L2CAP. |
| `113` | `EHOSTUNREACH` | Віддалений пристрій вимкнено або він перебуває поза зоною радіозв'язку (не відповідає на радіоопитування). |
| `32` | `EPIPE` | Віддалена сторона надіслала кадр `DISC`, або зв'язок обірвався під час спроби відправки даних через `write()`. |
| `104` | `ECONNRESET` | З'єднання примусово скинуто через тайм-аут нагляду зв'язку Link Supervision Timeout або апаратний збій контролера. |
| `11` | `EWOULDBLOCK` / `EAGAIN` | Сокет перебуває в неблокуючому режимі, а внутрішній буфер передачі заповнений або вичерпано доступні кредити CBFC. |
| `13` | `EACCES` | Помилка автентифікації: користувач відхилив запит спарювання або ввів невірний PIN-код під час перевірки `RFCOMM_LM_AUTH`. |
| `19` | `ENODEV` | Апаратний Bluetooth-адаптер було вимкнено або фізично витягнуто з USB-порту під час активної сесії. |

### Повний приклад: ехо-сервер та клієнт на C та C++

Нижче наведено повноцінні приклади реалізації клієнт-серверного обміну через сокети RFCOMM під Linux.

Сервер прив'язується до Server Channel `1`, переходить у режим прослуховування, приймає підключення від клієнта, зчитує вхідний рядок та надсилає його назад у вигляді ехо-відповіді. Клієнт підключається за вказаною MAC-адресою, передає тестове повідомлення і виводить отриману відповідь.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

int run_rfcomm_server(uint8_t channel) {
    int server_fd = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    if (server_fd < 0) {
        perror("Помилка створення сокета");
        return -1;
    }

    struct sockaddr_rc loc_addr;
    memset(&loc_addr, 0, sizeof(loc_addr));
    loc_addr.rc_family = AF_BLUETOOTH;
    loc_addr.rc_bdaddr = *BDADDR_ANY;
    loc_addr.rc_channel = channel;

    if (bind(server_fd, (struct sockaddr *)&loc_addr, sizeof(loc_addr)) < 0) {
        perror("Помилка bind на каналі RFCOMM");
        close(server_fd);
        return -1;
    }

    if (listen(server_fd, 1) < 0) {
        perror("Помилка listen");
        close(server_fd);
        return -1;
    }

    printf("RFCOMM сервер слухає канал %u...\n", channel);

    struct sockaddr_rc rem_addr;
    socklen_t opt = sizeof(rem_addr);
    int client_fd = accept(server_fd, (struct sockaddr *)&rem_addr, &opt);
    if (client_fd < 0) {
        perror("Помилка accept");
        close(server_fd);
        return -1;
    }

    char client_mac[18];
    ba2str(&rem_addr.rc_bdaddr, client_mac);
    printf("Клієнт підключився: %s (канал %u)\n", client_mac, rem_addr.rc_channel);

    char buf[1024];
    ssize_t bytes_read = read(client_fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("Отримано %zd байтів: %s\n", bytes_read, buf);
        write(client_fd, buf, bytes_read); // Ехо-відповідь назад
    }

    close(client_fd);
    close(server_fd);
    return 0;
}

int run_rfcomm_client(const char *dest_mac, uint8_t channel) {
    int sock = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);
    if (sock < 0) {
        perror("Помилка створення клієнтського сокета");
        return -1;
    }

    struct sockaddr_rc addr;
    memset(&addr, 0, sizeof(addr));
    addr.rc_family = AF_BLUETOOTH;
    addr.rc_channel = channel;
    if (str2ba(dest_mac, &addr.rc_bdaddr) < 0) {
        fprintf(stderr, "Некоректний формат MAC-адреси: %s\n", dest_mac);
        close(sock);
        return -1;
    }

    printf("Підключення до %s на каналі %u...\n", dest_mac, channel);
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка connect");
        close(sock);
        return -1;
    }

    const char *msg = "Hello RFCOMM from C";
    write(sock, msg, strlen(msg));

    char buf[1024];
    ssize_t bytes_read = read(sock, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        printf("Відповідь сервера: %s\n", buf);
    }

    close(sock);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/rfcomm.h>

namespace bt {

class RfcommSocket {
public:
    RfcommSocket() : fd_(::socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)) {}
    
    explicit RfcommSocket(int fd) noexcept : fd_(fd) {}
    
    ~RfcommSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    RfcommSocket(const RfcommSocket&) = delete;
    RfcommSocket& operator=(const RfcommSocket&) = delete;

    RfcommSocket(RfcommSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    RfcommSocket& operator=(RfcommSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    std::expected<void, std::error_code> bind_and_listen(uint8_t channel, int backlog = 1) {
        if (!is_valid()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        sockaddr_rc addr{};
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_bdaddr = *BDADDR_ANY;
        addr.rc_channel = channel;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(fd_, backlog) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

    std::expected<void, std::error_code> connect(std::string_view dest_mac, uint8_t channel) {
        if (!is_valid()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        sockaddr_rc addr{};
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_channel = channel;

        std::string mac_str(dest_mac);
        if (str2ba(mac_str.c_str(), &addr.rc_bdaddr) < 0) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        if (::connect(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

    std::expected<std::pair<RfcommSocket, std::string>, std::error_code> accept_client() {
        sockaddr_rc rem_addr{};
        socklen_t opt = sizeof(rem_addr);
        int client_fd = ::accept(fd_, reinterpret_cast<sockaddr*>(&rem_addr), &opt);
        if (client_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        char mac_str[18]{};
        ba2str(&rem_addr.rc_bdaddr, mac_str);
        return std::make_pair(RfcommSocket(client_fd), std::string(mac_str));
    }

    std::expected<size_t, std::error_code> send(std::span<const uint8_t> data) {
        ssize_t sent = ::write(fd_, data.data(), data.size());
        if (sent < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(sent);
    }

    std::expected<size_t, std::error_code> receive(std::span<uint8_t> buffer) {
        ssize_t recvd = ::read(fd_, buffer.data(), buffer.size());
        if (recvd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(recvd);
    }

private:
    int fd_{-1};
};

} // namespace bt

int main() {
    bt::RfcommSocket server;
    if (!server.is_valid()) {
        std::cerr << "Не вдалося відкрити Bluetooth сокет\n";
        return 1;
    }

    constexpr uint8_t channel = 1;
    if (auto res = server.bind_and_listen(channel); !res) {
        std::cerr << "Помилка запуску сервера: " << res.error().message() << '\n';
        return 1;
    }

    std::cout << "C++ RFCOMM сервер запущено на каналі " << int(channel) << '\n';

    auto client_res = server.accept_client();
    if (!client_res) {
        std::cerr << "Помилка accept: " << client_res.error().message() << '\n';
        return 1;
    }

    auto [client, client_mac] = std::move(*client_res);
    std::cout << "Підключено клієнта з адресою: " << client_mac << '\n';

    std::vector<uint8_t> buffer(1024);
    auto recv_res = client.receive(buffer);
    if (recv_res && *recv_res > 0) {
        std::string_view msg(reinterpret_cast<char*>(buffer.data()), *recv_res);
        std::cout << "Отримано повідомлення: " << msg << '\n';
        auto send_res = client.send(std::span(buffer.data(), *recv_res));
        if (!send_res) {
            std::cerr << "Помилка відправки ехо: " << send_res.error().message() << '\n';
        }
    }

    return 0;
}
```
:::

Для успішної компіляції програм під Linux необхідно встановити пакет заголовних файлів ядра та бібліотеку розробки BlueZ (`libbluetooth-dev` у дистрибутивах Debian/Ubuntu або `bluez-libs-devel` у Fedora/RHEL). Збирання виконується з обов'язковою лінковкою бібліотеки:

```bash
gcc -Wall -O2 server.c -lbluetooth -o rfcomm_server
g++ -std=c++23 -Wall -O2 server.cpp -lbluetooth -o rfcomm_server_cpp
```
