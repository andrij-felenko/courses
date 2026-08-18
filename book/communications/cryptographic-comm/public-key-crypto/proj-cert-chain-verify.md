# ⚙️ Перевірка ланцюга сертифікатів X.509: алгоритм та імплементація

Під час встановлення захищеного з'єднання TLS клієнт отримує від сервера ланцюг сертифікатів. Якщо клієнт прийме неперевірений відкритий ключ, уся криптографічна стійкість сесійного шифрування нівелюється: зловмисник посередині (MITM) зможе підсунути власний відкритий ключ і прозоро розшифровувати весь трафік.

У цьому проєкті реалізовано повнофункціональний верифікатор сертифікатів X.509 на базі криптографічного рушія OpenSSL 3.x двома мовами — процедурною **C** та об'єктно-орієнтованою ідіоматичною **C++20** з використанням безпечних обгорток керування ресурсами (RAII). Верифікатор перевіряє криптографічну цілісність ланцюга підписів, чинність часових міток, допустимість базових обмежень та відповідність доменного імені за розширенням SAN. Окрім цього, наведено автономний бінарний парсер ASN.1 DER для прямого видобування відбитка відкритого ключа (Key Pinning).

---

### 1. Математичні та протокольні вимоги до перевірки ланцюга

Згідно зі специфікацією RFC 5280 (розділ 6: «Certification Path Validation Algorithm»), перевірка ланцюга сертифікатів не є простим послідовним викликом функції перевірки підпису. Це комплексний алгоритм обходу графа довіри, який зобов'язаний підтримувати такі інваріанти на кожному кроці `i` (від кінцевого сертифіката `0` до кореневого якоря `n`):

1. **Цілісність та авторство підпису:** кожен сертифікат `Cert[i]` підписаний таємним ключем, що відповідає відкритому ключу попереднього сертифіката `Cert[i+1]`. Для перевірки підпису видобувається відкритий ключ з поля `SubjectPublicKeyInfo` сертифіката `Cert[i+1]`, обчислюється криптографічний геш від DER-представлення блоку `TBSCertificate` сертифіката `Cert[i]` і перевіряється збіг із полем `signatureValue`.
2. **Узгодження простору імен (Distinguished Name Chaining):** рядок `Cert[i].Issuer` повинен побайтово або канонічно (з урахуванням правил порівняння атрибутів RDN) збігатися з рядком `Cert[i+1].Subject`.
3. **Часове вікно чинності:** системний час перевірки `T_now` зобов'язаний задовольняти нерівність `Cert[i].Validity.notBefore ≤ T_now ≤ Cert[i].Validity.notAfter` для абсолютно кожного сертифіката в ланцюгу, включаючи проміжні та кореневий.
4. **Семантика базових обмежень (Basic Constraints):** для кожного проміжного сертифіката `Cert[i]` (`i > 0`) розширення `BasicConstraints` обов'язково має містити прапорець `cA = TRUE`. Якщо сертифікат кінцевого вузла (Leaf) містить `cA = TRUE`, або якщо проміжний центр має `cA = FALSE`, ланцюг визнається недійсним.
5. **Обмеження глибини ієрархії (Path Length Constraints):** якщо в сертифікаті `Cert[k]` задано ціле число `pathLenConstraint = M`, кількість проміжних центрів між цим сертифікатом і кінцевим вузлом не може перевищувати `M`.
6. **Призначення ключів (Key Usage):** проміжний сертифікат зобов'язаний мати встановлений біт `keyCertSign` у розширенні `KeyUsage`. Використання звичайного серверного сертифіката без цього біта для підпису інших вузлів блокується.
7. **Зіставлення доменного імені (Host Name Validation):** ім'я хоста, до якого підключається клієнт (наприклад, `api.service.gov.ua`), зіставляється із записами `dNSName` розширення `SubjectAlternativeName` кінцевого сертифіката.

---

### 2. Архітектура програмного модуля та керування пам'яттю

Під час роботи з бібліотекою OpenSSL на мові C розробник стикається з десятками динамічних структур пам'яті (`BIO`, `X509`, `X509_STORE`, `X509_STORE_CTX`, `EVP_MD_CTX`), кожна з яких вимагає строго визначеної функції вивільнення ресурсів. Будь-яка помилка або достроковий вихід через невдалу перевірку спричиняє витік оперативної пам'яті.

У версії на C++20 цю проблему вирішено через патерн **RAII** (англ. *Resource Acquisition Is Initialization*). Створено універсальний функціональний об'єкт `OpenSSLDeleter`, який передається параметром у розумні вказівники `std::unique_ptr`. Це гарантує автоматичне та детерміноване звільнення пам'яті при виході зі скоупу функцій незалежно від того, чи завершилася верифікація успішно, чи було повернуто помилку `std::unexpected`.

---

### 3. Повний вихідний код модуля верифікації

Нижче наведено робочу реалізацію перевірки ланцюга сертифікатів та видобування відбитка відкритого ключа двома мовами.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/evp.h>

/* Результат верифікації сертифіката */
typedef struct {
    int is_valid;
    int error_code;
    const char *error_string;
    unsigned char leaf_spki_sha256[32];
} CertVerifyResult;

/* Обчислення SHA-256 відбитка відкритого ключа (SubjectPublicKeyInfo) */
static int compute_spki_sha256(X509 *cert, unsigned char *out_hash) {
    X509_PUBKEY *pubkey = X509_get_X509_PUBKEY(cert);
    if (!pubkey) return 0;

    const unsigned char *spki_der = NULL;
    int spki_len = i2d_X509_PUBKEY(pubkey, (unsigned char **)&spki_der);
    if (spki_len <= 0 || !spki_der) return 0;

    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        OPENSSL_free((void *)spki_der);
        return 0;
    }

    int ok = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) &&
             EVP_DigestUpdate(ctx, spki_der, (size_t)spki_len) &&
             EVP_DigestFinal_ex(ctx, out_hash, NULL);

    EVP_MD_CTX_free(ctx);
    OPENSSL_free((void *)spki_der);
    return ok ? 1 : 0;
}

/* Головна функція верифікації ланцюга */
CertVerifyResult verify_certificate_chain(
    const char *leaf_pem,
    const char *intermediate_pem,
    const char *root_ca_pem,
    const char *expected_hostname
) {
    CertVerifyResult result;
    memset(&result, 0, sizeof(result));
    result.is_valid = 0;
    result.error_code = X509_V_ERR_UNSPECIFIED;

    BIO *bio_leaf = NULL;
    BIO *bio_interm = NULL;
    BIO *bio_root = NULL;
    X509 *leaf = NULL;
    X509 *interm = NULL;
    X509 *root = NULL;
    X509_STORE *store = NULL;
    X509_STORE_CTX *ctx = NULL;
    STACK_OF(X509) *untrusted_stack = NULL;

    /* 1. Читання кінцевого сертифіката */
    bio_leaf = BIO_new_mem_buf(leaf_pem, -1);
    if (!bio_leaf) goto cleanup;
    leaf = PEM_read_bio_X509(bio_leaf, NULL, NULL, NULL);
    if (!leaf) goto cleanup;

    /* 2. Читання проміжного сертифіката */
    if (intermediate_pem) {
        bio_interm = BIO_new_mem_buf(intermediate_pem, -1);
        if (!bio_interm) goto cleanup;
        interm = PEM_read_bio_X509(bio_interm, NULL, NULL, NULL);
        if (!interm) goto cleanup;
    }

    /* 3. Читання кореневого сертифіката довіри */
    bio_root = BIO_new_mem_buf(root_ca_pem, -1);
    if (!bio_root) goto cleanup;
    root = PEM_read_bio_X509(bio_root, NULL, NULL, NULL);
    if (!root) goto cleanup;

    /* 4. Створення та заповнення сховища довіри */
    store = X509_STORE_new();
    if (!store) goto cleanup;
    if (X509_STORE_add_cert(store, root) != 1) goto cleanup;

    /* 5. Формування стеку проміжних сертифікатів */
    untrusted_stack = sk_X509_new_null();
    if (!untrusted_stack) goto cleanup;
    if (interm) {
        sk_X509_push(untrusted_stack, interm);
    }

    /* 6. Ініціалізація контексту верифікації */
    ctx = X509_STORE_CTX_new();
    if (!ctx) goto cleanup;
    if (X509_STORE_CTX_init(ctx, store, leaf, untrusted_stack) != 1) goto cleanup;

    /* 7. Налаштування суворої перевірки імені хоста через SAN */
    if (expected_hostname && strlen(expected_hostname) > 0) {
        X509_VERIFY_PARAM *param = X509_STORE_CTX_get0_param(ctx);
        X509_VERIFY_PARAM_set_hostflags(param, X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS);
        if (X509_VERIFY_PARAM_set1_host(param, expected_hostname, 0) != 1) {
            goto cleanup;
        }
    }

    /* 8. Виконання верифікації */
    int verify_status = X509_verify_cert(ctx);
    if (verify_status == 1) {
        result.is_valid = 1;
        result.error_code = X509_V_OK;
        result.error_string = "Certificate verification successful";
        compute_spki_sha256(leaf, result.leaf_spki_sha256);
    } else {
        result.is_valid = 0;
        result.error_code = X509_STORE_CTX_get_error(ctx);
        result.error_string = X509_verify_cert_error_string(result.error_code);
    }

cleanup:
    if (ctx) X509_STORE_CTX_free(ctx);
    if (untrusted_stack) sk_X509_free(untrusted_stack);
    if (store) X509_STORE_free(store);
    if (leaf) X509_free(leaf);
    if (interm) X509_free(interm);
    if (root) X509_free(root);
    if (bio_leaf) BIO_free(bio_leaf);
    if (bio_interm) BIO_free(bio_interm);
    if (bio_root) BIO_free(bio_root);

    return result;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <expected>
#include <array>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/evp.h>

namespace crypto {

/* Користувацькі деструктори для об'єктів OpenSSL (RAII) */
struct OpenSSLDeleter {
    void operator()(BIO *b) const noexcept { if (b) BIO_free(b); }
    void operator()(X509 *x) const noexcept { if (x) X509_free(x); }
    void operator()(X509_STORE *s) const noexcept { if (s) X509_STORE_free(s); }
    void operator()(X509_STORE_CTX *c) const noexcept { if (c) X509_STORE_CTX_free(c); }
    void operator()(EVP_MD_CTX *m) const noexcept { if (m) EVP_MD_CTX_free(m); }
    void operator()(STACK_OF(X509) *st) const noexcept { if (st) sk_X509_free(st); }
    void operator()(void *p) const noexcept { if (p) OPENSSL_free(p); }
};

using BioPtr         = std::unique_ptr<BIO, OpenSSLDeleter>;
using X509Ptr        = std::unique_ptr<X509, OpenSSLDeleter>;
using StorePtr       = std::unique_ptr<X509_STORE, OpenSSLDeleter>;
using StoreCtxPtr    = std::unique_ptr<X509_STORE_CTX, OpenSSLDeleter>;
using MdCtxPtr       = std::unique_ptr<EVP_MD_CTX, OpenSSLDeleter>;
using X509StackPtr   = std::unique_ptr<STACK_OF(X509), OpenSSLDeleter>;

struct VerificationSuccess {
    std::array<uint8_t, 32> spki_sha256;
    std::string subject_name;
    std::string issuer_name;
};

struct VerificationFailure {
    int error_code;
    std::string error_message;
};

class CertificateVerifier {
public:
    /* Додавання довіреного кореневого сертифіката (Trust Anchor) */
    bool add_trusted_root_pem(std::string_view root_pem) {
        if (!store_) {
            store_.reset(X509_STORE_new());
            if (!store_) return false;
        }

        BioPtr bio(BIO_new_mem_buf(root_pem.data(), static_cast<int>(root_pem.size())));
        if (!bio) return false;

        X509Ptr root(PEM_read_bio_X509(bio.get(), nullptr, nullptr, nullptr));
        if (!root) return false;

        return X509_STORE_add_cert(store_.get(), root.get()) == 1;
    }

    /* Верифікація кінцевого сертифіката з проміжними та перевіркою SAN */
    std::expected<VerificationSuccess, VerificationFailure> verify_chain(
        std::string_view leaf_pem,
        std::span<const std::string> intermediates_pem,
        std::string_view expected_hostname
    ) const {
        if (!store_) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Trust store is uninitialized"
            });
        }

        BioPtr leaf_bio(BIO_new_mem_buf(leaf_pem.data(), static_cast<int>(leaf_pem.size())));
        if (!leaf_bio) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to allocate leaf BIO buffer"
            });
        }

        X509Ptr leaf(PEM_read_bio_X509(leaf_bio.get(), nullptr, nullptr, nullptr));
        if (!leaf) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to parse leaf certificate PEM"
            });
        }

        X509StackPtr untrusted_stack(sk_X509_new_null());
        if (!untrusted_stack) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to allocate intermediate stack"
            });
        }

        std::vector<X509Ptr> parsed_intermediates;
        for (const auto &interm_str : intermediates_pem) {
            BioPtr bio(BIO_new_mem_buf(interm_str.data(), static_cast<int>(interm_str.size())));
            if (!bio) continue;
            X509Ptr cert(PEM_read_bio_X509(bio.get(), nullptr, nullptr, nullptr));
            if (cert) {
                sk_X509_push(untrusted_stack.get(), cert.get());
                parsed_intermediates.push_back(std::move(cert));
            }
        }

        StoreCtxPtr ctx(X509_STORE_CTX_new());
        if (!ctx || X509_STORE_CTX_init(ctx.get(), store_.get(), leaf.get(), untrusted_stack.get()) != 1) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to initialize X509_STORE_CTX"
            });
        }

        if (!expected_hostname.empty()) {
            X509_VERIFY_PARAM *param = X509_STORE_CTX_get0_param(ctx.get());
            X509_VERIFY_PARAM_set_hostflags(param, X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS);
            if (X509_VERIFY_PARAM_set1_host(param, expected_hostname.data(), expected_hostname.size()) != 1) {
                return std::unexpected(VerificationFailure{
                    X509_V_ERR_UNSPECIFIED, "Failed to configure hostname verification parameters"
                });
            }
        }

        if (X509_verify_cert(ctx.get()) != 1) {
            int err = X509_STORE_CTX_get_error(ctx.get());
            return std::unexpected(VerificationFailure{
                err, X509_verify_cert_error_string(err)
            });
        }

        VerificationSuccess success;
        success.spki_sha256 = extract_spki_sha256(leaf.get());
        
        char buf[256];
        X509_NAME_oneline(X509_get_subject_name(leaf.get()), buf, sizeof(buf));
        success.subject_name = buf;
        X509_NAME_oneline(X509_get_issuer_name(leaf.get()), buf, sizeof(buf));
        success.issuer_name = buf;

        return success;
    }

private:
    StorePtr store_;

    static std::array<uint8_t, 32> extract_spki_sha256(X509 *cert) {
        std::array<uint8_t, 32> hash{};
        X509_PUBKEY *pubkey = X509_get_X509_PUBKEY(cert);
        if (!pubkey) return hash;

        unsigned char *spki_der = nullptr;
        int len = i2d_X509_PUBKEY(pubkey, &spki_der);
        std::unique_ptr<unsigned char, OpenSSLDeleter> spki_guard(spki_der);

        if (len > 0 && spki_der) {
            MdCtxPtr md_ctx(EVP_MD_CTX_new());
            if (md_ctx &&
                EVP_DigestInit_ex(md_ctx.get(), EVP_sha256(), nullptr) &&
                EVP_DigestUpdate(md_ctx.get(), spki_der, static_cast<size_t>(len))) {
                EVP_DigestFinal_ex(md_ctx.get(), hash.data(), nullptr);
            }
        }
        return hash;
    }
};

} // namespace crypto
```
:::

---

### 4. Автономний парсер бінарного ASN.1 DER (Zero-Allocation TLV Walk)

Для систем з обмеженими ресурсами (Embedded, мікроконтролери, RTOS), де підключення важкої бібліотеки OpenSSL є небажаним або неможливим через дефіцит оперативної пам'яті, часто потрібно реалізувати швидку попередню перевірку чи видобування відкритого ключа для прив'язки (Public Key Pinning).

Нижче наведено низькорівневий парсер, що обходить дерево тегів ASN.1 DER без жодного виділення динамічної пам'яті (`malloc` чи `new`), працюючи виключно над переданим буфером пам'яті.

:::tabs
```c
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t tag;
    const uint8_t *value;
    size_t length;
    size_t total_tlv_size;
} DerElement;

/* Зчитування чергового вузла TLV з потоку пам'яті */
bool der_read_element(const uint8_t *data, size_t max_len, DerElement *elem) {
    if (!data || max_len < 2 || !elem) return false;

    elem->tag = data[0];
    size_t offset = 1;
    size_t val_len = 0;

    if ((data[offset] & 0x80) == 0) {
        /* Коротка форма: довжина 0..127 байтів */
        val_len = data[offset];
        offset += 1;
    } else {
        /* Довга форма: перший байт містить кількість байтів довжини */
        size_t len_octets = data[offset] & 0x7F;
        offset += 1;
        if (len_octets == 0 || len_octets > sizeof(size_t) || offset + len_octets > max_len) {
            return false;
        }
        val_len = 0;
        for (size_t i = 0; i < len_octets; ++i) {
            val_len = (val_len << 8) | data[offset + i];
        }
        offset += len_octets;
    }

    if (offset + val_len > max_len) return false;

    elem->value = &data[offset];
    elem->length = val_len;
    elem->total_tlv_size = offset + val_len;
    return true;
}

/* Пошук блоку SubjectPublicKeyInfo всередині TBSCertificate */
bool der_find_spki(const uint8_t *cert_der, size_t cert_len, const uint8_t **spki_ptr, size_t *spki_len) {
    DerElement cert_seq, tbs_seq;
    if (!der_read_element(cert_der, cert_len, &cert_seq) || cert_seq.tag != 0x30) return false;
    if (!der_read_element(cert_seq.value, cert_seq.length, &tbs_seq) || tbs_seq.tag != 0x30) return false;

    /* Обхід полів всередині TBSCertificate */
    const uint8_t *cursor = tbs_seq.value;
    size_t remaining = tbs_seq.length;
    int field_index = 0;

    while (remaining > 0) {
        DerElement elem;
        if (!der_read_element(cursor, remaining, &elem)) return false;

        /* Поле 0 може бути версією [0] (0xA0) */
        if (field_index == 0 && elem.tag == 0xA0) {
            /* Пропускаємо явний тег версії */
            cursor += elem.total_tlv_size;
            remaining -= elem.total_tlv_size;
            continue;
        }

        /* 
         * Послідовність полів:
         * 0: serialNumber (INTEGER 0x02)
         * 1: signature (SEQUENCE 0x30)
         * 2: issuer (SEQUENCE 0x30)
         * 3: validity (SEQUENCE 0x30)
         * 4: subject (SEQUENCE 0x30)
         * 5: SubjectPublicKeyInfo (SEQUENCE 0x30)
         */
        if (field_index == 5 && elem.tag == 0x30) {
            *spki_ptr = cursor;
            *spki_len = elem.total_tlv_size;
            return true;
        }

        cursor += elem.total_tlv_size;
        remaining -= elem.total_tlv_size;
        field_index++;
    }
    return false;
}
```
```cpp
#include <cstddef>
#include <cstdint>
#include <span>
#include <optional>

namespace asn1 {

struct DerElement {
    uint8_t tag{};
    std::span<const uint8_t> value{};
    size_t total_tlv_size{};
};

/* Читання TLV-елемента у стилі сучасного C++20 без виділення пам'яті */
constexpr std::optional<DerElement> read_element(std::span<const uint8_t> data) noexcept {
    if (data.size() < 2) return std::nullopt;

    uint8_t tag = data[0];
    size_t offset = 1;
    size_t val_len = 0;

    if ((data[offset] & 0x80) == 0) {
        val_len = data[offset];
        offset += 1;
    } else {
        size_t len_octets = data[offset] & 0x7F;
        offset += 1;
        if (len_octets == 0 || len_octets > sizeof(size_t) || offset + len_octets > data.size()) {
            return std::nullopt;
        }
        val_len = 0;
        for (size_t i = 0; i < len_octets; ++i) {
            val_len = (val_len << 8) | data[offset + i];
        }
        offset += len_octets;
    }

    if (offset + val_len > data.size()) return std::nullopt;

    return DerElement{
        tag,
        data.subspan(offset, val_len),
        offset + val_len
    };
}

/* Пошук блоку SubjectPublicKeyInfo */
std::optional<std::span<const uint8_t>> find_spki(std::span<const uint8_t> cert_der) noexcept {
    auto cert_seq = read_element(cert_der);
    if (!cert_seq || cert_seq->tag != 0x30) return std::nullopt;

    auto tbs_seq = read_element(cert_seq->value);
    if (!tbs_seq || tbs_seq->tag != 0x30) return std::nullopt;

    auto cursor = tbs_seq->value;
    int field_index = 0;

    while (!cursor.empty()) {
        auto elem = read_element(cursor);
        if (!elem) return std::nullopt;

        if (field_index == 0 && elem->tag == 0xA0) {
            cursor = cursor.subspan(elem->total_tlv_size);
            continue;
        }

        if (field_index == 5 && elem->tag == 0x30) {
            return cursor.subspan(0, elem->total_tlv_size);
        }

        cursor = cursor.subspan(elem->total_tlv_size);
        field_index++;
    }
    return std::nullopt;
}

} // namespace asn1
```
:::

---

### 5. Прив'язка відкритого ключа (Public Key Pinning) проти прив'язки сертифіката

При побудові високонадійних клієнтських додатків (банківські мобільні клієнти, захищена телеметрія дронів, IoT-шлюзи) стандартної перевірки за сховищем кореневих сертифікатів операційної системи іноді недостатньо: якщо зловмисник скомпрометує хоча б один із понад 150 довірених Root CA у системі (або встановить шкідливий локальний корінь), він зможе підписати фальшивий сертифікат для будь-якого домену.

Для захисту від цієї загрози застосовують техніку **прив'язки ключів** (англ. *Key Pinning*).

#### Чому слід прив'язувати саме SPKI, а не весь сертифікат:
1. **Прив'язка сертифіката цілком (Certificate Pinning):** клієнт перевіряє SHA-256 геш від усього бінарного файлу сертифіката. 
   - *Недолік:* Сертифікати мають обмежений строк дії (90–398 днів). При плановому перепуску сертифіката змінюється його серійний номер, дати чинності та підпис видавця, через що геш усього сертифіката повністю змінюється. Це вимагає обов'язкового одночасного оновлення прошивки чи мобільного додатку у всіх користувачів.
2. **Прив'язка відкритого ключа (SubjectPublicKeyInfo Pinning):** клієнт видобуває блок `SubjectPublicKeyInfo` і перевіряє виключно його SHA-256 дайджест.
   - *Перевага:* Власник сервера може щорічно оновлювати сертифікат у Let's Encrypt або DigiCert, генеруючи новий запит CSR на основі **того самого закритого ключа**. Блок SPKI, відкритий ключ і його SHA-256 відбиток залишаються незмінними, і клієнти продовжують успішно працювати без перепрошивки.

---

### 6. Детальний построковий розбір коду верифікації

#### 6.1. Логіка роботи обгортки OpenSSL (C та C++):
1. **Ініціалізація BIO-буферів (`BIO_new_mem_buf`):** Функція створює об'єкти абстрактного вводу-виводу пам'яті (Memory BIO) у режимі тільки для читання без копіювання переданих рядків. Функція `PEM_read_bio_X509` декодує рядок Base64, перевіряє заголовки `-----BEGIN CERTIFICATE-----` і парсить бінарну DER-структуру в C-структуру `X509`.
2. **Сховище довіри (`X509_STORE`):** Кореневі сертифікати додаються до сховища `store` викликом `X509_STORE_add_cert`. Сховище будує внутрішню геш-таблицю за іменами суб'єктів (`X509_NAME_hash`), що дозволяє знаходити батьківський сертифікат за час `O(1)`.
3. **Стек недовірених сертифікатів (`STACK_OF(X509)`):** Проміжні сертифікати передаються верифікатору окремим списком. Важливо: вони не додаються до довіреного сховища `store`, оскільки клієнт їм апріорі не довіряє. Їхня роль — служити «будівельним матеріалом» для відновлення ланцюга підписів до відомого кореня.
4. **Налаштування валідації хоста (`X509_VERIFY_PARAM_set1_host`):** Прапорець `X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS` блокує часткові маски на кшталт `f*o.example.com`, які історично спричиняли вразливості парсерів. Функція налаштовує контекст на суворе порівняння лише повного першого ярлика в розширенні SAN.
5. **Виконання перевірки (`X509_verify_cert`):** Внутрішній рушій OpenSSL виконує побудову ланцюга: починаючи з кінцевого сертифіката, він шукає видавця серед проміжних; якщо знаходить — повторює крок, доки не досягне кореневого сертифіката зі сховища `store`. Після цього перевіряються всі цифрові підписи, дати чинності та розширення.

#### 6.2. Логіка бінарного парсера TLV:
1. **Зчитування байта тегу (`data[0]`):** Перший байт визначає клас і тип елемента.
2. **Розбір байта довжини:** Якщо старший біт нульовий (`(data[1] & 0x80) == 0`), наступні 7 бітів безпосередньо містять довжину поля від 0 до 127 байтів. Якщо старший біт дорівнює одиниці, маска `& 0x7F` вказує на кількість наступних байтів (1, 2, 3 або 4), що кодують загальну довжину блоку у порядку від старшого до молодшого (Big-Endian).
3. **Обхід полів `TBSCertificate`:** Парсер знаходить другий вкладений `SEQUENCE` і послідовно пропускає поля: серійний номер (INTEGER), алгоритм підпису (SEQUENCE), ім'я видавця (SEQUENCE), часовий інтервал (SEQUENCE) та ім'я суб'єкта (SEQUENCE). Шостий знайдений елемент є структурою `SubjectPublicKeyInfo`.

---

### 7. Глибокий аналіз реальних інженерних пасток верифікації

#### Пастка 1: Плутанина між SAN та застарілим `CommonName` (CN)
- **Механізм вразливості:** Історично перші версії вебсертифікатів зберігали доменне ім'я в полі `Subject.CommonName` (наприклад, `CN=example.com`). Згодом стандарт запровадив розширення `SubjectAlternativeName` (SAN), яке дозволяє вказувати десятки доменів і IP-адрес.
- **Помилка коду:** Якщо бібліотека перевірки читає лише `CommonName`, атакуючий, який легітимно отримав сертифікат на `CN=example.com` з розширенням `SAN: dNSName=badsite.org`, зможе пройти перевірку як `example.com`.
- **Правило інженерного захисту:** Стандарти RFC 6125 та CA/Browser Forum Baseline Requirements прямо забороняють використання `CommonName` для валідації доменних імен у TLS. Якщо розширення SAN присутнє, поле CN зобов'язане повністю ігноруватися.

#### Пастка 2: Проблема відсутнього проміжного сертифіката (Incomplete Chain)
- **Механізм виникнення:** Вебсервер надсилає клієнту лише сертифікат кінцевого домену, опускаючи сертифікат Intermediate CA.
- **Чому це важко відловити під час тестування:** Сучасні десктопні браузери (Google Chrome, Firefox) мають механізми автоматичного довантаження відсутніх сертифікатів через розширення `AIA` (`id-ad-caIssuers`) або тримають попередньо закешовані проміжні центри. Під час тестування у браузері сайт відкривається із зеленим замком. Проте мобільний додаток, IoT-пристрій чи консольна утиліта `curl` не виконують AIA-запитів і негайно обривають з'єднання з фатальною помилкою `X509_V_ERR_UNABLE_TO_GET_ISSUER_CERT_LOCALLY`.
- **Діагностика:** Перевірка через консольну команду `openssl s_client -connect api.example.com:443 -showcerts`. У виводі повинен відображатися повний ланцюг: `Certificate chain 0 s:... i:...` та `1 s:... i:...`.

#### Пастка 3: Збій системного годинника на вбудованих контролерах (Clock Skew)
- **Механізм виникнення:** Мікроконтролери (ESP32, STM32) без батарейкового модуля RTC після знеструмлення ініціалізують системний таймер нулем (1 січня 1970 року, Unix Epoch).
- **Симптом:** Функція `X509_verify_cert` повертає код помилки `X509_V_ERR_CERT_NOT_YET_VALID` (номер 9), оскільки поточний системний час є меншим за дату випуску сертифіката `notBefore`.
- **Рішення:** Архітектура прошивки зобов'язана виконувати первинну синхронізацію часу через відкритий протокол SNTP (Simple Network Time Protocol) перед спробою відкрити перше захищене TLS-з'єднання.

#### Пастка 4: Закінчення строку крос-підписаних кореневих сертифікатів (Cross-Signing Expiry)
- **Історичний урок (Вересень 2021 року, DST Root CA X3):** Центр Let's Encrypt для підтримки старих пристроїв Android мав проміжний сертифікат `R3`, підписаний двома коренями: новим власним `ISRG Root X1` та старим довіреним `DST Root CA X3` (IdenTrust). 30 вересня 2021 року термін дії `DST Root CA X3` завершився.
- **Чому впали клієнти:** Старі версії OpenSSL 1.0.2 знаходили в ланцюгу шлях до `DST Root CA X3`, бачили прострочену дату і негайно переривали верифікацію з помилкою `X509_V_ERR_CERT_HAS_EXPIRED`, не намагаючись знайти альтернативний чинний шлях до встановленого `ISRG Root X1`.
- **Рішення:** Використання сучасних версій TLS-бібліотек з обов'язковим увімкненням прапорця `X509_V_FLAG_TRUSTED_FIRST`, який змушує верифікатор будувати дерево сертифікатів знизу вгору, надаючи безумовний пріоритет локально довіреним якорям.

#### Пастка 5: Підміна ролі сертифіката через відсутність перевірки Basic Constraints
- **Механізм атаки:** Зловмисник легітимно купує звичайний кінцевий сертифікат для сайту `attacker.com` (`cA = FALSE`). Потім він використовує свій закритий ключ для підпису підробленого сертифіката на ім'я `bank.gov.ua` і надсилає цей ланцюг клієнту.
- **Наслідок слабкого коду:** Якщо програма перевіряє виключно математичний збіг підпису, підпис зійдеться (бо сертифікат справді підписаний ключем `attacker.com`, а той — довіреним центром).
- **Захист:** Сувора перевірка наявності `cA = TRUE` та біта `keyCertSign` у розширенні `KeyUsage` для кожного вузла, що виступає в ролі підписувача. Будь-який сертифікат без `cA = TRUE` відхиляється з помилкою `X509_V_ERR_INVALID_CA`.

#### Пастка 6: Некоректне зіставлення шаблонних імен (Wildcard Matching)
- **Механізм помилки:** Наївна реалізація перевірки замінює зірочку `*` регулярним виразом `.*`. Сертифікат із записом `*.example.com` у такому разі помилково приймається для `example.com` (кореневий апекс) та `sub.deep.example.com` (глибокі піддомени).
- **Вимога стандарту RFC 6125:** Маска `*` має право зіставлятися строго з одним рівнем доменного імені, що знаходиться ліворуч від крапки, і ніколи не відповідає крапкам усередині імені. Сертифікат `*.example.com` дійсний для `api.example.com`, але недійсний для `example.com` і `v1.api.example.com`.

---

### 8. Методика тестування та контрольні тестові вектори

Для забезпечення безвідмовної роботи верифікатора в автоматизованому тестовому конвеєрі (CI/CD) створюється набір штучних сертифікатів, що покривають як позитивні, так і негативні сценарії:

#### 8.1. Генерація тестового стенду засобами OpenSSL:
1. **Генерація самопідписаного кореневого центру (Root CA):**
```
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 \
  -keyout root.key -out root.pem -days 3650 -nodes \
  -subj "/C=UA/O=Test Root Authority/CN=Test Root CA" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"
```
2. **Генерація проміжного центру (Intermediate CA):**
```
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 \
  -keyout interm.key -out interm.csr -nodes \
  -subj "/C=UA/O=Test Intermediate Authority/CN=Test Intermediate CA"

openssl x509 -req -in interm.csr -CA root.pem -CAkey root.key \
  -CAcreateserial -out interm.pem -days 1825 \
  -extfile <(printf "basicConstraints=critical,CA:TRUE,pathLen:0\nkeyUsage=critical,keyCertSign,cRLSign")
```
3. **Генерація дійсного кінцевого сертифіката сервера (Leaf):**
```
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 \
  -keyout leaf.key -out leaf.csr -nodes \
  -subj "/C=UA/CN=api.service.gov.ua"

openssl x509 -req -in leaf.csr -CA interm.pem -CAkey interm.key \
  -CAcreateserial -out leaf.pem -days 365 \
  -extfile <(printf "basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nsubjectAltName=DNS:api.service.gov.ua,DNS:service.gov.ua")
```

#### 8.2. Обов'язкова матриця негативних тестів:
- **Тест 1 (Mismatched Hostname):** виклик `verify_chain` з очікуваним ім'ям `evil.com`. Очікуваний результат: `is_valid = 0`, код помилки `X509_V_ERR_HOSTNAME_MISMATCH` (номер 62).
- **Тест 2 (Untrusted Root):** передача валідного ланцюга, але сховище `store` ініціалізується стороннім коренем. Очікуваний результат: `is_valid = 0`, код `X509_V_ERR_UNABLE_TO_GET_ISSUER_CERT_LOCALLY` (номер 20).
- **Тест 3 (Broken Signature):** модифікація одного байта в блоці `signatureValue` кінцевого сертифіката. Очікуваний результат: `is_valid = 0`, код `X509_V_ERR_CERT_SIGNATURE_FAILURE` (номер 7).
- **Тест 4 (Path Length Exceeded):** проміжний центр з `pathLenConstraint = 0` підписує інший проміжний центр, який потім підписує кінцевий вузол. Очікуваний результат: `is_valid = 0`, код `X509_V_ERR_PATH_LENGTH_EXCEEDED` (номер 25).
---

### 9. Інтеграція верифікації у мережевий сокетний клієнт (TLS Client Flow)

У реальному мережевому додатку валідація сертифіката є частиною процесу встановлення з'єднання на прикладному рівні:

1. **Створення сокета та TCP Handshake:** Програма створює стандартний TCP-сокет (`socket`, `connect`) і встановлює базове з'єднання з IP-адресою сервера на порту 443.
2. **Ініціалізація TLS-контексту (`SSL_CTX`):** Створюється об'єкт `SSL_CTX_new(TLS_client_method())`. За допомогою `SSL_CTX_set_verify` встановлюється режим `SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT`.
3. **Встановлення Server Name Indication (SNI):** Обов'язковий виклик `SSL_set_tlsext_host_name(ssl, "api.service.gov.ua")`. Це надсилає ім'я віртуального хоста у відкритому заголовку `ClientHello`, дозволяючи вебсерверу обрати правильний сертифікат із багатьох розміщених на одній IP-адресі.
4. **Виконання рукостискання (`SSL_connect`):** Клієнт надсилає `ClientHello`, отримує `ServerHello`, сертифікати та обмін ключами ECDHE. Бібліотека автоматично виконує ланцюгову валідацію.
5. **Узгодження прикладного протоколу (ALPN):** Клієнт налаштовує список підтримуваних протоколів через `SSL_set_alpn_protos(ssl, "\x02h2\x08http/1.1", 11)`. Сервер повертає обраний протокол у `ServerHello`. Валідація сертифіката гарантує, що узгоджений протокол виконується над автентифікованим каналом.
6. **Перевірка міток Certificate Transparency (SCT):** Клієнт видобуває розширення TLS `signed_certificate_timestamp` або читає вбудовані SCT з розширення сертифіката `1.3.6.1.4.1.11129.2.4.2` та перевіряє криптографічні підписи публічних логів аудиту CT перед фіналізацією з'єднання.
7. **Контрольна перевірка результату (`SSL_get_verify_result`):** Навіть якщо функція `SSL_connect` повернула успіх, безпечний код зобов'язаний виконати додатковий виклик `long res = SSL_get_verify_result(ssl)` і переконатися, що повернене значення дорівнює `X509_V_OK`. Будь-який інший числовий код свідчить про спробу підміни сертифіката або збій перевірки і вимагає негайного закриття сокета. У разі невдачі слід вилучити текстовий опис помилки через `X509_verify_cert_error_string(res)` та залогувати діагностичну інформацію для аудиту безпеки.



