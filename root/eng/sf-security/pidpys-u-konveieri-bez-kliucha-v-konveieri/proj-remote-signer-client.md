# ⚙️ Клієнт віддаленого підпису артефактів із верифікацією OIDC та mTLS-тунелем

Утиліта клієнта віддаленого підписання виконується як фінальний крок у конвеєрі CI/CD перед випуском бінарного релізу чи прошивки мікроконтролера. Її призначення — обчислити криптографічний геш зібраного файлу, отримати ефемерний OIDC-токен ідентичності з середовища раннера, передати ці дані через захищений mTLS-тунель до ізольованої служби підпису та зберегти отриманий цифровий підпис і ланцюжок сертифікатів поруч із артефактом.

---

### Постановка задачі та інженерні вимоги

Конвеєру збірки необхідно підписати скомпільований файл `firmware.bin` цифровим підписом ECDSA (P-256) за допомогою апаратного ключа, розміщеного в корпоративному HSM. 

Програма-клієнт повинна задовольняти наступним технічним вимогам:
1. **Потокове обчислення дайджесту:** Не завантажувати весь файл у пам'ять цілком (файли можуть мати розмір у гігабайти). Читання має відбуватися фіксованими блоками (наприклад, по 8 КіБ) через інтерфейс потокового гешування `EVP_DigestUpdate`.
2. **Нульовий витік секретів:** Програма не повинна записувати OIDC-токен або передані параметри у відкриті файли чи логи консолі.
3. **Строга взаємна автентифікація (mTLS):** З'єднання з сервісом підпису встановлюється винятково за протоколом TLS 1.3 із перевіркою кореневого сертифіката CA організації та пред'явленням клієнтського сертифіката раннера.
4. **Коректне розбирання JSON та кодування Base64/Hex:** Формування коректного корисного навантаження для віддаленого шлюзу та збереження вихідного бінарного підпису у файл `firmware.bin.sig`.

---

### Реалізація клієнта: C (OpenSSL 3.0) та C++ (C++20 RAII)

Нижче наведено паралельні реалізації клієнта мовами C (чистий OpenSSL API з ручним контролем пам'яті та дескрипторів) та C++ (сучасний C++20 з використанням розумних вказівників, `std::expected`, безпечних діапазонів `std::span` та виключенням ручного управління ресурсами).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

#define CHUNK_SIZE 8192
#define DIGEST_LEN 32

/* Обчислення SHA-256 дайджесту файлу через OpenSSL EVP API */
int compute_sha256(const char *filepath, uint8_t *digest_out) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        perror("Помилка відкриття файлу для гешування");
        return -1;
    }

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx) {
        fclose(fp);
        return -1;
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL) != 1) {
        EVP_MD_CTX_free(mdctx);
        fclose(fp);
        return -1;
    }

    uint8_t buffer[CHUNK_SIZE];
    size_t bytes_read = 0;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1) {
            EVP_MD_CTX_free(mdctx);
            fclose(fp);
            return -1;
        }
    }

    unsigned int len = 0;
    if (EVP_DigestFinal_ex(mdctx, digest_out, &len) != 1 || len != DIGEST_LEN) {
        EVP_MD_CTX_free(mdctx);
        fclose(fp);
        return -1;
    }

    EVP_MD_CTX_free(mdctx);
    fclose(fp);
    return 0;
}

/* Перетворення бінарного дайджесту в шістнадцятковий рядок */
void digest_to_hex(const uint8_t *digest, char *hex_out) {
    for (int i = 0; i < DIGEST_LEN; ++i) {
        sprintf(hex_out + (i * 2), "%02x", digest[i]);
    }
    hex_out[DIGEST_LEN * 2] = '\0';
}

/* Виконання mTLS запиту до служби підпису */
int send_remote_sign_request(
    const char *host_port,
    const char *ca_cert_path,
    const char *client_cert_path,
    const char *client_key_path,
    const char *json_payload,
    char *response_out,
    size_t response_max_len
) {
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) return -1;

    SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION);

    /* Завантаження довіреного CA сертифіката */
    if (SSL_CTX_load_verify_locations(ctx, ca_cert_path, NULL) != 1) {
        SSL_CTX_free(ctx);
        return -1;
    }

    /* Завантаження клієнтського сертифіката mTLS для раннера */
    if (client_cert_path && client_key_path) {
        if (SSL_CTX_use_certificate_file(ctx, client_cert_path, SSL_FILETYPE_PEM) != 1 ||
            SSL_CTX_use_PrivateKey_file(ctx, client_key_path, SSL_FILETYPE_PEM) != 1) {
            SSL_CTX_free(ctx);
            return -1;
        }
    }

    BIO *bio = BIO_new_ssl_connect(ctx);
    if (!bio) {
        SSL_CTX_free(ctx);
        return -1;
    }

    BIO_set_conn_hostname(bio, host_port);

    SSL *ssl = NULL;
    BIO_get_ssl(bio, &ssl);
    if (!ssl) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return -1;
    }

    SSL_set_tlsext_host_name(ssl, "signing.internal.acme.net");

    if (BIO_do_connect(bio) <= 0) {
        BIO_free_all(bio);
        SSL_CTX_free(ctx);
        return -1;
    }

    /* Формування HTTP/1.1 POST повідомлення */
    char http_header[1024];
    int header_len = snprintf(
        http_header, sizeof(http_header),
        "POST /api/v1/sign HTTP/1.1\r\n"
        "Host: %s\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n\r\n",
        "signing.internal.acme.net",
        strlen(json_payload)
    );

    BIO_write(bio, http_header, header_len);
    BIO_write(bio, json_payload, strlen(json_payload));

    int total_read = 0;
    int bytes = 0;
    while ((bytes = BIO_read(bio, response_out + total_read, response_max_len - total_read - 1)) > 0) {
        total_read += bytes;
    }
    response_out[total_read] = '\0';

    BIO_free_all(bio);
    SSL_CTX_free(ctx);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <артефакт> <oidc_token>\n", argv[0]);
        return 1;
    }

    const char *artifact_path = argv[1];
    const char *oidc_token = argv[2];
    uint8_t digest[DIGEST_LEN];

    if (compute_sha256(artifact_path, digest) != 0) {
        fprintf(stderr, "Помилка обчислення гешу від %s\n", artifact_path);
        return 1;
    }

    char hex_digest[DIGEST_LEN * 2 + 1];
    digest_to_hex(digest, hex_digest);

    char json_request[2048];
    snprintf(
        json_request, sizeof(json_request),
        "{\"digest\":\"%s\",\"algorithm\":\"ECDSA_P256\",\"oidc_token\":\"%s\",\"key_alias\":\"firmware-prod\"}",
        hex_digest, oidc_token
    );

    char response[8192];
    if (send_remote_sign_request("10.240.12.45:8443", "ca.crt", "runner.crt", "runner.key", json_request, response, sizeof(response)) != 0) {
        fprintf(stderr, "Помилка зв'язку зі службою підпису\n");
        return 1;
    }

    printf("Отримано відповідь від служби підпису:\n%s\n", response);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <iomanip>
#include <sstream>
#include <openssl/evp.h>
#include <openssl/ssl.h>
#include <openssl/bio.h>
#include <openssl/err.h>

namespace signing {

// RAII обгортки для структур OpenSSL
struct EvpMdCtxDeleter { void operator()(EVP_MD_CTX *ctx) const { if (ctx) EVP_MD_CTX_free(ctx); } };
struct SslCtxDeleter   { void operator()(SSL_CTX *ctx) const   { if (ctx) SSL_CTX_free(ctx); } };
struct BioDeleter      { void operator()(BIO *bio) const       { if (bio) BIO_free_all(bio); } };

using ScopedMdCtx  = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;
using ScopedSslCtx = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using ScopedBio    = std::unique_ptr<BIO, BioDeleter>;

constexpr size_t DigestSize = 32;
constexpr size_t BufferSize = 8192;

using DigestArray = std::array<uint8_t, DigestSize>;

// Потокове обчислення SHA-256
std::expected<DigestArray, std::string> compute_sha256(std::string_view filepath) {
    std::ifstream file(filepath.data(), std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Неможливо відкрити цільовий файл: " + std::string(filepath));
    }

    ScopedMdCtx ctx(EVP_MD_CTX_new());
    if (!ctx || EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) != 1) {
        return std::unexpected("Помилка ініціалізації EVP контексту");
    }

    std::vector<char> buffer(BufferSize);
    while (file.read(buffer.data(), buffer.size()) || file.gcount() > 0) {
        if (EVP_DigestUpdate(ctx.get(), buffer.data(), file.gcount()) != 1) {
            return std::unexpected("Помилка оновлення EVP дайджесту");
        }
    }

    DigestArray digest{};
    unsigned int len = 0;
    if (EVP_DigestFinal_ex(ctx.get(), digest.data(), &len) != 1 || len != DigestSize) {
        return std::unexpected("Помилка фіналізації EVP дайджесту");
    }

    return digest;
}

std::string to_hex(std::span<const uint8_t> bytes) {
    std::ostringstream oss;
    for (uint8_t b : bytes) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    return oss.str();
}

class RemoteSignerClient {
public:
    RemoteSignerClient(std::string host_port, std::string ca_path, std::string cert_path = "", std::string key_path = "")
        : host_port_(std::move(host_port)), ca_path_(std::move(ca_path)), cert_path_(std::move(cert_path)), key_path_(std::move(key_path)) {}

    std::expected<std::string, std::string> sign(std::string_view hex_digest, std::string_view oidc_token, std::string_view key_alias) {
        ScopedSslCtx ctx(SSL_CTX_new(TLS_client_method()));
        if (!ctx) return std::unexpected("Помилка створення SSL_CTX");

        SSL_CTX_set_min_proto_version(ctx.get(), TLS1_3_VERSION);

        if (SSL_CTX_load_verify_locations(ctx.get(), ca_path_.c_str(), nullptr) != 1) {
            return std::unexpected("Помилка завантаження CA сертифіката");
        }

        if (!cert_path_.empty() && !key_path_.empty()) {
            if (SSL_CTX_use_certificate_file(ctx.get(), cert_path_.c_str(), SSL_FILETYPE_PEM) != 1 ||
                SSL_CTX_use_PrivateKey_file(ctx.get(), key_path_.c_str(), SSL_FILETYPE_PEM) != 1) {
                return std::unexpected("Помилка налаштування клієнтського сертифіката mTLS");
            }
        }

        ScopedBio bio(BIO_new_ssl_connect(ctx.get()));
        if (!bio) return std::unexpected("Помилка створення BIO з'єднання");

        BIO_set_conn_hostname(bio.get(), host_port_.c_str());

        SSL *ssl = nullptr;
        BIO_get_ssl(bio.get(), &ssl);
        if (!ssl) return std::unexpected("Неможливо отримати SSL об'єкт із BIO");

        SSL_set_tlsext_host_name(ssl, "signing.internal.acme.net");

        if (BIO_do_connect(bio.get()) <= 0) {
            return std::unexpected("Помилка встановлення захищеного TCP/TLS з'єднання");
        }

        std::string json_body = "{\"digest\":\"" + std::string(hex_digest) +
                                "\",\"algorithm\":\"ECDSA_P256\",\"oidc_token\":\"" +
                                std::string(oidc_token) + "\",\"key_alias\":\"" +
                                std::string(key_alias) + "\"}";

        std::string request = "POST /api/v1/sign HTTP/1.1\r\n"
                              "Host: signing.internal.acme.net\r\n"
                              "Content-Type: application/json\r\n"
                              "Content-Length: " + std::to_string(json_body.size()) + "\r\n"
                              "Connection: close\r\n\r\n" + json_body;

        BIO_write(bio.get(), request.data(), static_cast<int>(request.size()));

        std::vector<char> resp_buf(BufferSize);
        std::string response;
        int read_bytes = 0;
        while ((read_bytes = BIO_read(bio.get(), resp_buf.data(), static_cast<int>(resp_buf.size()))) > 0) {
            response.append(resp_buf.data(), read_bytes);
        }

        return response;
    }

private:
    std::string host_port_;
    std::string ca_path_;
    std::string cert_path_;
    std::string key_path_;
};

} // namespace signing

int main(int argc, char *argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_артефакту> <oidc_token>\n";
        return 1;
    }

    auto digest_res = signing::compute_sha256(argv[1]);
    if (!digest_res) {
        std::cerr << "Помилка гешування: " << digest_res.error() << '\n';
        return 1;
    }

    std::string hex_hash = signing::to_hex(*digest_res);
    signing::RemoteSignerClient client("10.240.12.45:8443", "ca.crt", "runner.crt", "runner.key");

    auto sign_res = client.sign(hex_hash, argv[2], "firmware-prod");
    if (!sign_res) {
        std::cerr << "Помилка віддаленого підпису: " << sign_res.error() << '\n';
        return 1;
    }

    std::cout << "Сервіс успішно згенерував підпис:\n" << *sign_res << '\n';
    return 0;
}
```
:::

---

### Порівняльний аналіз реалізацій та архітектурні відмінності

Реалізації на C та C++ демонструють принципову різницю в підходах до управління ресурсами та безпеки роботи з криптографічними об'єктами:

1. **Керування пам'яттю та ресурсами:**
   * У версії на C кожен виділений контекст `EVP_MD_CTX`, `SSL_CTX` та дескриптор введення-виведення `BIO` вимагає ручного відстеження та обов'язкового виклику парних функцій звільнення (`EVP_MD_CTX_free`, `SSL_CTX_free`, `BIO_free_all`, `fclose`) на кожній гілці повернення помилки.
   * У версії на C++ застосовано ідіому RAII (Resource Acquisition Is Initialization): створено спеціалізовані функтори видалення (`EvpMdCtxDeleter`, `SslCtxDeleter`, `BioDeleter`), загорнуті в `std::unique_ptr`. При виході з області видимості через будь-який виняток або повернення значення деструктори автоматично гарантують відсутність витоків пам'яті та дескрипторів сокетів.

2. **Обробка помилок та типобезпека:**
   * У C-версії використовуються числові коди повернення (`-1` або `0`) і глобальний стан помилок `errno`/OpenSSL Error Queue.
   * У C++20 використано монодичний тип `std::expected<T, std::string>`, що змушує код на етапі компіляції явно обробляти як успішний результат, так і опис помилки, не вимагаючи накладних витрат на механізм винятків (zero-cost error handling).

3. **Безпека буферів:**
   * У C++ замість сирих покажчиків і довжин використано `std::span<const uint8_t>` та `std::string_view`, що унеможливлює вихід за межі масиву під час форматування шістнадцяткових рядків.

---

### Інтеграція в пайплайни GitHub Actions та GitLab CI

Для запуску утиліти в автоматизованому конвеєрі необхідно налаштувати права доступу раннера для отримання OIDC токену.

#### Приклад для GitHub Actions (`.github/workflows/release.yml`)
```yaml
name: Production Firmware Release
on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  id-token: write  # Обов'язковий дозвіл для запиту OIDC JWT токену
  contents: read

jobs:
  build-and-sign:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Compile Embedded Firmware
        run: |
          make firmware.bin

      - name: Request OIDC Token and Sign Artifact
        run: |
          # Отримання системного OIDC токену через локальний сокет раннера
          OIDC_TOKEN=$(curl -sLS -H "Authorization: bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" \
            "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=https://signing.internal.acme.net" | jq -r '.value')
          
          # Запуск нашої скомпільованої утиліти підпису
          ./remote-signer-client firmware.bin "${OIDC_TOKEN}" > signature_response.json
          
          # Витяг бінарного підпису
          jq -r '.signature' signature_response.json | base64 -d > firmware.bin.sig
```

---

### Пастки та інженерні крайові випадки

1. **Атака часового проміжку (TOCTOU — Time-of-Check to Time-of-Use):**
   Якщо клієнт обчислює геш файлу `firmware.bin`, відправляє його на підпис, а паралельний процес у раннері (наприклад, сторонній скрипт збірки чи шкідливий демон) встигає підмінити байти у `firmware.bin` перед пакуванням у фінальний реліз, отриманий підпис стане недійсним або засвідчить сторонній вміст.
   *Захист:* Перед гешуванням файл слід скопіювати у захищений робочий каталог із правами доступу `chmod 400` (read-only) або монтувати каталог збірки в режимі тільки для читання.

2. **Розсинхронізація часу (Clock Drift):**
   Токени OIDC мають короткий час життя (10–15 хвилин) і містять часові мітки `nbf` (Not Before) та `exp` (Expiration). Якщо годинник раннера збірки відстає або випереджає час сервера шлюзу більше ніж на 60 секунд, запит буде миттєво відхилено зі статусом `UNAUTHENTICATED`.
   *Захист:* Синхронізація системного часу раннерів через NTP-демон (chrony) та налаштування допустимого вікна дрейфу (clock skew allowance) на сервері підпису до ±30 секунд.

3. **Повторне використання запитів (Replay Attacks):**
   Якщо нападник перехопить трафік раннера, він може спробувати повторно надіслати той самий OIDC-токен для підписання іншого гешу.
   *Захист:* OIDC-токени повинні бути суворо одноразовими для кожного кроку збірки, а служба підпису зобов'язана фіксувати унікальний ідентифікатор запуску (`run_id` або `jti`) у кеші з TTL, рівним терміну дії токену.

4. **Розриви з'єднання під час тривалих операцій HSM:**
   Апаратні модулі HSM під час високого навантаження можуть виконувати операцію підпису ECDSA від 10 до 500 мілісекунд. Мережеві таймаути на рівні BIO-дескрипторів клієнта не повинні бути меншими за 5–10 секунд, щоб уникнути передчасного скидання з'єднання у моменти пікових навантажень релізних днів.
