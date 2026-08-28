# ⚙️ Валідатор підписів образу ядра та емуляція криптографічного завантажувача

У вбудованих системах та завантажувачах операційних систем (U-Boot, Barebox, Shim) алгоритм перевірки цілісності образу прошивки є критичною точкою відліку ланцюга безпеки. Завантажувач повинен розібрати бінарний заголовок файлу, виділити корисне навантаження (машинний код ядра), розрахувати криптографічний геш вмісту та перевірити цифровий підпис за допомогою відкритого ключа, що зберігається в захищеному сховищі ключів.

Розглянемо практичну реалізацію валідатора завантажувальних образів, який підтримує концепцію двох рівнів авторизації: фабричного ключа виробника (OEM Root Key) та користувацького ключа вторинного підпису (User MOK Key), що дозволяє виконувати вимоги антитайвоізації статті 6 GPLv3 без втрати загальної безпеки пристрою.

## Структура бінарного образу та протокол верифікації

Формат підписаного завантажувального образу складається з трьох послідовних сегментів:
1. **Заголовок образу (`ImageHeader`):** фіксована 64-байтна структура, що містить магічне число `0x53454355` (`SECU`), версію протоколу, номер релізу для захисту від відкочування (*anti-rollback counter*), розмір корисного навантаження ядра та розмір блоку цифрового підпису.
2. **Корисне навантаження (`Payload`):** виконуваний двійковий код ядра Linux або вторинного завантажувача.
3. **Блок криптографічного підпису (`SignatureBlock`):** ідентифікатор алгоритму (ECDSA P-256 з SHA-256), ідентифікатор використаного ключа (Key ID) та сам двійковий підпис у форматі ASN.1 DER або сирих байтів `(r, s)`.

```
┌─────────────────┬──────────────────────────────────┬─────────────────────┐
│ Header (64 B)   │ Kernel Payload (N байтів)        │ Signature (M байтів)│
│ Magic, Len, Ver │ Виконуваний машинний код ядра   │ ECDSA P-256/SHA-256 │
└─────────────────┴──────────────────────────────────┴─────────────────────┘
 ◄─────────────────────── Обчислення SHA-256 ──────────────────────────────►
```

Процес верифікації виконується за такими суворими етапами:
- Перевірка сигнатури заголовка (`magic == 0x53454355`).
- Перевірка версії прошивки: значення лічильника версії в заголовку повинно бути більшим або рівним значенню апаратного лічильника eFuses.
- Обчислення гешу SHA-256 від усього обсягу `Payload`.
- Пошук публічного ключа: спочатку перевіряється збіг із кореневим OEM-ключем; якщо підпис не відповідає OEM-ключу, система перевіряє наявність ключа в базі дозволених користувацьких ключів (User MOK Key Slot).
- Верифікація математичної коректності підпису через криптографічний рушій.

## Інженерні вимоги до пам'яті та стану процесора

Під час виконання криптографічної перевірки завантажувач функціонує в умовах суворих апаратних обмежень:
- **Контроль таблиць сторінок MMU:** пам'ять, куди завантажується образ ядра для перевірки, повинна бути налаштована як доступна лише для читання та запису даних (RW-), але з обов'язково активним бітом заборони виконання коду (NX/XN — Never Execute). Лише після того, як криптографічний рушій поверне статус успішної перевірки, завантажувач перемикає атрибути сторінок у режим виконання (R-X) і передає керування точці входу.
- **Очищення криптографічного контексту:** перед передачею керування новому ядру весь проміжний стан обчислення гешів (структури `EVP_MD_CTX`) та тимчасові буфери у внутрішній пам'яті процесора (SRAM) повинні бути перезаписані нулями (`OPENSSL_cleanse`), щоб унеможливити відновлення залишків ключів або дампів пам'яті сторонніми програмами.
- **Делегація прав користувача:** якщо образ підписано не кореневим OEM-ключем, а додатковим MOK-ключем користувача, валідатор виставляє спеціальний прапорець `is_user_authorized`. У комерційних пристроях цей статус дозволяє запустити ядро, але обмежує доступ до апаратних DRM-ключів та банківських сертифікатів безпеки, що повністю відповідає нормам статті 6 GPLv3.

## Реалізація верифікатора підписів

Нижче наведено повнофункціональний код модуля верифікації підписів. У вкладці C реалізовано низькорівневий процедурний алгоритм із прямим керуванням пам'яттю бібліотеки OpenSSL EVP; у вкладці C++ реалізовано ідіоматичний об'єктно-орієнтований інтерфейс на базі стандарту C++20 із застосуванням RAII-обгорток, незмінних зрізів пам'яті `std::span` та типізованих помилок `std::expected`.

:::tabs
```c
/* boot_verifier.c — Процедурна реалізація криптографічного валідатора для C99/C11 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/sha.h>

#define SECURE_BOOT_MAGIC 0x53454355U /* "SECU" */

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t header_version;
    uint32_t firmware_version;
    uint32_t payload_size;
    uint32_t signature_size;
    uint8_t  key_id[16];
    uint8_t  reserved[28];
} ImageHeader;

typedef enum {
    VERIFY_SUCCESS = 0,
    ERR_INVALID_MAGIC,
    ERR_ROLLBACK_DETECTED,
    ERR_IMAGE_TOO_SHORT,
    ERR_UNKNOWN_KEY,
    ERR_SIGNATURE_FAILED,
    ERR_CRYPTO_ENGINE
} VerifyResult;

typedef struct {
    uint8_t key_id[16];
    EVP_PKEY *pubkey;
    bool is_user_mok;
} KeyEntry;

typedef struct {
    KeyEntry *keys;
    size_t key_count;
    uint32_t min_anti_rollback_ver;
} BootKeystore;

static EVP_PKEY *load_pubkey_from_pem(const char *pem_str) {
    BIO *bio = BIO_new_mem_buf(pem_str, -1);
    if (!bio) return NULL;
    EVP_PKEY *pkey = PEM_read_bio_PUBKEY(bio, NULL, NULL, NULL);
    BIO_free(bio);
    return pkey;
}

VerifyResult verify_boot_image(const BootKeystore *keystore,
                               const uint8_t *raw_data,
                               size_t total_size,
                               bool *out_is_user_authorized) {
    if (total_size < sizeof(ImageHeader)) {
        return ERR_IMAGE_TOO_SHORT;
    }

    const ImageHeader *hdr = (const ImageHeader *)raw_data;
    if (hdr->magic != SECURE_BOOT_MAGIC) {
        return ERR_INVALID_MAGIC;
    }

    if (hdr->firmware_version < keystore->min_anti_rollback_ver) {
        return ERR_ROLLBACK_DETECTED;
    }

    /* Захист від цілочисельного переповнення під час розрахунку загального розміру */
    if (hdr->payload_size > total_size || hdr->signature_size > total_size) {
        return ERR_IMAGE_TOO_SHORT;
    }

    size_t expected_total = sizeof(ImageHeader) + hdr->payload_size + hdr->signature_size;
    if (expected_total < sizeof(ImageHeader) || total_size < expected_total) {
        return ERR_IMAGE_TOO_SHORT;
    }

    const uint8_t *payload = raw_data + sizeof(ImageHeader);
    const uint8_t *sig = payload + hdr->payload_size;

    /* Пошук публічного ключа за ідентифікатором key_id */
    const KeyEntry *matched_key = NULL;
    for (size_t i = 0; i < keystore->key_count; ++i) {
        if (memcmp(keystore->keys[i].key_id, hdr->key_id, 16) == 0) {
            matched_key = &keystore->keys[i];
            break;
        }
    }

    if (!matched_key || !matched_key->pubkey) {
        return ERR_UNKNOWN_KEY;
    }

    /* Криптографічна перевірка підпису через OpenSSL EVP API */
    EVP_MD_CTX *md_ctx = EVP_MD_CTX_new();
    if (!md_ctx) {
        return ERR_CRYPTO_ENGINE;
    }

    VerifyResult result = ERR_SIGNATURE_FAILED;
    if (EVP_DigestVerifyInit(md_ctx, NULL, EVP_sha256(), NULL, matched_key->pubkey) != 1) {
        result = ERR_CRYPTO_ENGINE;
        goto cleanup;
    }

    if (EVP_DigestVerifyUpdate(md_ctx, payload, hdr->payload_size) != 1) {
        result = ERR_CRYPTO_ENGINE;
        goto cleanup;
    }

    if (EVP_DigestVerifyFinal(md_ctx, sig, hdr->signature_size) == 1) {
        result = VERIFY_SUCCESS;
        if (out_is_user_authorized) {
            *out_is_user_authorized = matched_key->is_user_mok;
        }
    }

cleanup:
    EVP_MD_CTX_free(md_ctx);
    return result;
}
```
```cpp
// boot_verifier.hpp / boot_verifier.cpp — Ідіоматична реалізація на сучасному C++20
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <expected>
#include <array>
#include <algorithm>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/pem.h>

namespace bootsec {

inline constexpr uint32_t SecureBootMagic = 0x53454355U; // "SECU"

struct alignas(4) ImageHeader {
    uint32_t magic;
    uint32_t header_version;
    uint32_t firmware_version;
    uint32_t payload_size;
    uint32_t signature_size;
    std::array<uint8_t, 16> key_id;
    std::array<uint8_t, 28> reserved;
};

enum class VerifyError {
    InvalidMagic,
    RollbackDetected,
    ImageTooShort,
    UnknownKey,
    SignatureInvalid,
    CryptoEngineFault
};

struct EvpPkeyDeleter {
    void operator()(EVP_PKEY* ptr) const noexcept {
        if (ptr) EVP_PKEY_free(ptr);
    }
};
using UniquePkey = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;

struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ptr) const noexcept {
        if (ptr) EVP_MD_CTX_free(ptr);
    }
};
using UniqueMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

struct KeyRecord {
    std::array<uint8_t, 16> key_id;
    UniquePkey pubkey;
    bool is_user_mok;
};

class BootImageVerifier {
public:
    explicit BootImageVerifier(uint32_t min_anti_rollback)
        : min_anti_rollback_ver_(min_anti_rollback) {}

    bool register_key(std::array<uint8_t, 16> id, std::string_view pem_key, bool is_mok) {
        BIO* bio = BIO_new_mem_buf(pem_key.data(), static_cast<int>(pem_key.size()));
        if (!bio) return false;

        EVP_PKEY* raw_pkey = PEM_read_bio_PUBKEY(bio, nullptr, nullptr, nullptr);
        BIO_free(bio);
        if (!raw_pkey) return false;

        keys_.push_back(KeyRecord{id, UniquePkey(raw_pkey), is_mok});
        return true;
    }

    struct VerifyOutcome {
        bool is_user_mok_authorized;
        uint32_t fw_version;
        std::span<const uint8_t> payload;
    };

    [[nodiscard]] std::expected<VerifyOutcome, VerifyError>
    verify(std::span<const uint8_t> raw_image) const noexcept {
        if (raw_image.size() < sizeof(ImageHeader)) {
            return std::unexpected(VerifyError::ImageTooShort);
        }

        ImageHeader header{};
        std::memcpy(&header, raw_image.data(), sizeof(ImageHeader));

        if (header.magic != SecureBootMagic) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        if (header.firmware_version < min_anti_rollback_ver_) {
            return std::unexpected(VerifyError::RollbackDetected);
        }

        // Захист від цілочисельного переповнення розміру
        if (header.payload_size > raw_image.size() || header.signature_size > raw_image.size()) {
            return std::unexpected(VerifyError::ImageTooShort);
        }

        const size_t expected_size = sizeof(ImageHeader) + header.payload_size + header.signature_size;
        if (expected_size < sizeof(ImageHeader) || raw_image.size() < expected_size) {
            return std::unexpected(VerifyError::ImageTooShort);
        }

        const auto payload_span = raw_image.subspan(sizeof(ImageHeader), header.payload_size);
        const auto sig_span = raw_image.subspan(sizeof(ImageHeader) + header.payload_size, header.signature_size);

        // Пошук сертифіката у внутрішньому сховищі ключів
        const auto it = std::find_if(keys_.begin(), keys_.end(), [&](const KeyRecord& k) {
            return k.key_id == header.key_id;
        });

        if (it == keys_.end() || !it->pubkey) {
            return std::unexpected(VerifyError::UnknownKey);
        }

        UniqueMdCtx ctx(EVP_MD_CTX_new());
        if (!ctx) {
            return std::unexpected(VerifyError::CryptoEngineFault);
        }

        if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, it->pubkey.get()) != 1) {
            return std::unexpected(VerifyError::CryptoEngineFault);
        }

        if (EVP_DigestVerifyUpdate(ctx.get(), payload_span.data(), payload_span.size()) != 1) {
            return std::unexpected(VerifyError::CryptoEngineFault);
        }

        if (EVP_DigestVerifyFinal(ctx.get(), sig_span.data(), sig_span.size()) != 1) {
            return std::unexpected(VerifyError::SignatureInvalid);
        }

        return VerifyOutcome{
            .is_user_mok_authorized = it->is_user_mok,
            .fw_version = header.firmware_version,
            .payload = payload_span
        };
    }

private:
    uint32_t min_anti_rollback_ver_{0};
    std::vector<KeyRecord> keys_{};
};

} // namespace bootsec
```
:::

## Покроковий розбір обробки помилок та апаратних пасток

Під час проектування підсистеми валідації образів інженери стикаються з трьома критичними архітектурними пастками:

1. **Атака підміни у часі перевірки проти часу використання (TOCTOU):**
   Якщо завантажувач перевіряє образ у зовнішній динамічній пам'яті (DDR SDRAM), а потім через певний проміжок часу передає туди керування, зловмисник із прямим доступом до шини (наприклад, через DMA-пристрій на шині PCIe або мікроконтролер перехоплення пам'яті) може підмінити машинний код ядра вже після успішного завершення перевірки підпису. Для запобігання цій вразливості ядро або копіюється у захищену апаратно ізольовану пам'ять (TrustZone Secure SRAM), або перевіряється безпосередньо у внутрішній пам'яті кристала процесора перед увімкненням зовнішніх контролерів прямого доступу до пам'яті.
2. **Атаки на затримку криптографічних операцій (Side-Channel Timing Attacks):**
   Порівняння гешів чи підписів через стандартні бібліотечні функції на зразок `memcmp()` виконується за неконстантний час (функція зупиняється на першому незбіжному байті). Це дозволяє зловмиснику поступово відновлювати байти валідного підпису або автентифікаційного токена за мікросекундними коливаннями часу реакції завантажувача. Перевірка повинна виконуватися суворо з використанням функцій константного часу виконання, таких як `CRYPTO_memcmp()`.
3. **Обрізання заголовків та переповнення цілих чисел:**
   Перевірка `sizeof(ImageHeader) + payload_size + signature_size` може стати причиною цілочисельного переповнення (Integer Overflow), якщо значення розміру `payload_size` близьке до максимального беззнакового 32-бітного числа `UINT32_MAX`. Код перевірки зобов'язаний явно валідувати межі кожного блоку пам'яті до виконання арифметичних операцій додавання.
4. **Апаратна валідація відкликання ключів (Revocation Lists / DBX):**
   Якщо приватний ключ користувача або сертифікат стороннього завантажувача скомпрометовано, система повинна мати механізм додавання гешу скомпрометованого образу до чорного списку (аналог бази `dbx` у специфікації UEFI). Перевірка чорного списку повинна передувати перевірці валідності підпису: навіть якщо математичний підпис повністю коректний, наявність гешу в базі відкликаних сертифікатів має негайно блокувати запуск пристрою.
