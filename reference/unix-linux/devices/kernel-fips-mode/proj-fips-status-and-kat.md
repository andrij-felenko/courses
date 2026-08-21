# ⚙️ Практика: діагностика FIPS-режиму ядра та виклик криптографічних тестів

Ця практична робота демонструє створення системної утиліти для перевірки стану FIPS-режиму ядра Linux, глибокої інспекції зареєстрованих алгоритмів у реєстрі `/proc/crypto` та виконання безпосередніх криптографічних перевірок через інтерфейс сокетів `AF_ALG`.

## Завдання

Системному інженеру, розробнику безпекового програмного забезпечення та аудитору необхідно автоматизовано верифікувати криптографічну підсистему хоста. Перевірка має підтвердити чотири критичні властивості операційного середовища:
1. Ядро дійсно працює в активному режимі FIPS: системний прапорець `/proc/sys/crypto/fips_enabled` існує та містить числове значення `1`.
2. Усі зареєстровані в ядрі криптографічні трансформації успішно пройшли обов'язкові самоперевірки Known Answer Tests (KAT) під час завантаження ядра або завантаження модулів (`selftest: passed`).
3. Заборонені та криптографічно дискредитовані алгоритми (такі як MD5 або DES) гарантовано блокуються ядром при спробі їх ініціалізації через системний інтерфейс `AF_ALG` простору користувача.
4. Схвалений стандартом FIPS симетричний шифр (AES у режимі CBC зі 128-бітним ключем) коректно функціонує в просторі ядра та повертає детерміністичний шифротекст, ідентичний еталонному вектору NIST SP 800-38A.

## Архітектура перевірки та інтерфейс `AF_ALG`

Для взаємодії з криптографічною підсистемою ядра з простору користувача Linux надає спеціальний сокетний інтерфейс `AF_ALG` (Address Family Algorithm, числове значення константи `38`). Робота з ним побудована на трифазній моделі:

1. **Створення сокета та прив'язка до алгоритму:** процес створює керівний сокет викликом `socket(AF_ALG, SOCK_SEQPACKET, 0)` та прив'язує його викликом `bind()` до структури `sockaddr_alg`. У структурі вказується тип перетворення (`"skcipher"`, `"hash"`, `"aead"`, `"rng"`) та ім'я алгоритму (наприклад, `"cbc(aes)"` або `"md5"`). Якщо ядро перебуває в режимі FIPS і запитаний алгоритм заборонений, `bind()` негайно завершується з помилкою `-ENOENT`.
2. **Конфігурація ключа та відкриття робочого каналу:** за допомогою `setsockopt(sock, SOL_ALG, ALG_SET_KEY, ...)` встановлюється симетричний ключ. Після цього виклик `accept(sock, NULL, 0)` повертає новий файловий дескриптор робочої сесії шифрування, а початковий сокет можна закрити.
3. **Передача даних і параметрів керування:** вектор ініціалізації (IV) та напрямок операції (шифрування чи дешифрування) передаються у ядро через допоміжні керівні повідомлення `struct msghdr` (ancillary control messages / `cmsg`) під час виклику `sendmsg()`. Ядро виконує перетворення у відповідному криптографічному контексті драйвера (наприклад, використовуючи апаратні інструкції процесора AES-NI) і повертає готовий шифротекст через системний виклик `read()`.

## Реалізація

Утиліту реалізовано мовою C та її ідіоматичним еквівалентом на сучасному C++20 із застосуванням RAII для дескрипторів та обробкою результатів через `std::expected`.

:::tabs
```c
/* fips_inspector.c — перевірка статусу FIPS ядра та тестування через AF_ALG */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

#ifndef AF_ALG
#define AF_ALG 38
#endif
#ifndef SOL_ALG
#define SOL_ALG 279
#endif

/* Перевірка прапорця в procfs */
static int check_fips_sysctl(void) {
    int fd = open("/proc/sys/crypto/fips_enabled", O_RDONLY);
    if (fd < 0) {
        if (errno == ENOENT) {
            printf("[INFO] /proc/sys/crypto/fips_enabled відсутній (ядро без CONFIG_CRYPTO_FIPS)\n");
            return 0;
        }
        perror("[ERR] Не вдалося відкрити fips_enabled");
        return -1;
    }

    char buf[16];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = '\0';

    int enabled = (buf[0] == '1');
    printf("[INFO] Статус ядра FIPS: %s (fips_enabled = %c)\n",
           enabled ? "АКТИВНИЙ" : "ВИМКНЕНО", buf[0]);
    return enabled;
}

/* Інспекція /proc/crypto на предмет провалених тестів */
static int audit_proc_crypto(void) {
    FILE *f = fopen("/proc/crypto", "r");
    if (!f) {
        perror("[ERR] Не вдалося відкрити /proc/crypto");
        return -1;
    }

    char line[256];
    char current_driver[128] = "unknown";
    int passed_count = 0, failed_count = 0;

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "driver", 6) == 0) {
            char *colon = strchr(line, ':');
            if (colon) {
                sscanf(colon + 1, "%127s", current_driver);
            }
        } else if (strncmp(line, "selftest", 8) == 0) {
            char *colon = strchr(line, ':');
            if (colon) {
                char status[32];
                sscanf(colon + 1, "%31s", status);
                if (strcmp(status, "passed") == 0) {
                    passed_count++;
                } else if (strcmp(status, "failed") == 0) {
                    printf("[WARN] Алгоритм %s провалив KAT (selftest: failed)!\n", current_driver);
                    failed_count++;
                }
            }
        }
    }
    fclose(f);
    printf("[INFO] Реєстр /proc/crypto: перевірено %d алгоритмів, помилок: %d\n",
           passed_count, failed_count);
    return failed_count == 0 ? 0 : -1;
}

/* Тест дозволеного AES-CBC через AF_ALG */
static int test_af_alg_aes_cbc(void) {
    /* NIST SP 800-38A вектор: Key 128, Plaintext 16, IV 16 */
    static const unsigned char key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    static const unsigned char iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    static const unsigned char pt[16] = {
        0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96,
        0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a
    };
    static const unsigned char expected_ct[16] = {
        0x76, 0x49, 0xab, 0xac, 0x81, 0x19, 0xb2, 0x46,
        0xce, 0xe9, 0x8e, 0x9b, 0x12, 0xe9, 0x19, 0x7d
    };

    int sock = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (sock < 0) {
        perror("[ERR] socket(AF_ALG)");
        return -1;
    }

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "skcipher",
        .salg_name = "cbc(aes)"
    };

    if (bind(sock, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("[ERR] bind(cbc(aes))");
        close(sock);
        return -1;
    }

    if (setsockopt(sock, SOL_ALG, ALG_SET_KEY, key, sizeof(key)) < 0) {
        perror("[ERR] setsockopt(ALG_SET_KEY)");
        close(sock);
        return -1;
    }

    int op_fd = accept(sock, NULL, 0);
    close(sock);
    if (op_fd < 0) {
        perror("[ERR] accept(op_fd)");
        return -1;
    }

    /* Підготовка структури керування для передачі IV та команди шифрування */
    char cbuf[CMSG_SPACE(sizeof(__u32)) + CMSG_SPACE(sizeof(struct af_alg_iv) + 16)];
    memset(cbuf, 0, sizeof(cbuf));

    struct msghdr msg = {0};
    struct iovec iov = { .iov_base = (void *)pt, .iov_len = sizeof(pt) };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_OP;
    cmsg->cmsg_len = CMSG_LEN(sizeof(__u32));
    *(__u32 *)CMSG_DATA(cmsg) = ALG_OP_ENCRYPT;

    cmsg = CMSG_NXTHDR(&msg, cmsg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_IV;
    cmsg->cmsg_len = CMSG_LEN(sizeof(struct af_alg_iv) + 16);
    struct af_alg_iv *iv_msg = (struct af_alg_iv *)CMSG_DATA(cmsg);
    iv_msg->ivlen = 16;
    memcpy(iv_msg->iv, iv, 16);

    if (sendmsg(op_fd, &msg, 0) < 0) {
        perror("[ERR] sendmsg()");
        close(op_fd);
        return -1;
    }

    unsigned char ct[16];
    if (read(op_fd, ct, sizeof(ct)) != sizeof(ct)) {
        perror("[ERR] read(ct)");
        close(op_fd);
        return -1;
    }
    close(op_fd);

    if (memcmp(ct, expected_ct, sizeof(ct)) == 0) {
        printf("[OK] Тест шифрування cbc(aes) через ядро: ВЕКТОР ЗБІГСЯ\n");
        return 0;
    } else {
        printf("[FAIL] Шифротекст cbc(aes) не відповідає еталону!\n");
        return -1;
    }
}

/* Негативний тест спроби ініціалізації забороненого алгоритму */
static int test_disallowed_cipher(void) {
    int sock = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (sock < 0) return -1;

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "hash",
        .salg_name = "md5"
    };

    int res = bind(sock, (struct sockaddr *)&sa, sizeof(sa));
    int saved_errno = errno;
    close(sock);

    if (res < 0 && saved_errno == ENOENT) {
        printf("[OK] Заборонений алгоритм md5 успішно заблоковано ядром (ENOENT)\n");
        return 0;
    } else if (res == 0) {
        printf("[WARN] Алгоритм md5 успішно створено (FIPS не заблокував алгоритм)\n");
        return 1;
    } else {
        printf("[INFO] bind(md5) повернув несподіваний статус: errno=%d\n", saved_errno);
        return -1;
    }
}

int main(void) {
    printf("=== Інспекція FIPS-режиму ядра Linux ===\n");
    int fips = check_fips_sysctl();
    audit_proc_crypto();
    test_af_alg_aes_cbc();
    test_disallowed_cipher();
    return 0;
}
```
```cpp
// fips_inspector.cpp — ідіоматична перевірка FIPS ядра та AF_ALG на C++20
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <array>
#include <memory>
#include <span>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

#ifndef AF_ALG
#define AF_ALG 38
#endif
#ifndef SOL_ALG
#define SOL_ALG 279
#endif

// RAII обгортка для володіння системними файловими дескрипторами
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_{fd} {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_{other.release()} {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

enum class FipsError {
    SysctlNotFound,
    AccessDenied,
    ProcCryptoCorrupt,
    SocketError,
    BindFailed,
    CryptoMismatch,
    DisallowedAllowed
};

// Перевірка прапорця fips_enabled через потік C++
std::expected<bool, FipsError> check_fips_status() {
    std::ifstream file("/proc/sys/crypto/fips_enabled");
    if (!file.is_open()) {
        return std::unexpected(FipsError::SysctlNotFound);
    }
    char val{'0'};
    file >> val;
    return val == '1';
}

// Повний аудит статусів самоперевірок у /proc/crypto
std::expected<std::pair<int, int>, FipsError> audit_crypto_registry() {
    std::ifstream file("/proc/crypto");
    if (!file.is_open()) {
        return std::unexpected(FipsError::ProcCryptoCorrupt);
    }

    std::string line;
    std::string current_driver = "unknown";
    int passed = 0, failed = 0;

    while (std::getline(file, line)) {
        if (line.starts_with("driver")) {
            auto pos = line.find(':');
            if (pos != std::string::npos) {
                current_driver = line.substr(pos + 1);
            }
        } else if (line.starts_with("selftest")) {
            auto pos = line.find(':');
            if (pos != std::string::npos) {
                auto status = line.substr(pos + 1);
                if (status.find("passed") != std::string::npos) {
                    ++passed;
                } else if (status.find("failed") != std::string::npos) {
                    std::cerr << "[WARN] Драйвер " << current_driver << " провалив KAT!\n";
                    ++failed;
                }
            }
        }
    }
    return std::pair{passed, failed};
}

// Тестування шифрування AES-CBC через AF_ALG з перевіркою вектора
std::expected<void, FipsError> test_aes_encryption() {
    constexpr std::array<uint8_t, 16> key{
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    constexpr std::array<uint8_t, 16> iv{
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    constexpr std::array<uint8_t, 16> plaintext{
        0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96,
        0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a
    };
    constexpr std::array<uint8_t, 16> expected_ct{
        0x76, 0x49, 0xab, 0xac, 0x81, 0x19, 0xb2, 0x46,
        0xce, 0xe9, 0x8e, 0x9b, 0x12, 0xe9, 0x19, 0x7d
    };

    FileDescriptor sock{::socket(AF_ALG, SOCK_SEQPACKET, 0)};
    if (!sock.is_valid()) return std::unexpected(FipsError::SocketError);

    sockaddr_alg sa{};
    sa.salg_family = AF_ALG;
    std::strncpy(reinterpret_cast<char*>(sa.salg_type), "skcipher", sizeof(sa.salg_type) - 1);
    std::strncpy(reinterpret_cast<char*>(sa.salg_name), "cbc(aes)", sizeof(sa.salg_name) - 1);

    if (::bind(sock.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected(FipsError::BindFailed);
    }

    if (::setsockopt(sock.get(), SOL_ALG, ALG_SET_KEY, key.data(), key.size()) < 0) {
        return std::unexpected(FipsError::BindFailed);
    }

    FileDescriptor op_fd{::accept(sock.get(), nullptr, nullptr)};
    if (!op_fd.is_valid()) return std::unexpected(FipsError::SocketError);

    char cbuf[CMSG_SPACE(sizeof(uint32_t)) + CMSG_SPACE(sizeof(af_alg_iv) + 16)]{};
    msghdr msg{};
    iovec iov{ .iov_base = const_cast<uint8_t*>(plaintext.data()), .iov_len = plaintext.size() };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    auto* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_OP;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint32_t));
    *reinterpret_cast<uint32_t*>(CMSG_DATA(cmsg)) = ALG_OP_ENCRYPT;

    cmsg = CMSG_NXTHDR(&msg, cmsg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_IV;
    cmsg->cmsg_len = CMSG_LEN(sizeof(af_alg_iv) + 16);
    auto* iv_msg = reinterpret_cast<af_alg_iv*>(CMSG_DATA(cmsg));
    iv_msg->ivlen = 16;
    std::memcpy(iv_msg->iv, iv.data(), iv.size());

    if (::sendmsg(op_fd.get(), &msg, 0) < 0) {
        return std::unexpected(FipsError::SocketError);
    }

    std::array<uint8_t, 16> ct{};
    if (::read(op_fd.get(), ct.data(), ct.size()) != static_cast<ssize_t>(ct.size())) {
        return std::unexpected(FipsError::SocketError);
    }

    if (ct != expected_ct) {
        return std::unexpected(FipsError::CryptoMismatch);
    }

    return {};
}

// Тестування блокування несхваленого алгоритму MD5
std::expected<bool, FipsError> test_md5_rejection() {
    FileDescriptor sock{::socket(AF_ALG, SOCK_SEQPACKET, 0)};
    if (!sock.is_valid()) return std::unexpected(FipsError::SocketError);

    sockaddr_alg sa{};
    sa.salg_family = AF_ALG;
    std::strncpy(reinterpret_cast<char*>(sa.salg_type), "hash", sizeof(sa.salg_type) - 1);
    std::strncpy(reinterpret_cast<char*>(sa.salg_name), "md5", sizeof(sa.salg_name) - 1);

    int res = ::bind(sock.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa));
    if (res < 0 && errno == ENOENT) {
        return true; // Алгоритм коректно заблоковано ядром
    }
    if (res == 0) {
        return false; // Алгоритм не заблоковано (порушення FIPS)
    }
    return std::unexpected(FipsError::BindFailed);
}

int main() {
    std::cout << "=== Інспекція FIPS-режиму ядра (C++20) ===\n";

    if (auto status = check_fips_status(); status) {
        std::cout << "[INFO] FIPS статус: " << (*status ? "АКТИВНИЙ" : "ВИМКНЕНО") << "\n";
    } else {
        std::cout << "[INFO] Файл fips_enabled не знайдено (ядро без CONFIG_CRYPTO_FIPS)\n";
    }

    if (auto reg = audit_crypto_registry(); reg) {
        std::cout << "[INFO] Реєстр /proc/crypto: перевірено " << reg->first
                  << " алгоритмів, помилок: " << reg->second << "\n";
    }

    if (auto aes_res = test_aes_encryption(); aes_res) {
        std::cout << "[OK] Тест шифрування cbc(aes): ВЕКТОР ЗБІГСЯ\n";
    } else {
        std::cout << "[FAIL] Помилка виконання тесту AES\n";
    }

    if (auto md5_res = test_md5_rejection(); md5_res) {
        if (*md5_res) {
            std::cout << "[OK] MD5 успішно заблоковано ядром (ENOENT)\n";
        } else {
            std::cout << "[WARN] MD5 дозволено до використання\n";
        }
    }
    return 0;
}
```
:::

## Розбір роботи програми та аналіз поведінки

Після компіляції програми (`gcc -O2 fips_inspector.c -o fips_c` або `g++ -std=c++20 -O2 fips_inspector.cpp -o fips_cpp`) її виконання в різних середовищах демонструє принципову різницю в поведінці криптографічного ядра.

### 1. Виконання на звичайному ядрі без `fips=1`

```
=== Інспекція FIPS-режиму ядра Linux ===
[INFO] Статус ядра FIPS: ВИМКНЕНО (fips_enabled = 0)
[INFO] Реєстр /proc/crypto: перевірено 142 алгоритмів, помилок: 0
[OK] Тест шифрування cbc(aes) через ядро: ВЕКТОР ЗБІГСЯ
[WARN] Алгоритм md5 успішно створено (FIPS не заблокував алгоритм)
```

На стандартному ядрі перевірка `cbc(aes)` успішна, проте запит на створення трансформації `md5` також проходить безперешкодно, оскільки фільтр обмежень вимкнений.

### 2. Виконання на сертифікованому ядрі з `fips=1`

```
=== Інспекція FIPS-режиму ядра Linux ===
[INFO] Статус ядра FIPS: АКТИВНИЙ (fips_enabled = 1)
[INFO] Реєстр /proc/crypto: перевірено 86 алгоритмів, помилок: 0
[OK] Тест шифрування cbc(aes) через ядро: ВЕКТОР ЗБІГСЯ
[OK] Заборонений алгоритм md5 успішно заблоковано ядром (ENOENT)
```

У FIPS-режимі загальна кількість видимих у реєстрі алгоритмів зменшується: усі несхвалені реалізації або не завантажуються, або позначаються як внутрішні. Спроба прив'язки до `md5` перехоплюється функцією ядра `crypto_alloc_tfm()`, яка повертає `-ENOENT`, гарантуючи, що жодна програма не зможе використати слабкий алгоритм через ядерний інтерфейс.

## Синхронні та асинхронні криптографічні трансформації

У викликах `AF_ALG` важливо враховувати тип драйвера, який обслуговує запит у просторі ядра. Драйвери бувають двох категорій:
1. **Синхронні драйвери (наприклад, `aes-generic` або `aes-aesni`):** операція шифрування виконується на поточному ядрі процесора безпосередньо під час обробки системного виклику `sendmsg()`. Коли системний виклик повертає керування, результат уже готовий у внутрішніх буферах сокета.
2. **Асинхронні драйвери (апаратні прискорювачі Intel QAT, AMD CCP, ARM Crypto):** ядро передає дескриптор буфера в кільцеву чергу DMA апаратного контролера. Якщо апаратний прискорювач працює в асинхронному режимі, ядро призупиняє викликаючий процес або використовує внутрішню структуру `crypto_wait` для очікування сигналу завершення переривання від контролера пристрою. У FIPS-режимі апаратні прискорювачі проходять окремі Known Answer Tests під час ініціалізації відповідного драйвера PCI.

## Простеження виконання через Ftrace та системні трасування

Для детального аналізу внутрішньої послідовності викликів у ядрі під час роботи утиліти можна скористатися механізмом `ftrace`. Коли утиліта виконує системний виклик `bind()` до сокета `AF_ALG`, ядро викликає ланцюжок внутрішніх функцій підсистеми криптографії:

```
sys_bind()
  └── alg_bind()
        ├── crypto_alloc_skcipher("cbc(aes)", 0, 0)
        │     ├── crypto_find_alg()
        │     └── crypto_larval_lookup()
        └── skcipher_setkey()
```

Якщо передати ім'я несхваленого алгоритму (`md5`), функція `crypto_find_alg()` під час активного прапорця `fips_enabled` перевіряє таблицю реєстрації та виявляє відсутність дозволу на публічне використання алгоритму. У журналі `dmesg` та системному трейсі це відображається як повернення покажчика помилки `ERR_PTR(-ENOENT)`.

## Пастки та крайові випадки

1. **Відмінність між `fips_enabled == 0` та відсутністю файлу:** якщо файл `/proc/sys/crypto/fips_enabled` не існує взагалі, ядро було скомпільовано без опції `CONFIG_CRYPTO_FIPS=y`. У такому разі прапорець неможливо активувати жодними параметрами завантажувача (`fips=1` у cmdline буде просто проігноровано ядром як невідомий параметр).
2. **Семантика помилки `-ENOENT` у сокетах `AF_ALG`:** якщо запитати алгоритм `md5` або `des` на звичайному ядрі без завантаженого відповідного модуля, ядро поверне `-ENOENT`. Проте в режимі FIPS ядро повертає `-ENOENT` навіть тоді, коли модуль `md5.ko` фізично присутній на диску, оскільки внутрішній фільтр Crypto API блокує його реєстрацію або маскує його видимість для простору користувача.
3. **Обмеження довжини буфера керування `cbuf`:** при передачі вектора ініціалізації через `sendmsg()` структура `af_alg_iv` вимагає суворого вирівнювання за допомогою макросів `CMSG_SPACE` та `CMSG_LEN`. Некоректний розрахунок довжини заголовка призводить до негайної відмови системного виклику з кодом `-EINVAL`.
4. **Вимоги до привілеїв:** інтерфейс `AF_ALG` доступний неініційованим користувачам без привілеїв суперкористувача `root` (не вимагає `CAP_SYS_ADMIN`), що дозволяє будь-якому непривілейованому процесу валідувати стан криптографічного модуля ядра.
5. **Робота в контейнерах та мережевих просторах імен:** простір імен `netns` ізолює мережеві інтерфейси, проте сокети `AF_ALG` використовують єдиний глобальний реєстр криптографічних трансформацій ядра хоста. Якщо на хості увімкнено FIPS, усі контейнери автоматично успадковують обмеження на рівні сокетів `AF_ALG`.
