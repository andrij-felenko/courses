# ⚙️ Клієнтський маршрутизатор каналів та валідатор криптографічних підписів

Клієнтський демон оновлення вбудованої системи або розподіленого сервісу повинен автономно керувати підпискою на канали, завантажувати метадані, валідувати криптографічні підписи, перевіряти апаратні обмеження захисту від відкоту та безпечно записувати образ у пасивний дисковий розділ за схемою подвійного банку (A/B partitioning).

Нижче наведено робочу реалізацію ядра маршрутизатора каналів та перевірки підписів двома мовами — класичною системною C та сучасним ідіоматичним C++20.

---

## 1. Архітектурні принципи та послідовність верифікації

Маршрутизатор каналів діє як детермінований контролер безпеки перед початком будь-яких операцій запису у постійну пам'ять. Процес обробки маніфесту оновлення складається з п'яти обов'язкових етапів:

1. **Зіставлення каналу з апаратними прапорцями:** перевірка, чи не суперечить запитаний канал апаратним блокуванням процесора. Якщо у мікроконтролері активовано регістр eFuse `CHANNEL_LOCK_LTS`, спроба обробити маніфест для каналів `nightly`, `beta` або `stable` негайно відхиляється з генерацією тривожного повідомлення безпеки.
2. **Перевірка лічильника захисту від відкоту (Anti-Rollback Gate):** порівняння поля `rollback_counter` із захищеним апаратним лічильником у незалежній пам'яті NVRAM/TPM. Якщо нова версія має менший лічильник, оновлення блокується для унеможливлення експлуатації закритих вразливостей (Downgrade Attack).
3. **Криптографічна валідація підпису маніфесту:** пошук набору публічних ключів (Key Ring), закріпленого саме за цільовим каналом, та перевірка цифрового підпису Ed25519 для контрольної суми SHA-256 бінарного артефакту. Підпис вважається дійсним, якщо він підтверджується хоча б одним невідкликаним ключем зі зв'язки каналу (або досягнуто необхідний поріг кворуму).
4. **Вибір цільового розділу пам'яті (A/B Partition Switch):** визначення пасивного слота накопичувача (`bank_a` ↔ `bank_b`). Якщо система завантажена з банку `A`, запис нового образу дозволяється виключно в банк `B`.
5. **Фіксація стану в завантажувачі:** запис змінних конфігурації завантажувача U-Boot (`boot_partition=B`, `boot_attempts=3`) для виконання одноразового тестового старту з можливістю автоматичного відкоту при падінні ядра.

---

## 2. Реалізація клієнтського маршрутизатора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_VERSION_LEN 32
#define MAX_HASH_LEN 65
#define MAX_SIG_LEN 128
#define MAX_KEYS_PER_CHANNEL 4

typedef enum {
    CHANNEL_NIGHTLY = 0,
    CHANNEL_BETA    = 1,
    CHANNEL_STABLE  = 2,
    CHANNEL_LTS     = 3,
    CHANNEL_UNKNOWN = 255
} channel_type_t;

typedef struct {
    uint8_t key_data[32];
    uint32_t key_id;
    bool is_revoked;
} crypto_key_t;

typedef struct {
    channel_type_t channel;
    size_t key_count;
    crypto_key_t keys[MAX_KEYS_PER_CHANNEL];
} channel_keyring_t;

typedef struct {
    char version[MAX_VERSION_LEN];
    channel_type_t channel;
    uint32_t rollback_counter;
    char sha256_hex[MAX_HASH_LEN];
    uint8_t signature[MAX_SIG_LEN];
    size_t signature_len;
    size_t image_size_bytes;
} release_manifest_t;

typedef struct {
    char current_version[MAX_VERSION_LEN];
    channel_type_t subscribed_channel;
    channel_type_t hardware_lock_channel; // Обмеження eFuse
    uint32_t hw_rollback_counter;
    char active_partition; // 'A' або 'B'
} device_state_t;

typedef enum {
    ROUTER_OK = 0,
    ROUTER_ERR_CHANNEL_FORBIDDEN,
    ROUTER_ERR_ROLLBACK_DETECTED,
    ROUTER_ERR_SIGNATURE_INVALID,
    ROUTER_ERR_NO_VALID_KEY,
    ROUTER_ERR_STORAGE_FAILURE
} router_status_t;

// Спрощена імітація криптографічної перевірки Ed25519
static bool mock_ed25519_verify(const uint8_t *pubkey, const char *hash_hex, 
                                const uint8_t *sig, size_t sig_len) {
    if (!pubkey || !hash_hex || !sig || sig_len == 0) {
        return false;
    }
    // У реальній системі: ed25519_verify(sig, hash_hex, strlen(hash_hex), pubkey)
    return (sig[0] == 0xAA && pubkey[0] != 0x00);
}

router_status_t route_and_validate_update(
    const device_state_t *device,
    const channel_keyring_t *keyrings,
    size_t keyring_count,
    const release_manifest_t *manifest,
    char *out_target_partition
) {
    if (!device || !keyrings || !manifest || !out_target_partition) {
        return ROUTER_ERR_STORAGE_FAILURE;
    }

    // 1. Перевірка апаратного обмеження eFuse
    if (device->hardware_lock_channel == CHANNEL_LTS && manifest->channel != CHANNEL_LTS) {
        fprintf(stderr, "[SECURITY ALERT] eFuse блокує оновлення: пристрій заблоковано на LTS!\n");
        return ROUTER_ERR_CHANNEL_FORBIDDEN;
    }

    // 2. Перевірка лічильника захисту від відкоту (Anti-Rollback)
    if (manifest->rollback_counter < device->hw_rollback_counter) {
        fprintf(stderr, "[SECURITY ALERT] Спроба відкоту: маніфест (%u) < залізо (%u)\n",
                manifest->rollback_counter, device->hw_rollback_counter);
        return ROUTER_ERR_ROLLBACK_DETECTED;
    }

    // 3. Пошук відповідної зв'язки ключів (Keyring) для запитаного каналу
    const channel_keyring_t *target_ring = NULL;
    for (size_t i = 0; i < keyring_count; ++i) {
        if (keyrings[i].channel == manifest->channel) {
            target_ring = &keyrings[i];
            break;
        }
    }

    if (!target_ring || target_ring->key_count == 0) {
        fprintf(stderr, "[ERROR] Не знайдено довірених ключів для каналу %d\n", manifest->channel);
        return ROUTER_ERR_NO_VALID_KEY;
    }

    // 4. Валідація підпису всіма дійсними ключами зв'язки каналу
    bool signature_verified = false;
    for (size_t k = 0; k < target_ring->key_count; ++k) {
        const crypto_key_t *key = &target_ring->keys[k];
        if (key->is_revoked) {
            continue;
        }

        if (mock_ed25519_verify(key->key_data, manifest->sha256_hex, 
                                manifest->signature, manifest->signature_len)) {
            signature_verified = true;
            break;
        }
    }

    if (!signature_verified) {
        fprintf(stderr, "[SECURITY ALERT] Підпис маніфесту не відповідає ключам каналу %d!\n", 
                manifest->channel);
        return ROUTER_ERR_SIGNATURE_INVALID;
    }

    // 5. Вибір неактивного банку пам'яті (A/B Partition Switch)
    *out_target_partition = (device->active_partition == 'A') ? 'B' : 'A';

    printf("[ROUTER OK] Валідація успішна. Канал: %d, Версія: %s. Цільовий банк: %c\n",
           manifest->channel, manifest->version, *out_target_partition);

    return ROUTER_OK;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <optional>
#include <expected>
#include <array>
#include <algorithm>

enum class Channel : uint8_t {
    Nightly = 0,
    Beta    = 1,
    Stable  = 2,
    Lts     = 3,
    Unknown = 255
};

struct CryptoKey {
    std::array<uint8_t, 32> key_data{};
    uint32_t key_id{0};
    bool is_revoked{false};
};

struct ChannelKeyring {
    Channel channel{Channel::Unknown};
    std::vector<CryptoKey> keys;
};

struct ReleaseManifest {
    std::string version;
    Channel channel{Channel::Unknown};
    uint32_t rollback_counter{0};
    std::string sha256_hex;
    std::vector<uint8_t> signature;
    size_t image_size_bytes{0};
};

struct DeviceState {
    std::string current_version;
    Channel subscribed_channel{Channel::Stable};
    Channel hardware_lock_channel{Channel::Unknown}; // Апаратний замок eFuse
    uint32_t hw_rollback_counter{0};
    char active_partition{'A'};
};

enum class RouterError {
    ChannelForbidden,
    RollbackDetected,
    SignatureInvalid,
    NoValidKeyring,
    StorageFailure
};

class ChannelRouter {
public:
    explicit ChannelRouter(std::vector<ChannelKeyring> keyrings)
        : keyrings_(std::move(keyrings)) {}

    [[nodiscard]] std::expected<char, RouterError> evaluate_and_route(
        const DeviceState& device,
        const ReleaseManifest& manifest) const noexcept 
    {
        // 1. Перевірка апаратного eFuse обмеження
        if (device.hardware_lock_channel == Channel::Lts && manifest.channel != Channel::Lts) {
            std::cerr << "[SECURITY ALERT] eFuse захист: пристрій заблоковано виключно на LTS!\n";
            return std::unexpected(RouterError::ChannelForbidden);
        }

        // 2. Захист від відкоту (Anti-Rollback)
        if (manifest.rollback_counter < device.hw_rollback_counter) {
            std::cerr << "[SECURITY ALERT] Спроба Downgrade: лічильник маніфесту " 
                      << manifest.rollback_counter << " < апаратного " 
                      << device.hw_rollback_counter << "\n";
            return std::unexpected(RouterError::RollbackDetected);
        }

        // 3. Пошук зв'язки ключів цільового каналу
        const auto it = std::ranges::find_if(keyrings_, [&](const auto& kr) {
            return kr.channel == manifest.channel;
        });

        if (it == keyrings_.end() || it->keys.empty()) {
            std::cerr << "[ERROR] Не знайдено довірених ключів для цільового каналу!\n";
            return std::unexpected(RouterError::NoValidKeyring);
        }

        // 4. Перевірка цифрового підпису Ed25519
        const bool verified = std::ranges::any_of(it->keys, [&](const auto& key) {
            if (key.is_revoked) return false;
            return verify_signature(key.key_data, manifest.sha256_hex, manifest.signature);
        });

        if (!verified) {
            std::cerr << "[SECURITY ALERT] Цифровий підпис не відповідає жодному ключу каналу!\n";
            return std::unexpected(RouterError::SignatureInvalid);
        }

        // 5. Вибір пасивного розділу
        const char target_bank = (device.active_partition == 'A') ? 'B' : 'A';
        return target_bank;
    }

private:
    std::vector<ChannelKeyring> keyrings_;

    static bool verify_signature(
        std::span<const uint8_t, 32> pubkey,
        std::string_view hash_hex,
        std::span<const uint8_t> signature) noexcept 
    {
        if (pubkey.empty() || hash_hex.empty() || signature.empty()) {
            return false;
        }
        // Імітація криптографічної перевірки
        return (signature[0] == 0xAA && pubkey[0] != 0x00);
    }
};
```
:::

---

## 3. Інтеграція з підсистемами ядра Linux та інтерфейсами sysfs

У реальній вбудованій системі під керуванням Linux клієнтський маршрутизатор оновлень тісно інтегрований із драйверами ядра через символьні пристрої та файлову систему `/sys`.

### 3.1. Керування апаратним сторожовим псом (/dev/watchdog)
Перед початком процедури запису нового образу в пасивний банк демон оновлення ініціалізує таймер апаратного сторожового пса (Watchdog). Це гарантує, що якщо процес оновлення зависне через збій контролера eMMC або переривання живлення, мікроконтролер виконає апаратне перезавантаження:

:::tabs
```c
int wd_fd = open("/dev/watchdog", O_WRONLY);
if (wd_fd >= 0) {
    int timeout = 120; // 2 хвилини на запис
    ioctl(wd_fd, WDIOC_SETTIMEOUT, &timeout);
    close(wd_fd);
}
```
```cpp
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>
#include <string_view>

class WatchdogDevice {
public:
    explicit WatchdogDevice(std::string_view dev_path = "/dev/watchdog") noexcept {
        fd_ = ::open(dev_path.data(), O_WRONLY);
    }
    ~WatchdogDevice() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    bool set_timeout(int seconds) noexcept {
        if (fd_ < 0) return false;
        return (::ioctl(fd_, WDIOC_SETTIMEOUT, &seconds) >= 0);
    }
private:
    int fd_{-1};
};
```
:::

### 3.2. Сповіщення системного менеджера systemd
Після успішного завантаження нової прошивки та проходження системних самотестів демон надсилає сигнал підтвердження здоров'я вузла через сокет IPC systemd за допомогою виклику `sd_notify`:

:::tabs
```c
// Повідомлення менеджера служб про успішний старт та готовність
sd_notify(0, "READY=1\nWATCHDOG=1\nSTATUS=Channel update verified and committed.");
```
```cpp
#include <string_view>
#include <string>
#include <systemd/sd-daemon.h>

void notify_systemd_ready(std::string_view status_msg) noexcept {
    const std::string payload = "READY=1\nWATCHDOG=1\nSTATUS=" + std::string(status_msg);
    ::sd_notify(0, payload.c_str());
}
```
:::

### 3.3. Транзакційний запис конфігурації U-Boot
Для захисту від пошкодження змінних середовища завантажувача під час аварійного знеструмлення використовується механізм подвійного середовища U-Boot (англ. *Redundant U-Boot Environment*). Демон викликає утиліту `fw_setenv`, яка записує оновлений лічильник завантажень і прапорець цільового банку з контрольною сумою CRC32 у чергову копію блоку конфігурації флеш-пам'яті, гарантуючи, що завантажувач завжди матиме цілісну копію попереднього робочого стану.

---

## 4. Практичні пастки, крайові випадки та відновлення

1. **Несумісність структури бази даних при стрибках каналів (Down-Channel Jump):**
   Коли пристрій тимчасово переводиться на канал `Beta`, локальний сервіс оновлює схему вбудованої бази даних SQLite (додаючи нові стовпці, індекси та зовнішні ключі). Якщо згодом користувач вручну повертає пристрій у канал `Stable`, старий бінарник версії `Stable` не розпізнає нову структуру таблиць і аварійно завершує роботу під час ініціалізації.
   *Правило реалізації:* Операція пониження каналу (`Beta` → `Stable`) повинна або блокуватися до моменту випуску стабільної версії з аналогічною схемою даних, або супроводжуватися обов'язковим попередженням та скиданням користувацького розділу до заводського стану (Factory Reset).

2. **Підміна та фальсифікація ключів у оперативній пам'яті:**
   Якщо зловмисник отримує права на запис у конфігураційний каталог `/etc/ota/`, він може модифікувати локальний файл `keyrings.json`, підмінивши відкритий ключ каналу `Stable` на свій власний підроблений ключ.
   *Правило реалізації:* Кореневі відкриті ключі каналів мають бути зашиті в незмінний розділ образу операційної системи (змонтований як `read-only` через `squashfs` з перевіркою цілісності `dm-verity`) або зберігатися в захищеному апаратному сховищі крипточипа TPM чи Secure Element.

3. **Захист від шторму одночасних запитів (Thundering Herd Problem):**
   При публікації оновлення для масового стабільного каналу сотні тисяч пристроїв можуть одночасно розпочати завантаження важкого бінарного образу розміром у десятки мегабайтів, що спричинить відмову серверної інфраструктури CDN.
   *Правило реалізації:* Клієнтський маршрутизатор зобов'язаний додавати детермінований псевдовипадковий зсув часу завантаження (англ. *randomized jitter*) у діапазоні від 0 до 12 годин на основі залишку від ділення апаратного ідентифікатора пристрою на тривалість вікна розгортання.

4. **Аварійний відкат за таймером сторожового пса (Watchdog Rollback):**
   Після перемикання розділу на Bank B завантажувач запускає нове ядро. Якщо ядро входить у `Kernel Panic` до запуску мережевого стека, апаратний сторожовий таймер перезавантажує мікроконтролер. Завантажувач U-Boot зменшує лічильник `bootcount`. Коли лічильник досягає нуля, завантажувач автоматично повертає активний статус розділу Bank A, забезпечуючи стовідсоткову автономну живучість системи без втручання людини.
