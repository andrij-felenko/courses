# ⚙️ Практикум: Налаштування kTLS та відправка файлів через sendfile(2)

Створення високопродуктивного HTTPS-сервера роздачі контенту з підтримкою Kernel TLS дозволяє передавати файли з диска у мережу за допомогою системного виклику `sendfile(2)` без копіювання байтів у простір користувача та без навантаження CPU на шифрування. Нижче наведено реалізацію конвеєра ініціалізації kTLS сокета, передачі ключів та відправки даних на мовах C та C++ з обробкою неблокуючих I/O помилок.

## 1. Архітектурний план та етапи роботи програми

Створення сервера з підтримкою kTLS вимагає чіткого дотримання послідовності системних дій. На відміну від стандартного з'єднання, де шифрування відбувається прозоро всередині користувацьких бібліотек, при роботі з kTLS додаток бере на себе пряме управління сокетними опціями ядра.

Повний конвеєр обробки з'єднання складається з наступних послідовних кроків:

1. **Створення та прийняття TCP-з'єднання**: сервер створює слухаючий сокет, прив'язує його до порту (наприклад, 443) та приймає вхідні клієнтські підключення за допомогою системного виклику `accept()` або `accept4()`.
2. **Фаза TLS Handshake у просторі користувача**: додаток виконує стандартне встановлення TLS-з'єднання за допомогою бібліотеки OpenSSL, BoringSSL або MbedTLS. На цьому етапі відбувається аутентифікація сервера, узгодження версії протоколу (TLS 1.2 або TLS 1.3) та алгоритму шифрування (наприклад, AES-128-GCM), а також генерація спільних секретних ключів сесії.
3. **Вилучення симетричних ключів з OpenSSL**: з об'єкта сесії TLS-бібліотеки додаток зчитує згенеровані симетричні ключі (`master secret`, `key`, `iv`, `salt`). Для цього в OpenSSL використовуються внутрішні функції розбору контексту `EVP_CIPHER_CTX` або спеціалізовані експортери ключів `SSL_export_keying_material()`.
4. **Активація ULP на сокеті**: додаток викликає системну опцію `setsockopt(client_fd, IPPROTO_TCP, TCP_ULP, "tls", 3)`. Ця дія підміняє таблицю функцій сокета в ядрі Linux та готує контекст `struct tls_context`.
5. **Конфігурація передавача kTLS (TX)**: заповнюється двійкова структура `struct tls12_crypto_info_aes_gcm_128` (або її 256-бітний аналог) і передається в ядро через системний виклик `setsockopt(client_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info))`.
6. **Zero-Copy передача файлу**: відкривається цільовий файл на диску за допомогою `open()`, визначається його розмір через `fstat()`, після чого викликається `sendfile(client_fd, file_fd, &offset, file_size)`. Ядро бере сторінки безпосередньо з файлового кешу (Page Cache), виконує шифрування та передає зашифровані TCP-пакети мережевому адаптеру без жодного копіювання байтів у простір користувача.
7. **Коректне завершення з'єднання**: після завершення передачі файл і сокет закриваються через `close()`.

## 2. Реалізація сервера на мовах C та C++

Нижче наведено повноцінні, готові до компіляції приклади функцій ініціалізації kTLS та передачі файлів через `sendfile(2)` для мов C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <netinet/tcp.h>
#include <linux/tls.h>

/* Ініціалізація kTLS TX з ключами AES-128-GCM */
int setup_ktls_tx(int client_fd, const unsigned char *key, const unsigned char *iv, const unsigned char *salt) {
    /* 1. Активація ULP модуля "tls" */
    const char *ulp_name = "tls";
    if (setsockopt(client_fd, IPPROTO_TCP, TCP_ULP, ulp_name, strlen(ulp_name)) < 0) {
        perror("setsockopt TCP_ULP");
        return -1;
    }

    /* 2. Підготовка криптографічних параметрів */
    struct tls12_crypto_info_aes_gcm_128 crypto_info;
    memset(&crypto_info, 0, sizeof(crypto_info));

    crypto_info.info.version = TLS_1_2_VERSION;
    crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    memcpy(crypto_info.key, key, TLS_CIPHER_AES_GCM_128_KEY_SIZE);
    memcpy(crypto_info.iv, iv, TLS_CIPHER_AES_GCM_128_IV_SIZE);
    memcpy(crypto_info.salt, salt, TLS_CIPHER_AES_GCM_128_SALT_SIZE);
    /* Початковий послідовний номер запису (8 байт нулів на початку) */
    memset(crypto_info.rec_seq, 0, TLS_CIPHER_AES_GCM_128_REC_SEQ_SIZE);

    /* 3. Передача ключів у ядро для напрямку TX */
    if (setsockopt(client_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
        perror("setsockopt SOL_TLS TLS_TX");
        return -1;
    }

    return 0;
}

/* Передача файлу через sendfile безпосередньо у kTLS сокет з обробкою часткової відправки */
ssize_t send_file_ktls(int client_fd, const char *filepath) {
    int file_fd = open(filepath, O_RDONLY);
    if (file_fd < 0) {
        perror("open file");
        return -1;
    }

    struct stat st;
    if (fstat(file_fd, &st) < 0) {
        perror("fstat");
        close(file_fd);
        return -1;
    }

    off_t offset = 0;
    size_t total_to_send = st.st_size;
    ssize_t total_sent = 0;

    /* Цикл для обробки можливої часткової відправки даних */
    while (total_sent < total_to_send) {
        ssize_t sent = sendfile(client_fd, file_fd, &offset, total_to_send - total_sent);
        if (sent < 0) {
            if (errno == EINTR) {
                continue; /* Переривання сигналом, повторюємо спробу */
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                /* Буфер сокета заповнено у неблокуючому режимі */
                break;
            }
            perror("sendfile error");
            close(file_fd);
            return -1;
        }
        if (sent == 0) {
            break; /* Досягнуто кінця файлу або сокет закрито */
        }
        total_sent += sent;
    }

    close(file_fd);
    return total_sent;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <array>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <netinet/tcp.h>
#include <linux/tls.h>

namespace ktls {

// RAII обгортка для безпечного керування дескрипторами файлів та сокетів
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
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
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// Ідіоматична C++ обгортка конфігурації та відправки kTLS
class TlsSocketSession {
public:
    using KeyArray = std::array<uint8_t, TLS_CIPHER_AES_GCM_128_KEY_SIZE>;
    using IvArray = std::array<uint8_t, TLS_CIPHER_AES_GCM_128_IV_SIZE>;
    using SaltArray = std::array<uint8_t, TLS_CIPHER_AES_GCM_128_SALT_SIZE>;

    // Ініціалізація kTLS TX на сокеті
    static std::error_code enable_ktls_tx(int client_fd, 
                                          const KeyArray& key, 
                                          const IvArray& iv, 
                                          const SaltArray& salt) noexcept
    {
        // 1. Активація модуля ULP "tls"
        constexpr std::string_view ulp_name = "tls";
        if (::setsockopt(client_fd, IPPROTO_TCP, TCP_ULP, ulp_name.data(), ulp_name.size()) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        // 2. Заповнення двійкової структури для ядра
        struct tls12_crypto_info_aes_gcm_128 crypto_info{};
        crypto_info.info.version = TLS_1_2_VERSION;
        crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

        std::memcpy(crypto_info.key, key.data(), key.size());
        std::memcpy(crypto_info.iv, iv.data(), iv.size());
        std::memcpy(crypto_info.salt, salt.data(), salt.size());

        // 3. Передача ключів сесії у ядро
        if (::setsockopt(client_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        return {};
    }

    // Безкопійна відправка файлу через sendfile з повним контролем помилок
    static std::pair<size_t, std::error_code> send_zero_copy_file(int client_fd, std::string_view filepath) noexcept {
        SocketHandle file_fd(::open(filepath.data(), O_RDONLY));
        if (!file_fd.valid()) {
            return {0, std::error_code(errno, std::generic_category())};
        }

        struct stat st{};
        if (::fstat(file_fd.get(), &st) < 0) {
            return {0, std::error_code(errno, std::generic_category())};
        }

        off_t offset = 0;
        size_t total_to_send = st.st_size;
        size_t total_sent = 0;

        while (total_sent < total_to_send) {
            ssize_t sent = ::sendfile(client_fd, file_fd.get(), &offset, total_to_send - total_sent);
            if (sent < 0) {
                if (errno == EINTR) {
                    continue;
                }
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    break; // Сокет переповнено у неблокуючому режимі
                }
                return {total_sent, std::error_code(errno, std::generic_category())};
            }
            if (sent == 0) {
                break;
            }
            total_sent += static_cast<size_t>(sent);
        }

        return {total_sent, std::error_code{}};
    }
};

} // namespace ktls
```
:::

## 3. Детальний аналіз крайових випадків та обробка помилок

При практичній експлуатації підсистеми kTLS у високозавантажених проєктах розробники стикаються з низкою крайових випадків (Edge Cases), недотримання яких може призвести до зависання з'єднань або витоків ресурсів.

### 3.1. Неблокуючий режим (Non-blocking I/O) та помилка `EAGAIN`

У сучасних подієво-орієнтованих серверах (Epoll, io_uring, Nginx, Envoy) сокети працюють у неблокуючому режимі (`O_NONBLOCK`). 

При використанні `sendfile(2)` разом із kTLS необхідно враховувати наступні системні нюанси:
- Якщо вихідний TCP-буфер сокета переповнюється, системний виклик `sendfile()` повертає значення `-1` та встановлює `errno` у `EAGAIN` або `EWOULDBLOCK`.
- При отриманні `EAGAIN` додаток зобов'язаний зберегти поточне значення змінної `offset` і зареєструвати сокет у підсистемі `epoll` на подію запису (`EPOLLOUT`). Після отримання сповіщення про готовність сокета додаток має продовжити виклик `sendfile()` з останньої збереженої позиції `offset`.

### 3.2. Часткова відправка даних (Partial Sends) та межі TLS-записів

Системний виклик `sendfile()` у поєднанні з kTLS гарантує атомарність заголовків запису TLS, проте сам загальний обсяг відправлених даних може бути меншим за запитаний `count`.

Ядро розбиває переданий потік файлових сторінок на TLS-записи розміром до 16384 байтів. Якщо у сокетному буфері ядра залишається місце лише під 2 записи (32 КБ), а додаток просить відправити 1 МБ, `sendfile()` відправить 32 КБ і поверне значення `32768`. Додаток зобов'язаний виконувати виклик у циклі `while (total_sent < total_size)`, коректно підсумовуючи повернуті значення та інкрементуючи `offset`.

### 3.3. Переривання сигналами (`EINTR`)

Якщо під час виконання шифрування чи відправки через `sendfile()` процес отримує системний сигнал (наприклад, `SIGALRM` чи `SIGHUP`), системний виклик переривається і повертає `-1` з `errno = EINTR`. Наведений вище C та C++ код містить явну перевірку `if (errno == EINTR) continue;`, що запобігає передчасному аварійному завершенню передачі файлу.

### 3.4. Коректне закриття сокета (Close Notify Alert)

Перед закриттям сокета стандарти TLS вимагають відправки протокольного повідомлення `Close Notify Alert` (тип запису `21`). Для цього сервер повинен викликати `sendmsg()` із встановленням `cmsg_type = TLS_SET_RECORD_TYPE` до виклику `close(client_fd)`. Якщо закрити сокет без відправки Alert, клієнт отримає помилку `Truncated Record` або `Connection Reset by Peer`.

### 3.5. Взаємодія з io_uring та асинхронним викликом splice()

У сучасних ядрах Linux (версії 5.10+) виклик `sendfile()` може бути замінений на асинхронну пару `splice()` через асинхронне ядро `io_uring`. У цій схемі сторінки з дискового файлу передаються у кільцевий буфер `pipe`, звідки за допомогою `IORING_OP_SPLICE` переправляються безпосередньо у kTLS-сокет. Це забезпечує ще вищу щільність обробки запитів, виключаючи навіть перемикання контексту системних викликів.

Завдяки грамотному поєднанню C/C++ RAII-обгорток, обробки крайових випадків `EAGAIN` та безапаратного `sendfile()`, kTLS дозволяє створювати сервери роздачі контенту з гранично високою пропускною здатністю та мінімальними накладними витратами на системні виклики.
