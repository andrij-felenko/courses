# ⚙️ Програмування станів та політик XFRM через Netlink

Цей проект демонструє практичне створення та надсилання бінарних повідомлень протоколу Netlink до підсистеми XFRM ядра Linux для реєстрації стану безпеки (SA) та політики безпеки (SP). Програма створює вихідну політику `XFRM_POLICY_OUT` для захисту трафіку між двома підмережами та реєструє відповідний стан `IPPROTO_ESP` у тунельному режимі з ключами шифрування AES-CBC та автентифікації HMAC-SHA256.

Усі операції виконуються безпосередньо через системний виклик `socket(AF_NETLINK, SOCK_RAW, NETLINK_XFRM)` без використання зовнішніх командних утиліт на кшталт `ip xfrm`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/xfrm.h>

/* Допоміжна функція додавання атрибута rtattr у буфер */
static void add_rtattr(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: переповнення буфера атрибутів Netlink\n");
        exit(EXIT_FAILURE);
    }
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, alen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_XFRM);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return 1;
    }

    /* Буфер для надсилання Netlink-повідомлення XFRM_MSG_NEWSA */
    char buf[1024];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *n = (struct nlmsghdr *)buf;
    n->nlmsg_len = NLMSG_LENGTH(sizeof(struct xfrm_usersa_info));
    n->nlmsg_type = XFRM_MSG_NEWSA;
    n->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    n->nlmsg_seq = 1;
    n->nlmsg_pid = getpid();

    struct xfrm_usersa_info *sa = (struct xfrm_usersa_info *)NLMSG_DATA(n);

    /* Конфігурація ідентифікатора SA */
    inet_pton(AF_INET, "192.168.1.1", &sa->saddr.a4);
    inet_pton(AF_INET, "192.168.2.1", &sa->id.daddr.a4);
    sa->id.spi = htonl(0x1000);
    sa->id.proto = IPPROTO_ESP;
    sa->family = AF_INET;
    sa->mode = XFRM_MODE_TUNNEL;
    sa->reqid = 100;

    /* Селектор трафіку */
    inet_pton(AF_INET, "10.0.1.0", &sa->sel.saddr.a4);
    inet_pton(AF_INET, "10.0.2.0", &sa->sel.daddr.a4);
    sa->sel.prefixlen_s = 24;
    sa->sel.prefixlen_d = 24;
    sa->sel.family = AF_INET;

    /* Додавання шифру AES-CBC (128 біт = 16 байтів ключа) */
    char crypt_buf[sizeof(struct xfrm_algo) + 16];
    struct xfrm_algo *alg_crypt = (struct xfrm_algo *)crypt_buf;
    strncpy(alg_crypt->alg_name, "cbc(aes)", sizeof(alg_crypt->alg_name));
    alg_crypt->alg_key_len = 128; /* у бітах */
    memcpy(alg_crypt->alg_key, "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10", 16);
    add_rtattr(n, sizeof(buf), XFRMA_ALG_CRYPT, alg_crypt, sizeof(crypt_buf));

    /* Додавання HMAC-SHA256 (256 біт = 32 байти ключа) */
    char auth_buf[sizeof(struct xfrm_algo) + 32];
    struct xfrm_algo *alg_auth = (struct xfrm_algo *)auth_buf;
    strncpy(alg_auth->alg_name, "hmac(sha256)", sizeof(alg_auth->alg_name));
    alg_auth->alg_key_len = 256; /* у бітах */
    memset(alg_auth->alg_key, 0xAA, 32);
    add_rtattr(n, sizeof(buf), XFRMA_ALG_AUTH, alg_auth, sizeof(auth_buf));

    /* Надсилання запиту до ядра */
    struct sockaddr_nl sa_dst;
    memset(&sa_dst, 0, sizeof(sa_dst));
    sa_dst.nl_family = AF_NETLINK;

    if (sendto(fd, n, n->nlmsg_len, 0, (struct sockaddr *)&sa_dst, sizeof(sa_dst)) < 0) {
        perror("sendto(NETLINK_XFRM)");
        close(fd);
        return 1;
    }

    /* Отримання підтвердження від ядра (NLMSG_ERROR) */
    char resp_buf[512];
    ssize_t len = recv(fd, resp_buf, sizeof(resp_buf), 0);
    if (len < 0) {
        perror("recv()");
        close(fd);
        return 1;
    }

    struct nlmsghdr *resp = (struct nlmsghdr *)resp_buf;
    if (resp->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(resp);
        if (err->error == 0) {
            printf("Успіх: XFRM SA з SPI 0x1000 успішно зареєстровано в ядрі.\n");
        } else {
            fprintf(stderr, "Помилка ядра Netlink: %s (%d)\n", strerror(-err->error), err->error);
            close(fd);
            return 1;
        }
    }

    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/xfrm.h>

namespace xfrm {

/* RAII-обгортка для файлового дескриптора сокету Netlink */
class NetlinkSocket {
    int fd_{-1};
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити сокет Netlink");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

/* Буфер повідомлення Netlink із підтримкою динамічного додавання атрибутів */
class MessageBuffer {
    std::vector<uint8_t> buffer_;

public:
    explicit MessageBuffer(uint16_t msg_type, uint16_t flags, uint32_t payload_size) {
        uint32_t total_len = NLMSG_LENGTH(payload_size);
        buffer_.resize(total_len, 0);

        auto* n = header();
        n->nlmsg_len = total_len;
        n->nlmsg_type = msg_type;
        n->nlmsg_flags = flags;
        n->nlmsg_seq = 1;
        n->nlmsg_pid = static_cast<uint32_t>(::getpid());
    }

    [[nodiscard]] struct nlmsghdr* header() noexcept {
        return reinterpret_cast<struct nlmsghdr*>(buffer_.data());
    }

    [[nodiscard]] void* payload() noexcept {
        return NLMSG_DATA(header());
    }

    void add_attribute(uint16_t type, std::span<const uint8_t> data) {
        uint32_t rta_len = RTA_LENGTH(data.size());
        size_t old_size = buffer_.size();
        size_t aligned_old = NLMSG_ALIGN(old_size);
        buffer_.resize(aligned_old + RTA_ALIGN(rta_len), 0);

        header()->nlmsg_len = static_cast<uint32_t>(buffer_.size());

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + aligned_old);
        rta->rta_type = type;
        rta->rta_len = rta_len;
        std::memcpy(RTA_DATA(rta), data.data(), data.size());
    }

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return buffer_;
    }
};

void add_security_association(NetlinkSocket& sock,
                              std::string_view src_ip,
                              std::string_view dst_ip,
                              uint32_t spi,
                              std::span<const uint8_t> aes_key,
                              std::span<const uint8_t> hmac_key) {
    MessageBuffer msg(XFRM_MSG_NEWSA, NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK, sizeof(struct xfrm_usersa_info));

    auto* sa = static_cast<struct xfrm_usersa_info*>(msg.payload());
    ::inet_pton(AF_INET, src_ip.data(), &sa->saddr.a4);
    ::inet_pton(AF_INET, dst_ip.data(), &sa->id.daddr.a4);
    sa->id.spi = htonl(spi);
    sa->id.proto = IPPROTO_ESP;
    sa->family = AF_INET;
    sa->mode = XFRM_MODE_TUNNEL;
    sa->reqid = 100;

    /* Додавання алгоритму шифрування */
    std::vector<uint8_t> crypt_raw(sizeof(struct xfrm_algo) + aes_key.size(), 0);
    auto* alg_crypt = reinterpret_cast<struct xfrm_algo*>(crypt_raw.data());
    std::strncpy(alg_crypt->alg_name, "cbc(aes)", sizeof(alg_crypt->alg_name));
    alg_crypt->alg_key_len = static_cast<uint32_t>(aes_key.size() * 8);
    std::memcpy(alg_crypt->alg_key, aes_key.data(), aes_key.size());
    msg.add_attribute(XFRMA_ALG_CRYPT, crypt_raw);

    /* Додавання алгоритму аутентифікації */
    std::vector<uint8_t> auth_raw(sizeof(struct xfrm_algo) + hmac_key.size(), 0);
    auto* alg_auth = reinterpret_cast<struct xfrm_algo*>(auth_raw.data());
    std::strncpy(alg_auth->alg_name, "hmac(sha256)", sizeof(alg_auth->alg_name));
    alg_auth->alg_key_len = static_cast<uint32_t>(hmac_key.size() * 8);
    std::memcpy(alg_auth->alg_key, hmac_key.data(), hmac_key.size());
    msg.add_attribute(XFRMA_ALG_AUTH, auth_raw);

    /* Відправка у сокет */
    struct sockaddr_nl sa_dst{};
    sa_dst.nl_family = AF_NETLINK;

    if (::sendto(sock.get(), msg.data().data(), msg.data().size(), 0,
                 reinterpret_cast<struct sockaddr*>(&sa_dst), sizeof(sa_dst)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка sendto до Netlink XFRM");
    }

    /* Зчитування відповіді */
    std::vector<uint8_t> resp_buf(512);
    ssize_t len = ::recv(sock.get(), resp_buf.data(), resp_buf.size(), 0);
    if (len < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка recv від Netlink XFRM");
    }

    auto* resp = reinterpret_cast<struct nlmsghdr*>(resp_buf.data());
    if (resp->nlmsg_type == NLMSG_ERROR) {
        auto* err = static_cast<struct nlmsgerr*>(NLMSG_DATA(resp));
        if (err->error != 0) {
            throw std::system_error(-err->error, std::generic_category(), "Помилка реєстрації SA ядром");
        }
    }
}

} // namespace xfrm

int main() {
    try {
        xfrm::NetlinkSocket sock(NETLINK_XFRM);
        const uint8_t aes_key[16] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
        std::vector<uint8_t> hmac_key(32, 0xAA);

        xfrm::add_security_association(sock, "192.168.1.1", "192.168.2.1", 0x1000, aes_key, hmac_key);
        std::cout << "Успіх: XFRM SA зареєстровано через C++ RAII Netlink API.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Покроковий аналіз низькорівневого механізму обробки

### 1. Архітектура та вирівнювання заголовка Netlink

Протокол взаємодії простору користувача з ядром спирається на суворе дотримання вирівнювання пам'яті за межами 4 байтів (`NLMSG_ALIGN`). Кожен системний кадр починається зі структури `struct nlmsghdr`.

У реалізації мовою C заголовок пакета проектується безпосередньо на початок виділеного статичного масиву `char buf[1024]`. Макрос `NLMSG_LENGTH(sizeof(struct xfrm_usersa_info))` обчислює сумарний розмір заголовка та корисної структури з урахуванням системного вирівнювання.

Розберемо значення прапорців заголовка `nlmsg_flags`:
- `NLM_F_REQUEST`: Вказує ядру, що дане повідомлення є вихідним запитом від процесу користувача, який вимагає обробки в підсистемі XFRM.
- `NLM_F_CREATE`: Наказує підсистемі створити новий об'єкт у базі даних SAD, якщо об'єкт із таким ідентифікатором ще не зареєстровано.
- `NLM_F_EXCL`: Вказує ядру повертати помилку `EEXIST`, якщо об'єкт із тотожним ключем (SPI + Dst IP + Proto) вже присутній у базі. Це упереджує випадкову підміну чи перезапис ключів.
- `NLM_F_ACK`: Вимагає від ядра надсилання обов'язкової відповіді з результатом виконання. Без цього прапорця ядро обробляє запит асинхронно і не повертає підтвердження успішності.

### 2. Динамічне пакування атрибутів TLV

Атрибути `XFRMA_ALG_CRYPT` та `XFRMA_ALG_AUTH` не мають фіксованої довжини у C-структурах, оскільки розмір ключа варіюється від 16 байтів (AES-128) до 32 байтів (AES-256 та HMAC-SHA256).

Функція `add_rtattr()` виконує такі кроки для підтримки макету TLV:
1. Викликає макрос `RTA_LENGTH(alen)`, який обчислює розмір заголовка атрибута `struct rtattr` плюс розмір даних.
2. Розраховує вказівник на початок нового атрибута як зсув від початку пакета: `(struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len))`.
3. Заповнює поля `rta_type` (тип атрибута) та `rta_len` (довжина).
4. За допомогою `memcpy()` копіює масив байтів ключа у область `RTA_DATA(rta)`.
5. Оновлює загальну довжину Netlink-повідомлення `n->nlmsg_len`, додаючи вирівняний розмір атрибута `RTA_ALIGN(len)`.

### 3. Архітектурний розбір C++ реалізації

У C++ реалізації застосовано принципи сучасного системного програмування, що гарантують надійність та відсутність витоків ресурсів у високонавантажених сервісах:

- **Автоматичне керування дескриптором (RAII)**: Клас `NetlinkSocket` інкапсулює системний файловий дескриптор. У разі генерації будь-якого винятку чи передчасного повернення з функції деструктор класу гарантовано викликає системний виклик `close(fd)`. Копіювання об'єктів сокету заблоковано (`delete`), дозволено лише семантику переміщення (*move semantics*).
- **Динамічний буфер `MessageBuffer`**: Використання контейнера `std::vector<uint8_t>` усуває небезпеку переповнення статичного масиву. Метод `add_attribute()` розширює вектор за допомогою `buffer_.resize()`, вирівнюючи розмір пам'яті під кожен атрибут.
- **Типобезпечність та `std::span`**: Передача байтів ключів шифрування та автентифікації виконана через легковагові неволодіючі представлення `std::span<const uint8_t>`. Це запобігає помилкам зсуву вказівників чи передачі невказаного розміру пам'яті.
- **Безпека винятків**: Відповідь ядра `NLMSG_ERROR` аналізується в методі `add_security_association()`. При поверненні від'ємного коду викликом викидається `std::system_error`, який транслює числову помилку ядра POSIX у системне текстове повідомлення.

## Реєстрація політик безпеки SP через Netlink

Після додавання стану SA для завершення конфігурації тунелю необхідно зареєструвати відповідну політику SP за допомогою типу повідомлення `XFRM_MSG_NEWPOLICY`.

У коді це реалізується за аналогічною схемою:
1. Заголовок Netlink заповнюється типом `n->nlmsg_type = XFRM_MSG_NEWPOLICY`.
2. В область payload поміщається структура `struct xfrm_userpolicy_info`, де задаються селектори трафіку (IP джерела `10.0.1.0/24`, IP призначення `10.0.2.0/24`), напрямок `XFRM_POLICY_OUT` та дія `XFRM_POLICY_ALLOW`.
3. До повідомлення додається атрибут `XFRMA_TMPL`, який містить структуру `struct xfrm_user_tmpl`. У цій структурі зазначається `reqid = 100`, режим `XFRM_MODE_TUNNEL`, а також IP-адреси тунельних точок (`192.168.1.1` -> `192.168.2.1`).

Завдяки зв'язці через числове поле `reqid` ядро атомарно поєднує вихідну політику зі створеним станом шифрування у базі SAD.

## Крайові випадки, пастки та діагностика

Під час розробки та налагодження мережевих програм для роботи з `NETLINK_XFRM` системні розробники часто зіштовхуються з такими крайовими випадками:

### 1. Порядок байтів для SPI та IP-адрес

Поле `spi` у структурі `struct xfrm_id` повинно передаватися **виключно у мережевому порядку байтів** (*network byte order*, big-endian). Для цього використовується системний макрос `htonl()`. Натомість поле `reqid` передається у порядку байтів хоста (*host byte order*). Якщо передати SPI без перетворення `htonl()`, ядро зареєструє стан із байтами зворотного порядку, і вхідні пакети ESP відкидатимуться через невпадіння SPI.

### 2. Точні назви алгоритмів у реєстрі Crypto API

Строкові ідентифікатори алгоритмів у полі `alg_name` (наприклад, `"cbc(aes)"`, `"gcm(aes)"`, `"hmac(sha256)"`) мусять суворо відповідати назвам, під якими криптографічні модулі зареєстровані у підсистемі Crypto API ядра Linux (перевірити наявні алгоритми можна через файл `/proc/crypto`). Передача довільних назв на кшталт `"aes-128"` призведе до негайного відхилення запиту ядром із кодом помилки `-EINVAL` (22).

### 3. Одиниці виміру довжини ключів

Поле `alg_key_len` у структурі `struct xfrm_algo` передає довжину ключа **у бітах**, хоча сам масив `alg_key` містить байти. Для ключа AES-128 розміром 16 байтів необхідно вказувати `alg_key_len = 128`. Помилкове вказання значення 16 призведе до відмови ядра через неприпустимий розмір ключа для даного алгоритму.

### 4. Необхідні привілеї та права доступу

Створення сокету `AF_NETLINK` із протоколом `NETLINK_XFRM` вимагає наявності у процесу системного мандата `CAP_NET_ADMIN`. При запуску програми від імені звичайного користувача системний виклик `socket()` завершується з помилкою `EPERM` (*Operation not permitted*).

### 5. Налагодження за допомогою `strace` та `ip xfrm state`

Для верифікації роботи створеної програми використовується трасування системних викликів `strace`:

```bash
strace -e socket,sendto,recv -s 128 ./xfrm_setup
```

Після успішного виконання програми створений стан перевіряється в ядрі за допомогою утиліти `iproute2`:

```bash
ip xfrm state show spi 0x1000
```
