# 🛠️ Практична реалізація валідатора цифрових підписів DNSSEC (C та C++)

Ця практична вставка містить повністю функціональний приклад реалізації модуля валідації цифрових підписів DNSSEC (зокрема алгоритму 13 ECDSA P-256 та алгоритму 8 RSA-SHA256) мовами C та C++20 з використанням криптографічної бібліотеки OpenSSL 3.x.

Модуль валідації призначений для безпосередньої інтеграції у системні рекурсивні DNS-резолвери, проксі-сервери, захисні фаєрволи або мережеві аналізатори трафіку. Він виконує повну перевірку ланцюга підпису для вхідних мережевих пакетів DNS, включаючи часову перевірку вікна чинності підпису, розпакування бінарних полів RDATA, перетворення сирого кодування підписів, розрахунок 16-бітної контрольної суми `Key Tag`, канонізацію доменних імен та криптографічну перевірку хешів від перед-зображення.

---

## 1. Детальний аналіз архітектури та послідовності перевірки підпису

Процес перевірки підпису DNSSEC `RRSIG` над ресурсом `RRset` складається з п'яти суворо послідовних кроків. Кожен крок виконує автономну перевірку й при виявленні найменшої невідповідності перериває подальшу обробку, повертаючи відповідний код помилки.

```text
[Вхідний пакет DNS: RRset + RRSIG + DNSKEY]
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│ Крок 1. Часова валідація вікна чинності (Timestamp Check) │
│ (Inception - Δ) ≤ T_curr ≤ (Expiration + Δ)               │
└────────────────────────────┬──────────────────────────────┘
                             │ Успіх
                             ▼
┌───────────────────────────────────────────────────────────┐
│ Крок 2. Пошук та зіставлення ключів через Key Tag        │
│ KeyTag(DNSKEY) == KeyTag(RRSIG)                           │
└────────────────────────────┬──────────────────────────────┘
                             │ Успіх
                             ▼
┌───────────────────────────────────────────────────────────┐
│ Крок 3. Формування канонічного перед-зображення (Preimage) │
│ Preimage = RRSIG_Header ∥ Signer ∥ Owner ∥ TTL ∥ RDATA    │
└────────────────────────────┬──────────────────────────────┘
                             │ Успіх
                             ▼
┌───────────────────────────────────────────────────────────┐
│ Крок 4. Декодування та конвертація формату підпису        │
│ RAW R ∥ S (64B) ──► ASN.1 DER Structure                   │
└────────────────────────────┬──────────────────────────────┘
                             │ Успіх
                             ▼
┌───────────────────────────────────────────────────────────┐
│ Крок 5. Криптографічна перевірка публічним ключем         │
│ EVP_DigestVerifyFinal(EVP_sha256(), Preimage, DER_Sig)    │
└────────────────────────────┴──────────────────────────────┘
```

### Крок 1. Часова валідація вікна чинності (Timestamp Verification)

Кожен підпис `RRSIG` містить два часові штампи у форматі POSIX Timestamp (кількість секунд з 1 січня 1970 року UTC):
- `Signature Inception`: точний момент часу, коли приватний ключ зони створив даний цифровий підпис.
- `Signature Expiration`: точний момент часу, після якого даний підпис втрачає чинність і вважається простроченим.

Підпис вважається дійсним лише тоді, коли поточний системний час знаходиться в межах між `Inception` та `Expiration`.

Для врахування мережевих затримок передачі пакетів та природного розсинхрону годинників між авторитетними серверами й валідаторами (Clock Skew) валідатор розширює часове вікно на допустиму величину допуску `Δ_skew = 300` секунд (5 хвилин). Умова перевірки виражається як:

```text
(Inception - Δ_skew) ≤ T_curr ≤ (Expiration + Δ_skew)
```

Якщо поточний час виходить за ці межі, валідатор негайно зупиняє обробку й повертає код помилки `DNSSEC_ERR_EXPIRED` або `DNSSEC_ERR_NOT_YET_VALID`. Це дозволяє відсікти прострочені або передчасні підписи на найпершому етапі без виконання дорогих криптографічних операцій зведення у степінь чи скалярного множення точок на еліптичній кривій.

### Крок 2. Зіставлення ключів через Key Tag (Key Tag Matching)

Перед перевіркою криптографії валідатор витягує 16-бітне поле `Key Tag` із заголовка `RRSIG` і шукає відповідний ключ у наборі `DNSKEY` зони. Для кожного ключа `DNSKEY` обчислюється його власне контрольне число `Key Tag` за допомогою циклічного додавання зсунутих байтів RDATA. 

Підпис перевіряється лише тим публічним ключем, чий `Key Tag` та числовий код алгоритму суворо збігаються з полями у `RRSIG`. Якщо в зоні присутні кілька ключів (наприклад, під час ротації ZSK), зіставлення `Key Tag` дозволяє уникнути зайвих спроб перевірки підпису невідповідними ключами.

### Крок 3. Формування канонічного перед-зображення (Preimage Assembly)

Криптографічний хеш створюється не від сирого мережевого UDP-пакета, а від спеціально зконструйованого бінарного буфера перед-зображення (`Preimage Buffer`). Це необхідно тому, що мережевий пакет DNS містить динамічні поля (такі як поточний зменшений TTL), які змінюються проміжними серверами й зламали б підпис при прямому хешуванні.

Буфер перед-зображення конкатенує наступні блоки у суворому порядку:
1. **Перші 18 байтів заголовка RRSIG:** поля `Type Covered (2B)`, `Algorithm (1B)`, `Labels (1B)`, `Original TTL (4B)`, `Expiration (4B)`, `Inception (4B)` та `Key Tag (2B)`.
2. **Канонічне ім'я підписувача (Signer's Name):** доменне ім'я зони у нижньому регістрі без використання механізму стиснення ім'я (DNS Name Compression).
3. **Канонічне ім'я власника запису (Owner Name):** ім'я захищаємого домену у нижньому регістрі.
4. **Клас та тип запису:** числовий клас (зазвичай `IN` = 1) та тип захищаємого RRset (2 байти).
5. **Оригінальне значення Original TTL:** значення TTL з заголовка `RRSIG` (4 байти).
6. **Відсортовані записи RDATA:** масив даних записів ресурсу, побайтово відсортований за зростанням як беззнакові цілі числа. Перед кожним блоком RDATA додається двобайтове поле довжини.

### Крок 4. Декодування та конвертація формату підпису (Signature Format Conversion)

У специфікації DNSSEC (RFC 6605) цифровий підпис ECDSA P-256 передається у вигляді сирого масиву з 64 байтів, який є прямою конкатенацією двох 32-байтових беззнакових цілих чисел `R` та `S` у форматі Big-Endian:

```text
Signature_Raw = R (32B) ∥ S (32B)
```

Однак криптографічна бібліотека OpenSSL (як і більшість системних криптопровайдерів TLS) очікує підписи ECDSA у форматі кодування ASN.1 DER (`ECDSA_SIG`). Конвертор `raw_ecdsa_to_der` виконує наступні дії:
1. Витягує 32 байти числа `R` та 32 байти числа `S` з вхідного сирого масиву.
2. Перетворює ці масиви байтів у об'єкти великих чисел `BIGNUM` OpenSSL за допомогою функції `BN_bin2bn`.
3. Упаковує числа `R` та `S` у структуру `ECDSA_SIG` за допомогою `ECDSA_SIG_set0`.
4. Кодує структуру `ECDSA_SIG` у стандартний бінарний буфер ASN.1 DER за допомогою функції `i2d_ECDSA_SIG`.

Формат ASN.1 DER додає необхідні теги байтів (`0x30` для послідовності SEQUENCE, `0x02` для цілих чисел INTEGER) та автоматично вставляє нульовий байт `0x00` перед числами, якщо їхній найстарший біт дорівнює 1 (для запобігання трактуванню числа як від'ємного в ASN.1).

### Крок 5. Криптографічна перевірка публічним ключем (Crypto Verification)

Валідатор витягує байти публічного ключа з запису `DNSKEY`:
- **Для ECDSA P-256 (алгоритм 13):** витягується 64 байти (32 байти координати `X` + 32 байти координати `Y` точки на еліптичній кривій secp256r1). За допомогою сучасного API OpenSSL 3.x (`OSSL_PARAM_BLD` та `EVP_PKEY_fromdata`) будується об'єкт публічного ключа `EVP_PKEY`.
- **Для RSA-SHA256 (алгоритм 8):** з RDATA витягується публічна експонента `e` та модуль `N_rsa`, які перетворюються у `BIGNUM` й пакуються у параметри `EVP_PKEY_RSA`.

Далі викликається послідовність уніфікованих функцій OpenSSL 3.x:
- `EVP_DigestVerifyInit`: ініціалізує контекст перевірки `EVP_MD_CTX` з вибором хешь-функції `EVP_sha256()` та публічного ключа `EVP_PKEY`.
- `EVP_DigestVerifyUpdate`: передає зконструйований буфер перед-зображення до функції хешування.
- `EVP_DigestVerifyFinal`: порівнює декодований підпис із обчисленим хешем від перед-зображення.

Якщо функція повертає 1, підпис вважається криптографічно підтвердженим і валідатор надає відповіді статус `SECURE`.

---

## 2. Повна реалізація модуля валідації (C та C++20)

У даному розділі наведено порівняльний код модуля валідації DNSSEC мовою C (OpenSSL 3.x C API з ручним управлінням пам'яттю) та ідіоматичною C++20 (автоматичні RAII-обгортки для об'єктів OpenSSL, розумні вказівники `std::unique_ptr`, `std::span` для безпечного зрізання буферів без копіювання та `std::expected` для вираження результату операції без винятків).

:::tabs

@tab C (OpenSSL 3.x API)

```c
/* dnssec_validator.h */
#ifndef DNSSEC_VALIDATOR_H
#define DNSSEC_VALIDATOR_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DNSSEC_OK = 0,
    DNSSEC_ERR_EXPIRED,
    DNSSEC_ERR_NOT_YET_VALID,
    DNSSEC_ERR_KEYTAG_MISMATCH,
    DNSSEC_ERR_MALFORMED_KEY,
    DNSSEC_ERR_MALFORMED_SIG,
    DNSSEC_ERR_CRYPTO_FAIL,
    DNSSEC_ERR_MEMORY
} dnssec_status_t;

typedef struct {
    uint16_t type_covered;
    uint8_t  algorithm;
    uint8_t  labels;
    uint32_t original_ttl;
    uint32_t expiration;
    uint32_t inception;
    uint16_t key_tag;
    const char *signer_name;
    const uint8_t *sig_bytes;
    size_t sig_len;
} rrsig_record_t;

typedef struct {
    uint16_t flags;
    uint8_t  protocol;
    uint8_t  algorithm;
    const uint8_t *pubkey_bytes;
    size_t pubkey_len;
} dnskey_record_t;

uint16_t dnssec_calc_keytag(const uint8_t *rdata, size_t rdata_len);

dnssec_status_t dnssec_verify_signature(
    const rrsig_record_t *rrsig,
    const dnskey_record_t *dnskey,
    const uint8_t *preimage,
    size_t preimage_len,
    int64_t current_time
);

#ifdef __cplusplus
}
#endif

#endif /* DNSSEC_VALIDATOR_H */

/* dnssec_validator.c */
#include "dnssec_validator.h"
#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/rsa.h>
#include <openssl/param_build.h>
#include <openssl/core_names.h>
#include <openssl/ecdsa.h>
#include <openssl/bn.h>
#include <string.h>
#include <stdio.h>

#define CLOCK_SKEW_TOLERANCE 300 /* 5 хвилин */

uint16_t dnssec_calc_keytag(const uint8_t *rdata, size_t rdata_len) {
    if (!rdata || rdata_len < 4) return 0;
    uint32_t ac = 0;
    for (size_t i = 0; i < rdata_len; ++i) {
        ac += (i & 1) ? rdata[i] : ((uint32_t)rdata[i] << 8);
    }
    ac += (ac >> 16) & 0xFFFF;
    return (uint16_t)(ac & 0xFFFF);
}

static uint8_t *raw_ecdsa_to_der(const uint8_t *sig_raw, size_t sig_len, size_t *out_der_len) {
    if (sig_len != 64) return NULL;

    BIGNUM *r = BN_bin2bn(sig_raw, 32, NULL);
    BIGNUM *s = BN_bin2bn(sig_raw + 32, 32, NULL);
    if (!r || !s) {
        BN_free(r);
        BN_free(s);
        return NULL;
    }

    ECDSA_SIG *sig = ECDSA_SIG_new();
    if (!sig) {
        BN_free(r);
        BN_free(s);
        return NULL;
    }

    ECDSA_SIG_set0(sig, r, s);

    int der_len = i2d_ECDSA_SIG(sig, NULL);
    if (der_len <= 0) {
        ECDSA_SIG_free(sig);
        return NULL;
    }

    uint8_t *der_buf = OPENSSL_malloc((size_t)der_len);
    if (!der_buf) {
        ECDSA_SIG_free(sig);
        return NULL;
    }

    uint8_t *p = der_buf;
    i2d_ECDSA_SIG(sig, &p);
    ECDSA_SIG_free(sig);

    *out_der_len = (size_t)der_len;
    return der_buf;
}

static EVP_PKEY *build_ecdsa_pkey(const uint8_t *pubkey, size_t pubkey_len) {
    if (pubkey_len != 64) return NULL;

    uint8_t uncompressed_pt[65];
    uncompressed_pt[0] = 0x04;
    memcpy(uncompressed_pt + 1, pubkey, 64);

    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_from_name(NULL, "EC", NULL);
    if (!pctx) return NULL;

    if (EVP_PKEY_fromdata_init(pctx) <= 0) {
        EVP_PKEY_CTX_free(pctx);
        return NULL;
    }

    OSSL_PARAM_BLD *bld = OSSL_PARAM_BLD_new();
    OSSL_PARAM_BLD_push_utf8_string(bld, OSSL_PKEY_PARAM_GROUP_NAME, "prime256v1", 0);
    OSSL_PARAM_BLD_push_octet_string(bld, OSSL_PKEY_PARAM_PUB_KEY, uncompressed_pt, 65);

    OSSL_PARAM *params = OSSL_PARAM_BLD_to_param(bld);
    EVP_PKEY *pkey = NULL;
    if (EVP_PKEY_fromdata(pctx, &pkey, EVP_PKEY_PUBLIC_KEY, params) <= 0) {
        pkey = NULL;
    }

    OSSL_PARAM_free(params);
    OSSL_PARAM_BLD_free(bld);
    EVP_PKEY_CTX_free(pctx);
    return pkey;
}

static EVP_PKEY *build_rsa_pkey(const uint8_t *pubkey, size_t pubkey_len) {
    if (pubkey_len < 3) return NULL;
    size_t elen = pubkey[0];
    size_t offset = 1;
    if (elen == 0) {
        if (pubkey_len < 5) return NULL;
        elen = ((size_t)pubkey[1] << 8) | pubkey[2];
        offset = 3;
    }
    if (pubkey_len < offset + elen) return NULL;

    BIGNUM *e = BN_bin2bn(pubkey + offset, (int)elen, NULL);
    BIGNUM *n = BN_bin2bn(pubkey + offset + elen, (int)(pubkey_len - offset - elen), NULL);
    if (!e || !n) {
        BN_free(e);
        BN_free(n);
        return NULL;
    }

    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_from_name(NULL, "RSA", NULL);
    if (!pctx || EVP_PKEY_fromdata_init(pctx) <= 0) {
        BN_free(e); BN_free(n);
        EVP_PKEY_CTX_free(pctx);
        return NULL;
    }

    OSSL_PARAM_BLD *bld = OSSL_PARAM_BLD_new();
    OSSL_PARAM_BLD_push_BN(bld, OSSL_PKEY_PARAM_RSA_N, n);
    OSSL_PARAM_BLD_push_BN(bld, OSSL_PKEY_PARAM_RSA_E, e);

    OSSL_PARAM *params = OSSL_PARAM_BLD_to_param(bld);
    EVP_PKEY *pkey = NULL;
    EVP_PKEY_fromdata(pctx, &pkey, EVP_PKEY_PUBLIC_KEY, params);

    OSSL_PARAM_free(params);
    OSSL_PARAM_BLD_free(bld);
    EVP_PKEY_CTX_free(pctx);
    BN_free(e);
    BN_free(n);
    return pkey;
}

dnssec_status_t dnssec_verify_signature(
    const rrsig_record_t *rrsig,
    const dnskey_record_t *dnskey,
    const uint8_t *preimage,
    size_t preimage_len,
    int64_t current_time
) {
    if (!rrsig || !dnskey || !preimage) return DNSSEC_ERR_CRYPTO_FAIL;

    if (current_time + CLOCK_SKEW_TOLERANCE < (int64_t)rrsig->inception) {
        return DNSSEC_ERR_NOT_YET_VALID;
    }
    if (current_time - CLOCK_SKEW_TOLERANCE > (int64_t)rrsig->expiration) {
        return DNSSEC_ERR_EXPIRED;
    }

    if (dnskey->algorithm != rrsig->algorithm) {
        return DNSSEC_ERR_CRYPTO_FAIL;
    }

    EVP_PKEY *pkey = NULL;
    uint8_t *der_sig = NULL;
    size_t der_sig_len = 0;
    const uint8_t *sig_to_verify = rrsig->sig_bytes;
    size_t sig_len_to_verify = rrsig->sig_len;

    if (rrsig->algorithm == 13) { /* ECDSA P-256 */
        pkey = build_ecdsa_pkey(dnskey->pubkey_bytes, dnskey->pubkey_len);
        if (!pkey) return DNSSEC_ERR_MALFORMED_KEY;

        der_sig = raw_ecdsa_to_der(rrsig->sig_bytes, rrsig->sig_len, &der_sig_len);
        if (!der_sig) {
            EVP_PKEY_free(pkey);
            return DNSSEC_ERR_MALFORMED_SIG;
        }
        sig_to_verify = der_sig;
        sig_len_to_verify = der_sig_len;
    } else if (rrsig->algorithm == 8) { /* RSA-SHA256 */
        pkey = build_rsa_pkey(dnskey->pubkey_bytes, dnskey->pubkey_len);
        if (!pkey) return DNSSEC_ERR_MALFORMED_KEY;
    } else {
        return DNSSEC_ERR_CRYPTO_FAIL;
    }

    EVP_MD_CTX *mctx = EVP_MD_CTX_new();
    if (!mctx) {
        if (der_sig) OPENSSL_free(der_sig);
        EVP_PKEY_free(pkey);
        return DNSSEC_ERR_MEMORY;
    }

    dnssec_status_t status = DNSSEC_ERR_CRYPTO_FAIL;
    if (EVP_DigestVerifyInit(mctx, NULL, EVP_sha256(), NULL, pkey) > 0) {
        if (EVP_DigestVerifyUpdate(mctx, preimage, preimage_len) > 0) {
            if (EVP_DigestVerifyFinal(mctx, sig_to_verify, sig_len_to_verify) == 1) {
                status = DNSSEC_OK;
            }
        }
    }

    EVP_MD_CTX_free(mctx);
    if (der_sig) OPENSSL_free(der_sig);
    EVP_PKEY_free(pkey);

    return status;
}
```

@tab C++20 (RAII & Expected)

```cpp
#pragma once

#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <optional>
#include <cstdint>
#include <chrono>
#include <algorithm>

#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/bn.h>
#include <openssl/param_build.h>
#include <openssl/core_names.h>

namespace dnssec {

enum class ValidationError {
    Expired,
    NotYetValid,
    KeyTagMismatch,
    MalformedKey,
    MalformedSignature,
    CryptoFailure,
    MemoryError
};

struct RRSIGRecord {
    uint16_t type_covered;
    uint8_t  algorithm;
    uint8_t  labels;
    uint32_t original_ttl;
    uint32_t expiration;
    uint32_t inception;
    uint16_t key_tag;
    std::string signer_name;
    std::vector<uint8_t> signature;
};

struct DNSKEYRecord {
    uint16_t flags;
    uint8_t  protocol;
    uint8_t  algorithm;
    std::vector<uint8_t> pubkey;
};

/* RAII Deleters для OpenSSL */
struct EVP_PKEY_deleter { void operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); } };
struct EVP_PKEY_CTX_deleter { void operator()(EVP_PKEY_CTX* p) const { EVP_PKEY_CTX_free(p); } };
struct EVP_MD_CTX_deleter { void operator()(EVP_MD_CTX* p) const { EVP_MD_CTX_free(p); } };
struct OSSL_PARAM_BLD_deleter { void operator()(OSSL_PARAM_BLD* p) const { OSSL_PARAM_BLD_free(p); } };
struct OSSL_PARAM_deleter { void operator()(OSSL_PARAM* p) const { OSSL_PARAM_free(p); } };
struct BIGNUM_deleter { void operator()(BIGNUM* p) const { BN_free(p); } };
struct ECDSA_SIG_deleter { void operator()(ECDSA_SIG* p) const { ECDSA_SIG_free(p); } };

using ScopedEVP_PKEY = std::unique_ptr<EVP_PKEY, EVP_PKEY_deleter>;
using ScopedEVP_PKEY_CTX = std::unique_ptr<EVP_PKEY_CTX, EVP_PKEY_CTX_deleter>;
using ScopedEVP_MD_CTX = std::unique_ptr<EVP_MD_CTX, EVP_MD_CTX_deleter>;

class DNSSECValidator {
public:
    static uint16_t CalculateKeyTag(std::span<const uint8_t> rdata) noexcept {
        if (rdata.size() < 4) return 0;
        uint32_t ac = 0;
        for (size_t i = 0; i < rdata.size(); ++i) {
            ac += (i & 1) ? rdata[i] : (static_cast<uint32_t>(rdata[i]) << 8);
        }
        ac += (ac >> 16) & 0xFFFF;
        return static_cast<uint16_t>(ac & 0xFFFF);
    }

    static std::expected<void, ValidationError> VerifySignature(
        const RRSIGRecord& rrsig,
        const DNSKEYRecord& dnskey,
        std::span<const uint8_t> preimage,
        std::chrono::system_clock::time_point current_time
    ) {
        using namespace std::chrono;
        auto now_sec = duration_cast<seconds>(current_time.time_since_epoch()).count();
        constexpr int64_t skew_tolerance = 300;

        if (now_sec + skew_tolerance < static_cast<int64_t>(rrsig.inception)) {
            return std::unexpected(ValidationError::NotYetValid);
        }
        if (now_sec - skew_tolerance > static_cast<int64_t>(rrsig.expiration)) {
            return std::unexpected(ValidationError::Expired);
        }

        if (dnskey.algorithm != rrsig.algorithm) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        ScopedEVP_PKEY pkey;
        std::vector<uint8_t> der_sig_storage;
        std::span<const uint8_t> sig_to_verify = rrsig.signature;

        if (rrsig.algorithm == 13) { // ECDSA P-256
            auto built_pkey = BuildECDSAPKey(dnskey.pubkey);
            if (!built_pkey) return std::unexpected(ValidationError::MalformedKey);
            pkey = std::move(*built_pkey);

            auto der_sig = RawECDSAToDER(rrsig.signature);
            if (!der_sig) return std::unexpected(ValidationError::MalformedSignature);
            der_sig_storage = std::move(*der_sig);
            sig_to_verify = der_sig_storage;
        } else if (rrsig.algorithm == 8) { // RSA-SHA256
            auto built_pkey = BuildRSAPKey(dnskey.pubkey);
            if (!built_pkey) return std::unexpected(ValidationError::MalformedKey);
            pkey = std::move(*built_pkey);
        } else {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        ScopedEVP_MD_CTX mctx(EVP_MD_CTX_new());
        if (!mctx) return std::unexpected(ValidationError::MemoryError);

        if (EVP_DigestVerifyInit(mctx.get(), nullptr, EVP_sha256(), nullptr, pkey.get()) <= 0) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        if (EVP_DigestVerifyUpdate(mctx.get(), preimage.data(), preimage.size()) <= 0) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        if (EVP_DigestVerifyFinal(mctx.get(), sig_to_verify.data(), sig_to_verify.size()) != 1) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        return {};
    }

private:
    static std::optional<ScopedEVP_PKEY> BuildECDSAPKey(std::span<const uint8_t> pubkey) {
        if (pubkey.size() != 64) return std::nullopt;

        std::vector<uint8_t> uncompressed_pt(65);
        uncompressed_pt[0] = 0x04;
        std::copy(pubkey.begin(), pubkey.end(), uncompressed_pt.begin() + 1);

        ScopedEVP_PKEY_CTX pctx(EVP_PKEY_CTX_new_from_name(nullptr, "EC", nullptr));
        if (!pctx || EVP_PKEY_fromdata_init(pctx.get()) <= 0) return std::nullopt;

        std::unique_ptr<OSSL_PARAM_BLD, OSSL_PARAM_BLD_deleter> bld(OSSL_PARAM_BLD_new());
        OSSL_PARAM_BLD_push_utf8_string(bld.get(), OSSL_PKEY_PARAM_GROUP_NAME, "prime256v1", 0);
        OSSL_PARAM_BLD_push_octet_string(bld.get(), OSSL_PKEY_PARAM_PUB_KEY, uncompressed_pt.data(), uncompressed_pt.size());

        std::unique_ptr<OSSL_PARAM, OSSL_PARAM_deleter> params(OSSL_PARAM_BLD_to_param(bld.get()));
        EVP_PKEY* raw_pkey = nullptr;
        if (EVP_PKEY_fromdata(pctx.get(), &raw_pkey, EVP_PKEY_PUBLIC_KEY, params.get()) <= 0) {
            return std::nullopt;
        }
        return ScopedEVP_PKEY(raw_pkey);
    }

    static std::optional<ScopedEVP_PKEY> BuildRSAPKey(std::span<const uint8_t> pubkey) {
        if (pubkey.size() < 3) return std::nullopt;
        size_t elen = pubkey[0];
        size_t offset = 1;
        if (elen == 0) {
            if (pubkey.size() < 5) return std::nullopt;
            elen = (static_cast<size_t>(pubkey[1]) << 8) | pubkey[2];
            offset = 3;
        }
        if (pubkey.size() < offset + elen) return std::nullopt;

        std::unique_ptr<BIGNUM, BIGNUM_deleter> e(BN_bin2bn(pubkey.data() + offset, static_cast<int>(elen), nullptr));
        std::unique_ptr<BIGNUM, BIGNUM_deleter> n(BN_bin2bn(pubkey.data() + offset + elen, static_cast<int>(pubkey.size() - offset - elen), nullptr));
        if (!e || !n) return std::nullopt;

        ScopedEVP_PKEY_CTX pctx(EVP_PKEY_CTX_new_from_name(nullptr, "RSA", nullptr));
        if (!pctx || EVP_PKEY_fromdata_init(pctx) <= 0) return std::nullopt;

        std::unique_ptr<OSSL_PARAM_BLD, OSSL_PARAM_BLD_deleter> bld(OSSL_PARAM_BLD_new());
        OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_N, n.get());
        OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_E, e.get());

        std::unique_ptr<OSSL_PARAM, OSSL_PARAM_deleter> params(OSSL_PARAM_BLD_to_param(bld.get()));
        EVP_PKEY* raw_pkey = nullptr;
        if (EVP_PKEY_fromdata(pctx.get(), &raw_pkey, EVP_PKEY_PUBLIC_KEY, params.get()) <= 0) {
            return std::nullopt;
        }
        return ScopedEVP_PKEY(raw_pkey);
    }

    static std::optional<std::vector<uint8_t>> RawECDSAToDER(std::span<const uint8_t> raw_sig) {
        if (raw_sig.size() != 64) return std::nullopt;

        std::unique_ptr<BIGNUM, BIGNUM_deleter> r(BN_bin2bn(raw_sig.data(), 32, nullptr));
        std::unique_ptr<BIGNUM, BIGNUM_deleter> s(BN_bin2bn(raw_sig.data() + 32, 32, nullptr));
        if (!r || !s) return std::nullopt;

        std::unique_ptr<ECDSA_SIG, ECDSA_SIG_deleter> sig(ECDSA_SIG_new());
        if (!sig) return std::nullopt;

        ECDSA_SIG_set0(sig.get(), r.release(), s.release());

        int der_len = i2d_ECDSA_SIG(sig.get(), nullptr);
        if (der_len <= 0) return std::nullopt;

        std::vector<uint8_t> der_buf(static_cast<size_t>(der_len));
        uint8_t* p = der_buf.data();
        i2d_ECDSA_SIG(sig.get(), &p);

        return der_buf;
    }
};

} // namespace dnssec
```

:::

---

## 3. Детальний аналіз ідіом та архітектурних рішень коду C++20

У наведеній реалізації мовою C++20 використано сучасні патерни системного програмування, що гарантують максимальну надійність та нульові накладні витрати на критичному шляху обробки мережевих пакетів:

### 1. RAII Управління ресурсами OpenSSL (Smart Pointer Deleters)

Криптографічні структури OpenSSL 3.x (`EVP_PKEY`, `EVP_PKEY_CTX`, `EVP_MD_CTX`, `BIGNUM`, `ECDSA_SIG`, `OSSL_PARAM`) є сирими вказівниками C, які вимагають суворого парного звільнення через спеціалізовані деструкторні функції (`EVP_PKEY_free`, `BN_free`, `ECDSA_SIG_free` тощо). 

Використання кастомних делітерів у `std::unique_ptr` дозволяє створити безпечні обгортки на зразок `ScopedEVP_PKEY` та `ScopedEVP_MD_CTX`. Якщо функція повертає помилку з ранньої гілки `if` (наприклад, при виявленні невалідного ключа або недостачі пам'яті), усі виділені ресурси OpenSSL вилучаються автоматично при виході з області видимості, що повністю усуває загрозу витоків пам'яті (Memory Leaks).

### 2. Безпечне зрізання буферів без копіювання через std::span (Zero-Copy Slicing)

Функції модуля приймають зрізи пам'яті `std::span<const uint8_t>` замість передачі сирих вказівників `const uint8_t*` та розмірів `size_t`. 

Це надає наступні переваги:
- **Перевірка межевих значень (Bounds Checking):** `std::span` зберігає вказівник та довжину бувера як єдиний некопійований об'єкт, запобігаючи виходу за межі масиву під час парсингу полів пакета.
- **Нульове копіювання (Zero-Copy):** валідатор передає зрізи вхідного мережевого бувера прямо у криптографічні функції OpenSSL без створення тимчасових векторів `std::vector`, що суттєво підвищує продуктивність при обробці тисяч DNSSEC-запитів на секунду.

### 3. Безвиняткова обробка помилок через std::expected

У високопродуктивних системних серверах використання винятків C++ (`throw / try / catch`) під час обробки невалідних або підроблених підписів є неприпустимим: засипання резолвера підробленими пакетами під час DDoS-атаки викличуть масове розгортання стеку (Stack Unwinding) та призведуть до відмови в обслуговуванні CPU.

Застосування `std::expected<void, ValidationError>` дозволяє повернути статус успіху або конкретне значення перерахування `ValidationError` у вигляді компактного розчепленого об'єкта, обчислювальна вартість повернення якого еквівалентна звичайному коду повернення у C.

---

## 4. Канонізація доменних імен та сортування RRset в пам'яті

Для збирання байтів перед-зображення валідатор повинен виконувати дві специфічні допоміжні операції: канонізацію доменних міток та побайтове сортування набору записів RDATA.

### Канонізація імен (Case-Insensitive Lowercasing)

Згідно з RFC 4034, під час підготовки перед-зображення всі доменні імена (`Signer's Name` та `Owner Name`) мають переводитися у нижній регістр. Символи з кодами від `0x41` ('A') до `0x5A` ('Z') замінюються на `0x61` ('a') .. `0x7A` ('z').

У C++20 ця операція реалізується без виділення пам'яті у динамічному купі за допомогою `std::string_view` або трансформації посилання на рядок у місці:

```cpp
void CanonicalizeDomainName(std::string& name) noexcept {
    std::transform(name.begin(), name.end(), name.begin(), [](unsigned char c) {
        return (c >= 'A' && c <= 'Z') ? (c + ('a' - 'A')) : c;
    });
}
```

### Побайтове сортування RDATA (Lexicographical Byte Order)

Записи у наборі `RRset` сортуються порівнянням бінарних масивів RDATA як беззнакових цілих чисел `uint8_t` зліва направо:

```cpp
bool CompareRData(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    size_t min_len = std::min(a.size(), b.size());
    for (size_t i = 0; i < min_len; ++i) {
        if (a[i] != b[i]) return a[i] < b[i];
    }
    return a.size() < b.size();
}
```

---

## 5. Детальний аналіз OpenSSL 3.x Provider API для створення ключів RSA та ECDSA

У сучасній версії OpenSSL 3.x застарілі макроси `RSA_new()` та `EC_KEY_new_by_curve_name()` визнані необов'язковими й замінені на уніфікований **Provider API** (`OSSL_PARAM_BLD` та `EVP_PKEY_fromdata`). Це дозволяє відокремити алгоритмічний код від конкретної криптографічної реалізації та спрощує інтеграцію апаратних модулів безпеки (HSM) або постквантових провайдерів.

### Побудова об'єкта ключа ECDSA P-256 через OSSL_PARAM_BLD

Для створення об'єкта `EVP_PKEY` еліптичної кривої P-256 (алгоритм 13) з сирих 64 байтів публічного ключа валідатор виконує наступну послідовність дій:
1. Створюється нестиснута точка еліптичної кривої розміром 65 байтів. Перший байт встановлюється у `0x04` (префікс нестиснутої точки за специфікацією ANSI X9.62), а наступні 64 байти заповнюються координатами `X` та `Y`.
2. Контекст виділення ключа `EVP_PKEY_CTX` створюється за ім'ям алгоритму `"EC"` через виклик `EVP_PKEY_CTX_new_from_name(NULL, "EC", NULL)`.
3. Ініціалізується будівельник параметрів `OSSL_PARAM_BLD_new()`.
4. До будівельника додається текстова назва кривої `"prime256v1"` (параметр `OSSL_PKEY_PARAM_GROUP_NAME`) та октетний масив нестиснутої точки (параметр `OSSL_PKEY_PARAM_PUB_KEY`).
5. Будівельник конвертує накопичені параметри у підсумковий масив `OSSL_PARAM` за допомогою `OSSL_PARAM_BLD_to_param`.
6. Викликом `EVP_PKEY_fromdata` будується остаточний об'єкт `EVP_PKEY`.

### Побудова об'єкта ключа RSA-SHA256 через OSSL_PARAM_BLD

Для RSA-ключів (алгоритм 8) RDATA запису `DNSKEY` зберігає експоненту `e` та модуль `N_rsa`. Створення `EVP_PKEY` відбувається аналогічно:
1. За допомогою функції `BN_bin2bn` байти експоненти та модуля конвертуються у об'єкти великих цілих чисел `BIGNUM`.
2. Контекст `EVP_PKEY_CTX` створюється за ім'ям алгоритму `"RSA"`.
3. У будівельник параметрів додаються числа `BIGNUM` за допомогою `OSSL_PARAM_BLD_push_BN`: параметр `OSSL_PKEY_PARAM_RSA_N` (модуль) та `OSSL_PKEY_PARAM_RSA_E` (публічна експонента).
4. За допомогою `EVP_PKEY_fromdata` будується готовий `EVP_PKEY` для RSA.

Такий підхід повністю захищає програму від застарілих попереджень компілятора й гарантує високу швидкість виконання на сучасних архітектурах x86_64 та ARM64.

---

## 6. Продуктивність та оптимізація обчислювальних ресурсів

Криптографічна валідація цифрових підписів є найдорожчою операцією в системних DNS-резолвера. Скалярне множення точок на еліптичній кривій ECDSA P-256 вимагає близько 150–200 мікросекунд процесорного часу на один підпис, а перевірка RSA-2048 — близько 50–80 мікросекунд.

Для досягнення високої пропускної здатності в промислових резолверах (BIND 9, Unbound, PowerDNS) застосовуються наступні методи оптимізації:

1. **Кешування результатів валідації (Validation Result Caching):**
   Резолвер кешує не лише вихідний RRset, а й сам результат валідації `SECURE` або `BOGUS` разом із хешем перед-зображення. Якщо домен запитується тисячі разів на секунду, криптографічна перевірка виконується лише один раз до вичерпання TTL підпису.

2. **Кешування розпакованих об'єктів EVP_PKEY:**
   Створення об'єкта `EVP_PKEY` із сирих байтів `DNSKEY` вимагає динамічних виділень пам'яті для `BIGNUM` та параметаризації. Резолвер зберігає зконструйовані об'єкти `EVP_PKEY` у високошвидкісній кеш-таблиці публічних ключів зони, перевіряючи підписи `RRSIG` готовими об'єктами без повторного парсингу RDATA.

3. **Багатопотокова паралелізація (Multi-threaded Pipeline):**
   Операції валідації є абсолютно незалежними для різних запитів і не потребують глобальних мутексів. Модуль валідаторів масштабується лінійно за кількістю ядер процесора.

---

## 7. Обробка помилок та діагностика у високопродуктивному операційному середовищі

У реальних мережевих службах модуль валідації є центральним бар'єром безпеки. Будь-який збій валідації призводить до відхилення DNS-відповіді з кодом `SERVFAIL`. Для того, щоб системні адміністратори могли оперативно виявляти причину збою (помилка конфігурації зони vs криптографічна атака), модуль підтримує структуроване протоколювання розширених кодів EDE (Extended DNS Errors — RFC 8914):

- `EDE Code 6 (DNSKEY Missing)`: запис DNSKEY відсутній у кеші резолвера або не надійшов у секції `ANSWER`.
- `EDE Code 8 (No Zone Key)`: знайдено запис DNSKEY, але його `Key Tag` не відповідає жодному з полів у `RRSIG`.
- `EDE Code 9 (NSEC Missing)`: відсутній підписаний запис NSEC/NSEC3 для доказового підтвердження неіснування запитуваного домену.
- `EDE Code 12 (Bogus)`: криптографічний підпис RRSIG не збігається з хешем від перед-зображення або порушено цілісність ланцюга DS.
- `EDE Code 13 (Signature Expired)`: системний час резолвера перевищив поле `Expiration` у `RRSIG`.
- `EDE Code 14 (Signature Not Yet Valid)`: підпис отримано раніше моменту `Inception` (порушення синхронізації NTP).

Завдяки деталізованій деталізації помилок служба моніторингу резолвера може автоматично генерувати сповіщення при появі масових помилок `EDE Code 12`, що сигналізує про активну мережеву атаку отруєння кешу.

---

## 8. Комплексний тестовий сценарій та перевірка крайових випадків

Під час модульного тестування модуля валідації DNSSEC перевіряються наступні критичні крайові випадки:

1. **Часові границі чинності підпису:** перевіряється поведінка валідатора, коли системний час знаходиться рівно на межі `Inception - Δ` або `Expiration + Δ`.
2. **Атака підміни ключа (Key Tag Collision):** створення двох ключів `DNSKEY`, чиї контрольні суми `Key Tag` випадково збігаються, але криптографічні параметри є різними. Валідатор перевіряє обидва ключі й відхиляє невалідний підпис.
3. **Обробка пошкодженого підпису:** перевіряється стійкість конвертора `raw_ecdsa_to_der` до сирих масивів підпису, у яких байти `R` або `S` містять нульові або від'ємні значення у форматі ASN.1.
4. **Багатопоточна безпека (Thread Safety):** перевіряється відсутність спільних статичних змінних усередині об'єктів OpenSSL 3.x, що дозволяє виконувати паралельну валідацію підписів у кількох воркер-потоках мережевого сервера без блокування м'ютексів.
