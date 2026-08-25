# 📋 API шифрування NVS в ESP-IDF

Для надійного захисту секретів у сховищі NVS фреймворк ESP-IDF надає спеціалізований програмний інтерфейс (API, від англ. *Application Programming Interface* — інтерфейс прикладного програмування), що керує зчитуванням ключів шифрування, їхньою апаратною генерацією та безпечною ініціалізацією окремих розділів Flash-пам'яті. Цей інтерфейс абстрагує роботу з блочним шифром AES-XTS і дає змогу розробникові прозоро записувати й зчитувати конфіденційні параметри стандартними функціями NVS без ручного шифрування кожного окремого байта.

Усі структури даних, функції та константи оголошено в заголовному файлі `nvs_flash.h` компонента `nvs_flash`.

---

### Структури даних

Головною структурою для збереження криптографічного контексту є `nvs_sec_cfg_t` (від англ. *NVS security configuration* — конфігурація безпеки NVS). Вона вміщує два незалежні 256-бітні симетричні ключі (разом 64 байти = 512 бітів), необхідні для функціонування режиму AES-XTS:

:::tabs
```c
typedef struct {
    uint8_t ekey[32];  /**< Ключ шифрування даних (AES-256 encryption key) */
    uint8_t tkey[32];  /**< Ключ налаштування зміщення (AES-256 tweak key) */
} nvs_sec_cfg_t;
```
```cpp
#include <array>
#include <cstdint>

namespace esp_nvs {

struct SecurityConfig {
    std::array<uint8_t, 32> encryption_key{}; /**< Ключ шифрування корисних даних */
    std::array<uint8_t, 32> tweak_key{};      /**< Ключ налаштування зміщення */
};

} // namespace esp_nvs
```
:::

Поле `ekey` використовується для безпосереднього перетворення відкритого тексту кожного 32-байтового слота запису NVS на шифротекст. Поле `tkey` використовується для криптографічного шифрування значення налаштування (tweak), яке обчислюється на основі фізичного зміщення запису в розділі пам'яті.

Внутрішня організація структури вимагає суворого вирівнювання за 4-байтовою або 32-байтовою межею для прямої сумісності з апаратним криптографічним блоком AES мікроконтролера ESP32. Передавання некоректно вирівняного покажчика може призводити до апаратних винятків процесора під час завантаження регістрів шифрування.

---

### Функції керування ключами та ініціалізації

Нижче наведено детальний опис функцій, що відповідають за життєвий цикл ключів та запуск зашифрованого сховища.

#### 1. Зчитування ключів безпеки: `nvs_flash_read_security_cfg`

:::tabs
```c
esp_err_t nvs_flash_read_security_cfg(
    const esp_partition_t* partition,
    nvs_sec_cfg_t* cfg
);
```
```cpp
#include "nvs_flash.h"
#include <expected>
#include <system_error>

namespace esp_nvs {

[[nodiscard]] inline esp_err_t read_security_config(
    const esp_partition_t* partition,
    nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_read_security_cfg(partition, &cfg);
}

} // namespace esp_nvs
```
:::

- **Призначення:** Зчитує 64-байтову конфігурацію ключів шифрування з указаного розділу типу `data` та підтипу `nvs_keys`. Якщо на мікроконтролері ввімкнено апаратний захист [Flash Encryption](root:sys-fw/flash-encryption), зчитування відбувається через прозоре апаратне дешифрування Flash MMU.
- **Параметри:**
  - `partition`: Вказівник на дескриптор розділу ключів (знайдений через `esp_partition_find_first`). Якщо передати `NULL`, функція автоматично шукає перший розділ із підтипом `nvs_keys` у таблиці розділів.
  - `cfg`: Вказівник на структуру `nvs_sec_cfg_t`, куди буде записано прочитані 64 байти ключів.
- **Повертає:**
  - `ESP_OK`: Ключі успішно прочитано з Flash-пам'яті.
  - `ESP_ERR_NVS_KEYS_NOT_INITIALIZED`: Розділ ключів знайдено, але він містить лише стерті байти `0xFF` (порожній сектор, ключі ще не згенеровано).
  - `ESP_ERR_INVALID_ARG`: Некоректні вхідні аргументи (наприклад, нульовий покажчик `cfg`).
  - `ESP_ERR_NOT_FOUND`: Розділ з підтипом `nvs_keys` відсутній у таблиці розділів пристрою.

#### 2. Генерація нових ключів: `nvs_flash_generate_keys`

:::tabs
```c
esp_err_t nvs_flash_generate_keys(
    const esp_partition_t* partition,
    nvs_sec_cfg_t* cfg
);
```
```cpp
#include "nvs_flash.h"

namespace esp_nvs {

[[nodiscard]] inline esp_err_t generate_security_keys(
    const esp_partition_t* partition,
    nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_generate_keys(partition, &cfg);
}

} // namespace esp_nvs
```
:::

- **Призначення:** Генерує 64 байти криптографічно стійких випадкових даних за допомогою вбудованого апаратного генератора випадкових чисел (TRNG, від англ. *True Random Number Generator*), записує їх у виділений розділ `nvs_keys` на Flash і повертає заповнену структуру `cfg` у RAM.
- **Параметри:**
  - `partition`: Вказівник на дескриптор розділу `nvs_keys`.
  - `cfg`: Вказівник на структуру `nvs_sec_cfg_t`, куди записуються новостворені ключі.
- **Повертає:**
  - `ESP_OK`: Ключі згенеровано й записано у Flash.
  - `ESP_ERR_INVALID_ARG`: Некоректні аргументи.
  - `ESP_ERR_FLASH_OP_FAIL`: Помилка фізичного запису у Flash-пам'ять.

#### 3. Безпечна ініціалізація розділу за замовчуванням: `nvs_flash_secure_init`

:::tabs
```c
esp_err_t nvs_flash_secure_init(nvs_sec_cfg_t* cfg);
```
```cpp
#include "nvs_flash.h"

namespace esp_nvs {

[[nodiscard]] inline esp_err_t secure_init_default(nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_secure_init(&cfg);
}

} // namespace esp_nvs
```
:::

- **Призначення:** Ініціалізує стандартний розділ NVS (з міткою `"nvs"`) у зашифрованому режимі з переданими ключами.
- **Параметри:**
  - `cfg`: Вказівник на заповнену структуру `nvs_sec_cfg_t`.
- **Повертає:**
  - `ESP_OK`: Розділ успішно ініціалізовано й змонтовано.
  - `ESP_ERR_NVS_NO_FREE_PAGES`: У розділі немає вільних сторінок (потрібне повне очищення через `nvs_flash_erase`).
  - `ESP_ERR_NVS_WRONG_ENCRYPTION`: Розділ уже містить дані, але вони зашифровані іншим ключем або були створені без шифрування.

#### 4. Безпечна ініціалізація довільного розділу: `nvs_flash_secure_init_partition`

:::tabs
```c
esp_err_t nvs_flash_secure_init_partition(
    const char* part_name,
    nvs_sec_cfg_t* cfg
);
```
```cpp
#include "nvs_flash.h"
#include <string_view>

namespace esp_nvs {

[[nodiscard]] inline esp_err_t secure_init_custom_partition(
    std::string_view partition_name,
    nvs_sec_cfg_t& cfg) noexcept
{
    return nvs_flash_secure_init_partition(partition_name.data(), &cfg);
}

} // namespace esp_nvs
```
:::

- **Призначення:** Ініціалізує кастомний розділ NVS з іменем `part_name` у зашифрованому режимі.
- **Параметри:**
  - `part_name`: Текстова назва розділу в таблиці розділів (наприклад, `"secret_nvs"`).
  - `cfg`: Вказівник на структуру `nvs_sec_cfg_t`.
- **Повертає:**
  - `ESP_OK`: Розділ успішно змонтовано.
  - `ESP_ERR_NOT_FOUND`: Розділ із назвою `part_name` не знайдено в таблиці.
  - `ESP_ERR_NVS_WRONG_ENCRYPTION`: Невідповідність ключа шифрування наявним даним.

#### 5. Деініціалізація та вивантаження сховища: `nvs_flash_deinit_partition`

:::tabs
```c
esp_err_t nvs_flash_deinit_partition(const char* partition_name);
```
```cpp
#include "nvs_flash.h"
#include <string_view>

namespace esp_nvs {

[[nodiscard]] inline esp_err_t deinit_custom_partition(
    std::string_view partition_name) noexcept
{
    return nvs_flash_deinit_partition(partition_name.data());
}

} // namespace esp_nvs
```
:::

- **Призначення:** Звільняє внутрішні динамічні ресурси драйвера NVS, пов'язані з розділом, та закриває доступ. Викликається перед перепрошиванням, зміною конфігурації або переведенням системи в режим глибокого сну.

---

### Конфігураційні опції Kconfig

У файлі `sdkconfig` або через візуальне меню `idf.py menuconfig` поведінку підсистеми шифрування NVS налаштовують такими параметрами:

| Опція Kconfig | Тип | Замовчування | Призначення та вплив на збірку |
|---|---|---|---|
| `CONFIG_NVS_ENCRYPTION` | boolean | `n` (вимкнено) | Дозволяє використання шифрування NVS та включає підтримку алгоритму AES-XTS у бінарний код прошивки |
| `CONFIG_NVS_KEY_PART_NAME` | string | `"nvs_key"` | Назва розділу в `partitions.csv`, який містить структуру ключів `nvs_sec_cfg_t` |
| `CONFIG_NVS_SEC_KEY_PROTECT_USING_HMAC` | boolean | `n` | Використовує апаратний периферійний модуль HMAC на мікроконтролерах ESP32-S2/S3/C3 для динамічної генерації ключів NVS безпосередньо з кремнієвого eFuse |

Якщо увімкнено параметр `CONFIG_NVS_SEC_KEY_PROTECT_USING_HMAC`, драйвер NVS автоматично налаштовує роботу з апаратним блоком HMAC. При цьому схема читання ключів через Flash MMU замінюється на прямий апаратний виклик генерації сеансового ключа з eFuse, що усуває потребу зберігати навіть зашифрований файл ключів на зовнішньому носії.

---

### Багатопоточність і потокобезпечність API

Усі функції роботи з NVS є повністю потокобезпечними (thread-safe) у середовищі операційної системи реального часу FreeRTOS. Усередині драйвера NVS доступ до кожної ініціалізованої структури розділу захищено рекурсивним м'ютексом FreeRTOS (`SemaphoreHandle_t`). 

Це гарантує, що кілька паралельних завдань FreeRTOS можуть одночасно викликати операції читання та запису:
- Якщо завдання А виконує тривалий запис блоба `nvs_set_blob()`, завдання Б, яке намагається виконати `nvs_get_u32()`, буде заблоковано на м'ютексі до завершення операції шифрування та оновлення бітової карти.
- Дескриптор `nvs_handle_t` безпечно передавати між різними функціями, проте закриття дескриптора через `nvs_close()` має виконуватися лише тоді, коли всі потоки завершили роботу з відповідним простором імен.

---

### Коди помилок шифрування NVS

Підсистема NVS повертає детальні діагностичні коди повернення, що дають змогу програмі точно розрізнити стан відсутності ключів, апаратні помилки запису та спроби використання чужого ключа:

| Назва макросу помилки | Числовий код | Пояснення причини виникнення та спосіб усунення |
|---|---|---|
| `ESP_ERR_NVS_KEYS_NOT_INITIALIZED` | `0x1116` | Розділ `nvs_keys` знайдено, але він містить лише неініціалізовані байти `0xFF`. Слід викликати функцію `nvs_flash_generate_keys()`. |
| `ESP_ERR_NVS_WRONG_ENCRYPTION` | `0x1117` | Спроба монтування розділу з ключем, відмінним від того, яким дані було зашифровано раніше, або спроба змонтувати відкритий NVS у зашифрованому режимі. |
| `ESP_ERR_NVS_PAGE_FULL` | `0x1102` | На поточній сторінці немає вільних слотів для розміщення нового запису. Викликає внутрішнє збирання сміття. |
| `ESP_ERR_NVS_NOT_INITIALIZED` | `0x1101` | Спроба відкрити простір імен `nvs_open()` до завершення процедури ініціалізації сховища. |
| `ESP_ERR_NVS_CORRUPT_KEY_PART` | `0x1118` | Пошкоджено дані у розділі ключів (не збігається контрольна сума або заголовок). Потрібне відновлення розділу. |

---

### Трасування та налагодження

Для діагностики процесу шифрування на рівні логів увімкніть детальний рівень логування для тегу `"nvs"`:

:::tabs
```c
esp_log_level_set("nvs", ESP_LOG_DEBUG);
```
```cpp
#include "esp_log.h"

inline void enable_nvs_debug_logs() noexcept
{
    esp_log_level_set("nvs", ESP_LOG_DEBUG);
}
```
:::

Під час ініціалізації в консолі з'являться докладні повідомлення про стан кожної сторінки, кількість знайдених чинних та застарілих слотів, а також підтвердження використання апаратного прискорювача AES.

---

### Повний приклад використання програмного інтерфейсу

Нижче показано цілісний модуль безпечної ініціалізації сховища та читання конфіденційного рядка з автоматичною обробкою першого старту.

:::tabs
```c
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string.h>

static const char* TAG = "nvs_sec_api";

esp_err_t init_encrypted_storage_c(const char* part_label)
{
    nvs_sec_cfg_t cfg;
    const esp_partition_t* key_part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA,
        ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
        NULL
    );
    if (!key_part) {
        ESP_LOGE(TAG, "Розділ nvs_keys не знайдено у таблиці розділів!");
        return ESP_ERR_NOT_FOUND;
    }

    esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
    if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
        ESP_LOGW(TAG, "Ключі відсутні (перший старт). Генеруємо нову конфігурацію...");
        err = nvs_flash_generate_keys(key_part, &cfg);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося отримати ключі шифрування: 0x%x", err);
        return err;
    }

    err = nvs_flash_secure_init_partition(part_label, &cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка монтування зашифрованого розділу %s: 0x%x", part_label, err);
    }

    // Очищення структури ключів у RAM
    explicit_bzero(&cfg, sizeof(cfg));
    return err;
}
```
```cpp
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string_view>
#include <system_error>
#include <algorithm>
#include <cstring>

namespace sys {

class EncryptedNvsStorage {
public:
    static esp_err_t init(std::string_view partition_label) noexcept {
        const esp_partition_t* key_part = esp_partition_find_first(
            ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
            nullptr
        );
        if (!key_part) {
            ESP_LOGE("NVS_CPP", "Розділ nvs_keys не знайдено!");
            return ESP_ERR_NOT_FOUND;
        }

        nvs_sec_cfg_t cfg{};
        esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
        if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
            ESP_LOGW("NVS_CPP", "Перший запуск: генерація ключів через TRNG...");
            err = nvs_flash_generate_keys(key_part, &cfg);
        }
        if (err != ESP_OK) {
            return err;
        }

        err = nvs_flash_secure_init_partition(partition_label.data(), &cfg);

        // Гарантоване затирання конфіденційних даних у пам'яті
        std::fill(reinterpret_cast<uint8_t*>(&cfg),
                  reinterpret_cast<uint8_t*>(&cfg) + sizeof(cfg), 0);
        return err;
    }
};

} // namespace sys
```
:::
