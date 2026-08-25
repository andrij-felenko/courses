# 📋 Програмні інтерфейси HMAC: OpenSSL, криптопідсистема ядра Linux та вектори FIPS

Довідник програмних інтерфейсів стандарту HMAC (RFC 2104 / FIPS 198-1) регламентує системні контракти виклику, структури керування контекстом, правила обробки помилок та еталонні вектори валідації для OpenSSL 3.0, криптографічної підсистеми ядра Linux та середовищ високого рівня.

## 1. Інтерфейс OpenSSL 3.0+ (EVP_MAC)

Починаючи з версії OpenSSL 3.0, застарілий низькорівневий API `HMAC_CTX` замінено на уніфіковану модель провайдерів `EVP_MAC`. Вона відокремлює алгоритмічну логіку від конкретної апаратної чи програмної реалізації (провайдер за замовчуванням `default`, FIPS-провайдер `fips` або апаратний прискорювач).
Починаючи з версії OpenSSL 3.0, застарілий низькорівневий API `HMAC_CTX` та одноразову функцію `HMAC()` оголошено застарілими (deprecated). Їх замінено на уніфіковану об'єктну модель провайдерів `EVP_MAC`. Вона повністю відокремлює алгоритмічну логіку автентифікації від конкретної апаратної чи програмної реалізації (стандартний програмний провайдер `default`, сертифікований криптомодуль `fips`, застарілий `legacy` або спеціалізовані апаратні прискорювачі Intel QAT).

### Архітектура провайдерів та життєвий цикл контексту

Робота з HMAC в OpenSSL 3.0 будується навколо двох ключових структур:
1. **`EVP_MAC` (дескриптор алгоритму):** незмінний глобальний об'єкт, що представляє конкретний алгоритм у вибраному провайдері. Об'єкт є потокобезпечним (thread-safe), створюється одноразово під час запуску програми викликом `EVP_MAC_fetch()` і може спільно використовуватися всіма потоками застосунку.
2. **`EVP_MAC_CTX` (контекст обчислення):** стан конкретної операції підписування або верифікації. Контекст містить внутрішні буфери, копію нормалізованого ключа та вектори стану базової геш-функції. Контекст **не є потокобезпечним** і повинен бути індивідуальним для кожного потоку або захищеним м'ютексом.

### Оптимізація продуктивності через клонування стану (EVP_MAC_CTX_dup)

Якщо сервер обслуговує довготривалу захищену сесію з фіксованим симетричним ключем (наприклад, у веб-сокетах чи тунелях), повторна ініціалізація `EVP_MAC_init` для кожного пакета створює зайві накладні витрати на накладання масок `ipad`/`opad` та обробку першого блоку.

OpenSSL дозволяє оптимізувати цей процес:
- Головний контекст ініціалізується ключем один раз: `EVP_MAC_init(master_ctx, key, key_len, params)`.
- Для кожного вхідного або вихідного пакета створюється швидкий клон стану через `EVP_MAC_CTX_dup(master_ctx)`. Клонування просто копіює вже обчислені внутрішні вектори стану без повторного виконання побітових операцій, заощаджуючи процесорний час на кожному повідомленні.

### Сигнатури функцій OpenSSL 3.0

:::tabs
```c
#include <openssl/evp.h>
#include <openssl/params.h>

/* Отримання дескриптора алгоритму */
EVP_MAC *EVP_MAC_fetch(OSSL_LIB_CTX *libctx, const char *algorithm, const char *properties);

/* Створення та копіювання контексту */
EVP_MAC_CTX *EVP_MAC_CTX_new(EVP_MAC *mac);
EVP_MAC_CTX *EVP_MAC_CTX_dup(const EVP_MAC_CTX *src);

/* Ініціалізація ключем та параметрами OSSL_PARAM */
int EVP_MAC_init(EVP_MAC_CTX *ctx, const unsigned char *key, size_t keylen, const OSSL_PARAM params[]);

/* Потокове оновлення та фіналізація */
int EVP_MAC_update(EVP_MAC_CTX *ctx, const unsigned char *data, size_t datalen);
int EVP_MAC_final(EVP_MAC_CTX *ctx, unsigned char *out, size_t *outl, size_t outsize);

/* Звільнення пам'яті */
void EVP_MAC_CTX_free(EVP_MAC_CTX *ctx);
void EVP_MAC_free(EVP_MAC *mac);
```
```cpp
#include <openssl/evp.h>
#include <openssl/params.h>

// Сигнатури функцій OpenSSL C API залишаються ідентичними в C++
// Проте ідіоматичний C++ огортає їх у RAII-покажчики std::unique_ptr:
extern "C" {
    EVP_MAC *EVP_MAC_fetch(OSSL_LIB_CTX *libctx, const char *algorithm, const char *properties);
    EVP_MAC_CTX *EVP_MAC_CTX_new(EVP_MAC *mac);
    EVP_MAC_CTX *EVP_MAC_CTX_dup(const EVP_MAC_CTX *src);
    int EVP_MAC_init(EVP_MAC_CTX *ctx, const unsigned char *key, size_t keylen, const OSSL_PARAM params[]);
    int EVP_MAC_update(EVP_MAC_CTX *ctx, const unsigned char *data, size_t datalen);
    int EVP_MAC_final(EVP_MAC_CTX *ctx, unsigned char *out, size_t *outl, size_t outsize);
    void EVP_MAC_CTX_free(EVP_MAC_CTX *ctx);
    void EVP_MAC_free(EVP_MAC *mac);
}
```
:::

### Таблиця параметрів OSSL_PARAM для HMAC

Конфігурація обчислень виконується через статичний або динамічний масив структур `OSSL_PARAM`, що завершується елементом `OSSL_PARAM_construct_end()`:

| Назва параметра | Рядковий макрос OpenSSL | Тип даних | Призначення та допустимі значення |
| :--- | :--- | :--- | :--- |
| `"digest"` | `OSSL_MAC_PARAM_DIGEST` | `UTF8_STRING` | Ім'я базового алгоритму гешування: `"SHA256"`, `"SHA512"`, `"SHA384"`, `"SHA224"`, `"SHA3-256"`, `"SHA3-512"`. |
| `"properties"` | `OSSL_MAC_PARAM_PROPERTIES` | `UTF8_STRING` | Рядок запиту властивостей вибору провайдера: наприклад, `"?fips=yes"` або `"provider=default"`. |
| `"key"` | `OSSL_MAC_PARAM_KEY` | `OCTET_STRING` | Альтернативний спосіб передачі таємного ключа через список параметрів замість аргументу `EVP_MAC_init`. |
| `"size"` | `OSSL_MAC_PARAM_SIZE` | `UNSIGNED_INTEGER` | Режим читання (`OSSL_PARAM_get_size_t`): повертає довжину підпису в байтах (`32` для SHA-256). |
| `"block-size"` | `OSSL_MAC_PARAM_BLOCK_SIZE` | `UNSIGNED_INTEGER` | Режим читання: розмір блоку стиснення `B` базового гешу (`64` для SHA-256, `128` для SHA-512). |

### Діагностика помилок та статус повернення

1. Функції `EVP_MAC_init()`, `EVP_MAC_update()` та `EVP_MAC_final()` повертають ціле число `1` у разі успішного завершення та `0` у разі виникнення помилки.
2. При поверненні `0` детальний код збою витягується з черги потоку викликом `ERR_get_error()`, а текстовий опис формується через `ERR_error_string_n()`.
3. Типові причини збоїв:
   - Невідоме ім'я геш-функції у параметрі `OSSL_MAC_PARAM_DIGEST`.
   - Розмір буфера `outsize` у виклику `EVP_MAC_final` менший за фактичний розмір підпису `EVP_MAC_CTX_get_mac_size(ctx)`.
   - Спроба виклику `EVP_MAC_update` без попередньої успішної ініціалізації `EVP_MAC_init`.

### Робочий приклад використання OpenSSL EVP_MAC

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

int compute_openssl_hmac_sha256(
    const unsigned char *key, size_t key_len,
    const unsigned char *data, size_t data_len,
    unsigned char *out_mac, size_t *out_mac_len)
{
    EVP_MAC *mac = EVP_MAC_fetch(NULL, "HMAC", NULL);
    if (!mac) return 0;

    EVP_MAC_CTX *ctx = EVP_MAC_CTX_new(mac);
    if (!ctx) {
        EVP_MAC_free(mac);
        return 0;
    }

    char digest_name[] = "SHA256";
    OSSL_PARAM params[2];
    params[0] = OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST, digest_name, 0);
    params[1] = OSSL_PARAM_construct_end();

    int ok = 1;
    ok &= EVP_MAC_init(ctx, key, key_len, params);
    ok &= EVP_MAC_update(ctx, data, data_len);
    ok &= EVP_MAC_final(ctx, out_mac, out_mac_len, 32);

    EVP_MAC_CTX_free(ctx);
    EVP_MAC_free(mac);
    return ok;
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <stdexcept>
#include <string_view>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

namespace crypto {

class OpenSslHmac {
public:
    explicit OpenSslHmac(std::span<const uint8_t> key, std::string_view hash_name = "SHA256")
        : mac_(EVP_MAC_fetch(nullptr, "HMAC", nullptr), EVP_MAC_free),
          ctx_(nullptr, EVP_MAC_CTX_free)
    {
        if (!mac_) throw std::runtime_error("Не вдалося завантажити провайдер HMAC");
        ctx_.reset(EVP_MAC_CTX_new(mac_.get()));
        if (!ctx_) throw std::runtime_error("Не вдалося створити контекст EVP_MAC_CTX");

        std::array<OSSL_PARAM, 2> params{};
        params[0] = OSSL_PARAM_construct_utf8_string(
            OSSL_MAC_PARAM_DIGEST, const_cast<char*>(hash_name.data()), hash_name.size());
        params[1] = OSSL_PARAM_construct_end();

        if (EVP_MAC_init(ctx_.get(), key.data(), key.size(), params.data()) <= 0) {
            throw std::runtime_error("Помилка ініціалізації EVP_MAC_init");
        }
    }

    void update(std::span<const uint8_t> data) {
        if (EVP_MAC_update(ctx_.get(), data.data(), data.size()) <= 0) {
            throw std::runtime_error("Помилка оновлення EVP_MAC_update");
        }
    }

    [[nodiscard]] std::array<uint8_t, 32> finalize() {
        std::array<uint8_t, 32> out{};
        size_t written = 0;
        if (EVP_MAC_final(ctx_.get(), out.data(), &written, out.size()) <= 0) {
            throw std::runtime_error("Помилка фіналізації EVP_MAC_final");
        }
        return out;
    }

private:
    std::unique_ptr<EVP_MAC, decltype(&EVP_MAC_free)> mac_;
    std::unique_ptr<EVP_MAC_CTX, decltype(&EVP_MAC_CTX_free)> ctx_;
};

} // namespace crypto
```
:::

## 2. Інтерфейс ядра Linux (Linux Kernel Crypto API)

У ядрі Linux (зокрема в мережевому стеку IPsec XFRM, тунелях WireGuard, підсистемах автентифікації TCP-MD5/TCP-AO та модулях захисту dm-verity/dm-crypt) обчислення HMAC виконується через спеціалізовану підсистему Crypto API.

### Синхронний (shash) проти асинхронного (ahash) інтерфейсу

Ядро Linux надає два паралельні інтерфейси для роботи з HMAC:

1. **`crypto_shash` (Synchronous Hash):** виконує обчислення безпосередньо в контексті поточного потоку або переривання (Software Interrupt / SoftIRQ) на центральному процесорі. Використовується для швидкої обробки пакетів у пам'яті, коли накладні витрати на перемикання контексту перевищують час самого гешування.
2. **`crypto_ahash` (Asynchronous Hash):** оперує списками розсіювання-збирання (`struct scatterlist`) та повідомленнями завершення (Completion Callbacks). Призначений для передачі завдань на апаратні криптографічні співпроцесори (наприклад, Intel QuickAssist Technology або модулі CAAM у NXP i.MX) через черги DMA без блокування CPU.

### Правила керування пам'яттю дескриптора shash_desc

Структура `shash_desc` має змінний розмір: базовий заголовок займає фіксовану кількість байтів, а хвіст структури резервується під внутрішній стан конкретного драйвера. Розмір цього хвоста повертає макрос `crypto_shash_descsize(tfm)`:

- **Виділення на купі ядра (`GFP_KERNEL`):** застосовується у звичайних системних викликах та потоках ядра (Process Context), де дозволено блокування та очікування вивільнення сторінок пам'яті.
- **Виділення в атомарному контексті (`GFP_ATOMIC`):** обов'язкове при обробці пакетів у контексті мережевих переривань (Bottom Half / SoftIRQ), де засинання чи блокування потоку призведе до Kernel Panic.
- **Розміщення на стеку (VLA або виділений масив):** для мікрооптимізації на стеку ядра оголошують масив байтів:
  `char desc_buf[sizeof(struct shash_desc) + HASH_MAX_DESCSIZE] __aligned(__alignof__(struct shash_desc));`

### Сигнатури функцій ядра Linux

:::tabs
```c
#include <crypto/hash.h>
#include <linux/crypto.h>

/* Виділення та звільнення трансформації алгоритму */
struct crypto_shash *crypto_alloc_shash(const char *alg_name, u32 type, u32 mask);
void crypto_free_shash(struct crypto_shash *tfm);

/* Встановлення таємного ключа сесії */
int crypto_shash_setkey(struct crypto_shash *tfm, const u8 *key, unsigned int keylen);

/* Одноразове обчислення підпису над неперервним буфером */
int crypto_shash_digest(struct shash_desc *desc, const u8 *data, unsigned int len, u8 *out);

/* Потоковий API для фрагментованих пакетів (sk_buff) */
int crypto_shash_init(struct shash_desc *desc);
int crypto_shash_update(struct shash_desc *desc, const u8 *data, unsigned int len);
int crypto_shash_final(struct shash_desc *desc, u8 *out);
```
```cpp
// У просторі ядра Linux компіляція здійснюється виключно компілятором C (GCC/Clang для ядра).
// C++ у ядрі заборонений через відсутність середовища виконання, винятків та RTTI (§5).
```
:::

### Коди повернення та помилки ядра

- `0` — успішне завершення операції.
- `-ENOMEM` — недостатньо оперативної пам'яті ядра під час виділення дескриптора або контексту.
- `-EINVAL` — неприпустима довжина ключа або некоректні параметри вирівнювання буфера.
- `-ENOENT` — зазначений алгоритм (наприклад, `"hmac(sha256)"`) відсутній у таблиці реєстрації криптографічних драйверів ядра (відсутні модулі `crypto/hmac.ko` або `crypto/sha256_generic.ko`).

### Робочий модуль ядра Linux

:::tabs
```c
#include <linux/module.h>
#include <linux/crypto.h>
#include <crypto/hash.h>
#include <linux/err.h>
#include <linux/slab.h>

int kernel_compute_hmac_sha256(const u8 *key, unsigned int key_len,
                               const u8 *data, unsigned int data_len,
                               u8 *out_mac)
{
    struct crypto_shash *tfm;
    struct shash_desc *desc;
    int ret;

    /* 1. Виділення трансформації HMAC на базі SHA-256 */
    tfm = crypto_alloc_shash("hmac(sha256)", 0, 0);
    if (IS_ERR(tfm)) {
        pr_err("crypto_alloc_shash hmac(sha256) failed: %ld\n", PTR_ERR(tfm));
        return PTR_ERR(tfm);
    }

    /* 2. Встановлення секретного ключа */
    ret = crypto_shash_setkey(tfm, key, key_len);
    if (ret) {
        crypto_free_shash(tfm);
        return ret;
    }

    /* 3. Виділення пам'яті під дескриптор зі збереженням секретного стану */
    desc = kmalloc(sizeof(*desc) + crypto_shash_descsize(tfm), GFP_KERNEL);
    if (!desc) {
        crypto_free_shash(tfm);
        return -ENOMEM;
    }
    desc->tfm = tfm;

    /* 4. Одноразове обчислення дайджесту */
    ret = crypto_shash_digest(desc, data, data_len, out_mac);

    /* 5. Безпечне очищення чутливих даних дескриптора */
    kfree_sensitive(desc);
    crypto_free_shash(tfm);
    return ret;
}
```
```cpp
// Приклад виклику криптопідсистеми з простору користувача через сокети AF_ALG (C++20)
#include <array>
#include <cstdint>
#include <cstring>
#include <span>
#include <stdexcept>
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <unistd.h>

namespace crypto {

class LinuxAfAlgHmac {
public:
    explicit LinuxAfAlgHmac(std::span<const uint8_t> key) {
        sock_ = socket(AF_ALG, SOCK_SEQPACKET, 0);
        if (sock_ < 0) throw std::runtime_error("Не вдалося відкрити AF_ALG сокет");

        struct sockaddr_alg sa{};
        sa.salg_family = AF_ALG;
        std::strcpy(reinterpret_cast<char*>(sa.salg_type), "hash");
        std::strcpy(reinterpret_cast<char*>(sa.salg_name), "hmac(sha256)");

        if (bind(sock_, reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            close(sock_);
            throw std::runtime_error("Помилка bind AF_ALG hmac(sha256)");
        }
        if (setsockopt(sock_, SOL_ALG, ALG_SET_KEY, key.data(), key.size()) < 0) {
            close(sock_);
            throw std::runtime_error("Помилка встановлення ключа ALG_SET_KEY");
        }
        op_sock_ = accept(sock_, nullptr, nullptr);
        if (op_sock_ < 0) {
            close(sock_);
            throw std::runtime_error("Помилка accept AF_ALG");
        }
    }

    ~LinuxAfAlgHmac() {
        if (op_sock_ >= 0) close(op_sock_);
        if (sock_ >= 0) close(sock_);
    }

    [[nodiscard]] std::array<uint8_t, 32> sign(std::span<const uint8_t> data) {
        if (write(op_sock_, data.data(), data.size()) < 0) {
            throw std::runtime_error("Помилка запису даних у AF_ALG сокет");
        }
        std::array<uint8_t, 32> out{};
        if (read(op_sock_, out.data(), out.size()) != static_cast<ssize_t>(out.size())) {
            throw std::runtime_error("Помилка читання підпису з AF_ALG сокета");
        }
        return out;
    }

private:
    int sock_{-1};
    int op_sock_{-1};
};

} // namespace crypto
```
:::

## 3. Інтерфейси Web Crypto API та Node.js

У веб-розробці, безсерверних середовищах Node.js, Deno, Cloudflare Workers та браузерах обчислення HMAC стандартизовано у двох взаємодоповнюючих інтерфейсах.

### Web Crypto API (W3C Recommendation)

Стандарт W3C Web Cryptography API гарантує апаратну ізоляцію ключів: об'єкт `CryptoKey` зберігається у внутрішній захищеній пам'яті браузера (або апаратному модулі TPM/Secure Enclave). Якщо під час імпорту встановлено прапорець `extractable: false`, JavaScript-код застосунку принципово не може прочитати байти ключа, що унеможливлює його викрадення через XSS-атаки.

#### Покрокова робота з Web Crypto API

1. **`crypto.subtle.importKey()`:** перетворює сирий масив байтів або JWK (JSON Web Key) на непрозорий дескриптор `CryptoKey`. Обов'язково вказується алгоритм `"HMAC"`, параметри базового гешу (`hash: { name: "SHA-256" }`) та дозволені операції (`["sign", "verify"]`).
2. **`crypto.subtle.sign()`:** асинхронно обчислює HMAC над буфером `ArrayBuffer` або типізованим масивом `Uint8Array`.
3. **`crypto.subtle.verify()`:** виконує вбудоване константне порівняння отриманого підпису з очікуваним значенням безпосередньо у скомпільованому коді браузерного рушія C++, запобігаючи витоку за часом виконання.

```typescript
// Повний цикл підписування та перевірки у TypeScript
async function runWebCryptoHmacDemo(): Promise<void> {
    const rawKey = new Uint8Array([0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b,
                                  0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b,
                                  0x0b, 0x0b, 0x0b, 0x0b]);
    const message = new TextEncoder().encode("Hi There");

    // 1. Імпорт ключа в захищений криптографічний контекст
    const cryptoKey: CryptoKey = await crypto.subtle.importKey(
        "raw",
        rawKey,
        { name: "HMAC", hash: { name: "SHA-256" } },
        false, // Заборона експорту значення ключа в JS-пам'ять
        ["sign", "verify"]
    );

    // 2. Обчислення підпису
    const signatureBuffer: ArrayBuffer = await crypto.subtle.sign(
        "HMAC",
        cryptoKey,
        message
    );

    // 3. Константна перевірка автентичності
    const isValid: boolean = await crypto.subtle.verify(
        "HMAC",
        cryptoKey,
        signatureBuffer,
        message
    );

    console.log(`Статус перевірки: ${isValid ? "OK" : "FAILED"}`);
}
```

### Node.js Crypto API

У серверному середовищі Node.js модуль `node:crypto` надає прямий доступ до оптимізованих C++ обгорток OpenSSL через клас `Hmac` та функцію `crypto.timingSafeEqual`:

```javascript
import crypto from 'node:crypto';

// Одноразове підписування рядка чи бінарного буфера
function signPayload(secretKey, payloadString) {
    const hmac = crypto.createHmac('sha256', secretKey);
    hmac.update(payloadString, 'utf8');
    return hmac.digest('hex');
}

// Захищена верифікація з обов'язковою попередньою перевіркою довжини буферів
function verifyPayload(secretKey, payloadString, expectedHexSignature) {
    const computedSignature = crypto.createHmac('sha256', secretKey)
                                    .update(payloadString, 'utf8')
                                    .digest();
    const expectedSignature = Buffer.from(expectedHexSignature, 'hex');

    // Перевірка рівності довжин перед викликом timingSafeEqual:
    // timingSafeEqual викидає виняток RangeError, якщо довжини буферів не збігаються!
    if (computedSignature.length !== expectedSignature.length) {
        return false;
    }

    return crypto.timingSafeEqual(computedSignature, expectedSignature);
}
```

## 4. Еталонні вектори валідації RFC 4231 (HMAC-SHA-256)

Стандарт RFC 4231 визначає сім еталонних тестових наборів (Test Cases), які охоплюють усі граничні випадки роботи алгоритму HMAC-SHA-256: короткі ключі, точні ключі розміром 64 байти, наддовгі ключі, зрізання виходу та довгі повідомлення.

### Повна таблиця тестових векторів RFC 4231

| Набір | Довжина ключа | Ключ у шістнадцятковому форматі (Hex) | Довжина даних | Дані (ASCII / Hex) | Очікуваний вихід HMAC-SHA256 (Hex) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC 1** | 20 байтів | `0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b` | 8 байтів | `"Hi There"` | `b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7` |
| **TC 2** | 4 байти | `4a656665` (`"Jefe"`) | 28 байтів | `"what do ya want for nothing?"` | `5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843` |
| **TC 3** | 20 байтів | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` | 50 байтів | `0xdd` повторено 50 разів | `773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe` |
| **TC 4** | 25 байтів | `0102030405060708090a0b0c0d0e0f10111213141516171819` | 50 байтів | `0xcd` повторено 50 разів | `82558a389a443c0ea4cc811899b4d0fb82de6fa831816add6741a49f5c721999` |
| **TC 5** | 20 байтів | `0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c` | 20 байтів | `"Test With Truncation"` | `a3b6167473100ee06e0c796c2955552b` *(128-бітний зріз)* |
| **TC 6** | 131 байт | `0xaa` повторено 131 раз (`\|K\| > 64` байти) | 54 байти | `"Test Using Larger Than Block-Size Key - Hash Key First"` | `60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54` |
| **TC 7** | 131 байт | `0xaa` повторено 131 раз (`\|K\| > 64` байти) | 152 байти | `"This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm."` | `9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2` |

### Покроковий інженерний аналіз граничних випадків:

1. **TC 1 та TC 2 (Короткі ключі):** демонструють коректність заповнення нулями `K' = K || 0x00...0x00` для ключів, довжина яких менша за 64 байти. Тест 2 особливо показовий тим, що 4-байтний ключ `"Jefe"` доповнюється 60 нульовими байтами.
2. **TC 3 та TC 4 (Фіксовані шістнадцяткові патерни):** перевіряють відсутність проблем зі знаковими типами `char` та правильність обробки байтів із встановленим старшим бітом (`0xdd`, `0xcd`), де помилка розширення знака в C (`(int)(char)0xdd = -35`) призводить до спотворення внутрішнього дайджесту.
3. **TC 5 (Усічення тегу):** підтверджує сумісність із протоколом IPsec ESP (RFC 4868), де з 32 байтів фінального дайджесту відбираються рівно перші 16 байтів (`128` бітів).
4. **TC 6 та TC 7 (Ключі, більші за блок):** обов'язковий тест попереднього стиснення `K' = SHA256(K) || 0x00...0x00`. 131-байтний ключ із байтів `0xaa` спочатку перетворюється на 32-байтний геш `SHA256(K)`, який потім доповнюється 32 нулями до 64 байтів перед накладанням масок `ipad` та `opad`.

## 5. Порівняльна таблиця параметрів HMAC для всіх стандартних геш-функцій

Специфікація FIPS 198-1 та RFC 2104 визначають параметри нормалізації для всіх затверджених геш-функцій сімейств SHA-1, SHA-2 та SHA-3:

| Алгоритм HMAC | Розмір блоку `B` (байти / біти) | Розмір підпису `L` (байти / біти) | Рекомендований розмір ключа | Рівень стійкості (Security Strength) | Статус за FIPS 140-3 / NIST SP 800-131A |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HMAC-MD5** | 64 байти (512 біт) | 16 байтів (128 біт) | 16 байтів (128 біт) | Застарілий (≤ 64 біти) | **Заборонено** для нових застосунків |
| **HMAC-SHA1** | 64 байти (512 біт) | 20 байтів (160 біт) | 20 байтів (160 біт) | 80 бітів (застарілий) | Дозволено лише для сумісності (Legacy Use) |
| **HMAC-SHA224** | 64 байти (512 біт) | 28 байтів (224 біти) | 28 байтів (224 біти) | 112 бітів | **Затверджено** NIST |
| **HMAC-SHA256** | 64 байти (512 біт) | 32 байти (256 біт) | 32 байти (256 біт) | 128 бітів | **Затверджено** (основний галузевий стандарт) |
| **HMAC-SHA384** | 128 байтів (1024 біти) | 48 байтів (384 біти) | 48 байтів (384 біти) | 192 біти | **Затверджено** (Suite B / CNSA 1.0) |
| **HMAC-SHA512** | 128 байтів (1024 біти) | 64 байти (512 біт) | 64 байти (512 біт) | 256 бітів | **Затверджено** (максимальний рівень захисту) |
| **HMAC-SHA512/256** | 128 байтів (1024 біти) | 32 байти (256 біт) | 32 байти (256 біт) | 128 бітів | **Затверджено** (оптимізовано під 64-бітні CPU) |
| **HMAC-SHA3-256** | 136 байтів (1088 біт) | 32 байти (256 біт) | 32 байти (256 біт) | 128 бітів | **Затверджено** (губчаста основа Keccak) |
| **HMAC-SHA3-512** | 72 байти (576 біт) | 64 байти (512 біт) | 64 байти (512 біт) | 256 бітів | **Затверджено** (губчаста основа Keccak) |

## 6. Міграція з OpenSSL 1.1.1 на OpenSSL 3.0+

У старих проектах часто зустрічається застарілий інтерфейс `HMAC_CTX` бібліотеки OpenSSL 1.1.1:

:::tabs
```c
/* Застарілий підхід OpenSSL 1.1.1 (deprecated у 3.0) */
#include <openssl/hmac.h>

void legacy_openssl_hmac(const unsigned char *key, int key_len,
                         const unsigned char *data, size_t data_len,
                         unsigned char *out_mac, unsigned int *out_len)
{
    HMAC_CTX *ctx = HMAC_CTX_new();
    HMAC_Init_ex(ctx, key, key_len, EVP_sha256(), NULL);
    HMAC_Update(ctx, data, data_len);
    HMAC_Final(ctx, out_mac, out_len);
    HMAC_CTX_free(ctx);
}
```
```cpp
// Застарілий підхід OpenSSL 1.1.1 з використанням RAII-обгортки (deprecated у 3.0)
#include <memory>
#include <span>
#include <array>
#include <openssl/hmac.h>

namespace legacy {

[[nodiscard]] std::array<uint8_t, 32> hmac_sha256(
    std::span<const uint8_t> key,
    std::span<const uint8_t> data)
{
    std::unique_ptr<HMAC_CTX, decltype(&HMAC_CTX_free)> ctx(HMAC_CTX_new(), HMAC_CTX_free);
    if (!ctx) return {};

    HMAC_Init_ex(ctx.get(), key.data(), static_cast<int>(key.size()), EVP_sha256(), nullptr);
    HMAC_Update(ctx.get(), data.data(), data.size());
    std::array<uint8_t, 32> out{};
    unsigned int len = 0;
    HMAC_Final(ctx.get(), out.data(), &len);
    return out;
}

} // namespace legacy
```
:::

### Чому OpenSSL відмовився від HMAC_CTX:

1. **Жорстке прив'язування до EVP_MD:** Старий API вимагав прямої передачі структури `EVP_sha256()`, що унеможливлювало використання алгоритмів, реалізованих сторонніми апаратними провайдерами без реєстрації у глобальній таблиці методів гешування.
2. **Сертифікація FIPS 140-3:** Новий інтерфейс `EVP_MAC` дозволяє суворо контролювати криптографічний периметр: якщо програма завантажує FIPS-провайдер (`EVP_MAC_fetch(NULL, "HMAC", "fips=yes")`), бібліотека автоматично блокує використання несертифікованих ключів або слабких геш-функцій (наприклад, MD5) на рівні провайдера.
3. **Уніфікація з іншими MAC:** Інтерфейс `EVP_MAC` є єдиним для HMAC, CMAC (на базі AES), GMAC, Poly1305, KMAC та SIPHASH, що дозволяє змінювати тип коду автентичності у конфігурації без зміни коду виклику.

## 7. Апаратні модулі безпеки та стандарт PKCS#11

У банківських системах, платежах за стандартом PCI DSS та захищених мережевих маршрутизаторах таємні ключі HMAC зберігаються в апаратних модулях безпеки (HSM, Hardware Security Module) або смарт-картах. Доступ до них здійснюється через стандартний інтерфейс PKCS#11 (Cryptoki API).

### Механізми PKCS#11 для HMAC

У стандарті PKCS#11 v2.40 та v3.0 визначено такі константи механізмів:
- `CKM_SHA256_HMAC`: повне обчислення HMAC-SHA256 усередині кремнію HSM.
- `CKM_SHA256_HMAC_GENERAL`: обчислення HMAC із можливістю конфігурації довжини усіченого тегу через параметр `CK_MAC_GENERAL_PARAMS`.
- `CKM_SHA512_HMAC`: обчислення HMAC-SHA512.

### Атрибути захищеного ключа PKCS#11:

Коли симетричний ключ HMAC створюється всередині апаратного токена, йому присвоюються строгі прапорці безпеки:
- `CKA_CLASS = CKO_SECRET_KEY`: тип об'єкта — симетричний ключ.
- `CKA_KEY_TYPE = CKK_GENERIC_SECRET` або `CKK_SHA256_HMAC`: алгоритмічний тип ключа.
- `CKA_SIGN = CK_TRUE` та `CKA_VERIFY = CK_TRUE`: дозвіл використання для генерації та перевірки підписів.
- `CKA_EXTRACTABLE = CK_FALSE`: **критичний прапорець**. Забороняє будь-яке зчитування сирих байтів ключа за межі чипа HSM.
- `CKA_SENSITIVE = CK_TRUE`: ключ зберігається в зашифрованому вигляді у захищеній пам'яті токена.

### Контракт виклику PKCS#11 у C та C++

:::tabs
```c
#include <stdio.h>
#include <string.h>

/* Типізовані структури PKCS#11 (Cryptoki) */
typedef unsigned long CK_RV;
typedef unsigned long CK_SESSION_HANDLE;
typedef unsigned long CK_OBJECT_HANDLE;
typedef unsigned long CK_MECHANISM_TYPE;

#define CKR_OK 0x00000000
#define CKM_SHA256_HMAC 0x00000251

typedef struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;
    void *pParameter;
    unsigned long ulParameterLen;
} CK_MECHANISM;

/* Сигнатури стандартних функцій Cryptoki */
CK_RV C_SignInit(CK_SESSION_HANDLE hSession, CK_MECHANISM *pMechanism, CK_OBJECT_HANDLE hKey);
CK_RV C_Sign(CK_SESSION_HANDLE hSession, unsigned char *pData, unsigned long ulDataLen,
             unsigned char *pSignature, unsigned long *pulSignatureLen);

/* Приклад використання апаратного HMAC */
int hsm_sign_message(CK_SESSION_HANDLE session, CK_OBJECT_HANDLE hmac_key,
                     const unsigned char *data, unsigned long data_len,
                     unsigned char *signature, unsigned long *sig_len)
{
    CK_MECHANISM mech = { CKM_SHA256_HMAC, NULL, 0 };
    CK_RV rv;

    /* 1. Ініціалізація операції підпису на захищеному токені */
    rv = C_SignInit(session, &mech, hmac_key);
    if (rv != CKR_OK) return 0;

    /* 2. Обчислення підпису всередині HSM (ключ не потрапляє в RAM хоста) */
    rv = C_Sign(session, (unsigned char *)data, data_len, signature, sig_len);
    return (rv == CKR_OK);
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <stdexcept>

namespace hsm {

using SessionHandle = unsigned long;
using ObjectHandle = unsigned long;
using ReturnValue = unsigned long;

constexpr ReturnValue CkrOk = 0;
constexpr unsigned long CkmSha256Hmac = 0x00000251;

struct Mechanism {
    unsigned long mechanism;
    void* parameter;
    unsigned long parameter_len;
};

extern "C" {
    ReturnValue C_SignInit(SessionHandle hSession, Mechanism* pMechanism, ObjectHandle hKey);
    ReturnValue C_Sign(SessionHandle hSession, unsigned char* pData, unsigned long ulDataLen,
                       unsigned char* pSignature, unsigned long* pulSignatureLen);
}

class HsmHmacSigner {
public:
    HsmHmacSigner(SessionHandle session, ObjectHandle key) noexcept
        : session_(session), key_(key) {}

    [[nodiscard]] std::array<uint8_t, 32> sign(std::span<const uint8_t> data) const {
        Mechanism mech{ CkmSha256Hmac, nullptr, 0 };
        if (C_SignInit(session_, &mech, key_) != CkrOk) {
            throw std::runtime_error("Помилка C_SignInit у HSM");
        }

        std::array<uint8_t, 32> signature{};
        unsigned long sig_len = signature.size();
        if (C_Sign(session_, const_cast<unsigned char*>(data.data()), data.size(),
                   signature.data(), &sig_len) != CkrOk) {
            throw std::runtime_error("Помилка C_Sign у HSM");
        }
        return signature;
    }

private:
    SessionHandle session_;
    ObjectHandle key_;
};

} // namespace hsm
```
:::

## 8. Інтерфейси у сучасних системних мовах: Go та Rust

Окрім C/C++, у сучасній хмарній та мережевій інфраструктурі провідну роль відіграють мови Go та Rust. Обидві мають стандартні захищені примітиви для HMAC.

### Інтерфейс мови Go (пакет `crypto/hmac`)

Стандартна бібліотека Go реалізує інтерфейс `hash.Hash`:

```go
package main

import (
    "crypto/hmac"
    "crypto/sha256"
)

// Генерація HMAC-SHA256 підпису
func Sign(key, data []byte) []byte {
    mac := hmac.New(sha256.New, key)
    mac.Write(data)
    return mac.Sum(nil)
}

// Захищена верифікація через hmac.Equal (вбудований константний час)
func Verify(key, data, expectedMAC []byte) bool {
    actualMAC := Sign(key, data)
    return hmac.Equal(actualMAC, expectedMAC)
}
```

#### Чому `hmac.Equal` обов'язковий:
Функція `hmac.Equal(mac1, mac2)` у стандартній бібліотеці Go виконує побайтове `XOR`-порівняння через `crypto/subtle.ConstantTimeCompare` і додатково перевіряє рівність довжин без витоку інформації через часові розгалуження. Використання оператора `bytes.Equal(mac1, mac2)` у Go є грубою вразливістю, оскільки він реалізований на базі інструкцій SIMD із раннім виходом.

### Інтерфейс мови Rust (крейти `hmac` та `subtle`)

У Rust ідіоматична робота з HMAC базується на системі типажів `crypto-bigint` та `digest`:

```rust
use hmac::{Hmac, Mac};
use sha2.Sha256;
use subtle::ConstantTimeEq;

type HmacSha256 = Hmac<Sha256>;

fn sign(key: &[u8], data: &[u8]) -> [u8; 32] {
    let mut mac = HmacSha256::new_from_slice(key)
        .expect("HMAC може приймати ключ будь-якої довжини");
    mac.update(data);
    mac.finalize().into_bytes().into()
}

fn verify(key: &[u8], data: &[u8], expected_mac: &[u8]) -> bool {
    let mut mac = HmacSha256::new_from_slice(key)
        .expect("HMAC може приймати ключ будь-якої довжини");
    mac.update(data);
    // Метод verify_slice використовує ConstantTimeEq
    mac.verify_slice(expected_mac).is_ok()
}
```

Крейт `subtle` гарантує через асемблерні чорні скриньки (`black_box`), що компілятор `rustc` / LLVM не оптимізує цикл перевірки підпису у векторний код із достроковим перериванням.

## 9. Захист пам'яті ключів: блокування сторінок у RAM (mlock)

На рівні операційної системи тривале зберігання симетричних ключів у процесах користувача несе ризик їх скидання на диск у файл підкачування (Swap / Paging File) під час дефіциту оперативної пам'яті.

Для запобігання цьому системні демони автентифікації застосовують системний виклик `mlock()`:
- `mlock(key_ptr, key_len)`: блокує сторінку пам'яті з ключем у фізичній RAM, забороняючи ядру скидати її на swap-розділ.
## 10. Стандарти авторизації на базі HMAC: AWS SigV4 та HTTP Message Signatures (RFC 9421)

Окрім класичних симетричних тунелів, HMAC є основою промислових протоколів авторизації API-запитів.

### Каскадна схема AWS Signature Version 4 (SigV4)

Хмарна інфраструктура Amazon Web Services використовує багаторівневу деривацію ключів на базі HMAC-SHA256 для захисту кожного HTTP-запиту:

1. **Крок 1 (DateKey):** `kDate = HMAC-SHA256("AWS4" + SecretAccessKey, "20260818")`
2. **Крок 2 (RegionKey):** `kRegion = HMAC-SHA256(kDate, "eu-central-1")`
3. **Крок 3 (ServiceKey):** `kService = HMAC-SHA256(kRegion, "s3")`
4. **Крок 4 (SigningKey):** `kSigning = HMAC-SHA256(kService, "aws4_request")`
5. **Крок 5 (Signature):** `Signature = Hex(HMAC-SHA256(kSigning, StringToSign))`

Така архітектура гарантує принцип мінімальних привілеїв: навіть якщо ключ підпису конкретного дня `kSigning` скомпрометовано, він дійсний лише протягом 24 годин, виключно в одному регіоні та для одного сервісу, не розкриваючи головного секрету `SecretAccessKey`.

### Стандарт HTTP Message Signatures (RFC 9421)

Сучасний стандарт IETF RFC 9421 регламентує використання HMAC через структуровані HTTP-заголовки:
- Заголовок `Signature-Input`: містить перелік підписаних компонентів (`@method`, `@path`, `@authority`, `content-digest`), мітку часу `created` та ідентифікатор ключа `keyid`.
- Заголовок `Signature`: містить бінарний підпис HMAC у форматі `Base64` або `Base64URL`.
- Заголовок `Content-Digest`: містить `sha-256=:...:` для контролю цілісності тіла запиту перед підписуванням заголовків.

Сервер-отримувач відтворює канонічний рядок підпису з отриманих HTTP-заголовків, проводить десеріалізацію параметрів та перевіряє код автентичності у константному часі. У разі неспівпадіння хоча б одного біта або порушення часового вікна запит негайно відхиляється з кодом помилки `401 Unauthorized`.

