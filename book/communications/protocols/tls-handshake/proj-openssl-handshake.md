# ⚙️ Практичне рукостискання TLS 1.3 на C та C++ з використанням OpenSSL

Нижче наведено практичний приклад реалізації клієнтського з'єднання TLS 1.3 поверх мережевого сокета POSIX з використанням системної бібліотеки OpenSSL (`libssl` та `libcrypto`). Код демонструє повний виробничий цикл: створення та налаштування криптографічного контексту `SSL_CTX`, примусове обмеження версій протоколу строго на TLS 1.3, автоматичну автентифікацію X.509-сертифіката сервера за допомогою системного сховища довірених центрів CA, виконання рукостискання `SSL_connect`, витяг параметрів узгодженої сесії та коректне двокрокове закриття каналу.

---

## 1. Архітектурні принципи та правила безпечної роботи з OpenSSL API

Під час проєктування мережевих клієнтів та серверних служб із використанням C/C++ та бібліотеки OpenSSL слід дотримуватися чотирьох фундаментальних правил інженерної безпеки:

1. **Суворе обмеження версій протоколу**: Задля відвернення атак зниження версії (Downgrade Attacks, таких як POODLE чи FREAK) розробник зобов'язаний явно зафіксувати версію `TLS1_3_VERSION` через виклики `SSL_CTX_set_min_proto_version` та `SSL_CTX_set_max_proto_version`. Надання OpenSSL свободи у виборі версій за замовчуванням створює небезпеку прихованого відкоту до TLS 1.2 або 1.0 при маніпуляціях з боку проміжних пристроїв.
2. **Передача розширення SNI (Server Name Indication)**: Виклик `SSL_set_tlsext_host_name(ssl, host)` додає до кадру `ClientHello` розширення `server_name`. У сучасних хмарних інфраструктурах (Kubernetes Ingress, Cloudflare, AWS ALB), де тисячі різних вебсайтів ділять одну й ту саму IP-адресу, відсутність SNI призведе до того, що сервер повернує дефолтний, невідповідний сертифікат або негайно розірве з'єднання з фатальною помилкою `unrecognized_name`.
3. **Строга перевірка ланцюжка сертифікатів та імені хоста**: Прапор `SSL_VERIFY_PEER` у поєднанні з викликом `SSL_set1_host(ssl, host)` інструктує OpenSSL виконати повний аналіз ланцюжка X.509 до довіреного кореневого центру CA, перевірити терміни придатності, списки відкликання (CRL) та переконатися, що доменне ім'я з SNI відповідає полі `Subject Alternative Name` (SAN) у сертифікаті.
4. **Обробка неблокуючих сокетів та стану `WANT_READ` / `WANT_WRITE`**: У високопродуктивних асинхронних серверах (на базі `epoll` у Linux чи `kqueue` у FreeBSD) сокети працюють у неблокуючому режимі. Системні виклики `SSL_connect`, `SSL_read` та `SSL_write` можуть повертати помилку `SSL_ERROR_WANT_READ` або `SSL_ERROR_WANT_WRITE`. Це означає, що внутрішньому автомату станів TLS потрібно виконати читання чи запис службових кадрів рукостискання, і застосунок зобов'язаний тимчасово змінити маску подій сокета у циклі `epoll_wait`.

---

## 2. Реалізація клієнта TLS 1.3 мовами C11 та C++20

Приклад розбито на дві паралельні вкладки. У вкладці **C11** показано класичний процедурний підхід із ручним керуванням ресурсами через `goto` та функціями вивільнення OpenSSL. У вкладці **C++20** реалізовано об'єктно-орієнтовану обгортку з використанням ідіоми **RAII (Resource Acquisition Is Initialization)**, смайликових розумних вказівників `std::unique_ptr` зі спеціальними видалячами (`deleter`), стрінг-в'ю `std::string_view` та обробкою винятків.

:::tabs
```c
/* C11 implementation: TLS 1.3 Client connection using OpenSSL */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#define HOST "example.com"
#define PORT "443"

static int create_socket(const char *hostname, const char *port_str) {
    struct addrinfo hints, *res, *p;
    int fd = -1;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(hostname, port_str, &hints, &res) != 0) {
        perror("getaddrinfo failed");
        return -1;
    }

    for (p = res; p != NULL; p = p->ai_next) {
        fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (fd < 0) continue;
        if (connect(fd, p->ai_addr, p->ai_addrlen) == 0) break;
        close(fd);
        fd = -1;
    }

    freeaddrinfo(res);
    return fd;
}

int main(void) {
    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_all_algorithms();

    /* Створення контексту TLS */
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        fprintf(stderr, "Unable to create SSL context\n");
        ERR_print_errors_fp(stderr);
        return EXIT_FAILURE;
    }

    /* Примусово вимагаємо TLS 1.3 як мінімальну та максимальну версію */
    if (!SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION) ||
        !SSL_CTX_set_max_proto_version(ctx, TLS1_3_VERSION)) {
        fprintf(stderr, "Failed to enforce TLS 1.3 protocol version\n");
        SSL_CTX_free(ctx);
        return EXIT_FAILURE;
    }

    /* Завантаження системних довірених кореневих сертифікатів CA */
    if (!SSL_CTX_set_default_verify_paths(ctx)) {
        fprintf(stderr, "Failed to load default CA paths\n");
    }

    int sock = create_socket(HOST, PORT);
    if (sock < 0) {
        fprintf(stderr, "Failed to connect to %s:%s\n", HOST, PORT);
        SSL_CTX_free(ctx);
        return EXIT_FAILURE;
    }

    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);

    /* Обов'язково додаємо SNI (Server Name Indication) */
    SSL_set_tlsext_host_name(ssl, HOST);
    /* Налаштування перевірки відповідності імені хоста у сертифікаті */
    SSL_set1_host(ssl, HOST);
    SSL_set_verify(ssl, SSL_VERIFY_PEER, NULL);

    printf("Initiating TLS 1.3 Handshake with %s...\n", HOST);
    if (SSL_connect(ssl) <= 0) {
        fprintf(stderr, "TLS Handshake failed!\n");
        ERR_print_errors_fp(stderr);
        SSL_free(ssl);
        close(sock);
        SSL_CTX_free(ctx);
        return EXIT_FAILURE;
    }

    printf("Handshake successful!\n");
    printf("Protocol version: %s\n", SSL_get_version(ssl));
    printf("Negotiated Cipher Suite: %s\n", SSL_get_cipher(ssl));

    /* Відправка HTTP GET запиту через захищений канал */
    const char *http_request = "GET / HTTP/1.1\r\nHost: " HOST "\r\nConnection: close\r\n\r\n";
    SSL_write(ssl, http_request, (int)strlen(http_request));

    char buf[512];
    int bytes = SSL_read(ssl, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("\nReceived Response Header:\n%.150s...\n", buf);
    }

    /* Охайне закриття з'єднання (send close_notify alert) */
    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);
    SSL_CTX_free(ctx);

    return EXIT_SUCCESS;
}
```
```cpp
// C++20 implementation: RAII-wrapped TLS 1.3 Client using OpenSSL
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>
#include <array>
#include <cstring>

#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

namespace tls {

struct SslCtxDeleter {
    void operator()(SSL_CTX* ctx) const noexcept { if (ctx) SSL_CTX_free(ctx); }
};
struct SslDeleter {
    void operator()(SSL* ssl) const noexcept { if (ssl) SSL_free(ssl); }
};

using CtxPtr = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using SslPtr = std::unique_ptr<SSL, SslDeleter>;

class TlsClient {
public:
    explicit TlsClient(std::string_view host, std::string_view port) 
        : host_(host), port_(port) {
        
        ctx_ = CtxPtr(SSL_CTX_new(TLS_client_method()));
        if (!ctx_) {
            throw std::runtime_error("Failed to create SSL_CTX");
        }

        if (!SSL_CTX_set_min_proto_version(ctx_.get(), TLS1_3_VERSION) ||
            !SSL_CTX_set_max_proto_version(ctx_.get(), TLS1_3_VERSION)) {
            throw std::runtime_error("Failed to set TLS 1.3 protocol version");
        }

        SSL_CTX_set_default_verify_paths(ctx_.get());
    }

    void connect() {
        int raw_fd = connect_socket();
        sock_fd_ = raw_fd;

        ssl_ = SslPtr(SSL_new(ctx_.get()));
        if (!ssl_) {
            close(sock_fd_);
            throw std::runtime_error("Failed to create SSL object");
        }

        SSL_set_fd(ssl_.get(), sock_fd_);
        SSL_set_tlsext_host_name(ssl_.get(), host_.c_str());
        SSL_set1_host(ssl_.get(), host_.c_str());
        SSL_set_verify(ssl_.get(), SSL_VERIFY_PEER, nullptr);

        if (SSL_connect(ssl_.get()) <= 0) {
            close(sock_fd_);
            throw std::runtime_error("TLS Handshake failed");
        }
    }

    void send(std::string_view data) {
        if (SSL_write(ssl_.get(), data.data(), static_cast<int>(data.size())) <= 0) {
            throw std::runtime_error("SSL_write failed");
        }
    }

    std::string receive() {
        std::array<char, 1024> buffer;
        int bytes = SSL_read(ssl_.get(), buffer.data(), static_cast<int>(buffer.size() - 1));
        if (bytes <= 0) {
            return "";
        }
        return std::string(buffer.data(), static_cast<size_t>(bytes));
    }

    ~TlsClient() {
        if (ssl_) {
            SSL_shutdown(ssl_.get());
        }
        if (sock_fd_ >= 0) {
            close(sock_fd_);
        }
    }

    [[nodiscard]] std::string cipher_name() const {
        return SSL_get_cipher(ssl_.get());
    }

    [[nodiscard]] std::string version() const {
        return SSL_get_version(ssl_.get());
    }

private:
    int connect_socket() {
        struct addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo(host_.c_str(), port_.c_str(), &hints, &res) != 0) {
            throw std::runtime_error("getaddrinfo failed");
        }

        int fd = -1;
        for (auto* p = res; p != nullptr; p = p->ai_next) {
            fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
            if (fd < 0) continue;
            if (::connect(fd, p->ai_addr, p->ai_addrlen) == 0) break;
            close(fd);
            fd = -1;
        }

        freeaddrinfo(res);
        if (fd < 0) {
            throw std::runtime_error("Could not connect to host socket");
        }
        return fd;
    }

    std::string host_;
    std::string port_;
    CtxPtr ctx_{nullptr};
    SslPtr ssl_{nullptr};
    int sock_fd_{-1};
};

} // namespace tls

int main() {
    try {
        tls::TlsClient client("example.com", "443");
        std::cout << "Connecting via TLS 1.3...\n";
        client.connect();

        std::cout << "Connected! Version: " << client.version() 
                  << ", Cipher: " << client.cipher_name() << "\n";

        client.send("GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n");
        std::string response = client.receive();
        std::cout << "Response excerpt:\n" << response.substr(0, 150) << "...\n";

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Глибокий розбір пасток реалізації та крайових випадків

Під час практичного використання бібліотеки OpenSSL для встановлення рукостискання розробники регулярно зіштовхуються з трьома складними інженерними ситуаціями:

### 1. Подвійний виклик `SSL_shutdown` для двостороннього закриття

Протокол TLS суворо вимагає симетричного закриття каналу. Коли клієнт більше не планує надсилати дані, він викликає `SSL_shutdown(ssl)`. Цей перший виклик формує та надсилає в сокет зашифрований кадр Alert `close_notify`.

Проте стан TLS-сесії не вважається повністю закритим, поки сервер не надішле у відповідь власний кадр `close_notify`. Тому правильний алгоритм вимагає **повторного виклику `SSL_shutdown(ssl)`** після надсилання Alert:
- Перший виклик повертає `0` (означає «Alert надсилається, але відповідь ще не отримана»).
- Другий виклик повертає `1` (означає «отримано підтвердження `close_notify` від віддаленого вузла»).

Якщо викликом пронехтувати й одразу закрити POSIX-сокет через `close(fd)`, віддалений сервер сприйме це як аномальний розрив TCP-з'єднання та може викинути помилку `Connection reset by peer`.

### 2. Асинхронне отримання `NewSessionTicket` після рукостискання

У попередніх версіях TLS 1.2 квитки сесії передавалися під час самого рукостискання. У TLS 1.3 повідомлення `NewSessionTicket` надсилається сервером **асинхронно вже в захищеному каналі** після надсилання `Finished`.

Це означає, що при першому виклику `SSL_read` для зчитування відповідей HTTP OpenSSL усередині прозоро розпакує кадр `NewSessionTicket`, збереже його внутрішні параметри в контексті `SSL_CTX` і лише після цього поверне прикладному коду HTTP-байти. Для збереження квитка на диск з метою подальшого 0-RTT відновлення необхідно зареєструвати зворотний виклик (callback) за допомогою функції `SSL_CTX_sess_set_new_cb`.

### 3. Діагностика помилок перевірки сертифіката (`X509_V_ERR_*`)

Якщо під час виклику `SSL_connect` перевірка ланцюжка сертифікатів зазнала невдачі, виклик `ERR_print_errors_fp` виведе детальний стек помилок OpenSSL. Найчастіші кодові причини:
- `X509_V_ERR_DEPTH_ZERO_SELF_SIGNED_CERT`: Сервер використовує самопідписаний сертифікат, відсутній у локальному сховищі CA.
- `X509_V_ERR_HOSTNAME_MISMATCH`: Доменне ім'я з `SSL_set1_host` не збігається з жодним записом у полі `Subject Alternative Name` (SAN) сертифіката сервера.
- `X509_V_ERR_CERT_HAS_EXPIRED`: Термін придатності сертифіката сервера закінчився або на локальному пристрої збився системний годинник RTC.

---

## 4. Керування пам'яттю та багатопотокова безпека OpenSSL

У сучасних багатопотокових C/C++ застосунках екземпляр `SSL_CTX` створюється **один раз на процес** і може безпечно використовуватися кількома потоками паралельно для викликів `SSL_new`.

Проте сам об'єкт `SSL*`, що репрезентує конкретне TLS-з'єднання, **не є багатопотоково безпечним**. Заборонено одночасно викликати `SSL_read` та `SSL_write` на одному й тому самому об'єкті `SSL*` з різних робочих потоків без явного синхронізуючого м'ютекса (`std::mutex`), оскільки це призведе до пошкодження внутрішніх системних буферів запису й зчитування OpenSSL.
