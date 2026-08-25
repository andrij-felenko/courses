# ⚙️ Діагностика помилок та стану вузла CAN у Linux SocketCAN

Підсистема SocketCAN ядра Linux перетворює апаратні переривання CAN-контролера про виявлені бітові збої, порушення стафінгу та переходи станів у спеціальні кадри помилок, доступні програмі через звичайний мережевий сокет. Цей практичний інструментарій демонструє, як налаштувати операційну систему на перехоплення таких подій, розібрати внутрішню структуру кадру помилки, прочитати апаратні лічильники TEC/REC і побудувати надійний механізм відновлення після критичного переходу в стан Bus-Off у просторі користувача.

За замовчуванням сирий сокет `SOCK_RAW` відфільтровує службові кадри помилок і передає додатку лише валідні пакети даних. Якщо мережевий дріт пошкоджено, відсутній термінальний резистор 120 Ом або на лінії виникло коротке замикання, програма без спеціального налаштування сокета просто перестане отримувати повідомлення, не маючи жодної діагностичної інформації про причину зупинки зв'язку.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ПРОСТІР КОРИСТУВАЧА                              │
│                                                                             │
│   socket(PF_CAN, SOCK_RAW, CAN_RAW)                                         │
│   setsockopt(fd, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(...))   │
│   read(fd, &frame, sizeof(frame))  ───►  Розбір can_id & CAN_ERR_FLAG       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Системний виклик read()
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                                ЯДРО LINUX                                   │
│                                                                             │
│   Драйвер CAN (напр. mcp251x, flexcan, c_can, bxcan, ti_k3_mcan)            │
│   1. Апаратне переривання помилки контролера                                │
│   2. Вичитування регістрів статусу та лічильників TEC/REC                   │
│   3. Синтез alloc_can_err_skb() з прапорцем CAN_ERR_FLAG                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Лінії TX/RX
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                          АПАРАТНИЙ КОНТРОЛЕР CAN                            │
│   Фіксація Bit/Stuff/CRC/Form/ACK Error ──► Інкремент TEC/REC ──► Переривання│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Архітектура SocketCAN та життєвий цикл кадру в ядрі

На відміну від традиційного підходу UNIX до послідовних портів через символьні пристрої (наприклад, `/dev/ttyUSB0` для RS-232 чи пропрієтарні вузли `/dev/can0`), архітектура SocketCAN, спочатку розроблена компанією Volkswagen Research і інтегрована в ядро Linux починаючи з версії 2.6.25, представляє контролери CAN як повноцінні мережеві інтерфейси (`struct net_device`). Таке архітектурне рішення надає системним розробникам низку принципових переваг:

1. **Мультиплексування процесів та ізоляція:** десятки незалежних користувацьких процесів можуть одночасно відкривати незалежні сокети до одного інтерфейсу `can0`. Кілька програм можуть паралельно слухати потік або надсилати повідомлення без необхідності створення центрального процесу-посередника (демона маршрутизації), оскільки арбітраж доступу та черги пакетів повністю керуються мережевою підсистемою ядра.
2. **Апаратна фільтрація та нульові накладні витрати на перемикання контексту:** ядро Linux підтримує накладання бітових масок фільтрації безпосередньо в обробнику переривань. Непотрібні кадри відсікаються до того, як ядро виконає дорогі операції копіювання даних та пробудження процесу, що критично для високонавантажених шин із частотою передачі в тисячі пакетів на секунду.
3. **Єдиний абстрактний інтерфейс обробки помилок:** апаратні відмінності між різними мікроконтролерами (наприклад, інтегрованими FlexCAN від NXP, FDCAN від STMicroelectronics або зовнішніми контролерами Microchip MCP2515 на шині SPI) повністю приховуються драйверами ядра. Коли контролер фіксує бітовий збій, функція драйвера `alloc_can_err_skb()` виділяє мережевий буфер `sk_buff`, формує стандартизований псевдокадр помилки й передає його в чергу сокета з увімкненим фільтром `CAN_RAW_ERR_FILTER`.

Життєвий цикл передачі кадру в ядрі реалізує механізм локального лупбеку (*Local Loopback*): коли сокет викликає `write()`, ядро передає пакет у чергу драйвера `ndo_start_xmit()`. Контролер записує пакет у буфер відправки й зберігає його копію у черзі відлуння (`can_put_echo_skb()`). Лише після того, як контролер отримає апаратне підтвердження ACK від шини й згенерує переривання успішної передачі, функція `can_get_echo_skb()` передає копію повідомлення іншим локальним сокетам із міткою часу апаратного передавання. Якщо ж передача зірвалася через помилку арбітражу або заваду на лінії, ядро знищує ехо-пакет і генерує `alloc_can_err_skb()`.

### Конфігурація інтерфейсу через Netlink та діагностика через sysfs

Керування CAN-інтерфейсами в сучасних дистрибутивах Linux здійснюється через підсистему Netlink за допомогою утиліти `ip` з пакету `iproute2`. Тут налаштовуються бітові швидкості, параметри квантів часу та правила поведінки при аварійній ізоляції:

```bash
# Встановлення номінальної швидкості 500 кбіт/с та автоматичного виходу з Bus-Off через 100 мс
sudo ip link set can0 type can bitrate 500000 restart-ms 100

# Для інтерфейсів CAN FD: номінальна швидкість 500 кбіт/с, фаза даних 2 Мбіт/с
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on restart-ms 100

# Підняття інтерфейсу
sudo ip link set can0 up

# Перевірка поточного стану контролера, лічильників та розширеної статистики
ip -details -statistics link show can0
```

У виводі команди `ip` блок статистики містить життєво важливі діагностичні метрики:
- `state`: поточний стан скінченного автомата контролера (`ERROR-ACTIVE`, `ERROR-WARNING`, `ERROR-PASSIVE` або `BUS-OFF`);
- `bus_error`: загальна кількість зафіксованих фізичних помилок на лінії;
- `arbitration_lost`: кількість випадків втрати арбітражу під час передачі;
- `error_warning`: лічильник переходів через поріг `TEC/REC ≥ 96`;
- `error_passive`: лічильник переходів у пасивний стан `TEC/REC ≥ 128`;
- `bus_off`: кількість переходів у стан аварійної ізоляції `TEC > 255`.

Ці ж метрики доступні для читання системними скриптами моніторингу через файлову систему `sysfs` у каталозі `/sys/class/net/can0/can_stats/`. Наприклад, файл `/sys/class/net/can0/can_stats/bus_error` повертає монотонно зростаючий лічильник усіх зафіксованих спотворень сигналу з моменту завантаження операційної системи.

### Внутрішня структура кадру помилки SocketCAN

Кадр помилки доставляється додатку в стандартній структурі `struct can_frame` (визначеній у заголовному файлі `<linux/can.h>`). Розпізнавання та інтерпретація вмісту здійснюються за такими правилами:

1. **Ідентифікатор (`can_id`)**:
   - Біт `CAN_ERR_FLAG` (біт 29, шістнадцяткова маска `0x20000000U`) встановлений у `1`. Це свідчить про те, що даний кадр не є звичайним пакетом даних.
   - Маска класу помилки (`can_id & CAN_ERR_MASK`, де `CAN_ERR_MASK = 0x1FFFFFFFU`):
     - `CAN_ERR_TX_TIMEOUT` (`0x00000001U`) — таймаут черги передавача;
     - `CAN_ERR_LOSTARB` (`0x00000002U`) — втрата арбітражу. Номер біта, на якому вузол поступився шиною, записується в байт `data[0]`;
     - `CAN_ERR_CRTL` (`0x00000004U`) — зміна стану контролера (перехід порогів лічильників);
     - `CAN_ERR_PROT` (`0x00000008U`) — порушення протоколу CAN (деталізовано в байтах `data[2]` та `data[3]`);
     - `CAN_ERR_TRX` (`0x00000010U`) — апаратна несправність фізичного трансивера;
     - `CAN_ERR_ACK` (`0x00000020U`) — відсутність підтвердження ACK від інших вузлів;
     - `CAN_ERR_BUSOFF` (`0x00000040U`) — перехід контролера в стан Bus-Off (повна ізоляція);
     - `CAN_ERR_BUSERROR` (`0x00000080U`) — спотворення сигналу на фізичній лінії;
     - `CAN_ERR_RESTARTED` (`0x00000100U`) — успішне відновлення контролера після стану Bus-Off.

2. **Байт `data[1]` (Деталізація зміни стану контролера `CAN_ERR_CRTL`)**:
   - `CAN_ERR_CRTL_RX_WARNING` (`0x04`) — `REC ≥ 96`;
   - `CAN_ERR_CRTL_TX_WARNING` (`0x08`) — `TEC ≥ 96`;
   - `CAN_ERR_CRTL_RX_PASSIVE` (`0x10`) — `REC ≥ 128` (приймач перейшов у стан Error Passive);
   - `CAN_ERR_CRTL_TX_PASSIVE` (`0x20`) — `TEC ≥ 128` (передавач перейшов у стан Error Passive);
   - `CAN_ERR_CRTL_ACTIVE` (`0x40`) — лічильники зменшилися, контролер повернувся в стан Error Active.

3. **Байт `data[2]` (Тип порушення протоколу `CAN_ERR_PROT`)**:
   - `CAN_ERR_PROT_BIT` (`0x01`) — помилка рівня біта (*Bit Error*);
   - `CAN_ERR_PROT_FORM` (`0x02`) — помилка форми кадру (*Form Error*);
   - `CAN_ERR_PROT_STUFF` (`0x04`) — порушення правила 5 однакових бітів (*Stuff Error*);
   - `CAN_ERR_PROT_BIT0` (`0x08`) — передавач виставив домінантний 0, але прочитав рецесивну 1;
   - `CAN_ERR_PROT_BIT1` (`0x10`) — передавач виставив рецесивну 1, але прочитав домінантний 0;
   - `CAN_ERR_PROT_OVERLOAD` (`0x20`) — зафіксовано кадр перевантаження;
   - `CAN_ERR_PROT_ACTIVE` (`0x40`) — помилка виникла під час активного прапорця помилки;
   - `CAN_ERR_PROT_TX` (`0x80`) — бітовий збій стався під час власної передачі кадру даним вузлом.

4. **Байт `data[3]` (Місце виникнення помилки в структурі кадру)**:
   Містить код поля, у якому стався збій: `CAN_ERR_PROT_LOC_SOF` (`0x03`), `CAN_ERR_PROT_LOC_DLC` (`0x0B`), `CAN_ERR_PROT_LOC_DATA` (`0x0A`), `CAN_ERR_PROT_LOC_CRC_SEQ` (`0x12`), `CAN_ERR_PROT_LOC_ACK` (`0x19`), `CAN_ERR_PROT_LOC_EOF` (`0x1A`).

5. **Байт `data[4]` (Стан трансивера `CAN_ERR_TRX`)**:
   Використовується інтелектуальними трансиверами з шиною діагностики (наприклад, NXP TJA1043) для сповіщення про фізичні замикання: `CAN_ERR_TRX_CANH_SHORT_TO_GND`, `CAN_ERR_TRX_CANH_SHORT_TO_VCC`, `CAN_ERR_TRX_CANL_SHORT_TO_GND`.

6. **Байти `data[6]` та `data[7]` (Значення лічильників помилок)**:
   Якщо апаратний драйвер контролера підтримує зчитування поточних регістрів лічильників в обробнику переривання, байт `data[6]` містить точне значення `TEC`, а байт `data[7]` — значення `REC`.

### Особливості роботи з кадрами CAN FD

Для роботи з розширеними кадрами CAN FD у сокеті вмикається опція `CAN_RAW_FD_FRAMES` через `setsockopt`:

:::tabs
```c
int enable_canfd = 1;
if (setsockopt(s, SOL_CAN_RAW, CAN_RAW_FD_FRAMES, &enable_canfd, sizeof(enable_canfd)) < 0) {
    perror("Помилка ввімкнення CAN FD");
}
```
```cpp
int enable_canfd = 1;
if (::setsockopt(sock_fd, SOL_CAN_RAW, CAN_RAW_FD_FRAMES, &enable_canfd, sizeof(enable_canfd)) < 0) {
    std::cerr << "Помилка ввімкнення CAN FD: " << std::strerror(errno) << std::endl;
}
```
:::

При цьому читання здійснюється в структуру `struct canfd_frame`, де поле `len` може набувати значень до 64 байтів, а поле `flags` містить статусний біт `CANFD_ESI` (*Error State Indicator*). Якщо інший вузол мережі перейшов у стан `Error Passive`, біт `CANFD_ESI` у його переданих пакетах буде встановлений у `1`, дозволяючи програмі оперативно фіксувати деградацію сусідніх вузлів ще до виникнення збоїв зв'язку.

### Вплив помилок кадру на протоколи вищого рівня (ISO-TP та UDS)

У реальних автомобільних системах поверх сирих кадрів CAN функціонує транспортний рівень **ISO-TP (ISO 15765-2)** та діагностичний протокол **UDS (ISO 14229)**. Коли на канальному рівні стається серія помилок, це безпосередньо впливає на роботу стеків вищого рівня:

1. **Фрагментація та таймаут `N_Bs` (Block Size):** під час передачі довгого пакету прошивки (наприклад, блоку 4 Кб через послідовні кадри Consecutive Frames) знищення одного кадру активним прапорцем помилки призводить до зупинки потоку. Передавач витрачає час на ретрансляцію, що може спричинити вичерпання таймауту `N_Bs` (зазвичай 1000 мс) на стороні діагностичного сканера.
2. **Негативні відповіді UDS (NRC — Negative Response Code):** якщо через помилки в шині вузол переходить у `Bus Off` під час запису конфігурації, діагностичний стек повертає клієнту помилки `NRC 0x78` (*Response Pending*) або `NRC 0x72` (*General Programming Failure*). Розуміння статусів SocketCAN дозволяє системному сервісу відрізнити помилку логіки прошивки від фізичного збою передачі даних у кабелі.

### Налаштування маски перехоплення помилок у додатку

Для того, щоб сокет почав приймати синтезовані ядром кадри помилок, програма повинна явно сконфігурувати опцію сокета `CAN_RAW_ERR_FILTER` через системний виклик `setsockopt`. За замовчуванням значення цієї маски дорівнює нулю (усі кадри помилок блокуються).

Маска формується побітовим логічним АБО з констант класів помилок, визначених у файлі `<linux/can/error.h>`:

:::tabs
```c
can_err_mask_t err_mask = (CAN_ERR_TX_TIMEOUT | CAN_ERR_LOSTARB |
                           CAN_ERR_CRTL | CAN_ERR_PROT |
                           CAN_ERR_TRX | CAN_ERR_ACK |
                           CAN_ERR_BUSOFF | CAN_ERR_BUSERROR |
                           CAN_ERR_RESTARTED);
```
```cpp
constexpr can_err_mask_t err_mask = (CAN_ERR_TX_TIMEOUT | CAN_ERR_LOSTARB |
                                     CAN_ERR_CRTL | CAN_ERR_PROT |
                                     CAN_ERR_TRX | CAN_ERR_ACK |
                                     CAN_ERR_BUSOFF | CAN_ERR_BUSERROR |
                                     CAN_ERR_RESTARTED);
```
:::

Якщо розробник бажає відстежувати абсолютно всі можливі несправності шини, застосовується макрос `CAN_ERR_MASK` (`0x1FFFFFFFU`), що вмикає перехоплення всіх відомих класів помилок. Додатково можна комбінувати фільтри помилок зі звичайними фільтрами ідентифікаторів повідомлень через `CAN_RAW_FILTER`, передаючи масив структур `struct can_filter`.

### Повна програмна реалізація діагностичного монітора

Нижче наведено робочий діагностичний монітор двома мовами (C та ідіоматичний C++20). Програма відкриває сокет CAN, конфігурує фільтр помилок через `setsockopt`, переводить читання в цикл і виводить детальний розбір усіх інцидентів на шині.

У версії на C++ застосовано сучасні патерни проектування: інкапсуляцію файлового дескриптора в RAII-клас `CanSocket` із забороною копіювання та підтримкою переміщення, повернення помилок через типізований контейнер `std::expected<CanSocket, std::error_code>`, використання `std::string_view` для передачі імені інтерфейсу без динамічного виділення пам'яті та строгу типізацію виводу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

void print_can_error(const struct can_frame *f) {
    if (!(f->can_id & CAN_ERR_FLAG)) {
        return;
    }

    uint32_t err_class = f->can_id & CAN_ERR_MASK;
    printf("[CAN ERROR] Клас: 0x%08X", err_class);

    if (err_class & CAN_ERR_TX_TIMEOUT) {
        printf(" | TX Timeout");
    }
    if (err_class & CAN_ERR_LOSTARB) {
        printf(" | Втрата арбітражу на біті %d", f->data[0]);
    }
    if (err_class & CAN_ERR_ACK) {
        printf(" | ACK Error (жоден вузол не відповів)");
    }
    if (err_class & CAN_ERR_BUSOFF) {
        printf(" | КРИТИЧНО: Стан BUS-OFF (ізоляція від шини)");
    }
    if (err_class & CAN_ERR_BUSERROR) {
        printf(" | Bus Error (фізичне спотворення лінії)");
    }
    if (err_class & CAN_ERR_RESTARTED) {
        printf(" | Відновлення контролера (Restarted)");
    }

    if (err_class & CAN_ERR_CRTL) {
        printf(" | Зміна стану:");
        if (f->data[1] & CAN_ERR_CRTL_RX_WARNING) printf(" RxWarn(REC>=96)");
        if (f->data[1] & CAN_ERR_CRTL_TX_WARNING) printf(" TxWarn(TEC>=96)");
        if (f->data[1] & CAN_ERR_CRTL_RX_PASSIVE) printf(" RxPassive(REC>=128)");
        if (f->data[1] & CAN_ERR_CRTL_TX_PASSIVE) printf(" TxPassive(TEC>=128)");
        if (f->data[1] & CAN_ERR_CRTL_ACTIVE)     printf(" Error-Active");
    }

    if (err_class & CAN_ERR_PROT) {
        printf(" | Протокол:");
        if (f->data[2] & CAN_ERR_PROT_BIT)   printf(" Bit-Error");
        if (f->data[2] & CAN_ERR_PROT_FORM)  printf(" Form-Error");
        if (f->data[2] & CAN_ERR_PROT_STUFF) printf(" Stuff-Error");
        if (f->data[2] & CAN_ERR_PROT_TX)    printf(" (при передачі)");
        else                                 printf(" (при прийомі)");
    }

    if (f->data[6] != 0 || f->data[7] != 0) {
        printf(" | Лічильники: TEC=%u, REC=%u", f->data[6], f->data[7]);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "can0";
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) {
        perror("Помилка відкриття сокета CAN");
        return 1;
    }

    struct ifreq ifr;
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) {
        perror("Не знайдено CAN інтерфейс");
        close(s);
        return 1;
    }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    can_err_mask_t err_mask = CAN_ERR_MASK; // перехоплювати всі класи помилок
    if (setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask)) < 0) {
        perror("Помилка налаштування фільтра помилок");
        close(s);
        return 1;
    }

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка прив'язки сокета");
        close(s);
        return 1;
    }

    printf("Діагностику запущено на інтерфейсі %s. Очікування подій...\n", ifname);

    struct can_frame frame;
    while (1) {
        ssize_t nbytes = read(s, &frame, sizeof(struct can_frame));
        if (nbytes < 0) {
            perror("Помилка читання з CAN сокета");
            break;
        }
        if (frame.can_id & CAN_ERR_FLAG) {
            print_can_error(&frame);
        }
    }

    close(s);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <expected>
#include <span>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

class CanSocket {
    int fd_{-1};

public:
    explicit CanSocket(int fd) noexcept : fd_{fd} {}
    ~CanSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    CanSocket(const CanSocket &) = delete;
    CanSocket &operator=(const CanSocket &) = delete;

    CanSocket(CanSocket &&other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    CanSocket &operator=(CanSocket &&other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    static std::expected<CanSocket, std::error_code> open(std::string_view ifname, can_err_mask_t err_mask) {
        int sock = ::socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (sock < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), IFNAMSIZ - 1);
        if (::ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
            auto ec = std::error_code(errno, std::generic_category());
            ::close(sock);
            return std::unexpected(ec);
        }

        if (::setsockopt(sock, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask)) < 0) {
            auto ec = std::error_code(errno, std::generic_category());
            ::close(sock);
            return std::unexpected(ec);
        }

        struct sockaddr_can addr{};
        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (::bind(sock, reinterpret_cast<struct sockaddr *>(&addr), sizeof(addr)) < 0) {
            auto ec = std::error_code(errno, std::generic_category());
            ::close(sock);
            return std::unexpected(ec);
        }

        return CanSocket{sock};
    }

    std::expected<struct can_frame, std::error_code> read_frame() const {
        struct can_frame frame{};
        ssize_t n = ::read(fd_, &frame, sizeof(frame));
        if (n < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return frame;
    }
};

void decode_error_frame(const struct can_frame &frame) {
    if (!(frame.can_id & CAN_ERR_FLAG)) return;

    const uint32_t err_class = frame.can_id & CAN_ERR_MASK;
    std::cout << "[CAN++ ERROR] Клас: 0x" << std::hex << err_class << std::dec;

    if (err_class & CAN_ERR_TX_TIMEOUT) std::cout << " | TX-Timeout";
    if (err_class & CAN_ERR_LOSTARB)    std::cout << " | Втрата арбітражу біт #" << static_cast<int>(frame.data[0]);
    if (err_class & CAN_ERR_ACK)        std::cout << " | ACK Error (відсутня відповідь)";
    if (err_class & CAN_ERR_BUSOFF)     std::cout << " | АВАРІЯ: BUS-OFF (ізоляція)";
    if (err_class & CAN_ERR_BUSERROR)   std::cout << " | Bus-Error (лінія)";
    if (err_class & CAN_ERR_RESTARTED)  std::cout << " | Авто-перезапуск";

    if (err_class & CAN_ERR_CRTL) {
        std::cout << " | Стан контролера:";
        const uint8_t ctrl = frame.data[1];
        if (ctrl & CAN_ERR_CRTL_RX_WARNING) std::cout << " RxWarn(REC>=96)";
        if (ctrl & CAN_ERR_CRTL_TX_WARNING) std::cout << " TxWarn(TEC>=96)";
        if (ctrl & CAN_ERR_CRTL_RX_PASSIVE) std::cout << " RxPassive(REC>=128)";
        if (ctrl & CAN_ERR_CRTL_TX_PASSIVE) std::cout << " TxPassive(TEC>=128)";
        if (ctrl & CAN_ERR_CRTL_ACTIVE)     std::cout << " Error-Active";
    }

    if (err_class & CAN_ERR_PROT) {
        std::cout << " | Порушення протоколу:";
        const uint8_t prot = frame.data[2];
        if (prot & CAN_ERR_PROT_BIT)   std::cout << " BitError";
        if (prot & CAN_ERR_PROT_FORM)  std::cout << " FormError";
        if (prot & CAN_ERR_PROT_STUFF) std::cout << " StuffError";
        std::cout << ((prot & CAN_ERR_PROT_TX) ? " (при передачі)" : " (при прийомі)");
    }

    if (frame.data[6] != 0 || frame.data[7] != 0) {
        std::cout << " | TEC=" << static_cast<int>(frame.data[6])
                  << ", REC=" << static_cast<int>(frame.data[7]);
    }
    std::cout << std::endl;
}

int main(int argc, char *argv[]) {
    const std::string_view ifname = (argc > 1) ? argv[1] : "can0";
    auto sock_res = CanSocket::open(ifname, CAN_ERR_MASK);
    if (!sock_res) {
        std::cerr << "Не вдалося відкрити CAN інтерфейс: " << sock_res.error().message() << std::endl;
        return 1;
    }

    const auto &can = *sock_res;
    std::cout << "C++ діагностику запущено на " << ifname << std::endl;

    while (true) {
        auto frame_res = can.read_frame();
        if (!frame_res) {
            std::cerr << "Помилка читання: " << frame_res.error().message() << std::endl;
            break;
        }
        if (frame_res->can_id & CAN_ERR_FLAG) {
            decode_error_frame(*frame_res);
        }
    }
    return 0;
}
```
:::

### Методика емуляції несправностей та лабораторного тестування

Під час розробки бортового програмного забезпечення перевірка обробки критичних збоїв ускладнюється тим, що на справному фізичному стенді помилки виникають вкрай рідко. Для повноцінного тестування застосовують такі інструменти:

1. **Використання утиліти `candump` з увімкненим фільтром помилок:**
   Утиліта `candump` з пакету `can-utils` дозволяє переглядати кадри помилок безпосередньо в терміналі:
   ```bash
   # Захоплення як звичайних повідомлень, так і всіх кадрів помилок з детальними прапорцями
   candump -td -e can0,0:0,#FFFFFFFF
   ```
   Прапорець `-e` вмикає отримання Error Frames, а маска `0:0,#FFFFFFFF` підписує утиліту на перехоплення всіх помилкових бітових класів.

2. **Емуляція помилок через інструмент `cangen`:**
   Утиліта генерації трафіку `cangen` має вбудовану опцію примусового створення помилок у кадрі:
   ```bash
   # Генерація випадкових пакетів зі штучним внесенням помилок у 10% переданих кадрів
   cangen can0 -g 10 -e
   ```

3. **Створення тестового середовища Virtual CAN (`vcan`):**
   Для тестування логіки додатку на комп'ютері без реального CAN-адаптера створюється віртуальний інтерфейс:
   ```bash
   sudo modprobe vcan
   sudo ip link add dev vcan0 type vcan
   sudo ip link set vcan0 up
   ```
   Віртуальний інтерфейс `vcan0` підтримує надсилання синтетичних кадрів помилок, що дозволяє покрити юніт-тестами всі гілки обробки переходів між станами `Error Passive` та `Bus Off`.

### Автономне відстеження таймаутів: Broadcast Manager (BCM)

Окрім сирих сокетів `SOCK_RAW`, підсистема SocketCAN містить спеціалізований протокольний модуль **Broadcast Manager (BCM)**, доступний через тип сокета `SOCK_DGRAM` з протоколом `CAN_BCM`. Модуль BCM функціонує безпосередньо всередині ядра Linux і дозволяє делегувати операційній системі періодичну відправку та контроль таймаутів вхідних повідомлень.

Якщо якийсь вузол на шині перестав виходити на зв'язок (наприклад, через вимикання живлення або перехід у стан Bus Off), конфігурація фільтра `RX_SETUP` з ненульовим таймаутом `ival2` змушує ядро самостійно згенерувати подію `RX_TIMEOUT` без необхідності періодичного пробудження процесу користувача через користувацькі таймери. Це принципово знижує навантаження на процесор у складних телеметричних системах.

### Інтеграція в асинхронні подієві цикли (epoll та non-blocking I/O)

У реальних високопродуктивних серверах збору телеметрії або контролерах автономного руху блокуюче читання сокета в окремому потоці створює надлишкові накладні витрати на синхронізацію. Сокет SocketCAN повністю підтримує неблокуючий режим введення-виведення та системний виклик `epoll`:

:::tabs
```c
// Переведення сокета в неблокуючий режим
int flags = fcntl(sock_fd, F_GETFL, 0);
fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

// Реєстрація дескриптора в epoll
int epoll_fd = epoll_create1(0);
struct epoll_event ev;
memset(&ev, 0, sizeof(ev));
ev.events = EPOLLIN | EPOLLET; // Edge-triggered режим
ev.data.fd = sock_fd;
epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sock_fd, &ev);
```
```cpp
// Переведення сокета в неблокуючий режим
int flags = ::fcntl(sock_fd, F_GETFL, 0);
::fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

// Реєстрація дескриптора в epoll
int epoll_fd = ::epoll_create1(0);
struct epoll_event ev{};
ev.events = EPOLLIN | EPOLLET; // Edge-triggered режим
ev.data.fd = sock_fd;
::epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sock_fd, &ev);
```
:::

Такий підхід дозволяє одному робочому потоку ефективно обслуговувати одночасно кілька фізичних шин CAN (`can0`, `can1`, `can2`), мережеві інтерфейси Ethernet і таймери без створення окремих потоків ОС.

### Апаратне маркування часу (Hardware Timestamping)

Для прецизійної кореляції моментів виникнення помилок із фізичними процесами (наприклад, увімкненням контактора високовольтної батареї або пуском соленоїда) стандартний системний годинник ядра дає похибку в десятки мікросекунд через затримку обробки переривань. Професійні контролери CAN підтримують апаратне маркування часу безпосередньо в момент фіксації біта SOF.

Ввімкнення апаратних міток часу в сокеті здійснюється через опцію `SO_TIMESTAMPING`:

:::tabs
```c
int val = SOF_TIMESTAMPING_RX_HARDWARE | SOF_TIMESTAMPING_RAW_HARDWARE;
if (setsockopt(s, SOL_SOCKET, SO_TIMESTAMPING, &val, sizeof(val)) < 0) {
    perror("Помилка налаштування апаратних міток часу");
}
```
```cpp
int val = SOF_TIMESTAMPING_RX_HARDWARE | SOF_TIMESTAMPING_RAW_HARDWARE;
if (::setsockopt(sock_fd, SOL_SOCKET, SO_TIMESTAMPING, &val, sizeof(val)) < 0) {
    std::cerr << "Помилка міток часу: " << std::strerror(errno) << std::endl;
}
```
:::

При цьому замість звичайного виклику `read()` використовується системний виклик `recvmsg()`, що повертає мітку часу високої точності в структурі допоміжних даних `cmsghdr`.

### Типові пастки реалізації та правила промислової розробки

1. **Нескінченний шторм переривань при відсутності другого вузла (ACK Error storm)**:
   Якщо вузол намагається надіслати кадр на шину, де немає жодного іншого увімкненого приймача (наприклад, під час тестування окремої плати на столі), передавач отримуватиме ACK Error на кожній спробі. Контролер збільшуватиме `TEC += 8`, перейде в стан `Error Passive` на 16-й спробі, але **ніколи не перейде в Bus-Off** через спеціальне правило стандарту ISO 11898-1: коли лічильник `TEC` досягає значення 128 виключно через відсутність підтвердження ACK, подальші помилки ACK не збільшують `TEC` понад 128! Контролер залишатиметься в `Error Passive` і нескінченно повторюватиме спроби передачі з максимальною частотою, забиваючи системну чергу ядра Linux мільйонами переривань. Для запобігання цьому явища в драйверах налаштовують тайм-аути спроб передачі або переводять контролер у режим прослуховування (*Listen-Only Mode*).

2. **Зависання в стані Bus-Off без таймера автоматичного перезапуску**:
   Якщо мережевий інтерфейс налаштовано без параметру `restart-ms`, перехід у `Bus-Off` вимикає апаратний периферійний модуль назавжди. Контролер залишається у відключеному стані доти, доки користувач або системний сервіс явно не виконає системний виклик або команду:
   ```bash
   sudo ip link set can0 type can restart
   ```
   У вбудованих системах керування (автомобільних блоках ECU, польотних контролерах дронів, промислових контролерах PLC) обов'язково встановлюють ненульове значення `restart-ms` (типово від 100 до 500 мс) або реалізують асинхронний моніторинг прапорця `CAN_ERR_BUSOFF` у сокеті з подальшим викликом перезапуску через інтерфейс Netlink.

3. **Переповнення черги `RX-FIFO` та помилка `ENOBUFS`**:
   Під час виникнення серйозної фізичної несправності на лінії (наприклад, замикання CAN_H на масу) контролер може генерувати тисячі кадрів помилок за секунду. Якщо користувацький процес читає дані недостатньо швидко, буфер сокета переповнюється, і системний виклик `read()` починає повертати помилку `ENOBUFS` (або `EAGAIN` у неблокуючому режимі). Діагностичний сервіс зобов'язаний застосовувати збільшений розмір буфера сокета через `SO_RCVBUF` та реалізовувати фільтрацію масок через `CAN_RAW_ERR_FILTER`, відсікаючи некритичні класи помилок.

4. **Обмеження швидкості логування (Rate Limiting) в системних службах**:
   Запис кожного кадру помилки у системний журнал `syslog` або на Flash-накопичувач за лічені секунди вичерпає дисковий простір або ресурси процесора під час фізичного обриву дроту. У виробничому коді обов'язково реалізують кільцевий буфер-агрегатор, який об'єднує події та виводить статистику (наприклад, «Зафіксовано 1500 помилок BitError за останню секунду») не частіше ніж один раз на 500..1000 мс.
