# ⚙️ Тестування драйвера на ПК за допомогою Mock-транспорту

Написання драйвера зовнішнього чипа традиційно вважається найбільш залежною від заліза частиною розробки вбудованих систем. За наївного підходу інженер змушений прошивати мікроконтролер, підключати плату з датчиком через дроти, запускати налагоджувач і вручну струшувати плату на столі, спостерігаючи за виводом у термінал. Якщо шина дає збій, важко визначити, що саме відмовило: фізичний контакт макетної плати, підтягувальні резистори, конфігурація периферії мікроконтролера чи логічна помилка у формулі бітових масок драйвера.

Ізоляція драйвера через таблицю функцій зворотного виклику (Platform Bus Abstraction) повністю усуває залежність від фізичного заліза. Це дозволяє скомпілювати код драйвера звичайним нативним компілятором для комп'ютера розробника (`gcc`, `clang`, `MSVC`) і покрити всю регістрову логіку, граничні випадки, відмовостійкість та математику перетворення в одиниці SI швидкими детермінованими модульними тестами (Unit Tests).

У промислових проєктах такий підхід є стандартом: драйвери пишуться за методологією розробки через тестування (TDD), а повний набір перевірок інтегрується в конвеєр неперервної інтеграції (CI/CD). Будь-яка зміна в бітових масках або логіці перетворення відразу валідується сотнями тестових сценаріїв за мікросекунди без залучення реальних апаратних стендів.

---

## 1. Архітектура віртуального апаратного мока (Virtual Hardware Mock)

Мок-транспорт імітує поведінку фізичної кремнієвої мікросхеми в оперативній пам'яті комп'ютера. Він складається з чотирьох ключових блоків:

1. **Регістрова пам'ять віртуального чипа (`uint8_t registers[128]`):** масив байтів, що повністю відтворює адресний простір реального датчика. При зчитуванні регістру мок повертає відповідний елемент масиву.
2. **Журнал транзакцій запису (Write History Log):** масив записів, у який фіксується кожна спроба запису (адреса регістру, значення байта, порядковий номер транзакції). Це дозволяє перевірити, чи правильні бітові маски застосовує функція `chip_init()` або `chip_set_range()`.
3. **Генератор апаратних збоїв (Fault Injection Engine):** лічильники та прапорці, які дозволяють заздалегідь запрограмувати відмову шини: повернення помилки NACK, обрив передачі на конкретному байті або спотворення ідентифікатора в регістрі `WHO_AM_I`.
4. **Генератор синтетичних фізичних даних:** допоміжні функції, які дозволяють тесту ввести сирі відліки прискорення (наприклад, синусоїду або калібрувальне значення `1.0g` по осі Z) і перевірити, як драйвер обробить ці дані.

```
+-------------------------------------------------------------+
|                  Тестовий сценарій (x86_64)                 |
+-------------------------------------------------------------+
                              |
       1. Виклик API          |        2. Звірка результату
       (chip_init, read_si)   |        (assert(status == OK))
                              v
+-------------------------------------------------------------+
|                   Драйвер чипа (Чистий C/C++)               |
+-------------------------------------------------------------+
                              |
       3. bus_read() / bus_write() (Таблиця callback-ів)
                              v
+-------------------------------------------------------------+
|                 Мок-транспорт (Mock Bus Driver)             |
|  - Масив регістрів: uint8_t mock_regs[0x7F]                 |
|  - Журнал запису:   vector<WriteLogEntry>                   |
|  - Ін'єкція збоїв:  mock_inject_read_failures(count)        |
|  - Імітація даних:  mock_set_accel_raw(x, y, z)             |
+-------------------------------------------------------------+
```

---

## 2. Реалізація Mock-транспорту та тестового стенду

:::tabs
```c
// C99: Реалізація емулятора шини та віртуального чипа для Unit-тестів
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

#define MOCK_REG_COUNT 128
#define MOCK_MAX_WRITE_LOG 64

// Фіктивні адреси регістрів еталонного акселерометра
#define REG_WHO_AM_I     0x0F
#define REG_CTRL_REG1    0x20
#define REG_CTRL_REG4    0x23
#define REG_STATUS_REG   0x27
#define REG_OUT_X_L      0x28

#define EXPECTED_CHIP_ID 0x33

typedef struct {
    uint8_t reg;
    uint8_t val;
} mock_write_entry_t;

typedef struct {
    uint8_t registers[MOCK_REG_COUNT];
    mock_write_entry_t write_log[MOCK_MAX_WRITE_LOG];
    uint32_t write_count;
    
    // Поля ін'єкції несправностей
    int32_t fail_reads_countdown;
    int32_t fail_writes_countdown;
    bool nack_device_address;
} mock_bus_ctx_t;

// Очищення та скидання стану мока
void mock_bus_reset(mock_bus_ctx_t *mock) {
    memset(mock->registers, 0, sizeof(mock->registers));
    mock->write_count = 0;
    mock->fail_reads_countdown = 0;
    mock->fail_writes_countdown = 0;
    mock->nack_device_address = false;
    
    // Встановлення заводського ідентифікатора за замовчуванням
    mock->registers[REG_WHO_AM_I] = EXPECTED_CHIP_ID;
}

// Запис сирих 16-бітних відліків у регістри даних віртуального датчика
void mock_set_raw_xyz(mock_bus_ctx_t *mock, int16_t x, int16_t y, int16_t z) {
    mock->registers[REG_OUT_X_L + 0] = (uint8_t)(x & 0xFF);
    mock->registers[REG_OUT_X_L + 1] = (uint8_t)((x >> 8) & 0xFF);
    mock->registers[REG_OUT_X_L + 2] = (uint8_t)(y & 0xFF);
    mock->registers[REG_OUT_X_L + 3] = (uint8_t)((y >> 8) & 0xFF);
    mock->registers[REG_OUT_X_L + 4] = (uint8_t)(z & 0xFF);
    mock->registers[REG_OUT_X_L + 5] = (uint8_t)((z >> 8) & 0xFF);
    
    // Встановлення прапорця готовності нових даних ZYXDA (біт 3 у STATUS_REG)
    mock->registers[REG_STATUS_REG] |= (1U << 3);
}

// Функція читання шини для драйвера
int32_t mock_bus_read(void *user_ctx, uint8_t reg_addr, uint8_t *data, uint16_t len) {
    mock_bus_ctx_t *mock = (mock_bus_ctx_t *)user_ctx;
    if (mock->nack_device_address) return -2; // Симуляція помилки адресації
    if (mock->fail_reads_countdown > 0) {
        mock->fail_reads_countdown--;
        return -2; // Симуляція апаратного збою
    }
    
    for (uint16_t i = 0; i < len; ++i) {
        uint8_t current_reg = (uint8_t)((reg_addr + i) & 0x7F);
        data[i] = mock->registers[current_reg];
    }
    return 0;
}

// Функція запису шини для драйвера
int32_t mock_bus_write(void *user_ctx, uint8_t reg_addr, const uint8_t *data, uint16_t len) {
    mock_bus_ctx_t *mock = (mock_bus_ctx_t *)user_ctx;
    if (mock->nack_device_address) return -2;
    if (mock->fail_writes_countdown > 0) {
        mock->fail_writes_countdown--;
        return -2;
    }
    
    for (uint16_t i = 0; i < len; ++i) {
        uint8_t current_reg = (uint8_t)((reg_addr + i) & 0x7F);
        mock->registers[current_reg] = data[i];
        
        if (mock->write_count < MOCK_MAX_WRITE_LOG) {
            mock->write_log[mock->write_count].reg = current_reg;
            mock->write_log[mock->write_count].val = data[i];
            mock->write_count++;
        }
    }
    return 0;
}

void mock_delay_ms(uint32_t ms) {
    // В юніт-тестах затримка виконується миттєво для максимальної швидкості
    (void)ms;
}
```
```cpp
// C++20: Mock-транспорт на базі концептів та перевірки інваріантів
#include <cstdint>
#include <array>
#include <vector>
#include <span>
#include <expected>
#include <cassert>
#include <iostream>

namespace embedded::testing {

enum class Status : std::int32_t {
    Ok = 0,
    CommFail = -2
};

struct WriteLogEntry {
    std::uint8_t reg;
    std::uint8_t val;
};

class MockTransport {
public:
    static constexpr std::uint8_t RegWhoAmI = 0x0F;
    static constexpr std::uint8_t RegOutXL  = 0x28;
    static constexpr std::uint8_t RegStatus = 0x27;
    static constexpr std::uint8_t ExpectedChipId = 0x33;

    constexpr MockTransport() noexcept {
        reset();
    }

    void reset() noexcept {
        registers_.fill(0);
        write_log_.clear();
        fail_reads_count_ = 0;
        fail_writes_count_ = 0;
        nack_device_address_ = false;
        registers_[RegWhoAmI] = ExpectedChipId;
    }

    void setRawXyz(std::int16_t x, std::int16_t y, std::int16_t z) noexcept {
        registers_[RegOutXL + 0] = static_cast<std::uint8_t>(x & 0xFF);
        registers_[RegOutXL + 1] = static_cast<std::uint8_t>((x >> 8) & 0xFF);
        registers_[RegOutXL + 2] = static_cast<std::uint8_t>(y & 0xFF);
        registers_[RegOutXL + 3] = static_cast<std::uint8_t>((y >> 8) & 0xFF);
        registers_[RegOutXL + 4] = static_cast<std::uint8_t>(z & 0xFF);
        registers_[RegOutXL + 5] = static_cast<std::uint8_t>((z >> 8) & 0xFF);
        registers_[RegStatus] |= (1U << 3); // ZYXDA data ready flag
    }

    void injectReadFailures(std::int32_t count) noexcept {
        fail_reads_count_ = count;
    }

    void setNackAddress(bool enable) noexcept {
        nack_device_address_ = enable;
    }

    Status read(std::uint8_t reg, std::span<std::uint8_t> buffer) noexcept {
        if (nack_device_address_) return Status::CommFail;
        if (fail_reads_count_ > 0) {
            --fail_reads_count_;
            return Status::CommFail;
        }

        for (std::size_t i = 0; i < buffer.size(); ++i) {
            std::uint8_t current_reg = static_cast<std::uint8_t>((reg + i) & 0x7F);
            buffer[i] = registers_[current_reg];
        }
        return Status::Ok;
    }

    Status write(std::uint8_t reg, std::span<const std::uint8_t> buffer) noexcept {
        if (nack_device_address_) return Status::CommFail;
        if (fail_writes_count_ > 0) {
            --fail_writes_count_;
            return Status::CommFail;
        }

        for (std::size_t i = 0; i < buffer.size(); ++i) {
            std::uint8_t current_reg = static_cast<std::uint8_t>((reg + i) & 0x7F);
            registers_[current_reg] = buffer[i];
            write_log_.push_back({current_reg, buffer[i]});
        }
        return Status::Ok;
    }

    void delay_ms(std::uint32_t) noexcept {
        // Миттєве виконання в юніт-тестах
    }

    [[nodiscard]] const std::vector<WriteLogEntry>& writeLog() const noexcept {
        return write_log_;
    }

    [[nodiscard]] std::uint8_t readRegister(std::uint8_t reg) const noexcept {
        return registers_[reg & 0x7F];
    }

private:
    std::array<std::uint8_t, 128> registers_{};
    std::vector<WriteLogEntry> write_log_{};
    std::int32_t fail_reads_count_{0};
    std::int32_t fail_writes_count_{0};
    bool nack_device_address_{false};
};

} // namespace embedded::testing
```
:::

---

## 3. Сценарії модульного тестування драйвера

Маючи повнофункціональний Mock-транспорт, ми створюємо тестовий набір, що перевіряє всі критичні шляхи виконання програми без жодного підключення фізичної плати.

### Тест 1: Перевірка правильної ініціалізації та конфігурації регістрів
Перевіряє, що функція ініціалізації:
1. Зчитує регістр `WHO_AM_I` та переконується у відповідності заводського ID.
2. Програмує біти частоти вибірки (ODR) та вмикає всі три осі X, Y, Z.
3. Активує режим блокування оновлення блоку даних (BDU) для запобігання розриву байтів між читаннями MSB і LSB.

### Тест 2: Захист від некоректного ідентифікатора (Invalid Chip ID & NACK)
Перевіряє, що якщо регістр `WHO_AM_I` повертає значення `0x00` або `0xFF` (наприклад, чип іншої ревізії або підроблений аналог), функція негайно повертає код `DEVICE_NOT_FOUND`, не намагаючись записувати конфігураційні регістри.

### Тест 3: Точність перетворення сирих кодів у фізичні величини SI
Перевіряє роботу математичного апарату:
* При встановленому діапазоні `±2g` код `+16384` (половина повної 16-бітної шкали) перетворюється на `+9.80665 м/с²` (1g) з високою точністю.
* Від'ємні числа у доповняльному двійковому коді (`-16384`) коректно поширюють знаковий біт (Sign Extension) і перетворюються на `-9.80665 м/с²`.

### Тест 4: Механізм автоматичних повторних спроб (Retries & Transient Faults)
Симулюється короткочасна завада: перші дві спроби читання шини завершуються апаратною помилкою `COMM FAIL`, а третя повертає коректні дані. Тест переконується, що драйвер успішно відновлює комунікацію і повертає статус успіху.

:::tabs
```c
// C99: Виконання повного тестового набору в main() на ПК
int main(void) {
    mock_bus_ctx_t mock;
    chip_dev_t dev;
    chip_bus_ops_t bus_ops = {
        .read = mock_bus_read,
        .write = mock_bus_write,
        .delay_ms = mock_delay_ms
    };
    
    printf("=== Запуск Unit-тестів драйвера чипа на ПК ===\n");
    
    // --- Тест 1: Успішна ініціалізація ---
    mock_bus_reset(&mock);
    chip_status_t status = chip_init(&dev, &bus_ops, &mock, 0x19);
    assert(status == CHIP_STATUS_OK);
    assert(dev.is_initialized == true);
    assert(mock.write_count >= 2); // Має бути записано CTRL_REG1 та CTRL_REG4
    printf("[PASS] Тест 1: Успішна ініціалізація та налаштування регістрів\n");
    
    // --- Тест 2: Помилка WHO_AM_I ---
    mock_bus_reset(&mock);
    mock.registers[REG_WHO_AM_I] = 0x00; // Некоректний ID
    status = chip_init(&dev, &bus_ops, &mock, 0x19);
    assert(status == CHIP_ERR_DEVICE_NOT_FOUND);
    assert(dev.is_initialized == false);
    printf("[PASS] Тест 2: Захист від некоректного ідентифікатора чипа\n");
    
    // --- Тест 3: Точність конвертації в SI ---
    mock_bus_reset(&mock);
    chip_init(&dev, &bus_ops, &mock, 0x19);
    chip_set_range(&dev, 2); // Встановлюємо діапазон ±2g
    
    // 1g вздовж осі Z (16384 відліків для 16-бітного формату 2g)
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    chip_axes_data_si_t accel;
    status = chip_read_sample_si(&dev, &accel);
    assert(status == CHIP_STATUS_OK);
    
    // Перевірка прискорення: X=0, Y=0, Z ≈ 9.81 м/с²
    assert(accel.x >= -0.01f && accel.x <= 0.01f);
    assert(accel.y >= -0.01f && accel.y <= 0.01f);
    assert(accel.z >= 9.75f && accel.z <= 9.85f);
    printf("[PASS] Тест 3: Точність перетворення коду у фізичні одиниці SI (м/с²)\n");
    
    // --- Тест 4: Стійкість до короткочасних завад (Retries) ---
    mock_bus_reset(&mock);
    chip_init(&dev, &bus_ops, &mock, 0x19);
    mock_set_raw_xyz(&mock, 0, 0, 16384);
    
    // Ін'єктуємо 2 послідовні збої шини (драйвер має виконати 3 спроби і виграти)
    mock.fail_reads_countdown = 2;
    status = chip_read_sample_si(&dev, &accel);
    assert(status == CHIP_STATUS_OK);
    printf("[PASS] Тест 4: Відпрацювання повторних спроб (Retries) при збоях шини\n");
    
    printf("\n>>> Усі модульні тести успішно пройдені за 1.2 мс! <<<\n");
    return 0;
}
```
```cpp
// C++20: Запуск тестів з сучасними асертами та перевірками статусів
int main() {
    using namespace embedded::testing;
    using namespace embedded::drivers;

    std::cout << "=== Запуск C++20 Unit-тестів драйвера чипа ===\n";

    MockTransport mock;
    ChipSensor sensor(mock, 0x19);

    // --- Тест 1: Успішна ініціалізація ---
    mock.reset();
    auto init_status = sensor.init();
    assert(init_status == Status::Ok);
    assert(sensor.isInitialized());
    assert(mock.writeLog().size() >= 2);
    std::cout << "[PASS] Тест 1: Ініціалізація та запис конфігурації\n";

    // --- Тест 2: Некоректний ідентифікатор пристрою ---
    mock.reset();
    mock.write(MockTransport::RegWhoAmI, std::array<const std::uint8_t, 1>{0xAA});
    auto fail_status = sensor.init();
    assert(fail_status == Status::DeviceNotFound);
    std::cout << "[PASS] Тест 2: Виявлення невідповідності ідентифікатора чипа\n";

    // --- Тест 3: Читання та фізичне масштабування SI ---
    mock.reset();
    sensor.init();
    sensor.setRange(2); // ±2g
    mock.setRawXyz(0, 0, 16384); // 1g по осі Z

    auto sample = sensor.readAccelerationSi();
    assert(sample.has_value());
    assert(sample->x >= -0.01F && sample->x <= 0.01F);
    assert(sample->y >= -0.01F && sample->y <= 0.01F);
    assert(sample->z >= 9.75F && sample->z <= 9.85F);
    std::cout << "[PASS] Тест 3: Конвертація в м/с² та перевірка границь похибки\n";

    // --- Тест 4: Автоматичне відновлення після короткочасного збою ---
    mock.reset();
    sensor.init();
    mock.setRawXyz(0, 0, 16384);
    mock.injectReadFailures(2);

    auto recovered_sample = sensor.readAccelerationSi();
    assert(recovered_sample.has_value());
    std::cout << "[PASS] Тест 4: Успішне відновлення через механізм повторів (Retries)\n";

    std::cout << "\n>>> Усі C++20 тести успішно виконані на комп'ютері розробника! <<<\n";
    return 0;
}
```
:::

---

## 4. Практичні переваги розробки драйверів через Mock-транспорт

Використання віртуального апаратного мока докорінно змінює культуру розробки та якість коду вбудованих систем:

1. **Миттєвий зворотний зв'язок у CI/CD:** Тестовий набір із сотень сценаріїв виконується менш ніж за 10 мілісекунд у середовищі неперервної інтеграції (GitHub Actions, GitLab CI), унеможливлюючи появу прихованих регресій коду при рефакторингу.
2. **100% покриття рідкісних аварійних сценаріїв:** На фізичній платі надзвичайно важко відтворити ситуацію, коли шина збивається рівно на 3-му байті пакетного читання 128-байтного FIFO-буфера або коли біт готовності даних не встановлюється через зависання аналогового ядра сенсора. На моці це налаштовується одним рядком коду: `mock.fail_reads_countdown = 3;`.
3. **Паралельна розробка заліза та прошивки:** Програмна частина може бути повністю спроєктована, протестована та задокументована ще до того, як фабрика виготовить перші дослідні зразки друкованих плат.
4. **Висока швидкість виконання Fuzzing-тестів:** Можна запустити мільйони ітерацій випадкових байтів у регістри мока (Fuzz-тестування), щоб переконатися, що жодна комбінація пошкоджених даних не призведе до ділення на нуль або переповнення буфера в математичному блоці драйвера.
