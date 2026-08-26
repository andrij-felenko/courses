# 📋 Інтерфейс AES-XTS у підсистемах dm-crypt та AF_ALG ядра Linux

Для роботи з режимом AES-XTS на рівні операційної системи Linux передбачено два основні програмні механізми: підсистема блокового перетворення `dm-crypt` (Device Mapper Crypt) для прозорого шифрування дискових розділів та інтерфейс сокетів простору користувача `AF_ALG` (User-space Crypto API) для виконання криптографічних операцій з використанням апаратно оптимізованих драйверів ядра.

Нижче наведено структурований довідник параметрів, системних викликів, внутрішніх структур даних ядра та практичних прикладів налаштування шифрування дисків.

### 1. Формат конфігурації цілі dm-crypt у Device Mapper

Створення шифрованого блокового пристрою здійснюється через утиліту `dmsetup` або бібліотеку `libcryptsetup` шляхом завантаження рядка таблиці зіставлення (mapping table). Таблиця зіставлення описує зв'язок між віртуальним розшифрованим пристроєм `/dev/mapper/<name>` та базовим фізичним носієм.

```
<start_sector> <size_sectors> crypt <cipher_spec> <key> <iv_offset> <device_path> <offset_sectors> [<num_optional_args> <optional_args>...]
```

#### Параметри рядка таблиці dm-crypt

| Поле | Тип | Опис | Приклад значення |
|---|---|---|---|
| `start_sector` | Integer | Початковий логічний сектор віртуального блокового пристрою | `0` |
| `size_sectors` | Integer | Загальна кількість 512-байтних секторів пристрою | `20971520` (10 ГіБ) |
| `target_type` | String | Тип цілі підсистеми Device Mapper | `crypt` |
| `cipher_spec` | String | Специфікація шифру, режиму функціонування та генератора IV | `aes-xts-plain64` |
| `key` | Hex-string / Keyring | Ключ шифрування у шістнадцятковому вигляді або посилання на зв'язку ключів ядра | `0123456789abcdef...` (128 hex-символів для AES-256) |
| `iv_offset` | Integer | Зсув, що додається до номера сектора під час генерації початкового твіка | `0` |
| `device_path` | String | Абсолютний шлях до фізичного блокового пристрою або розділу | `/dev/nvme0n1p3` |
| `offset_sectors` | Integer | Зсув початку шифрованих даних на фізичному накопичувачі | `32768` (16 МіБ заголовок LUKS2) |
| `num_optional_args` | Integer | Кількість додаткових прапорців конфігурації цілі | `2` |
| `optional_args` | String list | Опції продуктивності та безпеки: `sector_size:<bytes>`, `allow_discards`, `same_cpu_crypt` | `sector_size:4096 allow_discards` |

#### Специфікації шифру `cipher_spec` для режиму XTS

Специфікація шифру в `dm-crypt` має трискладовий формат `алгоритм-режим-генератор_iv`:

* `aes-xts-plain64` — сучасний стандарт за замовчуванням у форматі LUKS2. 64-бітний номер логічного сектора накопичувача (LBA) записується як 128-бітне число в порядку Little-Endian із доповненням старших 8 байтів нулями. Підтримує дискові томи до 8 зеттабайтів (`2⁶⁴` секторів).
* `aes-xts-plain` — застарілий 32-бітний варіант генератора LBA. Обмежує максимальний розмір зашифрованого розділу 2 тебібайтами (`2³²` секторів по 512 байтів), після чого номери секторів починають повторюватися, що призводить до небезпечного збігу твіків.
* `aes-xts-essiv:sha256` — режим із попереднім гешуванням ключа для обчислення $IV$. Для режиму XTS цей варіант є надлишковим і не рекомендованим, оскільки XTS уже містить вбудований незалежний ключ шифрування твіка `Key2`.

#### Додаткові прапорці продуктивності та безпеки

* `sector_size:<bytes>` — встановлює внутрішній криптографічний розмір сектора (зазвичай 4096 байтів замість стандартних 512 байтів). Збільшення сектора до 4096 байтів підвищує швидкість шифрування на 15–25% за рахунок зменшення кількості операцій генерації базового твіка `T[0]` на одиницю обсягу даних.
* `allow_discards` — дозволяє передачу команд TRIM/Discard від файлової системи до фізичного SSD-накопичувача. Покращує знос комірок флешпам'яті, проте створює витік інформації про розташування невикористаного простору на зашифрованому диску.
* `same_cpu_crypt` — примушує ядро виконувати шифрування та дешифрування на тому самому процесорному ядрі, яке ініціювало операцію вводу-виводу, уникаючи між'ядерних накладних витрат на синхронізацію кешів.
* `submit_from_crypt_cpus` — передає операції запису на контролер накопичувача безпосередньо з потоків шифрування, зменшуючи затримку (latency) на високошвидкісних накопичувачах NVMe.
* `no_read_workqueue` / `no_write_workqueue` — обходить черги робочих потоків `kcryptd`, виконуючи синхронне шифрування безпосередньо в контексті запиту вводу-виводу. Це суттєво підвищує кількість операцій на секунду (IOPS) на масивах NVMe RAID.

#### Практичні команди створення та діагностики контейнера

Створення шифрованого пристрою вручну без LUKS:

```bash
# Генерація 512-бітного випадкового ключа (64 байти в hex)
KEY=$(dd if=/dev/urandom bs=64 count=1 status=none | xxd -p -c 64)

# Отримання розміру блокового пристрою в секторах по 512 байтів
SECTORS=$(blockdev --getsz /dev/loop0)

# Створення віртуального відображення dm-crypt
dmsetup create secure_disk --table "0 $SECTORS crypt aes-xts-plain64 $KEY 0 /dev/loop0 0 1 sector_size:4096"

# Перевірка стану та параметрів створеної цілі
dmsetup status secure_disk
dmsetup table --showkeys secure_disk
```

---

### 2. Програмний інтерфейс ядра AF_ALG (User-Space Crypto API)

Криптографічна підсистема ядра Linux надає сокетне сімейство `AF_ALG`, що дозволяє додаткам простору користувача виконувати блокове шифрування XTS за допомогою оптимізованих драйверів ядра (AES-NI, AVX-512 VAES, ARMv8 CE) без прямого підключення сторонніх бібліотек.

Взаємодія через сокет `AF_ALG` складається з п'яти послідовних кроків:
1. **Створення сокета (`socket(AF_ALG, SOCK_SEQPACKET, 0)`):** Відкриває дескриптор підсистеми криптографії ядра.
2. **Прив'язка до алгоритму (`bind`):** Передає структуру `struct sockaddr_alg` із типом `"skcipher"` та назвою алгоритму `"xts(aes)"`.
3. **Завантаження ключа (`setsockopt` з опцією `ALG_SET_KEY`):** Передає подвійний ключ (32 або 64 байти). На цьому етапі ядро перевіряє довжину та умову `Key1 != Key2`.
4. **Створення робочої сесії (`accept`):** Повертає дескриптор операції для поточного потоку.
5. **Шифрування даних (`sendmsg` та `read`):** Передає відкритий текст разом із керуючим повідомленням `struct msghdr`, що містить тип операції (`ALG_OP_ENCRYPT`/`ALG_OP_DECRYPT`) та 128-бітний початковий твік.

Нижче наведено повну порівняльну реалізацію обгортки шифрування через сокети `AF_ALG` мовами C та C++ з використанням сучасних безпечних ідіом.

:::tabs
```c
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Виконання шифрування або дешифрування сектора XTS-AES через AF_ALG */
bool xts_af_alg_process(const uint8_t *key_512bit,
                        const uint8_t *tweak_128bit,
                        const uint8_t *in_data,
                        size_t len,
                        uint8_t *out_data,
                        uint32_t op_type) {
    if (!key_512bit || !tweak_128bit || !in_data || !out_data || len < 16) {
        return false;
    }

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "skcipher",
        .salg_name = "xts(aes)"
    };

    /* 1. Створення керуючого сокета */
    int tfm_fd = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (tfm_fd < 0) {
        return false;
    }

    if (bind(tfm_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        close(tfm_fd);
        return false;
    }

    /* 2. Завантаження 512-бітного подвійного ключа */
    if (setsockopt(tfm_fd, SOL_ALG, ALG_SET_KEY, key_512bit, 64) < 0) {
        close(tfm_fd);
        return false;
    }

    /* 3. Отримання робочого файлового дескриптора */
    int op_fd = accept(tfm_fd, NULL, 0);
    close(tfm_fd);
    if (op_fd < 0) {
        return false;
    }

    /* 4. Формування керуючого буфера з операцією та твіком */
    char cbuf[CMSG_SPACE(sizeof(uint32_t)) + CMSG_SPACE(sizeof(struct af_alg_iv) + 16)] = {0};
    struct msghdr msg = {
        .msg_control = cbuf,
        .msg_controllen = sizeof(cbuf)
    };

    /* Запис типу операції: ALG_OP_ENCRYPT або ALG_OP_DECRYPT */
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_OP;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint32_t));
    *((uint32_t *)CMSG_DATA(cmsg)) = op_type;

    /* Запис 128-бітного твіка як вектора ініціалізації (IV) */
    cmsg = CMSG_NXTHDR(&msg, cmsg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_IV;
    cmsg->cmsg_len = CMSG_LEN(sizeof(struct af_alg_iv) + 16);
    struct af_alg_iv *iv_hdr = (struct af_alg_iv *)CMSG_DATA(cmsg);
    iv_hdr->ivlen = 16;
    memcpy(iv_hdr->iv, tweak_128bit, 16);

    /* Передача вхідних даних через вектор вводу-виводу */
    struct iovec iov = {
        .iov_base = (void *)in_data,
        .iov_len = len
    };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    if (sendmsg(op_fd, &msg, 0) < 0) {
        close(op_fd);
        return false;
    }

    /* 5. Читання результату */
    ssize_t n_read = read(op_fd, out_data, len);
    close(op_fd);

    return (n_read == (ssize_t)len);
}
```
```cpp
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <unistd.h>
#include <cstring>
#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <memory>

namespace kernel_crypto {

enum class AlgError {
    kSocketCreationFailed,
    kBindFailed,
    kSetKeyFailed,
    kAcceptFailed,
    kSendFailed,
    kReadFailed,
    kInvalidInput
};

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

class KernelXtsCipher {
public:
    [[nodiscard]] static std::expected<KernelXtsCipher, AlgError> Create(
        std::span<const uint8_t, 64> key_512bit) noexcept {

        ScopedFd tfm_fd(::socket(AF_ALG, SOCK_SEQPACKET, 0));
        if (!tfm_fd.valid()) return std::unexpected(AlgError::kSocketCreationFailed);

        struct sockaddr_alg sa{};
        sa.salg_family = AF_ALG;
        std::strncpy(reinterpret_cast<char*>(sa.salg_type), "skcipher", sizeof(sa.salg_type) - 1);
        std::strncpy(reinterpret_cast<char*>(sa.salg_name), "xts(aes)", sizeof(sa.salg_name) - 1);

        if (::bind(tfm_fd.get(), reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(AlgError::kBindFailed);
        }

        if (::setsockopt(tfm_fd.get(), SOL_ALG, ALG_SET_KEY, key_512bit.data(), key_512bit.size()) < 0) {
            return std::unexpected(AlgError::kSetKeyFailed);
        }

        ScopedFd op_fd(::accept(tfm_fd.get(), nullptr, 0));
        if (!op_fd.valid()) return std::unexpected(AlgError::kAcceptFailed);

        return KernelXtsCipher(std::move(op_fd));
    }

    [[nodiscard]] std::expected<void, AlgError> Process(
        std::span<const uint8_t, 16> tweak_128bit,
        std::span<const uint8_t> input,
        std::span<uint8_t> output,
        uint32_t operation) const noexcept {

        if (input.size() < 16 || output.size() < input.size()) {
            return std::unexpected(AlgError::kInvalidInput);
        }

        alignas(struct cmsghdr) char cbuf[CMSG_SPACE(sizeof(uint32_t)) + CMSG_SPACE(sizeof(struct af_alg_iv) + 16)]{};
        struct msghdr msg{};
        msg.msg_control = cbuf;
        msg.msg_controllen = sizeof(cbuf);

        struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
        cmsg->cmsg_level = SOL_ALG;
        cmsg->cmsg_type = ALG_SET_OP;
        cmsg->cmsg_len = CMSG_LEN(sizeof(uint32_t));
        *reinterpret_cast<uint32_t*>(CMSG_DATA(cmsg)) = operation;

        cmsg = CMSG_NXTHDR(&msg, cmsg);
        cmsg->cmsg_level = SOL_ALG;
        cmsg->cmsg_type = ALG_SET_IV;
        cmsg->cmsg_len = CMSG_LEN(sizeof(struct af_alg_iv) + 16);
        auto *iv_hdr = reinterpret_cast<struct af_alg_iv*>(CMSG_DATA(cmsg));
        iv_hdr->ivlen = 16;
        std::memcpy(iv_hdr->iv, tweak_128bit.data(), 16);

        struct iovec iov{};
        iov.iov_base = const_cast<uint8_t*>(input.data());
        iov.iov_len = input.size();
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;

        if (::sendmsg(op_fd_.get(), &msg, 0) < 0) {
            return std::unexpected(AlgError::kSendFailed);
        }

        const ssize_t bytes_read = ::read(op_fd_.get(), output.data(), input.size());
        if (bytes_read != static_cast<ssize_t>(input.size())) {
            return std::unexpected(AlgError::kReadFailed);
        }

        return {};
    }

private:
    explicit KernelXtsCipher(ScopedFd op_fd) noexcept : op_fd_(std::move(op_fd)) {}
    ScopedFd op_fd_;
};

} // namespace kernel_crypto
```
:::

---

### 3. Внутрішній драйверний інтерфейс ядра `crypto_skcipher`

Усередині коду ядра (наприклад, у драйвері `dm-crypt.c` чи підсистемі `fscrypt`) криптографічні трансформації обслуговуються асинхронним інтерфейсом симетричного шифрування `struct crypto_skcipher`.

Драйвер ядра створює списки розсіювання-збирання (scatter-gather lists) `struct scatterlist` для прямого доступу до сторінок пам'яті (Direct Memory Access, DMA) без проміжного копіювання буферів:

```c
/* Фрагмент виділення трансформації та завантаження ключа в ядрі Linux */
struct crypto_skcipher *tfm = crypto_alloc_skcipher("xts(aes)", 0, 0);
if (IS_ERR(tfm)) {
    return PTR_ERR(tfm);
}

/* Встановлення 512-бітного ключа XTS */
int ret = crypto_skcipher_setkey(tfm, raw_key_512, 64);
if (ret < 0) {
    crypto_free_skcipher(tfm);
    return ret;
}
```

#### Потік обробки дискових запитів BIO у `dm-crypt`

Під час виконання операції запису на шифрований диск стек ядра виконує наступну послідовність дій:
1. Файлова система формує запит блокового вводу-виводу `struct bio` з відкритими даними.
2. Драйвер `dm-crypt` перехоплює запит і клонує структуру `bio`, виділяючи нові сторінки пам'яті під шифротекст.
3. Робочий потік ядра `kcryptd` обчислює базовий твік із номера логічного сектора `bio->bi_iter.bi_sector` та шифрує дані через виклик `crypto_skcipher_encrypt()`.
4. Зашифрований клон `bio` передається драйверу фізичного контролера накопичувача (NVMe або SATA) для запису на носій.

#### Перевірка нерівності ключів (FIPS 140-3 та стандарт NIST)

Під час виклику функції `crypto_skcipher_setkey()` ядро перевіряє подвійний ключ на відповідність криптографічним вимогам стандарту NIST SP 800-38E:

```c
/* Фрагмент реалізації crypto/xts.c у ядрі Linux */
static int xts_setkey(struct crypto_skcipher *tfm, const u8 *key, unsigned int keylen) {
    /* Перевірка мінімальної та максимальної довжини ключа */
    if (keylen != 32 && keylen != 64)
        return -EINVAL;

    /* Вимога FIPS 140-3: заборона збігу Key1 та Key2 */
    if (crypto_fips_enabled || IS_ENABLED(CONFIG_CRYPTO_FIPS)) {
        if (!crypto_memneq(key, key + (keylen / 2), keylen / 2))
            return -EINVAL;
    }
    /* Ініціалізація підлеглих контекстів Key1 та Key2 */
    ...
}
```

Якщо передано ключ, у якому перша половина `Key1` збігається з другою половиною `Key2` (`Key1 == Key2`), функція негайно повертає помилку `-EINVAL`, запобігаючи деградації режиму до вразливого стану.

#### Інспекція доступних драйверів у `/proc/crypto`

Перевірити наявність та пріоритет апаратних реалізацій `xts(aes)` у поточній системі можна через віртуальну файлову систему `procfs`:

```bash
cat /proc/crypto | grep -A 10 "xts(aes)"
```

У виводі відображаються доступні драйвери: апаратний драйвер `xts-aes-aesni` або `xts-aes-vaes` (із найвищим пріоритетом `priority: 400` або `500`) та загальний софтверний драйвер `xts(aes-generic)` (`priority: 100`). Ядро автоматично обирає реалізацію з найвищим пріоритетом.

Для швидкого вимірювання пропускної здатності шифрування на поточному обладнанні використовується вбудований бенчмарк утиліти `cryptsetup`:

```bash
cryptsetup benchmark --cipher aes-xts
```

На сучасних системах з підтримкою векторних інструкцій AES-NI швидкість AES-XTS сягає 4500–6000 МіБ/с для 256-бітного ключа та 5500–7500 МіБ/с для 128-бітного ключа.
