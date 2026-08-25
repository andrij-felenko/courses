# ⚙️ Практична атестація PCIe-пристрою через користувацьку утиліту

Атестація периферійного пристрою на базі специфікації SPDM вимагає послідовної перевірки двох фундаментальних фактів: підтвердження автентичності апаратного сертифіката пристрою (доведення виробництва довіреним вендором) та перевірки відповідності зчитаних криптографічних вимірювань (Measurements) еталонному маніфесту цілісності (Reference Integrity Manifest, RIM).

У той час як ядро Linux самостійно виконує атестацію під час завантаження або ініціалізації пристрою, у хмарних середовищах та центрах обробки даних часто виникає потреба у додатковій незалежній перевірці з боку користувацького простору. Демони безпеки, оркестратори контейнерів (наприклад, Kubernetes Device Plugins) або системи Zero Trust розгортають користувацькі утиліти для періодичного аудиту стану прошивок мережевих карт, NVMe-накопичувачів та GPU-прискорювачів.

У цій практичній вставці ми реалізуємо повноцінну користувацьку утиліти перевірки атестації PCIe-пристрою для системи Linux. Утиліта зчитує ланцюжок сертифікатів із `sysfs`, вилучає публічний ключ пристрою, відкриває сирий дайджест вимірювання та виконує криптографічну верифікацію цифрового підпису ECDSA-P384 за допомогою бібліотеки OpenSSL.

## Принцип роботи та архітектура утиліти

Утиліта приймає шлях до каталогу атестації PCIe-пристрою у файловій системі `sysfs` (наприклад, `/sys/bus/pci/devices/0000:03:00.0/attestation`).

Процес перевірки складається із таких послідовних кроків:
1. **Зчитування DER-сертифіката**: Програма зчитує вміст файла `certificates/slot0`, який містить ланцюжок сертифікатів X.509 у бінарному форматі ASN.1 DER.
2. **Декодування ASN.1 та вилучення ключа**: За допомогою криптографічного декодера OpenSSL `d2i_X509` бінарні байти парсяться у внутрішню структуру `X509`. Зі структури кінцевого сертифіката вилучається публічний ключ пристрою `EVP_PKEY`.
3. **Зчитування масиву вимірювань**: З файла `measurements/raw` зчитується бінарний масив, що містить об'єднаний блок корисного навантаження вимірювань (Measurement Data) та доданий до нього наприкінці 96-байтний цифровий підпис ECDSA-P384.
4. **Криптографічна верифікація підпису**: Формується контекст підпису `EVP_MD_CTX`, налаштовується алгоритм хешування SHA-384, передається корисне навантаження даних та виконується фінальна перевірка підпису `EVP_DigestVerifyFinal`.

## Реалізація мовами C та C++

Нижче наведено дві повноцінні реалізації утиліти перевірки атестації. Мова C застосовує традиційний низькорівневий підхід із ручним керуванням пам'яттю та явними викликами очищення OpenSSL-ресурсів. Мова C++ використовує сучасні ідіоми C++20/C++23: концепцію RAII для гарантованого звільнення криптографічних контекстів, типобезпечний механізм обробки помилок `std::expected`, безелементні зрізи `std::span` та роботу з файловою системою через `std::filesystem`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <openssl/bio.h>
#include <openssl/x509.h>
#include <openssl/pem.h>
#include <openssl/evp.h>

#define MAX_PATH 512
#define BUFFER_SIZE 8192

/* Читання бінарного файла із sysfs у динамічно виділений буфер */
static unsigned char *read_sysfs_file(const char *path, size_t *out_len) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("Failed to open sysfs attribute file");
        return NULL;
    }

    unsigned char *buf = malloc(BUFFER_SIZE);
    if (!buf) {
        close(fd);
        return NULL;
    }

    ssize_t bytes_read = read(fd, buf, BUFFER_SIZE);
    close(fd);

    if (bytes_read <= 0) {
        free(buf);
        return NULL;
    }

    *out_len = (size_t)bytes_read;
    return buf;
}

/* Перевірка підпису ECDSA над дайджестом вимірювання SPDM */
int verify_spdm_measurement(const char *sysfs_dir) {
    char cert_path[MAX_PATH];
    char meas_path[MAX_PATH];
    unsigned char *cert_buf = NULL;
    unsigned char *meas_buf = NULL;
    size_t cert_len = 0, meas_len = 0;
    int result = -1;

    snprintf(cert_path, sizeof(cert_path), "%s/certificates/slot0", sysfs_dir);
    snprintf(meas_path, sizeof(meas_path), "%s/measurements/raw", sysfs_dir);

    cert_buf = read_sysfs_file(cert_path, &cert_len);
    meas_buf = read_sysfs_file(meas_path, &meas_len);

    if (!cert_buf || !meas_buf) {
        fprintf(stderr, "Error: Missing SPDM certificates or measurements in sysfs.\n");
        goto cleanup;
    }

    /* Декодування DER-сертифіката X.509 */
    const unsigned char *p = cert_buf;
    X509 *cert = d2i_X509(NULL, &p, cert_len);
    if (!cert) {
        fprintf(stderr, "Error: Failed to parse X.509 DER certificate.\n");
        goto cleanup;
    }

    /* Вилучення публічного ключа зі структури сертифіката */
    EVP_PKEY *pubkey = X509_get0_pubkey(cert);
    if (!pubkey) {
        fprintf(stderr, "Error: Failed to extract public key from certificate.\n");
        X509_free(cert);
        goto cleanup;
    }

    /* Створення контексту перевірки підпису EVP_MD_CTX */
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        X509_free(cert);
        goto cleanup;
    }

    /* Налаштування перевірки ECDSA підпису з хешем SHA-384 */
    if (EVP_DigestVerifyInit(ctx, NULL, EVP_sha384(), NULL, pubkey) <= 0) {
        fprintf(stderr, "Error initializing DigestVerify context.\n");
        EVP_MD_CTX_free(ctx);
        X509_free(cert);
        goto cleanup;
    }

    /* meas_buf містить: [Data_Block (meas_len - 96)] [Signature (96 bytes)] */
    size_t sig_len = 96;
    if (meas_len <= sig_len) {
        fprintf(stderr, "Error: Measurement buffer too small for signature.\n");
        EVP_MD_CTX_free(ctx);
        X509_free(cert);
        goto cleanup;
    }

    size_t data_len = meas_len - sig_len;
    unsigned char *data_ptr = meas_buf;
    unsigned char *sig_ptr = meas_buf + data_len;

    if (EVP_DigestVerifyUpdate(ctx, data_ptr, data_len) <= 0) {
        fprintf(stderr, "Error in DigestVerifyUpdate.\n");
        EVP_MD_CTX_free(ctx);
        X509_free(cert);
        goto cleanup;
    }

    int rc = EVP_DigestVerifyFinal(ctx, sig_ptr, sig_len);
    if (rc == 1) {
        printf("SUCCESS: SPDM measurement signature is VALID for %s\n", sysfs_dir);
        result = 0;
    } else {
        fprintf(stderr, "FAILURE: SPDM measurement signature verification FAILED!\n");
        result = -1;
    }

    EVP_MD_CTX_free(ctx);
    X509_free(cert);

cleanup:
    free(cert_buf);
    free(meas_buf);
    return result;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <sysfs_spdm_path>\n", argv[0]);
        return 1;
    }
    return verify_spdm_measurement(argv[1]) == 0 ? 0 : 1;
}
```

```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <span>
#include <expected>
#include <filesystem>

#include <openssl/bio.h>
#include <openssl/x509.h>
#include <openssl/evp.h>

namespace fs = std::filesystem;

// RAII обгортки для гарантованого звільнення криптографічних ресурсів OpenSSL
struct X509Deleter {
    void operator()(X509* cert) const noexcept {
        if (cert) X509_free(cert);
    }
};

struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const noexcept {
        if (ctx) EVP_MD_CTX_free(ctx);
    }
};

using X509Ptr = std::unique_ptr<X509, X509Deleter>;
using EvpMdCtxPtr = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

// Системні коди помилок атестації
enum class AttestationError {
    FileNotFound,
    ReadFailed,
    ParseCertificateFailed,
    ExtractKeyFailed,
    VerifyInitFailed,
    InvalidSignatureLength,
    SignatureVerificationFailed
};

class SpdmAttestationVerifier {
public:
    explicit SpdmAttestationVerifier(fs::path sysfs_dir)
        : sysfs_dir_(std::move(sysfs_dir)) {}

    [[nodiscard]] std::expected<void, AttestationError> verify() const {
        auto cert_data_res = read_file(sysfs_dir_ / "certificates" / "slot0");
        if (!cert_data_res) return std::unexpected(cert_data_res.error());

        auto meas_data_res = read_file(sysfs_dir_ / "measurements" / "raw");
        if (!meas_data_res) return std::unexpected(meas_data_res.error());

        const auto& cert_bytes = *cert_data_res;
        const auto& meas_bytes = *meas_data_res;

        const unsigned char* p = cert_bytes.data();
        X509Ptr cert{d2i_X509(nullptr, &p, static_cast<long>(cert_bytes.size()))};
        if (!cert) {
            return std::unexpected(AttestationError::ParseCertificateFailed);
        }

        EVP_PKEY* pubkey = X509_get0_pubkey(cert.get());
        if (!pubkey) {
            return std::unexpected(AttestationError::ExtractKeyFailed);
        }

        EvpMdCtxPtr ctx{EVP_MD_CTX_new()};
        if (!ctx) {
            return std::unexpected(AttestationError::VerifyInitFailed);
        }

        if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha384(), nullptr, pubkey) <= 0) {
            return std::unexpected(AttestationError::VerifyInitFailed);
        }

        constexpr size_t sig_len = 96; // Довжина підпису ECDSA-P384
        if (meas_bytes.size() <= sig_len) {
            return std::unexpected(AttestationError::InvalidSignatureLength);
        }

        size_t data_len = meas_bytes.size() - sig_len;
        std::span<const unsigned char> payload_span{meas_bytes.data(), data_len};
        std::span<const unsigned char> sig_span{meas_bytes.data() + data_len, sig_len};

        if (EVP_DigestVerifyUpdate(ctx.get(), payload_span.data(), payload_span.size()) <= 0) {
            return std::unexpected(AttestationError::SignatureVerificationFailed);
        }

        int rc = EVP_DigestVerifyFinal(ctx.get(), sig_span.data(), sig_span.size());
        if (rc == 1) {
            return {}; // Успішна верифікація підпису
        }

        return std::unexpected(AttestationError::SignatureVerificationFailed);
    }

private:
    fs::path sysfs_dir_;

    [[nodiscard]] static std::expected<std::vector<unsigned char>, AttestationError> 
    read_file(const fs::path& path) {
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(AttestationError::FileNotFound);
        }

        std::vector<unsigned char> buffer(
            (std::istreambuf_iterator<char>(file)),
            std::istreambuf_iterator<char>()
        );

        if (buffer.empty()) {
            return std::unexpected(AttestationError::ReadFailed);
        }

        return buffer;
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <sysfs_spdm_path>\n";
        return 1;
    }

    SpdmAttestationVerifier verifier{argv[1]};
    auto result = verifier.verify();

    if (result.has_value()) {
        std::cout << "SUCCESS: SPDM measurement signature is VALID for " << argv[1] << "\n";
        return 0;
    }

    std::cerr << "FAILURE: SPDM attestation failed with error code: " 
              << static_cast<int>(result.error()) << "\n";
    return 1;
}
```
:::

## Детальний розбір реалізації та ідіом коду

Розглянемо ключові інженерні рішення, застосовані при розробці утиліти:

### 1. Управління пам'яттю та автоочищення RAII у C++

При роботі з C-бібліотеками типу OpenSSL найпоширенішою помилкою є витік пам'яті під час дострокового виходу з функції при виникненні помилки. У мові C для цього використовується традиційний паттерн `goto cleanup` із послідовним звільненням ресурсів наприкінці функції.

У C++ версії ця проблема вирішується декларативно за допомогою смарт-поінтерів `std::unique_ptr` із кастомними деструкторами (`X509Deleter` та `EvpMdCtxDeleter`). При виході з області видимості функції `verify()`, незалежно від того, чи стався виняток, чи виконалася операція повернення `return`, деструктори смарт-поінтерів автоматично викликають виклики OpenSSL `X509_free()` та `EVP_MD_CTX_free()`.

### 2. Типобезпечна обробка помилок через `std::expected`

Традиційний C-код повертає цілочисельні коди помилок (`0` при успіху, `-1` при невдачі) і друкує повідомлення у `stderr`. Це ускладнює програмну обробку помилок вищими шарами додатку.

У C++ версії застосовано тип `std::expected<void, AttestationError>` із стандарту C++23. Функція повертає або порожнє успішне значення, або строгий перелічуваний тип `AttestationError`. Це повністю усуває побічні ефекти, не вимагає важкого механізму винятків (exceptions) і дозволяє викликачу утиліти чітко розрізняти тип збою (наприклад, відсутність файла у sysfs від недійсного криптографічного підпису).

### 3. Безпечна робота з буферами пам'яті через `std::span`

При маніпуляціях з бінарними даними вимірювань необхідно відокремити корисне навантаження даних від доданого наприкінці цифрового підпису. У C-версії для цього використовується ризикова арифметика вказівників (`unsigned char *sig_ptr = meas_buf + data_len`).

У C++ версії застосовується безелементний обгортковий тип `std::span<const unsigned char>`. Він не копіює байти пам'яті, але забезпечує безпечну перевірку меж та чітке розділення масиву на два вікна даних: `payload_span` для хешування та `sig_span` для верифікації підпису.

## Компіляція та запуск утиліти

Для компіляції утиліти у системі Linux необхідна наявність заголовочних файлів OpenSSL (`libssl-dev` / `openssl-devel`) та сучасного компілятора GCC (версії 13+) або Clang з підтримкою стандарту C++23.

Команди для компіляції обох версій:
```bash
# Компіляція C-версії
gcc -O2 -Wall spdm_verifier.c -o spdm_verifier_c -lcrypto

# Компіляція C++ версії (C++23)
g++ -O2 -Wall -std=c++23 spdm_verifier.cpp -o spdm_verifier_cpp -lcrypto
```

Запуск утиліти проти реального PCIe-пристрою у системі:
```bash
./spdm_verifier_cpp /sys/bus/pci/devices/0000:03:00.0/attestation
```

У разі успішного проходження підпису утиліта виведе:
```text
SUCCESS: SPDM measurement signature is VALID for /sys/bus/pci/devices/0000:03:00.0/attestation
```

Якщо підпис пристрою виявиться скомпрометованим або модифікованим, утиліта поверне код помилки 1 та надрукує:
```text
FAILURE: SPDM attestation failed with error code: 6
```
(Де код 6 відповідає `AttestationError::SignatureVerificationFailed`).
