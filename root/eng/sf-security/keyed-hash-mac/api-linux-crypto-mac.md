# 📋 Інтерфейси обчислення та верифікації MAC в OpenSSL і ядрі Linux

Програмні інтерфейси для обчислення та перевірки кодів автентичності повідомлень (MAC) абстрагують внутрішню математику криптографічних примітивів за уніфікованим контрактом життєвого циклу. У системному програмуванні під Linux робота з MAC здійснюється на трьох рівнях: у просторі користувача через об'єктну модель `EVP_MAC` бібліотеки OpenSSL 3.x, на рівні системних викликів через сокети `AF_ALG`, та безпосередньо в ядрі через підсистему Linux Kernel Crypto API (`crypto_shash` та `crypto_ahash`).

---

## 1. Архітектурна модель OpenSSL 3.x EVP_MAC

Починаючи з випуску OpenSSL 3.0, монолітні та розрізнені інтерфейси минулих версій (такі як `HMAC_Init_ex`, `CMAC_Init`) було повністю виведено з експлуатації (deprecated). Їх замінила компонентна архітектура провайдерів (Providers Architecture), де всі алгоритми автентифікації функціонують через єдиний абстрактний тип `EVP_MAC`.

### Життєвий цикл та керування контекстом

Робота з `EVP_MAC` побудована на чіткому розділенні незмінного опису алгоритму та мутабельного стану сесії:
1. **Вибір та завантаження алгоритму (`EVP_MAC_fetch`):** Об'єкт `EVP_MAC` є фабрикою алгоритму, завантаженою з конкретного провайдера (Default, FIPS або Legacy). Цей об'єкт є потокобезпечним (thread-safe), не зберігає секретних ключів і може повторно використовуватися всіма робочими потоками програми паралельно.
2. **Виділення контексту сесії (`EVP_MAC_CTX_new`):** Контекст `EVP_MAC_CTX` містить внутрішній робочий стан: розгорнуті ключові розклади, попередньо обчислені маски `ipad`/`opad` для HMAC, або підключі `K1`/`K2` для CMAC. Контекст не є потокобезпечним і повинен належати одному конкретному потоку обробки.
3. **Ініціалізація та параметризація (`EVP_MAC_init`):** Приймає таємний ключ та динамічний масив конфігураційних параметрів `OSSL_PARAM`. У цей момент виконується первинне розгортання ключа.
4. **Потокова передача фрагментів (`EVP_MAC_update`):** Дозволяє передавати великі потоки даних частинами довільного розміру без необхідності тримати весь масив повідомлення у пам'яті.
5. **Отримання дайджесту (`EVP_MAC_final`):** Обчислює фінальний тег автентичності та повертає фактичну кількість записаних байтів.
6. **Повторне використання та оптимізація швидкодії:** Якщо потрібно автентифікувати серію повідомлень під одним і тим самим ключем, повторний виклик `EVP_MAC_init(ctx, NULL, 0, NULL)` скидає стан гешування до початкового без повторного витрачання ресурсів процесора на нормалізацію ключа та розгортання масок.
7. **Клонування стану (`EVP_MAC_CTX_dup`):** Дозволяє створити копію проміжного стану обчислення. Це особливо корисно у протоколах, де велика група повідомлень має спільний фіксований заголовок: заголовок обробляється один раз, стан копіюється, і для кожного повідомлення дораховується лише унікальне тіло.

### Таблиця функцій життєвого циклу EVP_MAC

| Функція | Призначення та сигнатура | Особливості виконання |
|---|---|---|
| `EVP_MAC_fetch` | `EVP_MAC *EVP_MAC_fetch(OSSL_LIB_CTX *ctx, const char *algo, const char *propq)` | Динамічно завантажує реалізацію алгоритму (`"HMAC"`, `"CMAC"`, `"Poly1305"`, `"KMAC128"`, `"KMAC256"`, `"GMAC"`) із підключеного провайдера. |
| `EVP_MAC_CTX_new` | `EVP_MAC_CTX *EVP_MAC_CTX_new(EVP_MAC *mac)` | Виділяє пам'ять під непрозору структуру контексту стану. Зберігає копії підключів, масок та вектори регістрів. |
| `EVP_MAC_init` | `int EVP_MAC_init(EVP_MAC_CTX *ctx, const unsigned char *key, size_t keylen, const OSSL_PARAM params[])` | Фіксує секретний ключ і конфігураційні параметри. Повертає `1` при успіху та `0` при помилці конфігурації. |
| `EVP_MAC_update` | `int EVP_MAC_update(EVP_MAC_CTX *ctx, const unsigned char *data, size_t datalen)` | Передає чергову порцію вхідного повідомлення. Може викликатися багаторазово для потокової обробки даних. |
| `EVP_MAC_final` | `int EVP_MAC_final(EVP_MAC_CTX *ctx, unsigned char *out, size_t *outl, size_t outsize)` | Завершує обчислення, накладає кінцеві маски і записує тег. Записує фактичну довжину тегу в `*outl`. |
| `EVP_MAC_CTX_dup` | `EVP_MAC_CTX *EVP_MAC_CTX_dup(const EVP_MAC_CTX *src)` | Створює глибоку копію контексту зі збереженням проміжного стану гешування для оптимізації спільних префіксів. |
| `EVP_MAC_CTX_free` | `void EVP_MAC_CTX_free(EVP_MAC_CTX *ctx)` | Безпечно затирає секретні ключі в оперативній пам'яті (виклик `OPENSSL_cleanse`) та звільняє виділені ресурси. |

### Параметризація алгоритмів через OSSL_PARAM

Конфігураційні параметри передаються як самоописові кортежі ключ-значення, де останнім елементом масиву обов'язково є термінатор `OSSL_PARAM_construct_end()`:

| Алгоритм MAC | Обов'язкові параметри (`OSSL_PARAM`) | Допустимі значення та інженерний опис |
|---|---|---|
| **HMAC** | `OSSL_MAC_PARAM_DIGEST` (`"digest"`) | Рядок із назвою базової геш-функції: `"SHA256"`, `"SHA512"`, `"SHA3-256"`, `"BLAKE2b-512"`. |
| **CMAC** | `OSSL_MAC_PARAM_CIPHER` (`"cipher"`) | Рядок із назвою симетричного блокового шифру: `"AES-128-CBC"`, `"AES-256-CBC"`, `"ARIA-128-CBC"`. |
| **Poly1305** | Не вимагає додаткових параметрів | Ключ повинен мати довжину рівно 32 байти (перші 16 байтів — `r`, наступні 16 байтів — `s`). |
| **KMAC128 / KMAC256** | `OSSL_MAC_PARAM_SIZE` (`"size"`), `OSSL_MAC_PARAM_CUSTOM` (`"custom"`) | Довжина вихідного тегу в байтах (XOF-властивість) та рядок контекстної кастомізації протоколу. |
| **GMAC** | `OSSL_MAC_PARAM_CIPHER` (`"cipher"`), `OSSL_MAC_PARAM_IV` (`"iv"`) | Назва шифру `"AES-128-GCM"` та обов'язковий унікальний вектор ініціалізації (12 байтів). |

### Приклад обчислення HMAC-SHA256 через OpenSSL 3.x

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

int compute_hmac_sha256(const unsigned char *key, size_t key_len,
                        const unsigned char *msg, size_t msg_len,
                        unsigned char *out_tag, size_t *out_tag_len) {
    EVP_MAC *mac = NULL;
    EVP_MAC_CTX *ctx = NULL;
    int success = 0;

    /* 1. Завантаження провайдера алгоритму HMAC */
    mac = EVP_MAC_fetch(NULL, "HMAC", NULL);
    if (!mac) goto cleanup;

    /* 2. Створення робочого контексту */
    ctx = EVP_MAC_CTX_new(mac);
    if (!ctx) goto cleanup;

    /* 3. Налаштування параметрів: вибір геш-функції SHA-256 */
    OSSL_PARAM params[2];
    params[0] = OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST, "SHA256", 0);
    params[1] = OSSL_PARAM_construct_end();

    /* 4. Ініціалізація контексту ключем та параметрами */
    if (!EVP_MAC_init(ctx, key, key_len, params)) goto cleanup;

    /* 5. Потокова передача даних повідомлення */
    if (!EVP_MAC_update(ctx, msg, msg_len)) goto cleanup;

    /* 6. Фіналізація та отримання 32-байтного тегу */
    if (!EVP_MAC_final(ctx, out_tag, out_tag_len, 32)) goto cleanup;

    success = 1;

cleanup:
    if (ctx) EVP_MAC_CTX_free(ctx);
    if (mac) EVP_MAC_free(mac);
    return success;
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

namespace crypto {

struct EvpMacDeleter {
    void operator()(EVP_MAC* mac) const noexcept {
        if (mac) EVP_MAC_free(mac);
    }
};

struct EvpMacCtxDeleter {
    void operator()(EVP_MAC_CTX* ctx) const noexcept {
        if (ctx) EVP_MAC_CTX_free(ctx);
    }
};

using ScopedMac = std::unique_ptr<EVP_MAC, EvpMacDeleter>;
using ScopedMacCtx = std::unique_ptr<EVP_MAC_CTX, EvpMacCtxDeleter>;

enum class MacError {
    AlgorithmFetchFailed,
    ContextAllocationFailed,
    InitializationFailed,
    UpdateFailed,
    FinalizationFailed
};

[[nodiscard]] std::expected<std::array<uint8_t, 32>, MacError>
compute_hmac_sha256(std::span<const uint8_t> key,
                    std::span<const uint8_t> message) noexcept {
    ScopedMac mac(EVP_MAC_fetch(nullptr, "HMAC", nullptr));
    if (!mac) {
        return std::unexpected(MacError::AlgorithmFetchFailed);
    }

    ScopedMacCtx ctx(EVP_MAC_CTX_new(mac.get()));
    if (!ctx) {
        return std::unexpected(MacError::ContextAllocationFailed);
    }

    std::array<OSSL_PARAM, 2> params = {
        OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST,
                                         const_cast<char*>("SHA256"), 0),
        OSSL_PARAM_construct_end()
    };

    if (EVP_MAC_init(ctx.get(), key.data(), key.size(), params.data()) != 1) {
        return std::unexpected(MacError::InitializationFailed);
    }

    if (EVP_MAC_update(ctx.get(), message.data(), message.size()) != 1) {
        return std::unexpected(MacError::UpdateFailed);
    }

    std::array<uint8_t, 32> tag{};
    size_t tag_len = 0;
    if (EVP_MAC_final(ctx.get(), tag.data(), &tag_len, tag.size()) != 1) {
        return std::unexpected(MacError::FinalizationFailed);
    }

    return tag;
}

} // namespace crypto
```
:::

---

## 2. Linux Kernel Crypto API (Простір ядра)

У ядрі Linux обчислення кодів автентичності інтегровано безпосередньо в мережевий стек (IPsec, WireGuard), дискові підсистеми цілісності (`dm-verity`, `fs-verity`, `IMA/EVM`) та криптографічні драйвери файлових систем. Підсистема ядра розділена на дві взаємодоповнюючі моделі виконання:

1. **Синхронний інтерфейс `crypto_shash` (Synchronous Hash):**
   * Обчислення виконується послідовно у контексті викликаючого потоку процесора або обробника переривань (softirq).
   * Функції не містять точок зупинки (sleep points) і є безпечними для використання всередині критичних секцій під блокуваннями типу `spinlock` або `rcu_read_lock`.
   * Призначений для швидких програмних реалізацій на базі векторних інструкцій ЦП (AVX2, ARM NEON).

2. **Асинхронний інтерфейс `crypto_ahash` (Asynchronous Hash):**
   * Працює через механізм списків розсіювання-збирання `struct scatterlist`.
   * Дозволяє передавати сторінки фізичної пам'яті безпосередньо контролерам апаратного прискорення через шину DMA.
   * Викликаючий потік передає дескриптор `struct ahash_request` разом із функцією зворотного виклику (completion callback) і переходить у стан очікування або перемикається на інші системні задачі, доки апаратний чип завершує обчислення тегу.

### Керування дескрипторами та динамічними розмірами

Оскільки кожен криптографічний алгоритм ядра має власний розмір внутрішнього стану, структура `struct shash_desc` вимагає динамічного розрахунку розміру пам'яті:

```
Загальний розмір пам'яті = sizeof(struct shash_desc) + crypto_shash_descsize(tfm)
```

Для короткоживучих операцій виділення пам'яті через `kmalloc()` є небажаним через накладні витрати на роботу алокатора слябів (SLUB). Ядро надає безпечний макрос `SHASH_DESC_ON_STACK(desc, tfm)`, який резервує необхідний масив байтів безпосередньо у поточному фреймі стека ядра.

### Реалізація CMAC-AES у модулі ядра Linux

Наведений модуль демонструє повний інженерний цикл: отримання дескриптора трансформації `cmac(aes)`, фіксацію ключа (під час якої драйвер ядра виконує піднесення до квадрата в `GF(2¹²⁸)` для генерації підключів `K1` та `K2`), та однопрохідне обчислення тегу через `crypto_shash_digest`.

```c
#include <linux/module.h>
#include <linux/crypto.h>
#include <crypto/hash.h>
#include <linux/err.h>
#include <linux/slab.h>

int kernel_compute_cmac_aes(const u8 *key, unsigned int key_len,
                            const u8 *data, unsigned int data_len,
                            u8 *out_tag) {
    struct crypto_shash *tfm;
    struct shash_desc *desc;
    int desc_size;
    int ret;

    /* 1. Виділення дескриптора трансформації алгоритму CMAC на базі AES */
    tfm = crypto_alloc_shash("cmac(aes)", 0, 0);
    if (IS_ERR(tfm)) {
        pr_err("crypto_alloc_shash failed: %ld\n", PTR_ERR(tfm));
        return PTR_ERR(tfm);
    }

    /* 2. Прив'язка ключа (драйвер генерує внутрішні підключі K1 та K2) */
    ret = crypto_shash_setkey(tfm, key, key_len);
    if (ret) {
        pr_err("crypto_shash_setkey failed: %d\n", ret);
        goto free_tfm;
    }

    /* 3. Виділення пам'яті під дескриптор запиту з урахуванням descsize */
    desc_size = sizeof(struct shash_desc) + crypto_shash_descsize(tfm);
    desc = kmalloc(desc_size, GFP_KERNEL);
    if (!desc) {
        ret = -ENOMEM;
        goto free_tfm;
    }
    desc->tfm = tfm;

    /* 4. Однопрохідне обчислення тегу (ініціалізація, оновлення, фіналізація) */
    ret = crypto_shash_digest(desc, data, data_len, out_tag);
    if (ret) {
        pr_err("crypto_shash_digest failed: %d\n", ret);
    }

    /* 5. Безпечне очищення чутливих структур даних перед звільненням */
    kfree_sensitive(desc);

free_tfm:
    crypto_free_shash(tfm);
    return ret;
}

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("CMAC-AES Kernel Crypto API example");
```

---

## 3. Інтерфейс системних сокетів AF_ALG

Підсистема `AF_ALG` (Address Family Algorithm) надає процесам простору користувача уніфікований доступ до апаратних та програмних драйверів ядра через стандартні сокети Berkeley. Це усуває потребу у встановленні важких користувацьких криптографічних бібліотек на обмежених вбудованих Linux-пристроях (Embedded Routers, IoT-гейтвеї).

### Послідовність системних викликів AF_ALG

Процес обчислення коду автентичності через сокетний інтерфейс складається з таких обов'язкових кроків:
1. **Створення сокета:** відкриття дескриптора сімейства `AF_ALG` викликом `socket(AF_ALG, SOCK_SEQPACKET, 0)`.
2. **Конфігурація типу алгоритму:** заповнення структури `struct sockaddr_alg` із типом `"hash"` та іменем `"hmac(sha256)"` і прив'язка через `bind()`.
3. **Встановлення таємного ключа:** передача ключа ядру через сокетну опцію `setsockopt(tfm_fd, SOL_ALG, ALG_SET_KEY, key, key_len)`.
4. **Створення операційного дескриптора:** виклик `accept(tfm_fd, NULL, 0)` повертає новий файловий дескриптор робочої сесії.
5. **Передача повідомлення та отримання дайджесту:** запис даних через `write()` (або нуль-копіювальний `splice()` для передачі сторінок файлового кешу без копіювання в пам'ять користувача) та зчитування обчисленого тегу викликом `read()`.

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

int af_alg_hmac_sha256(const unsigned char *key, size_t key_len,
                       const unsigned char *msg, size_t msg_len,
                       unsigned char *out_tag, size_t out_tag_len) {
    int tfm_fd = -1;
    int op_fd = -1;
    int success = 0;

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type   = "hash",
        .salg_name   = "hmac(sha256)"
    };

    tfm_fd = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (tfm_fd < 0) return 0;

    if (bind(tfm_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) goto out;
    if (setsockopt(tfm_fd, SOL_ALG, ALG_SET_KEY, key, key_len) < 0) goto out;

    op_fd = accept(tfm_fd, NULL, 0);
    if (op_fd < 0) goto out;

    if (write(op_fd, msg, msg_len) != (ssize_t)msg_len) goto out;
    if (read(op_fd, out_tag, out_tag_len) != (ssize_t)out_tag_len) goto out;

    success = 1;

out:
    if (op_fd >= 0) close(op_fd);
    if (tfm_fd >= 0) close(tfm_fd);
    return success;
}
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <expected>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

namespace sys_crypto {

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() noexcept { if (fd_ >= 0) ::close(fd_); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

enum class AlgError {
    SocketCreationFailed,
    BindFailed,
    SetKeyFailed,
    AcceptFailed,
    WriteFailed,
    ReadFailed
};

[[nodiscard]] std::expected<std::array<uint8_t, 32>, AlgError>
af_alg_hmac_sha256(std::span<const uint8_t> key,
                   std::span<const uint8_t> message) noexcept {
    ScopedFd tfm_fd(::socket(AF_ALG, SOCK_SEQPACKET, 0));
    if (!tfm_fd.valid()) {
        return std::unexpected(AlgError::SocketCreationFailed);
    }

    sockaddr_alg sa{};
    sa.salg_family = AF_ALG;
    __builtin_strncpy(reinterpret_cast<char*>(sa.salg_type), "hash", sizeof(sa.salg_type));
    __builtin_strncpy(reinterpret_cast<char*>(sa.salg_name), "hmac(sha256)", sizeof(sa.salg_name));

    if (::bind(tfm_fd.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected(AlgError::BindFailed);
    }

    if (::setsockopt(tfm_fd.get(), SOL_ALG, ALG_SET_KEY, key.data(), key.size()) < 0) {
        return std::unexpected(AlgError::SetKeyFailed);
    }

    ScopedFd op_fd(::accept(tfm_fd.get(), nullptr, nullptr));
    if (!op_fd.valid()) {
        return std::unexpected(AlgError::AcceptFailed);
    }

    if (::write(op_fd.get(), message.data(), message.size()) != static_cast<ssize_t>(message.size())) {
        return std::unexpected(AlgError::WriteFailed);
    }

    std::array<uint8_t, 32> tag{};
    if (::read(op_fd.get(), tag.data(), tag.size()) != static_cast<ssize_t>(tag.size())) {
        return std::unexpected(AlgError::ReadFailed);
    }

    return tag;
}

} // namespace sys_crypto
```
:::

### Діагностика через віртуальну файлову систему /proc/crypto

Диспетчер криптографічного ядра обирає конкретний драйвер на основі числового пріоритету, зареєстрованого в системі:

```bash
cat /proc/crypto | grep -A 10 "name.*hmac(sha256)"
```

У виводі утиліти відображаються атрибути активних рушіїв:
* `priority: 100` — базовий неоптимізований драйвер мовою C (`hmac(sha256-generic)`).
* `priority: 300` — асемблерна векторна оптимізація AVX-512 / SHA-NI (`hmac-sha256-ni`).
* `priority: 1000+` — виділений апаратний криптопроцесор безпеки (SoC Crypto Accelerator / TPM / CAAM).

Ядро завжди автоматично вибирає драйвер із найвищим пріоритетом, забезпечуючи максимальну швидкодію обчислення MAC без потреби внесення змін до вихідного коду прикладних програм.
