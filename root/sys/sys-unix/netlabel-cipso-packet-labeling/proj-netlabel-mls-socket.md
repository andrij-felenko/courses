# ⚙️ Проект: MLS-сервер із перевіркою контексту безпеки сокета через SO_PEERSEC

<preknowlist>
- [Мережевий сокетний інтерфейс у Linux](topic:sys-unix/socket-api-linux) — системні виклики socket, bind, listen, accept, getsockopt.
- [SELinux: Type Enforcement та контексти безпеки](topic:sys-unix/selinux-type-enforcement) — структура текстового представлення контексту безпеки процесу та сокета.
</preknowlist>

Коли мережевий вузол функціонує в режимі багаторівневої безпеки (Multi-Level Security, MLS) з увімкненою підсистемою NetLabel і протоколом CIPSO, кожне вхідне TCP-з'єднання несе в собі контекст безпеки віддаленого клієнта. Хоча ядро Linux автоматично перевіряє право доступу на рівні гачка `security_sock_rcv_skb()` (відкидаючи пакети, рівень яких не задовольняє правилу домінування Белла — ЛаПадули), прикладні сервери (вебсервери, брокери повідомлень, демони баз даних) повинні знати точний мандатний рівень клієнта. Це необхідно для гранулярного розмежування даних усередині застосунку, динамічної фільтрації записів або запису точного контексту в системний журнал аудиту.

Цей проект реалізує повнофункціональний TCP-сервер, який приймає мережеві з'єднання та видобуває повний мандатний контекст безпеки віддаленого клієнта за допомогою системного виклику `getsockopt()` із сокетною опцією `SO_PEERSEC`.

---

## 1. Архітектурний механізм: `SO_PEERSEC` проти суміжних опцій

Для роботи з ідентичністю та правами процесу на сокетах Linux надає три різні сокетні опції:

1. **`SO_PEERCRED`:** повертає структуру `struct ucred` (числові UID, GID та PID клієнта). Ця опція працює **виключно для локальних UNIX domain сокетів** (`AF_UNIX`) і не передається через мережу.
2. **`IP_PASSSEC`:** сокетна опція рівня `SOL_IP`, яка змушує ядро передавати мітку безпеки кожного окремого вхідного UDP-дейтаграми як допоміжне повідомлення керування (ancillary data / `cmsg`) під час виклику `recvmsg()`.
3. **`SO_PEERSEC`:** сокетна опція рівня `SOL_SOCKET`, яка повертає повний рядковий контекст безпеки віддаленого піра (`peer security context`). Для локальних сокетів `AF_UNIX` вона повертає контекст процесу-клієнта, а для мережевих сокетів `AF_INET`/`AF_INET6` — контекст безпеки, зібраний підсистемою NetLabel із заголовків CIPSO/CALIPSO вхідного TCP SYN-пакета.

### Послідовність дій ядра під час виклику `SO_PEERSEC`

```
Простір користувача (Server)              Ядро Linux (NetLabel / LSM)
         │                                              │
         ├────── accept(server_fd, ...) ───────────────>│
         │                                              │ 1. Клонування struct sock
         │                                              │ 2. Призначення secid із CIPSO тегу
         │<───── client_fd (новий дескриптор) ──────────┤
         │                                              │
         ├────── getsockopt(client_fd, SO_PEERSEC) ────>│
         │                                              │ 3. Виклик LSM гачка:
         │                                              │    security_socket_getpeersec_stream()
         │                                              │ 4. Трансляція secid у текстовий рядок
         │                                              │    (напр. system_u:system_r:client_t:s1:c2)
         │<───── буфер із рядком контексту ─────────────┤
         │                                              │
```

1. Під час надходження клієнтського запиту на з'єднання (TCP SYN) підсистема NetLabel розбирає опцію CIPSO Option 134 та зберігає атрибути в об'єкті `struct request_sock`.
2. Системний виклик `accept()` завершує встановлення з'єднання і клонує дочірній сокет `client_fd`, прив'язуючи до нього ідентифікатор безпеки клієнта.
3. Сервер викликає `getsockopt(client_fd, SOL_SOCKET, SO_PEERSEC, buf, &len)`.
4. Ядро викликає гачок `security_socket_getpeersec_stream()`, який звертається до модуля безпеки (SELinux/Smack). Модуль перетворює числовий `secid` сокета у повний текстовий рядок і копіює його в наданий буфер користувача.

---

## 2. Реалізація мовами C та C++

Наведені нижче приклади реалізують мережевий сервер, здатний працювати як у чистому C-середовищі, так і в сучасних C++23 проектах з використанням RAII-обгорток для сокетів та обробки результатів через `std::expected`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_PORT 8443
#define PEERSEC_BUF_SIZE 512

/*
 * Функція видобування контексту безпеки віддаленого піра через SO_PEERSEC.
 * Повертає 0 у разі успіху або від'ємний код помилки (-errno).
 */
static int get_peer_security_context(int sock_fd, char *buf, size_t buf_size) {
    socklen_t optlen = (socklen_t)buf_size;
    
    if (getsockopt(sock_fd, SOL_SOCKET, SO_PEERSEC, buf, &optlen) < 0) {
        return -errno;
    }
    
    /* Гарантуємо наявність нульового байта наприкінці рядка */
    if (optlen < buf_size) {
        buf[optlen] = '\0';
    } else {
        buf[buf_size - 1] = '\0';
    }
    return 0;
}

int main(void) {
    int server_fd = -1;
    int client_fd = -1;
    struct sockaddr_in server_addr;
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    char sec_context[PEERSEC_BUF_SIZE];
    int opt = 1;

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("Помилка створення сокета");
        return EXIT_FAILURE;
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Помилка setsockopt SO_REUSEADDR");
        close(server_fd);
        return EXIT_FAILURE;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(SERVER_PORT);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Помилка прив'язки bind()");
        close(server_fd);
        return EXIT_FAILURE;
    }

    if (listen(server_fd, 10) < 0) {
        perror("Помилка переведення в режим listen()");
        close(server_fd);
        return EXIT_FAILURE;
    }

    printf("[INFO] MLS TCP-сервер очікує з'єднання на порту %d...\n", SERVER_PORT);

    while (1) {
        client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            perror("Помилка accept()");
            break;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        printf("\n[CONNECT] Отримано запит від %s:%d\n", client_ip, ntohs(client_addr.sin_port));

        memset(sec_context, 0, sizeof(sec_context));
        int res = get_peer_security_context(client_fd, sec_context, sizeof(sec_context));
        if (res == 0) {
            printf("[NETLABEL/LSM] SO_PEERSEC контекст клієнта: %s\n", sec_context);
        } else {
            if (res == -ENOPROTOOPT) {
                printf("[NETLABEL/LSM] SO_PEERSEC не підтримується модулем безпеки або немає мітки\n");
            } else {
                printf("[NETLABEL/LSM] Помилка отримання мітки: %s (код %d)\n", strerror(-res), -res);
            }
        }

        const char *response = "HTTP/1.1 200 OK\r\nContent-Length: 15\r\n\r\nMLS ACK RECEIVED";
        write(client_fd, response, strlen(response));

        close(client_fd);
        client_fd = -1;
    }

    close(server_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/*
 * RAII-клас для безпечного володіння файловим дескриптором сокета.
 */
class [[nodiscard]] UniqueSocket {
public:
    UniqueSocket() noexcept : fd_{-1} {}
    explicit UniqueSocket(int fd) noexcept : fd_{fd} {}
    
    ~UniqueSocket() noexcept {
        reset();
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return isValid(); }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    [[nodiscard]] int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_;
};

/*
 * Сервіс для обслуговування MLS-з'єднань та видобування контекстів безпеки.
 */
class MlsPeerSecService {
public:
    static constexpr uint16_t kDefaultPort = 8443;
    static constexpr size_t kMaxSecContextLen = 512;

    /*
     * Отримує текстовий контекст безпеки SO_PEERSEC за допомогою getsockopt.
     */
    static std::expected<std::string, std::error_code> getPeerContext(int socketFd) {
        std::vector<char> buffer(kMaxSecContextLen, '\0');
        auto optlen = static_cast<socklen_t>(buffer.size());

        if (::getsockopt(socketFd, SOL_SOCKET, SO_PEERSEC, buffer.data(), &optlen) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (optlen > 0 && optlen <= buffer.size()) {
            size_t string_len = (buffer[optlen - 1] == '\0') ? optlen - 1 : optlen;
            return std::string(buffer.data(), string_len);
        }
        return std::string(buffer.data());
    }

    /*
     * Ініціалізує слухаючий сокет TCP-сервера.
     */
    static std::expected<UniqueSocket, std::error_code> createListener(uint16_t port = kDefaultPort) {
        int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        UniqueSocket serverSock(raw_fd);

        int opt = 1;
        if (::setsockopt(serverSock.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sockaddr_in server_addr{};
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = ::htonl(INADDR_ANY);
        server_addr.sin_port = ::htons(port);

        if (::bind(serverSock.get(), reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(serverSock.get(), 10) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return serverSock;
    }
};

int main() {
    auto listenerResult = MlsPeerSecService::createListener();
    if (!listenerResult) {
        std::cerr << "[ПОМИЛКА] Не вдалося створити MLS-сервер: " 
                  << listenerResult.error().message() << '\n';
        return 1;
    }

    UniqueSocket serverSocket = std::move(*listenerResult);
    std::cout << "[INFO] C++ MLS TCP-сервер слухає порт " << MlsPeerSecService::kDefaultPort << "...\n";

    while (true) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        
        int raw_client = ::accept(serverSocket.get(), reinterpret_cast<sockaddr*>(&client_addr), &client_len);
        if (raw_client < 0) {
            if (errno == EINTR) continue;
            std::cerr << "[ПОМИЛКА] Помилка accept: " << std::strerror(errno) << '\n';
            break;
        }

        UniqueSocket clientSocket(raw_client);
        char ipBuf[INET_ADDRSTRLEN];
        ::inet_ntop(AF_INET, &client_addr.sin_addr, ipBuf, sizeof(ipBuf));
        std::cout << "\n[CONNECT] З'єднання від " << ipBuf << ':' << ::ntohs(client_addr.sin_port) << '\n';

        auto contextResult = MlsPeerSecService::getPeerContext(clientSocket.get());
        if (contextResult) {
            std::cout << "[NETLABEL/LSM] Контекст SO_PEERSEC: " << *contextResult << '\n';
        } else {
            std::cout << "[NETLABEL/LSM] Не вдалося отримати мітку: " 
                      << contextResult.error().message() << '\n';
        }

        std::string_view reply = "HTTP/1.1 200 OK\r\nContent-Length: 18\r\n\r\nMLS-CPP ACK SUCESS";
        [[maybe_unused]] auto bytesWritten = ::write(clientSocket.get(), reply.data(), reply.size());
    }

    return 0;
}
```
:::

---

## 3. Практичні пастки та діагностика помилок

Під час розробки застосунків із підтримкою `SO_PEERSEC` розробники найчастіше стикаються з трьома категоріями проблем:

### 3.1. Помилка `ENOPROTOOPT` («Protocol not available»)
Системний виклик `getsockopt` повертає `ENOPROTOOPT` у таких випадках:
- У системі не завантажено жодного модуля безпеки LSM із підтримкою потокового пір-контексту (наприклад, система завантажена з параметром ядра `selinux=0` або `apparmor`);
- Трафік надійшов через інтерфейс зворотного зв'язку (`lo`) без попереднього налаштування статичного мапінгу `unlbl` або домену `pass` для локальних адрес;
- Сокет не підтримує потоковий контекст (наприклад, виклик виконано над UDP-сокетом `SOCK_DGRAM`, де мітки слід отримувати через допоміжні керуючі повідомлення `cmsg` за допомогою `IP_PASSSEC`).

### 3.2. Виклик над слухаючим сокетом (`ENOTCONN`)
Спроба виконати `getsockopt(server_fd, SOL_SOCKET, SO_PEERSEC, ...)` над дескриптором слухаючого сокета (який перебуває у стані `listen()`) поверне помилку `ENOTCONN` («Transport endpoint is not connected»). Контекст безпеки віддаленого піра асоціюється **виключно з дочірнім сокетом**, який створюється ядром і повертається після успішного виконання системного виклику `accept()`.

### 3.3. Недостатній розмір буфера
У складних конфігураціях SELinux MLS із сотнями категорій (наприклад, `system_u:system_r:trusted_app_t:s1:c0,c4,c8,c12,c16...c1020`) довжина текстового рядка контексту може легко перевищити 256 байтів. Якщо переданий буфер замалий, ядро поверне помилку `ERANGE` або обріже рядок. Рекомендований мінімальний розмір буфера для систем із розвиненою політикою MLS становить від 512 до 1024 байтів.

### 3.4. Вимоги до Type Enforcement політики SELinux
Навіть якщо пакет фізично містить Option 134, прикладний процес не зможе прочитати його або отримати `SO_PEERSEC`, якщо в завантаженій політиці SELinux немає явного дозволу:

```
allow server_t client_t : peer { recv };
allow server_t server_t : tcp_socket { getattr getopt };
```
Відсутність цих правил призведе до генерації повідомлень `avc: denied` у журналі `audit.log` та повернення помилки `EACCES` під час виклику сокетних функцій.

### 3.5. Стек кількох модулів безпеки (LSM Stacking) та `SO_GETPEERSEC_LSMPROTO`
У сучасних ядрах Linux (починаючи з ядра 6.8 та подальшого розвитку стеку LSM) одночасно можуть бути активними кілька модулів безпеки (наприклад, SELinux та BPF-LSM або AppArmor і Smack). Класичний виклик `SO_PEERSEC` повертає контекст лише першого мажоритарного модуля безпеки, зареєстрованого в системі.

Для точного вибору модуля в нових ядрах впроваджено сокетну опцію `SO_GETPEERSEC_LSMPROTO`, де застосунок передає числовий ідентифікатор LSM (наприклад, `LSM_ID_SELINUX` або `LSM_ID_SMACK`), гарантуючи отримання коректної мітки потрібної підсистеми навіть в умовах стекування кількох мандатних систем контролю доступу.

---

## 4. Практичне тестування через ізольовані простори мережі (Network Namespaces)

Для тестування роботи сервера без наявності двох окремих фізичних машин зручно використати мережеві простори імен ядра Linux (`ip netns`) та віртуальну пару інтерфейсів `veth`:

```bash
# 1. Створення ізольованих просторів імен для клієнта та сервера
ip netns add ns_server
ip netns add ns_client

# 2. Створення віртуальної пари інтерфейсів
ip link add veth_srv type veth peer name veth_cli
ip link set veth_srv netns ns_server
ip link set veth_cli netns ns_client

# 3. Налаштування IP-адрес та запуск інтерфейсів
ip netns exec ns_server ip addr add 192.168.100.1/24 dev veth_srv
ip netns exec ns_server ip link set veth_srv up
ip netns exec ns_server ip link set lo up

ip netns exec ns_client ip addr add 192.168.100.2/24 dev veth_cli
ip netns exec ns_client ip link set veth_cli up
ip netns exec ns_client ip link set lo up

# 4. Налаштування NetLabel для інтерфейсів у кожному просторі
ip netns exec ns_server netlabelctl cipsov4 add pass doi:1 tags:1
ip netns exec ns_server netlabelctl map add default protocol:cipsov4,1

ip netns exec ns_client netlabelctl cipsov4 add pass doi:1 tags:1
ip netns exec ns_client netlabelctl map add default protocol:cipsov4,1

# 5. Перевірка наявності CIPSO-опцій у мережевому трафіку через tcpdump
# У першому терміналі:
ip netns exec ns_server tcpdump -i veth_srv -vvv -n -X 'ip[20:1] == 0x86'

# 6. Запуск MLS-сервера та відправка тестового запиту від процесу з MLS-міткою
# Запуск сервера:
ip netns exec ns_server ./mls_server &

# Запуск клієнта під керуванням runcon з підвищеним рівнем чутливості s1:c0,c4:
ip netns exec ns_client runcon -l "s1:c0,c4" curl http://192.168.100.1:8443/
```
