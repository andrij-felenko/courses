# ⚙️ Реалізація взаємного mTLS та L7-авторизації через SPIFFE SVID у C та C++

У традиційних мережевих додатках авторизація між сервісами часто спирається на перевірку IP-адреси відправника або спільний статичний токен (*Bearer Token*), переданий у заголовку HTTP. Якщо зловмисник перехоплює трафік або компрометує сусідній контейнер у тій самій підмережі, він може легко підробити запит. В архітектурі нульової довіри (Zero Trust) кожен транспортний канал повинен захищатися за допомогою взаємного TLS (mTLS), де клієнт і сервер криптографічно доводять свою ідентичність за допомогою сертифікатів X.509 SVID стандарту SPIFFE, а права доступу ухвалюються на основі витягнутого ідентифікатора `spiffe://...` із розширення SAN.

Цей інженерний проєкт розбирає повну реалізацію захищеного mTLS-сервера з динамічною валідацією сертифікатів SPIFFE, парсингом розширень X.509, безпечною роботою з пам'яттю, аналізом життєвого циклу рукостискання та авторизацією запитів на рівні L7.

---

### Життєвий цикл захищеного з'єднання та архітектура рішення

Програма реалізує точку застосування політики (Policy Enforcement Point, PEP) на базі криптографічної бібліотеки OpenSSL / BoringSSL.

Процес встановлення безпечного каналу розгортається у чотири послідовні фази:
1. **Отримання ключів від вузлового демона SPIRE Agent**: Застосунок підключається до локального сокета `/tmp/spire-agent/public/api.sock`. Агент перевіряє облікові дані процесу через ядро ОС (`SO_PEERCRED`), звіряє селектори та передає у бінарному вигляді сертифікат X.509 SVID, приватний ключ та зв'язку кореневих сертифікатів CA Bundle.
2. **Ініціалізація криптографічного контексту TLS 1.3**: Сервер налаштовує контекст `SSL_CTX` із суворим режимом перевірки клієнтського сертифіката `SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT`. Це гарантує, що рукостискання буде примусово перервано ще на транспортному рівні, якщо клієнт не надав сертифікат або надав сертифікат, підписаний невідомим центром сертифікації.
3. **Завантаження матеріалу з оперативної пам'яті**: Сертифікат X.509 SVID, приватний ключ та довірена зв'язка CA Bundle завантажуються безпосередньо з буферів оперативної пам'яті без створення тимчасових файлів на диску, що запобігає витоку ключів через файлову систему або несанкціонований доступ інших процесів на хості.
4. **Рукостискання mTLS та парсинг SAN URI**: Клієнт і сервер проводять взаємне рукостискання TLS 1.3. Клієнт передає свій сертифікат у відповідь на запит `CertificateRequest`, а сервер перевіряє цифровий підпис `CertificateVerify`. Після успішного завершення сесії сервер витягує з сертифіката клієнта список розширень `Subject Alternative Name` (SAN) типу `GEN_URI`.
5. **L7-авторизація з правилом Deny-by-Default**: Витягнутий рядок SPIFFE ID зіставляється з таблицею дозволених маршрутів для конкретного HTTP-методу та шляху API (наприклад, доступ до `POST /v1/charge` дозволено лише для `spiffe://prod.corp/ns/billing/sa/checkout`). Будь-який невідомий або неавторизований ідентифікатор негайно відхиляється статусом помилки `403 Forbidden`.

---

### Реалізація mTLS-сервера та валідації SPIFFE ID

Нижче наведено паралельну реалізацію модуля авторизації мовами C та сучасним C++20:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

#define MAX_SPIFFE_LEN 256

/* Витягування SPIFFE ID з розширення Subject Alternative Name (SAN URI) */
int extract_spiffe_id(X509 *cert, char *out_spiffe_id, size_t max_len) {
    if (!cert || !out_spiffe_id || max_len == 0) return 0;

    int san_loc = X509_get_ext_by_NID(cert, NID_subject_alt_name, -1);
    if (san_loc < 0) return 0;

    X509_EXTENSION *ext = X509_get_ext(cert, san_loc);
    if (!ext) return 0;

    GENERAL_NAMES *names = (GENERAL_NAMES *)X509V3_EXT_d2i(ext);
    if (!names) return 0;

    int found = 0;
    int num_names = sk_GENERAL_NAME_num(names);
    for (int i = 0; i < num_names; ++i) {
        GENERAL_NAME *val = sk_GENERAL_NAME_value(names, i);
        if (val->type == GEN_URI) {
            const char *uri_str = (const char *)ASN1_STRING_get0_data(val->d.uniformResourceIdentifier);
            size_t uri_len = (size_t)ASN1_STRING_length(val->d.uniformResourceIdentifier);

            if (uri_len < max_len && strncmp(uri_str, "spiffe://", 9) == 0) {
                memcpy(out_spiffe_id, uri_str, uri_len);
                out_spiffe_id[uri_len] = '\0';
                found = 1;
                break;
            }
        }
    }

    GENERAL_NAMES_free(names);
    return found;
}

/* Перевірка правила авторизації: чи має SPIFFE ID право на ресурс */
int authorize_request(const char *spiffe_id, const char *http_method, const char *path) {
    if (!spiffe_id || !http_method || !path) return 0;

    /* Правило: сервіс платежів має доступ до фінансового API */
    if (strcmp(spiffe_id, "spiffe://prod.corp/ns/billing/sa/checkout") == 0) {
        if (strcmp(http_method, "POST") == 0 && strcmp(path, "/v1/charge") == 0) {
            return 1;
        }
    }

    /* Правило: аудит-сервіс має доступ лише до читання */
    if (strcmp(spiffe_id, "spiffe://prod.corp/ns/security/sa/auditor") == 0) {
        if (strcmp(http_method, "GET") == 0) {
            return 1;
        }
    }

    return 0; /* Deny by default */
}

/* Ініціалізація захищеного SSL_CTX з пам'яті */
SSL_CTX *create_spiffe_ssl_ctx(const char *cert_pem, const char *key_pem, const char *ca_bundle_pem) {
    SSL_CTX *ctx = SSL_CTX_new(TLS_server_method());
    if (!ctx) return NULL;

    /* Суворий TLS 1.3 та обов'язковий взаємний mTLS */
    SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION);
    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, NULL);

    /* Завантаження CA Bundle з пам'яті */
    BIO *ca_bio = BIO_new_mem_buf(ca_bundle_pem, -1);
    X509_STORE *store = SSL_CTX_get_cert_store(ctx);
    X509_INFO *it = NULL;
    STACK_OF(X509_INFO) *inf = PEM_X509_INFO_read_bio(ca_bio, NULL, NULL, NULL);
    BIO_free(ca_bio);

    if (inf) {
        for (int i = 0; i < sk_X509_INFO_num(inf); i++) {
            it = sk_X509_INFO_value(inf, i);
            if (it->x509) X509_STORE_add_cert(store, it->x509);
        }
        sk_X509_INFO_pop_free(inf, X509_INFO_free);
    }

    /* Завантаження сертифіката сервера */
    BIO *cert_bio = BIO_new_mem_buf(cert_pem, -1);
    X509 *cert = PEM_read_bio_X509(cert_bio, NULL, NULL, NULL);
    BIO_free(cert_bio);
    if (!cert || SSL_CTX_use_certificate(ctx, cert) <= 0) {
        X509_free(cert);
        SSL_CTX_free(ctx);
        return NULL;
    }
    X509_free(cert);

    /* Завантаження закритого ключа */
    BIO *key_bio = BIO_new_mem_buf(key_pem, -1);
    EVP_PKEY *pkey = PEM_read_bio_PrivateKey(key_bio, NULL, NULL, NULL);
    BIO_free(key_bio);
    if (!pkey || SSL_CTX_use_PrivateKey(ctx, pkey) <= 0) {
        EVP_PKEY_free(pkey);
        SSL_CTX_free(ctx);
        return NULL;
    }
    EVP_PKEY_free(pkey);

    return ctx;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <vector>
#include <cstring>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

namespace zero_trust {

// RAII делетери для ресурсів C API OpenSSL
struct OpenSSLDeleter {
    void operator()(SSL_CTX* ctx) const noexcept { if (ctx) SSL_CTX_free(ctx); }
    void operator()(SSL* ssl) const noexcept { if (ssl) SSL_free(ssl); }
    void operator()(X509* cert) const noexcept { if (cert) X509_free(cert); }
    void operator()(EVP_PKEY* pkey) const noexcept { if (pkey) EVP_PKEY_free(pkey); }
    void operator()(BIO* bio) const noexcept { if (bio) BIO_free(bio); }
    void operator()(GENERAL_NAMES* gn) const noexcept { if (gn) GENERAL_NAMES_free(gn); }
};

using SslCtxPtr = std::unique_ptr<SSL_CTX, OpenSSLDeleter>;
using X509Ptr   = std::unique_ptr<X509, OpenSSLDeleter>;
using EvpKeyPtr = std::unique_ptr<EVP_PKEY, OpenSSLDeleter>;
using BioPtr    = std::unique_ptr<BIO, OpenSSLDeleter>;

enum class SecurityError {
    CertificateMissing,
    SanExtensionNotFound,
    InvalidSpiffeUri,
    ContextInitFailed,
    PermissionDenied
};

class SpiffeValidator {
public:
    // Витягування SPIFFE ID з розширення SAN URI
    static std::expected<std::string, SecurityError> extract_spiffe_id(X509* cert) noexcept {
        if (!cert) return std::unexpected(SecurityError::CertificateMissing);

        int san_loc = X509_get_ext_by_NID(cert, NID_subject_alt_name, -1);
        if (san_loc < 0) return std::unexpected(SecurityError::SanExtensionNotFound);

        X509_EXTENSION* ext = X509_get_ext(cert, san_loc);
        if (!ext) return std::unexpected(SecurityError::SanExtensionNotFound);

        std::unique_ptr<GENERAL_NAMES, OpenSSLDeleter> names(
            static_cast<GENERAL_NAMES*>(X509V3_EXT_d2i(ext))
        );
        if (!names) return std::unexpected(SecurityError::SanExtensionNotFound);

        int count = sk_GENERAL_NAME_num(names.get());
        for (int i = 0; i < count; ++i) {
            GENERAL_NAME* val = sk_GENERAL_NAME_value(names.get(), i);
            if (val->type == GEN_URI) {
                const char* uri_str = reinterpret_cast<const char*>(
                    ASN1_STRING_get0_data(val->d.uniformResourceIdentifier)
                );
                int uri_len = ASN1_STRING_length(val->d.uniformResourceIdentifier);
                std::string_view uri(uri_str, static_cast<std::size_t>(uri_len));

                if (uri.starts_with("spiffe://")) {
                    return std::string(uri);
                }
            }
        }

        return std::unexpected(SecurityError::InvalidSpiffeUri);
    }

    // Авторизація запиту (Deny-by-Default)
    static bool is_authorized(std::string_view spiffe_id,
                             std::string_view method,
                             std::string_view path) noexcept {
        if (spiffe_id == "spiffe://prod.corp/ns/billing/sa/checkout") {
            return (method == "POST" && path == "/v1/charge");
        }
        if (spiffe_id == "spiffe://prod.corp/ns/security/sa/auditor") {
            return (method == "GET");
        }
        return false;
    }
};

class SecureTlsContext {
public:
    static std::expected<SslCtxPtr, SecurityError> create(std::string_view cert_pem,
                                                          std::string_view key_pem,
                                                          std::string_view ca_bundle_pem) {
        SslCtxPtr ctx(SSL_CTX_new(TLS_server_method()));
        if (!ctx) return std::unexpected(SecurityError::ContextInitFailed);

        SSL_CTX_set_min_proto_version(ctx.get(), TLS1_3_VERSION);
        SSL_CTX_set_verify(ctx.get(), SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, nullptr);

        // Завантаження CA зв'язки
        BioPtr ca_bio(BIO_new_mem_buf(ca_bundle_pem.data(), static_cast<int>(ca_bundle_pem.size())));
        STACK_OF(X509_INFO)* inf = PEM_X509_INFO_read_bio(ca_bio.get(), nullptr, nullptr, nullptr);
        if (inf) {
            X509_STORE* store = SSL_CTX_get_cert_store(ctx.get());
            for (int i = 0; i < sk_X509_INFO_num(inf); ++i) {
                X509_INFO* item = sk_X509_INFO_value(inf, i);
                if (item->x509) X509_STORE_add_cert(store, item->x509);
            }
            sk_X509_INFO_pop_free(inf, X509_INFO_free);
        }

        // Завантаження сертифіката
        BioPtr cert_bio(BIO_new_mem_buf(cert_pem.data(), static_cast<int>(cert_pem.size())));
        X509Ptr cert(PEM_read_bio_X509(cert_bio.get(), nullptr, nullptr, nullptr));
        if (!cert || SSL_CTX_use_certificate(ctx.get(), cert.get()) <= 0) {
            return std::unexpected(SecurityError::ContextInitFailed);
        }

        // Завантаження ключа
        BioPtr key_bio(BIO_new_mem_buf(key_pem.data(), static_cast<int>(key_pem.size())));
        EvpKeyPtr pkey(PEM_read_bio_PrivateKey(key_bio.get(), nullptr, nullptr, nullptr));
        if (!pkey || SSL_CTX_use_PrivateKey(ctx.get(), pkey.get()) <= 0) {
            return std::unexpected(SecurityError::ContextInitFailed);
        }

        return ctx;
    }
};

} // namespace zero_trust
```
:::

---

### Підводні камені та типові вразливості реалізації

Під час практичного впровадження взаємного mTLS розробники найчастіше припускаються чотирьох критичних помилок:

1. **Валідація `Subject.CommonName` (CN) замість SAN URI**:
   Історично багато систем авторизації зчитували ім'я клієнта з поля `CN`. У стандарті SPIFFE поле CN вважається застарілим і може бути порожнім або містити довільний текстовий опис. Якщо сервер перевіряє `CN`, атакувальник може згенерувати дійсний сертифікат із чужим CN усередині іншого домену довіри та обійти авторизацію. Перевірятися має виключно розширення `Subject Alternative Name` з обов'язковою верифікацією префікса схеми `spiffe://` та повного збігу Trust Domain.

2. **Блокування потоків під час ротації сертифікатів**:
   Оскільки SVID сертифікати живуть лише одну годину, оновлення `SSL_CTX` відбувається регулярно. Якщо замінювати контекст через глобальне блокування викликом м'ютекса (`std::mutex`), у високонавантажених сервісах із тисячами паралельних з'єднань виникає сплеск затримок (англ. *latency spike*). Правильний інженерний підхід — використання атомарного заміщення вказівника (`std::atomic<std::shared_ptr<SSL_CTX>>`) або колбеку вибору сертифіката `SSL_CTX_set_cert_cb`, який підставляє свіжі ключі безпосередньо під час чергового рукостискання, не зупиняючи паралельні робочі потоки.

3. **Скидання ключів у файл підкачки (Swap) та витік з оперативної пам'яті**:
   Приватні ключі `x509_svid_key` зберігаються в оперативній пам'яті процесу. Якщо операційна система скине сторінки пам'яті демона на диск під час браку RAM, закритий ключ опиниться на незашифрованому накопичувачі. Для захисту критичних структур пам'яті слід використовувати системний виклик `mlock()` або функцію `OPENSSL_cleanse()` перед звільненням буферів.

4. **Накладні витрати рукостискання та оптимізація TLS 1.3**:
   Повноцінне встановлення з'єднання mTLS додає один повний круговий обхід мережі (1-RTT). Для зменшення накладних витрат у високочастотних внутрішніх комунікаціях рекомендується використовувати постійні пули з'єднань (HTTP/2 та gRPC connection multiplexing), а також апаратне прискорення криптографії на еліптичних кривих Curve25519 (X25519/Ed25519) замість важких ключів RSA-4096.

5. **Коректне завершення з'єднань під час перезапуску (*Graceful Drain*)**:
   Коли сервіс отримує сигнал завершення роботи (`SIGTERM`), він повинен припинити приймати нові mTLS-з'єднання, надіслати клієнтам сповіщення `close_notify` або HTTP/2 `GOAWAY` і надати активним запитам фіксований час на коректне завершення виконання. Це усуває раптові обриви транзакцій під час плавного оновлення версій у кластері.
