# ⚙️ Виробничий конвеєр і безпечне сховище NVS

Під час серійного виробництва пристроїв на базі мікроконтролерів ESP32 постає практичне інженерне завдання: надійно зберегти унікальні конфіденційні параметри пристрою (приватний ключ клієнта TLS, сертифікат автентифікації пристрою, токен доступу до хмарного брокера повідомлень та заводські калібрувальні коефіцієнти) в енергонезалежному сховищі NVS ще на конвеєрі або забезпечити їхню безпечну автономну ініціалізацію під час першого увімкнення кінцевим користувачем. У цьому практичному проекті розібрано повний наскрізний конвеєр: від конструювання розкладки таблиці розділів і хостової генерації бінарних образів утилітою `nvs_partition_gen.py` до коду вбудованої прошивки мовами C та C++, що реалізує безпечну роботу з дескрипторами та обов'язкове очищення чутливих секретів з оперативної пам'яті (RAM) після завершення криптографічних операцій.

---

### 1. Розкладка розділів у `partitions.csv`

Для підтримки зашифрованого сховища таблиця розділів [Partition Table](root:sys-fw/partition-table) проекту мусить містити щонайменше два спеціалізовані блоки: розділ ключів шифрування `nvs_key` (підтип `nvs_keys`) та виділений розділ даних `secret_nvs`:

```csv
# Name,       Type, SubType,  Offset,   Size,     Flags
nvs,          data, nvs,      0x9000,   0x6000,
nvs_key,      data, nvs_keys, 0xf000,   0x1000,   encrypted
secret_nvs,   data, nvs,      0x10000,  0x10000,
otadata,      data, ota,      0x20000,  0x2000,
app_0,        app,  ota_0,    0x30000,  0x180000,
```

Розберімо фізичні вимоги до кожного поля:
- **Зсув `0xf000` для `nvs_key`:** Розділ починається на межі 4 КБ, що є мінімальним розміром сектора стирання Flash-пам'яті [Flash зсередини](root:hw-components/flash-internals).
- **Розмір `0x1000` (4096 байтів):** Сектор ключів займає рівно 1 сектор Flash. Хоча структура ключів `nvs_sec_cfg_t` має довжину лише 64 байти, апаратне блочне шифрування Flash вимагає виділення цілого сектора під незалежний розділ.
- **Прапорець `encrypted`:** Повідомляє утиліті прошивання `esptool.py` та завантажувачу другого ступеня (bootloader), що цей сектор підлягає апаратному шифруванню за допомогою [Flash Encryption](root:sys-fw/flash-encryption).
- **Розділ `secret_nvs`:** Має розмір `0x10000` (64 КБ = 16 сторінок NVS). Він залишається зі стандартним прапорцем без апаратного шифрування Flash, оскільки його сторінки шифруються на рівні слотів алгоритмом [AES-XTS](root:sf-security/aes-xts) через драйвер NVS.

Розрахунок зсувів виконується за правилом секторного стирання: кожен наступний розділ починається з адреси, що дорівнює сумі зсуву попереднього розділу та його розміру:

```
зсув secret_nvs = зсув nvs_key + розмір nvs_key
= 0xf000 + 0x1000
= 0x10000 [вирівняно на 64 КБ для безпечного сусідства з app-розділами]
```

---

### 2. Підготовка та прошивання образу на хості

Якщо виробничий процес передбачає зашивання індивідуальних сертифікатів на фабриці перед пакуванням пристрою, генерація ключів і формування образу виконуються на робочій станції за допомогою утиліт фреймворку ESP-IDF.

Цей процес забезпечує повний контроль над унікальними сертифікатами пристроїв на рівні конвеєра:

#### Крок 1. Генерація 64-байтового ключа шифрування XTS
Генератор створює файл `nvs_keys.bin`, що містить 32 байти ключа шифрування даних (`ekey`) та 32 байти ключа твіка (`tkey`):

```bash
python $IDF_PATH/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py \
    generate-key --keyfile nvs_keys.bin
```

#### Крок 2. Підготовка вхідного файлу конфігурацій `secrets.csv`
У текстовому файлі описують структуру просторів імен та типи даних (рядки, двійкові файли, цілі числа):

```csv
key,type,encoding,value
sec_ns,namespace,,
device_cert,file,binary,certs/device_cert.crt
tls_priv_key,file,binary,certs/device_private.key
cloud_endpoint,data,string,mqtts://a3b8c9d0e1f2.iot.eu-central-1.amazonaws.com
device_id,data,u32,4194304
```

#### Крок 3. Створення зашифрованого бінарного образу NVS
Утиліта зчитує `secrets.csv`, генерує правильну структуру сторінок NVS (з відкритими заголовками та бітовими картами) і шифрує кожен 32-байтовий слот алгоритмом AES-XTS за допомогою ключа `nvs_keys.bin`:

```bash
python $IDF_PATH/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py \
    encrypt secrets.csv secret_nvs.bin 0x10000 --inputkey nvs_keys.bin
```

#### Крок 4. Записування бінарних образів у фізичний Flash
Під час прошивання розділ ключів обов'язково передається команді `write_flash` із прапорцем `--encrypt`, аби апаратний шифратор мікроконтролера зашифрував його перед записом у Flash-пам'ять:

```bash
# 1. Записуємо ключ у розділ nvs_key з увімкненим апаратним Flash Encryption
esptool.py --port /dev/ttyUSB0 --baud 921600 write_flash --encrypt 0xf000 nvs_keys.bin

# 2. Записуємо зашифрований образ NVS у розділ secret_nvs
esptool.py --port /dev/ttyUSB0 --baud 921600 write_flash 0x10000 secret_nvs.bin
```

---

### 3. Програмна реалізація у прошивці: C та C++

Усередині мікроконтролера код прошивки повинен гарантувати безпечну роботу з ключами: отримати дескриптор розділу, зчитати ключі, ініціалізувати сховище, зчитати або зберегти приватний сертифікат і негайно очистити структури в оперативній пам'яті (RAM), щоб запобігти витоку секретів у разі аварійного дампу пам'яті (Core Dump).

У прикладі нижче показано створення обгортки дескриптора на основі ідіоми RAII (Resource Acquisition Is Initialization — захоплення ресурсу є ініціалізацією) у C++, яка унеможливлює витік пам'яті чи незакриті дескриптори при виникненні помилок.

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

static const char* TAG = "nvs_workflow";

esp_err_t manage_device_secrets_c(void)
{
    nvs_sec_cfg_t cfg;
    const esp_partition_t* key_part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA,
        ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
        NULL
    );
    if (!key_part) {
        ESP_LOGE(TAG, "Розділ nvs_keys відсутній у таблиці розділів!");
        return ESP_ERR_NOT_FOUND;
    }

    // Зчитуємо конфігурацію ключів з Flash (прозоре дешифрування через MMU)
    esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
    if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
        ESP_LOGW(TAG, "Розділ ключів порожній. Автономна генерація нового ключа...");
        err = nvs_flash_generate_keys(key_part, &cfg);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка конфігурації безпеки: 0x%x", err);
        return err;
    }

    // Ініціалізуємо виділений зашифрований розділ
    err = nvs_flash_secure_init_partition("secret_nvs", &cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося змонтувати secret_nvs: 0x%x", err);
        explicit_bzero(&cfg, sizeof(cfg));
        return err;
    }

    // Відкриваємо простір імен "sec_ns"
    nvs_handle_t handle;
    err = nvs_open_from_partition("secret_nvs", "sec_ns", NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка відкриття простору імен: 0x%x", err);
        explicit_bzero(&cfg, sizeof(cfg));
        return err;
    }

    // Зчитування приватного ключа клієнта (blob)
    size_t key_len = 0;
    err = nvs_get_blob(handle, "tls_priv_key", NULL, &key_len);
    if (err == ESP_OK && key_len > 0) {
        uint8_t* key_buffer = (uint8_t*)malloc(key_len);
        if (key_buffer) {
            err = nvs_get_blob(handle, "tls_priv_key", key_buffer, &key_len);
            if (err == ESP_OK) {
                ESP_LOGI(TAG, "Приватний ключ TLS успішно прочитано (%zu байтів)", key_len);
            }
            // Гарантоване затирання тимчасового буфера після використання
            explicit_bzero(key_buffer, key_len);
            free(key_buffer);
        }
    } else {
        ESP_LOGW(TAG, "Приватний ключ відсутній. Запис тимчасового токена...");
        const char test_token[] = "DEV_SESSION_TOKEN_998124";
        nvs_set_str(handle, "session_token", test_token);
        nvs_commit(handle);
    }

    // Закриваємо дескриптор сховища
    nvs_close(handle);

    // Обов'язкове затирання криптографічного контексту в стеку
    explicit_bzero(&cfg, sizeof(cfg));
    return ESP_OK;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <algorithm>
#include <cstring>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

namespace production {

class ScopedNvsHandle {
public:
    explicit ScopedNvsHandle(nvs_handle_t handle) noexcept : handle_(handle) {}
    ~ScopedNvsHandle() noexcept {
        if (handle_ != 0) {
            nvs_close(handle_);
        }
    }

    ScopedNvsHandle(const ScopedNvsHandle&) = delete;
    ScopedNvsHandle& operator=(const ScopedNvsHandle&) = delete;

    ScopedNvsHandle(ScopedNvsHandle&& other) noexcept : handle_(other.handle_) {
        other.handle_ = 0;
    }

    [[nodiscard]] nvs_handle_t get() const noexcept { return handle_; }
    [[nodiscard]] bool valid() const noexcept { return handle_ != 0; }

private:
    nvs_handle_t handle_{0};
};

class SecureProductionStorage {
public:
    static esp_err_t initialize_and_verify(std::string_view partition_name) noexcept {
        const esp_partition_t* key_part = esp_partition_find_first(
            ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
            nullptr
        );
        if (!key_part) {
            ESP_LOGE("NVS_PROJ", "Розділ nvs_keys не знайдено!");
            return ESP_ERR_NOT_FOUND;
        }

        nvs_sec_cfg_t cfg{};
        esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
        if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
            ESP_LOGW("NVS_PROJ", "Генерація ключів NVS на чіпі...");
            err = nvs_flash_generate_keys(key_part, &cfg);
        }
        if (err != ESP_OK) {
            return err;
        }

        err = nvs_flash_secure_init_partition(partition_name.data(), &cfg);

        // Безпечне затирання локальної структури ключів
        std::fill(reinterpret_cast<uint8_t*>(&cfg),
                  reinterpret_cast<uint8_t*>(&cfg) + sizeof(cfg), 0);
        return err;
    }

    static esp_err_t read_secret_blob(std::string_view part_name,
                                      std::string_view nspace,
                                      std::string_view key,
                                      std::vector<uint8_t>& output_buffer) {
        nvs_handle_t raw_h{0};
        esp_err_t err = nvs_open_from_partition(part_name.data(), nspace.data(), NVS_READONLY, &raw_h);
        if (err != ESP_OK) {
            return err;
        }
        ScopedNvsHandle handle(raw_h);

        size_t required_len = 0;
        err = nvs_get_blob(handle.get(), key.data(), nullptr, &required_len);
        if (err != ESP_OK || required_len == 0) {
            return err;
        }

        output_buffer.resize(required_len);
        return nvs_get_blob(handle.get(), key.data(), output_buffer.data(), &required_len);
    }
};

} // namespace production
```
:::

---

### Безпекова верифікація та типові помилки конвеєра

Під час розгортання виробничої лінії слід регулярно проводити перевірку стану захищеності зразків за допомогою утиліти `espsecure.py`:

```bash
# Перевірка статусу шифрування Flash
espsecure.py check_flash_encryption
```

Найпоширеніші пастки та правила їх усунення:

1. **Прошивання без прапорця `--encrypt`:** Якщо записати файл `nvs_keys.bin` у Flash у відкритому вигляді без апаратного Flash Encryption, зловмисник зможе зчитати ключ NVS простим підключенням логічного аналізатора до шини SPI і повністю розшифрувати розділ `secret_nvs`. Прапорець `encrypted` у `partitions.csv` та параметр `--encrypt` в `esptool.py` є строго обов'язковими.
2. **Стирання розділу ключів `nvs_key`:** Під час налагодження часто виконують повне стирання `esptool.py erase_flash`. Якщо розділ ключів видалено, усі раніше збережені у `secret_nvs` записи стають невідновлюваним сміттям, оскільки відтворити випадковий 256-бітний ключ неможливо. Для часткового очищення використовуйте команду `esptool.py erase_region 0x10000 0x10000`, яка стирає лише розділ даних, не зачіпаючи ключі.
3. **Залишення секретів у статичній пам'яті:** Секретні буфери, прочитані з NVS, не повинні зберігатися у глобальних статичних масивах. Їх слід розміщувати у динамічній пам'яті або на стеку та негайно обнуляти через `explicit_bzero()` після завершення передачі в криптографічні модулі mbedTLS.
4. **Неправильний розрахунок розміру NVS під час генерації:** Якщо розмір образу, вказаний в `nvs_partition_gen.py` (наприклад, `0x10000`), відрізняється від розміру розділу в `partitions.csv`, драйвер NVS визначить розділ як пошкоджений через розбіжність кількості сторінок. Розмір у скрипті мусить байт у байт відповідати числу в таблиці розділів.
