# ⚙️ Практика: створення компонента датчика з Kconfig та підтримкою C/C++

У виробничих прошивках на базі ESP-IDF апаратні драйвери та комунікаційні модулі ніколи не розміщують безпосередньо в каталозі `main/`. Утилітарний код, специфічний для сенсора, дисплея чи мережевого протоколу, виносять в автономний компонент у каталозі `components/`. Це забезпечує три ключові інженерні переваги: повну ізоляцію внутрішніх деталей реалізації від решти прошивки, можливість безболісного перенесення модуля між різними проєктами та винесення всіх апаратних налаштувань (номерів виводів GPIO, частоти шини, розмірів буферів пам'яті) у єдину систему конфігурації `menuconfig`.

Розглянемо практичний наскрізний приклад проектування такого компонента: цифрового датчика навколишнього середовища `sensor_driver`. Ми створимо декларативне дерево Kconfig із контролем діапазонів значень, зареєструємо таргет через `CMakeLists.txt`, реалізуємо потокобезпечний низькорівневий C-драйвер із захистом м'ютексом FreeRTOS та побудуємо ідіоматичний C++ клас-обгортку за принципом RAII з використанням типу результату `std::expected`.

---

## 1. Структура файлів компонента

Компонент розташовується у виділеній теці `components/sensor_driver/` з чітким розмежуванням відкритих інтерфейсів, внутрішньої реалізації та модульних тестів:

```text
components/sensor_driver/
├── CMakeLists.txt              # Скрипт реєстрації та декларації залежностей
├── Kconfig                     # Декларативне дерево меню для menuconfig
├── include/
│   ├── sensor_driver.h         # Публічний C-заголовок (експортується всім споживачам)
│   └── sensor_driver.hpp       # Публічна C++ RAII-обгортка для сучасного коду
├── src/
│   └── sensor_driver.c         # Внутрішня реалізація роботи з шиною I2C
└── test/
    └── test_sensor_driver.c    # Модульні тести на базі фреймворку Unity
```

Відокремлення каталогу `include/` від `src/` є фундаментальним архітектурним правилом ESP-IDF: усе, що розташоване в `include/`, потрапляє в публічний простір імен зовнішніх споживачів, тоді як вихідні файли та приватні заголовки в `src/` лишаються повністю прихованими від сторонніх модулів проєкту.

---

## 2. Опис опцій конфігурації: Kconfig

Файл `Kconfig` створює власне підменю в розділі «Component config» термінального інтерфейсу `menuconfig`. Тут задаються типи параметрів, межі допустимих значень та логічні зв'язки між окремими налаштуваннями:

```kconfig
menu "Конфігурація драйвера сенсора навколишнього середовища"

    config SENSOR_I2C_PORT
        int "Номер контролера I2C (0 або 1)"
        range 0 1
        default 0
        help
            Визначає номер апаратного периферійного блоку I2C мікроконтролера ESP32.

    config SENSOR_I2C_SDA_PIN
        int "GPIO пін лінії даних SDA"
        range 0 48
        default 21
        help
            Номер виводу GPIO, призначеного для двонаправленої лінії передачі даних I2C.

    config SENSOR_I2C_SCL_PIN
        int "GPIO пін лінії тактування SCL"
        range 0 48
        default 22
        help
            Номер виводу GPIO для генерації тактових імпульсів шини I2C.

    config SENSOR_I2C_FREQ_HZ
        int "Частота тактування шини I2C (в Герцах)"
        default 100000
        help
            Робоча швидкість шини. Стандартний режим: 100000 (100 кГц), швидкий: 400000 (400 кГц).

    config SENSOR_ENABLE_AVERAGING
        bool "Увімкнути фільтрацію шуму ковзним середнім"
        default y
        help
            Якщо активовано, драйвер накопичує виміри у кільцевому буфері та повертає усереднене значення.

    config SENSOR_SAMPLE_COUNT
        int "Кількість зразків для усереднення"
        depends on SENSOR_ENABLE_AVERAGING
        range 2 32
        default 8
        help
            Глибина вікна усереднення для згладжування випадкових сплесків вимірюваної величини.

endmenu
```

Директива `depends on SENSOR_ENABLE_AVERAGING` гарантує, що пункт вибору кількості зразків `SENSOR_SAMPLE_COUNT` з'явиться в інтерфейсі користувача лише тоді, коли увімкнено базовий прапорець `SENSOR_ENABLE_AVERAGING`. Це усуває можливість некоректного налаштування залежних параметрів при вимкненій підсистемі фільтрації.

---

## 3. Реєстрація компонента: CMakeLists.txt

Файл `components/sensor_driver/CMakeLists.txt` викликає макрос системи збірки, вказуючи вихідні файли, публічний каталог заголовків та приватні системні залежності:

```cmake
idf_component_register(
    SRCS
        "src/sensor_driver.c"
    INCLUDE_DIRS
        "include"
    PRIV_REQUIRES
        driver
        esp_timer
        freertos
)
```

Зверніть увагу: ми використовуємо `PRIV_REQUIRES` для системних бібліотек `driver` та `freertos`. Це означає, що компонент `main`, підключаючи наш заголовок `sensor_driver.h`, не отримуватиме прихованого доступу до сирих регістрів периферії I2C. Якщо коду в `main` колись знадобиться безпосередня робота з I2C, він буде змушений задекларувати цю залежність явно у власному `CMakeLists.txt`. Такий підхід запобігає «невидимим» транзитивним включенням і гарантує строгу модульність системи.

---

## 4. Публічний інтерфейс та реалізація

Заголовок `include/sensor_driver.h` оголошує чистий C-інтерфейс із захистом простору імен та строгою типізацією кодів помилок `esp_err_t`. Додатково надається C++ обгортка `include/sensor_driver.hpp`, яка інкапсулює життєвий цикл ресурсу та обробку станів:

:::tabs
```c
/* include/sensor_driver.h (C) */
#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "sdkconfig.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float temperature_celsius;
    float humidity_percent;
    uint32_t timestamp_ms;
} sensor_reading_t;

/**
 * @brief Ініціалізація шини I2C, створення м'ютекса та калібрування сенсора.
 * @return ESP_OK у разі успіху або відповідний код помилки esp_err_t.
 */
esp_err_t sensor_driver_init(void);

/**
 * @brief Потокобезпечне зчитування фізичних параметрів із сенсора.
 * @param[out] out_reading Вказівник на структуру для збереження результату.
 */
esp_err_t sensor_driver_read(sensor_reading_t *out_reading);

/**
 * @brief Зупинка роботи, видалення драйвера I2C та вивільнення пам'яті.
 */
esp_err_t sensor_driver_deinit(void);

#ifdef __cplusplus
}
#endif
```
```cpp
// include/sensor_driver.hpp (C++ RAII Wrapper)
#pragma once

#include <expected>
#include <string_view>
#include <chrono>
#include "sensor_driver.h"

namespace sensors {

class EnvironmentSensor {
public:
    EnvironmentSensor() {
        const esp_err_t err = sensor_driver_init();
        is_initialized_ = (err == ESP_OK);
    }

    ~EnvironmentSensor() {
        if (is_initialized_) {
            sensor_driver_deinit();
        }
    }

    // Заборона копіювання апаратного ресурсу
    EnvironmentSensor(const EnvironmentSensor&) = delete;
    EnvironmentSensor& operator=(const EnvironmentSensor&) = delete;

    // Підтримка переміщення (move semantics)
    EnvironmentSensor(EnvironmentSensor&& other) noexcept
        : is_initialized_(other.is_initialized_) {
        other.is_initialized_ = false;
    }

    EnvironmentSensor& operator=(EnvironmentSensor&& other) noexcept {
        if (this != &other) {
            if (is_initialized_) {
                sensor_driver_deinit();
            }
            is_initialized_ = other.is_initialized_;
            other.is_initialized_ = false;
        }
        return *this;
    }

    [[nodiscard]] std::expected<sensor_reading_t, esp_err_t> read() const {
        if (!is_initialized_) {
            return std::unexpected(ESP_ERR_INVALID_STATE);
        }
        sensor_reading_t data{};
        const esp_err_t err = sensor_driver_read(&data);
        if (err != ESP_OK) {
            return std::unexpected(err);
        }
        return data;
    }

    [[nodiscard]] bool is_ready() const noexcept {
        return is_initialized_;
    }

private:
    bool is_initialized_{false};
};

} // namespace sensors
```
:::

Реалізація драйвера в `src/sensor_driver.c` використовує згенеровані через Kconfig макроси `CONFIG_SENSOR_*` і гарантує потокобезпеку за допомогою м'ютекса FreeRTOS:

:::tabs
```c
/* src/sensor_driver.c (C) */
#include "sensor_driver.h"
#include "sdkconfig.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/i2c.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static const char *TAG = "sensor_driver";
static bool s_is_init = false;
static SemaphoreHandle_t s_lock = NULL;

esp_err_t sensor_driver_init(void) {
    if (s_is_init) {
        return ESP_OK;
    }

    s_lock = xSemaphoreCreateMutex();
    if (!s_lock) {
        return ESP_ERR_NO_MEM;
    }

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = CONFIG_SENSOR_I2C_SDA_PIN,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = CONFIG_SENSOR_I2C_SCL_PIN,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = CONFIG_SENSOR_I2C_FREQ_HZ,
    };

    esp_err_t err = i2c_param_config(CONFIG_SENSOR_I2C_PORT, &conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації I2C: %s", esp_err_to_name(err));
        vSemaphoreDelete(s_lock);
        s_lock = NULL;
        return err;
    }

    err = i2c_driver_install(CONFIG_SENSOR_I2C_PORT, conf.mode, 0, 0, 0);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення драйвера I2C: %s", esp_err_to_name(err));
        vSemaphoreDelete(s_lock);
        s_lock = NULL;
        return err;
    }

    s_is_init = true;
    ESP_LOGI(TAG, "Драйвер ініціалізовано: Port=%d, SDA=%d, SCL=%d, Частота=%d Гц",
             CONFIG_SENSOR_I2C_PORT, CONFIG_SENSOR_I2C_SDA_PIN, 
             CONFIG_SENSOR_I2C_SCL_PIN, CONFIG_SENSOR_I2C_FREQ_HZ);
    return ESP_OK;
}

esp_err_t sensor_driver_read(sensor_reading_t *out_reading) {
    if (!s_is_init || !out_reading) {
        return ESP_ERR_INVALID_STATE;
    }

    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(100)) != pdTRUE) {
        return ESP_ERR_TIMEOUT;
    }

    /* Моделювання вичитування даних через транзакцію I2C */
    out_reading->temperature_celsius = 24.2f;
    out_reading->humidity_percent = 52.5f;
    out_reading->timestamp_ms = (uint32_t)(esp_timer_get_time() / 1000ULL);

#if CONFIG_SENSOR_ENABLE_AVERAGING
    ESP_LOGD(TAG, "Ковзне середнє за %d зразками застосовано", CONFIG_SENSOR_SAMPLE_COUNT);
#endif

    xSemaphoreGive(s_lock);
    return ESP_OK;
}

esp_err_t sensor_driver_deinit(void) {
    if (!s_is_init) {
        return ESP_OK;
    }

    if (xSemaphoreTake(s_lock, pdMS_TO_TICKS(500)) == pdTRUE) {
        i2c_driver_delete(CONFIG_SENSOR_I2C_PORT);
        s_is_init = false;
        xSemaphoreGive(s_lock);
        vSemaphoreDelete(s_lock);
        s_lock = NULL;
        ESP_LOGI(TAG, "Драйвер сенсора успішно деініціалізовано.");
        return ESP_OK;
    }

    return ESP_ERR_TIMEOUT;
}
```
```cpp
// Приклад споживання в main/main.cpp (C++)
#include <iostream>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sensor_driver.hpp"

static const char *TAG = "main_app";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Запуск C++ вузла моніторингу...");

    // Створення RAII-екземпляра сенсора
    sensors::EnvironmentSensor sensor;

    if (!sensor.is_ready()) {
        ESP_LOGE(TAG, "Помилка: не вдалося ініціалізувати апаратний сенсор");
        return;
    }

    for (int i = 0; i < 3; ++i) {
        auto result = sensor.read();
        if (result.has_value()) {
            const auto& data = result.value();
            std::cout << "[Вимір #" << (i + 1) << " | " << data.timestamp_ms << " мс] "
                      << "Температура: " << data.temperature_celsius << " °C, "
                      << "Вологість: " << data.humidity_percent << " %\n";
        } else {
            ESP_LOGW(TAG, "Збій опитування датчика, помилка: %d", result.error());
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    ESP_LOGI(TAG, "Завершення сесії: деініціалізація відбудеться автоматично через деструктор RAII.");
}
```
:::

---

## 5. Модульне тестування компонента через Unity

ESP-IDF має вбудовану систему модульного тестування на базі фреймворку Unity. Якщо всередині каталогу компонента створити підкаталог `test/` із власним файлом `CMakeLists.txt` та вихідними кодами тестів, система збірки автоматично виявляє тестові кейси під час складання спеціального застосунку юніт-тестів:

:::tabs
```c
/* components/sensor_driver/test/test_sensor_driver.c (C) */
#include "unity.h"
#include "sensor_driver.h"

TEST_CASE("sensor_driver ініціалізація та деініціалізація", "[sensor]") {
    TEST_ASSERT_EQUAL(ESP_OK, sensor_driver_init());
    TEST_ASSERT_EQUAL(ESP_OK, sensor_driver_deinit());
}

TEST_CASE("sensor_driver зчитування даних без ініціалізації повертає помилку", "[sensor]") {
    sensor_reading_t reading;
    TEST_ASSERT_EQUAL(ESP_ERR_INVALID_STATE, sensor_driver_read(&reading));
}
```
```cpp
// components/sensor_driver/test/test_sensor_driver.cpp (C++)
#include "unity.h"
#include "sensor_driver.hpp"

TEST_CASE("EnvironmentSensor RAII життєвий цикл та зчитування", "[sensor][cpp]") {
    sensors::EnvironmentSensor sensor;
    TEST_ASSERT_TRUE(sensor.is_ready());

    const auto result = sensor.read();
    TEST_ASSERT_TRUE(result.has_value());
    TEST_ASSERT_FLOAT_WITHIN(50.0f, 25.0f, result.value().temperature_celsius);
}
```
:::

Для запуску тестів у середовищі розробки ESP-IDF використовується команда збірки тестового таргету або спеціальний допоміжний тестовий проєкт `$IDF_PATH/tools/unit-test-app`. Тестовий раннер компілює всі знайдені в дереві компонентів тестові сценарії, прошиває їх у пристрій і виводить інтерактивне меню вибору тестів через послідовний порт UART. Це дозволяє ізольовано верифікувати логіку кожного драйвера, перевіряти роботу крайових випадків та відловлювати витоки динамічної пам'яті за допомогою макросів `TEST_ASSERT` без необхідності запуску всієї громіздкої прошивки пристрою.

---

## 6. Перевірка конфігурації та налагодження

Під час зміни параметрів у `menuconfig` важливо вміти перевірити, чи дійшли нові значення до згенерованих файлів:

1. **Перевірка заголовка `sdkconfig.h`:**  
   Після виконання команди `idf.py reconfigure` відкрийте файл `build/config/sdkconfig.h` і знайдіть макрос `CONFIG_SENSOR_I2C_SDA_PIN`. Переконайтеся, що значення відповідає зміненому виводу GPIO.
2. **Перевірка згенерованого CMake-файлу `sdkconfig.cmake`:**  
   Перевірте `build/config/sdkconfig.cmake`. Якщо в ньому присутній рядок `set(CONFIG_SENSOR_ENABLE_AVERAGING 1)`, система збірки коректно розпізнала булевий прапорець і передасть його всім підлеглим модулям.
3. **Діагностика логів ініціалізації:**  
   Під час запуску `idf.py monitor` зверніть увагу на інформаційні рядки від тегу `sensor_driver`. Драйвер друкує точні номери виводів та швидкість шини, що дозволяє миттєво виявити помилки розпіновки плати ще до фізичного підключення логічного аналізатора.

---

## 7. Типові інженерні пастки

1. **Невизначений макрос через пропущений `#include "sdkconfig.h"`**:  
   Якщо розробник звертається до `CONFIG_SENSOR_I2C_PORT`, але забув підключити файл `sdkconfig.h`, компілятор у виразах `#if CONFIG_SENSOR_ENABLE_AVERAGING` тихо підставить нуль `0`, що призведе до неочевидного вимкнення функції без жодного попередження компілятора. Завжди явно включайте `sdkconfig.h` у файли реалізації.

2. **Конфлікт номерів GPIO під час роботи з SPI Flash**:  
   Якщо в меню `menuconfig` для пінів `SENSOR_I2C_SDA_PIN` або `SENSOR_I2C_SCL_PIN` помилково вказати виводи GPIO 6–11 (на класичному ESP32), мікроконтролер перестане завантажуватися і піде у вічний цикл паніки. Ці виводи апаратно підключені до внутрішньої мікросхеми SPI Flash пам'яті. У Kconfig рекомендується додавати текстову довідку з попередженням про зарезервовані виводи конкретного кристала.

3. **Скидання налаштувань при зміні цільового чипа**:  
   Команда `idf.py set-target esp32s3` повністю перестворює `sdkconfig`, очищуючи всі специфічні налаштування, якщо вони не були зафіксовані у файлі `sdkconfig.defaults`. Перед перемиканням архітектур завжди зберігайте унікальні опції вашого компонента у файлі базових налаштувань проєкту.
