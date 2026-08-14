# ⚙️ Практична реалізація kTLS: від низькорівневих сокетів до OpenSSL та sendfile

Ця вставка містить повністю робочі практичні приклади реалізації підсистеми Kernel TLS (kTLS) на мовах системного програмування C та C++. Ми детально розберемо два протилежних підходи: низькорівневе управління сокетом через виклики Linux Kernel Socket API (`setsockopt`) та високорівневу інтеграцію через інфраструктурну бібліотеку OpenSSL 3.0 із наступним застосуванням системного виклику `sendfile()`.

---

## 1. Архітектурне завдання та дизайн рішення

Мета цього практичного модуля — продемонструвати розробнику, як побудувати високонавантажений вебсервер або сервіс віддачі контенту, який поєднує безпеку протоколу TLS 1.2/1.3 з максимально можливою продуктивністю системного вводу-виводу Zero-Copy.

### Сценарій роботи мережевого додатка

1. **Ініціалізація та слухання TCP-порту:** Створення стандартного потокового сокета `SOCK_STREAM`, прив'язка до IP-адреси та порту `443`, переведення у стан слухання та прийом вхідного з'єднання від клієнта через виклик `accept()`.
2. **Фаза рукостискання (Handshake):** Виконання асиметричної автентифікації та обміну ключами. У першому підході ми моделюємо передачу симетричних ключів вручну; у другому підході ми довіряємо цей процес бібліотеці OpenSSL 3.0.
3. **Реєстрація kTLS ULP:** Перехід сокета під управління модуля ядра `net/tls` за допомогою системного виклику `setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls"))`.
4. **Ініціалізація криптоконтексту:** Формування бінарних структур `struct tls12_crypto_info_aes_gcm_128` із заповненням полів ключа, ініціалізаційного вектора, солі та порядкового номера запису, з подальшим викликом `setsockopt(sock_fd, SOL_TLS, TLS_TX, ...)`.
5. **Zero-Copy передача даних:** Виклик системного виклику `sendfile()`, який зчитує сторінки файлу з дискового кешу ядра (Page Cache) та передає їх у сокет без виходу у простір користувача.

---

## 2. Низькорівневе налаштування kTLS сокета через Socket API

У цьому розділі наведено код, який працює безпосередньо із сокетними опціями ядра Linux. Припускається, що асиметричне рукостискання вже відбулося, і додаток має у своєму розпорядженні 16-байтний ключ AES, 4-байтну сіль, 8-байтний вектор ініціалізації та поточний 64-бітний порядковий номер запису `rec_seq`.

:::tabs
```c
/* c_ktls_raw.c - Низькорівнева активація kTLS на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <linux/tls.h>
#include <sys/sendfile.h>
#include <fcntl.h>

/*
 * Функція enable_ktls_tx виконує переведення звичайного TCP сокета
 * під управління підсистеми kTLS для вихідного напрямку даних (TX).
 */
int enable_ktls_tx(int sock_fd, const unsigned char *key, const unsigned char *iv,
                   const unsigned char *salt, uint64_t seq_num) {
    /* 1. Активація ULP модуля "tls" у мережевому стеку ядра */
    if (setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls")) < 0) {
        fprintf(stderr, "Помилка: Не вдалося зареєструвати ULP 'tls'. Перевірте modprobe tls. Code: %d\n", errno);
        return -1;
    }

    /* 2. Заповнення специфічної структури AES-GCM 128 біт */
    struct tls12_crypto_info_aes_gcm_128 crypto_info;
    memset(&crypto_info, 0, sizeof(crypto_info));

    crypto_info.info.version = TLS_1_2_VERSION;
    crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    memcpy(crypto_info.key, key, TLS_CIPHER_AES_GCM_128_KEY_SIZE);
    memcpy(crypto_info.iv, iv, TLS_CIPHER_AES_GCM_128_IV_SIZE);
    memcpy(crypto_info.salt, salt, TLS_CIPHER_AES_GCM_128_SALT_SIZE);
    memcpy(crypto_info.rec_seq, &seq_num, sizeof(seq_num));

    /* 3. Передача криптографічних ключів у рівень SOL_TLS */
    if (setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
        fprintf(stderr, "Помилка: Не вдалося передати ключі SOL_TLS TLS_TX. Code: %d\n", errno);
        return -1;
    }

    printf("[kTLSEngine] kTLS ULP успішно активовано для TX на сокеті %d.\n", sock_fd);
    return 0;
}

/*
 * Передача файлу за допомогою Zero-Copy виклику sendfile() над kTLS сокетом.
 */
ssize_t send_file_ktls(int sock_fd, int file_fd, off_t *offset, size_t count) {
    ssize_t sent_bytes = sendfile(sock_fd, file_fd, offset, count);
    if (sent_bytes < 0) {
        fprintf(stderr, "Помилка виклику sendfile над kTLS сокетом: %d\n", errno);
    }
    return sent_bytes;
}
```
```cpp
// cpp_ktls_raw.cpp - Ідіоматична реалізація kTLS на мові C++20 (RAII, std::expected, std::span)
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <linux/tls.h>
#include <sys/sendfile.h>

// RAII обгортка для безпечного управління сокетним дескриптором
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Контейнер криптографічних параметрів із фіксованими розмірами поверхонь
struct KtlsKeys {
    std::span<const uint8_t, 16> key;
    std::span<const uint8_t, 8>  iv;
    std::span<const uint8_t, 4>  salt;
    uint64_t seq_num{0};
};

// Налаштування вихідного kTLS з використанням сучасного обробника std::expected
std::expected<void, std::error_code> configure_ktls_tx(int sock_fd, const KtlsKeys& keys) {
    // 1. Активація модуля ULP "tls" у ядрі
    if (::setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls")) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Формування бінарної структури ядра
    struct tls12_crypto_info_aes_gcm_128 crypto_info{};
    crypto_info.info.version = TLS_1_2_VERSION;
    crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    std::memcpy(crypto_info.key, keys.key.data(), keys.key.size());
    std::memcpy(crypto_info.iv, keys.iv.data(), keys.iv.size());
    std::memcpy(crypto_info.salt, keys.salt.data(), keys.salt.size());
    std::memcpy(crypto_info.rec_seq, &keys.seq_num, sizeof(keys.seq_num));

    // 3. Передача конфігурації у підсистему SOL_TLS
    if (::setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}

// Високоефективний потік даних із файлу у сокет через sendfile()
std::expected<size_t, std::error_code> stream_file_ktls(int sock_fd, int file_fd, off_t offset, size_t count) {
    ssize_t bytes_sent = ::sendfile(sock_fd, file_fd, &offset, count);
    if (bytes_sent < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<size_t>(bytes_sent);
}
```
:::

### Покроковий розбір низькорівневої реалізації:

1. **Реєстрація ULP (`TCP_ULP`):** Системний виклик `setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls"))` виконується першим. Ця операція каже ядру замінити таблицю методів сокета `sk_prot` на спеціалізовані процедури модуля `net/tls`. Якщо цей виклик виконується до того, як сокет увійшов у стан `TCP_ESTABLISHED`, ядро поверне помилку `EINVAL`.
2. **Заповнення бінарної структури:** Структура `tls12_crypto_info_aes_gcm_128` обнуляється за допомогою `memset`, після чого копіюються 16-байтний ключ, 8-байтний IV, 4-байтна сіль та 8-байтний порядковий номер `rec_seq`. Важливо пам'ятати, що масив `rec_seq` повинен містити поточний порядковий номер TLS-запису (Record Sequence Number), на якому завершилося рукостискання у користувацькому просторі. Якщо розбіжність становить хоч 1 запис, клієнт відхилить кадри через помилку аутентифікації Auth Tag (`bad_record_mac`).
3. **Передача конфігурації у `SOL_TLS`:** Другий виклик `setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info))` ініціалізує алгоритм AES-GCM у підсистемі Kernel Crypto API. З цього моменту сокет вважається "TLS-обізнаним" для напрямку відправки.
4. **Виклик `sendfile()`:** Після успішного налаштування `SOL_TLS` будь-який виклик `sendfile()` зчитує сторінки з дискового кешу (Page Cache) та передає їх у сокет. Модуль `net/tls` прозоро шифрує ці байти під час формування пакета `sk_buff`.

---

## 3. Високорівнева інтеграція kTLS з використанням OpenSSL 3.0

У реальних промислових серверах (NGINX, HAProxy, Envoy) виклики `setsockopt()` рідко виконують вручну. Замість цього довіряють процес встановлення сесії та передачі ключів бібліотеці OpenSSL 3.0+.

Бібліотека OpenSSL самостійно вилучає ключі після успішного виклику `SSL_accept()`, викликає `setsockopt(TCP_ULP)` та налаштовує `SOL_TLS`. Після цього додаток перевіряє стан сокета через прапорець `BIO_get_ktls_send()` і переходить на використанння виклику `sendfile()`.

:::tabs
```c
/* c_openssl_ktls.c - Використання OpenSSL 3.0 з kTLS на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

/*
 * Налаштування контексту OpenSSL для автоматичного використання kTLS
 */
void setup_openssl_ktls_ctx(SSL_CTX *ctx) {
    /* Дозволяємо OpenSSL автоматично передавати ключі у ядро Linux */
    SSL_CTX_set_options(ctx, SSL_OP_ENABLE_KTLS);
}

/*
 * Обслуговування клієнтського запиту: якщо kTLS активний, робимо sendfile(),
 * інакше використовуємо класичний цикл SSL_write().
 */
int serve_file_via_ktls(SSL *ssl, int sock_fd, int file_fd, size_t file_size) {
    BIO *wbio = SSL_get_wbio(ssl);

    /* Перевіряємо, чи ядро підхопило kTLS для вихідного напрямку TX */
    if (wbio != NULL && BIO_get_ktls_send(wbio)) {
        printf("[OpenSSL Integration] kTLS увімкнено! Використовуємо Zero-Copy sendfile()\n");
        off_t offset = 0;
        ssize_t sent = sendfile(sock_fd, file_fd, &offset, file_size);
        if (sent < 0) {
            perror("Помилка sendfile у режимі kTLS");
            return -1;
        }
        printf("[OpenSSL Integration] Успішно передано %zd байт через kTLS sendfile()\n", sent);
        return 0;
    }

    /* Фолбек для систем без підтримки kTLS: класичний Userspace шифрувальний цикл */
    printf("[OpenSSL Integration] kTLS недоступний. Використовуємо стандартне шифрування SSL_write()\n");
    char buffer[8192];
    ssize_t bytes_read;
    while ((bytes_read = read(file_fd, buffer, sizeof(buffer))) > 0) {
        int written = SSL_write(ssl, buffer, (int)bytes_read);
        if (written <= 0) {
            ERR_print_errors_fp(stderr);
            return -1;
        }
    }
    return 0;
}
```
```cpp
// cpp_openssl_ktls.cpp - Використання OpenSSL 3.0 з kTLS та RAII-обгортками на C++20
#include <iostream>
#include <memory>
#include <vector>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

// Кастомні делітери для розумних вказівників OpenSSL
struct SslCtxDeleter {
    void operator()(SSL_CTX* ctx) const noexcept { SSL_CTX_free(ctx); }
};
struct SslDeleter {
    void operator()(SSL* ssl) const noexcept { SSL_free(ssl); }
};

using SslCtxPtr = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using SslPtr = std::unique_ptr<SSL, SslDeleter>;

class KtlsServerSession {
    SslPtr ssl_;
    int sock_fd_;

public:
    KtlsServerSession(SslPtr ssl, int sock_fd) noexcept
        : ssl_(std::move(ssl)), sock_fd_(sock_fd) {}

    // Перевірка стану апаратного або програмного kTLS ядра
    [[nodiscard]] bool is_ktls_tx_active() const noexcept {
        BIO* wbio = SSL_get_wbio(ssl_.get());
        return wbio && BIO_get_ktls_send(wbio);
    }

    // Автоматичний вибір між Zero-Copy sendfile() та SSL_write()
    std::expected<size_t, std::error_code> transmit_file(int file_fd, size_t file_size) {
        if (is_ktls_tx_active()) {
            std::cout << "[C++ kTLS Engine] Zero-Copy sendfile() напрямок увімкнено.\n";
            off_t offset = 0;
            ssize_t bytes = ::sendfile(sock_fd_, file_fd, &offset, file_size);
            if (bytes < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            return static_cast<size_t>(bytes);
        }

        std::cout << "[C++ Userspace Engine] Фолбек на цикл SSL_write().\n";
        std::vector<char> buffer(65536);
        size_t total_written = 0;
        ssize_t read_bytes = 0;

        while ((read_bytes = ::read(file_fd, buffer.data(), buffer.size())) > 0) {
            int ret = SSL_write(ssl_.get(), buffer.data(), static_cast<int>(read_bytes));
            if (ret <= 0) {
                return std::unexpected(std::make_error_code(std::errc::io_error));
            }
            total_written += static_cast<size_t>(ret);
        }

        if (read_bytes < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return total_written;
    }
};
```
:::

---

## 4. Перевірка працездатності, трасування та профілювання

Для перевірки роботи розробленого коду на практиці використовується наступний алгоритм.

### Крок 1. Компіляція вихідних файлів

Переконайтеся, що у вашій операційній системі встановлено компілятори `gcc` / `g++` та системну бібліотеку OpenSSL 3.0+:

```bash
# Компіляція прикладу на C
gcc -O2 -Wall c_ktls_raw.c c_openssl_ktls.c -o ktls_server_c -lssl -lcrypto

# Компіляція прикладу на C++20
g++ -std=c++20 -O2 -Wall cpp_ktls_raw.cpp cpp_openssl_ktls.cpp -o ktls_server_cpp -lssl -lcrypto
```

### Крок 2. Перевірка та завантаження модуля ядра

Перед запуском сервера перевірте, чи завантажено модуль `tls`:

```bash
sudo modprobe tls
lsmod | grep tls
```

### Крок 3. Трасування системних викликів через `strace`

Запустіть сервер під управлінням утиліти `strace` для контролю виконання системних викликів `setsockopt` та `sendfile`:

```bash
strace -e setsockopt,sendfile ./ktls_server_c
```

Типовий вивід успішного трасування виглядає так:

```text
setsockopt(4, SOL_TCP, TCP_ULP, "tls", 4) = 0
setsockopt(4, SOL_TLS, TLS_TX, {info={version=771, cipher_type=51}...}, 40) = 0
sendfile(4, 3, [0], 524288000) = 524288000
```

Це підтверджує, що ядро прийняло ULP `"tls"`, встановило ключі `TLS_TX` і виконало пряму передачу 500 Мегабайт даних за один виклик `sendfile()`.

---

## 5. Поширені крайові випадки та їх вирішення

1. **Забутий прапорець `SSL_OP_ENABLE_KTLS`:** У бібліотеці OpenSSL 3.0 увімкнення kTLS за замовчуванням вимкнено з міркувань зворотної сумісності. Якщо ви не додасте виклик `SSL_CTX_set_options(ctx, SSL_OP_ENABLE_KTLS)`, функція `BIO_get_ktls_send()` завжди повертатиме `0`, а OpenSSL продовжуватиме шифрувати дані у користувацькому просторі.
2. **Обробка переривань сигналів `EINTR`:** При передачі великих файлів обсягом у кілька Гігабайт системний виклик `sendfile()` може бути перерваний сигналом асинхронного таймера або ОС. Важливо обгортати виклик `sendfile()` у цикл перевірки `while (bytes_sent < total && errno == EINTR)`.
3. **Неблокуючі сокети (`O_NONBLOCK`):** У подієвих вебсерверах (NGINX, Envoy), що працюють із механізмами `epoll` або `io_uring`, виклик `sendfile()` над kTLS сокетом може повернути помилку `EAGAIN` або `EWOULDBLOCK`. Додаток повинен коректно обробляти частковий запис (Partial Write) та відновлювати відправку при повторній події `EPOLLOUT`.
