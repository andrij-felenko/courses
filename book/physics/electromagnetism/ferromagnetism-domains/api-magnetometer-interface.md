# 📋 Інтерфейс та регістри цифрового тривісного магнітометра

Цей довідник описує апаратний та програмний інтерфейс, регістрову карту, протоколи зв'язку I2C/SPI та послідовність керування цифровим тривісним анізотропно-магніторезистивним магнітометром (на прикладі MMC5983MA / AK8963), який використовує розмагнічувальні імпульси SET/RESET для усунення залишкового доменного намагнічування та компенсації температурного зсуву нуля.

## Апаратний інтерфейс та принцип SET/RESET імпульсів

Цифровий тривісний магнітометр базується на використанні трьох тонкоплівкових анізотропно-магніторезистивних (AMR) мостових датчиків, орієнтованих строго уздовж осій `X`, `Y`, `Z`. Під дією зовнішнього магнітного поля `B` внутрішні домени в тонких плівках пермалою (`Ni-Fe` товщиною близько 30 нм) повертаються, що викликає зміну електричного опору мосту Уітстона за законом `R(θ) = R_0 + ΔR · cos²(θ)`.

Для забезпечення високої роздільної здатності (до 18 біт, еквівалентно `0.25` мГаусс на LSB) та компенсації температурного дрейфу й паразитичного залишкового намагнічування доменів у сенсорі застосовується технологія періодичного перемагнічування імпульсами **SET** та **RESET**:

- **Імпульс SET:** Внутрішній накачувач заряду розряджає вбудований конденсатор через низькоомне металеве мікрокільце, розташоване безпосередньо над AMR-містком. Короткочасний потужний імпульс струму амплітудою близько 1 Ампера та тривалістю 10 мікросекунд створює локальне магнітне поле понад 100 Ерстед. Це поле примусово орієнтує всі магнітні домени тонкої плівки пермалою в одному напрямку вздовж легкої осі.
- **Імпульс RESET:** Імпульс струму протилежної полярності перемагнічує домени в протилежний напрямок на 180 градусів.

Різниця двох послідовних вимірювань `(V_SET - V_RESET) / 2` повністю виключає паразитичне зміщення нуля (офсет) вимірювального підсилювача та усуває залишкову намагніченість доменів датчика, викликувану впливом сильних зовнішніх полів.

### Призначення виводів (Pinout)

| Вивід | Назва | Тип | Опис |
| :--- | :--- | :--- | :--- |
| 1 | VDD | Живлення | Аналогове живлення основної схеми (1.8 В ... 3.6 В) |
| 2 | VDDIO | Живлення | Живлення інтерфейсів вводу/виводу SPI/I2C (1.2 В ... VDD) |
| 3 | GND | Земля | Спільний нульовий провід |
| 4 | SCL / SPC | Вхід | Тактова лінія I2C (SCL) або тактова лінія SPI (SPC) |
| 5 | SDA / SDI | Вхід/Вихід | Лінія даних I2C (SDA) або вхід даних SPI (SDI) |
| 6 | SDO | Вихід | Вихід даних SPI (SDO) або вибір адреси I2C (ADDR0) |
| 7 | CS | Вхід | Вибір мікросхеми SPI (Chip Select, активний нуль) |
| 8 | INT | Вихід | Переривання готовності даних (Data Ready / DRDY, активна одиниця) |

## Карта регістрів (Register Map)

Нижче наведено повну карту внутрішніх регістрів пристрою:

| Адреса (Hex) | Назва регістра | Доступ | Опис |
| :--- | :--- | :--- | :--- |
| `0x00` | `XOUT_LOW` | R | Молодші 8 біт даних осі X (`X[7:0]`) |
| `0x01` | `XOUT_HIGH` | R | Старші 8 біт даних осі X (`X[15:8]`) |
| `0x02` | `YOUT_LOW` | R | Молодші 8 біт даних осі Y (`Y[7:0]`) |
| `0x03` | `YOUT_HIGH` | R | Старші 8 біт даних осі Y (`Y[15:8]`) |
| `0x04` | `ZOUT_LOW` | R | Молодші 8 біт даних осі Z (`Z[7:0]`) |
| `0x05` | `ZOUT_HIGH` | R | Старші 8 біт даних осі Z (`Z[15:8]`) |
| `0x06` | `XYZOUT_2` | R | Молодші 2 біти розширення розрядності 18-біт (`X[17:16]`, `Y[17:16]`, `Z[17:16]`) |
| `0x07` | `STATUS` | R | Регістр стану (Готовність даних, Переповнення, Помилка) |
| `0x08` | `CONTROL_0` | R/W | Керування вимірюванням, імпульси SET/RESET, скидання |
| `0x09` | `CONTROL_1` | R/W | Налаштування полоси пропускання (BW), розрядності та самодіагностики |
| `0x0A` | `CONTROL_2` | R/W | Керування частотою вихідних даних (ODR) та неперервним режимом |
| `0x2F` | `PRODUCT_ID` | R | Ідентифікатор пристрою (значення `0x30`) |

### Деталізований бітовий опис керуючих регістрів

#### Регістр STATUS (`0x07`)
- **Біт 0 (`Meas_Done`)**: `1` — вимірювання магнітного поля завершено, дані в регістрах `0x00...0x06` готові до зчитування.
- **Біт 1 (`Pump_On`)**: `1` — внутрішній накачувач заряду генератора імпульсів SET/RESET перебуває в процесі зарядки.
- **Біт 2 (`OTP_Read_Done`)**: `1` — зчитування внутрішніх заводських калібрувальних коефіцієнтів завершено.

#### Регістр CONTROL_0 (`0x08`)
- **Біт 0 (`TM_M`)**: Запуск одного вимірювання магнітного поля (Take Measurement). Автоматично скидається в `0`.
- **Біт 1 (`TM_T`)**: Запуск вимірювання внутрішньої температури.
- **Біт 3 (`SET`)**: Примусовий запуск розмагнічувального імпульсу SET.
- **Біт 4 (`RESET`)**: Примусовий запуск розмагнічувального імпульсу RESET.
- **Біт 5 (`Auto_SR_en`)**: Увімкнення автоматичного генератора імпульсів SET/RESET перед кожним вимірюванням.
- **Біт 7 (`SW_RST`)**: Програмне скидання мікросхеми (Software Reset).

#### Регістр CONTROL_1 (`0x09`)
- **Біти [1:0] (`BW`)**: Налаштування часу інтегрування / смуги пропускання:
  - `00` — 800 Гц (час вимірювання 0.5 мс, 14 біт);
  - `01` — 400 Гц (час вимірювання 1.0 мс, 16 біт);
  - `10` — 200 Гц (час вимірювання 2.0 мс, 17 біт);
  - `11` — 100 Гц (час вимірювання 4.0 мс, 18 біт).

## Докладний розбір вимірювального циклу та часових затримок

Конструкція датчика вимагає строгого дотримання часових інтервалів під час взаємодії по шині I2C або SPI. Нижче описано алгоритм послідовної роботи з магнітометром:

1. **Етап ініціалізації та скидання:**
   Після подачі живлення система чекає 10 мікросекунд для стабілізації аналогових кіл VDD. Потім у регістр `CONTROL_0` записується біт `SW_RST` (`0x80`). Мікроконтролер робить паузу тривалістю не менше ніж 15 мілісекунд, під час якої внутрішнє ядро пристрою зчитує коефіцієнти температурної компенсації з OTP-пам'яті. Зчитування регістра `PRODUCT_ID` повинно повернути байт `0x30`.

2. **Формування розмагнічувального імпульсу (Degaussing):**
   При тривалій роботі або потраплянні в сильне зовнішнє поле (понад 10 Гаусс) внутрішні домени пермалою застрягають у неоптимальних конфігураціях. Для відновлення лінійності мосту мікроконтролер записує біт `SET` (`0x08`), витримує затримку 1 мілісекунду для підзарядки внутрішнього конденсатора накачувача заряду, після чого записує біт `RESET` (`0x10`).

3. **Цикл вимірювання та зчитування:**
   Вимірювання запускається встановленням біта `TM_M` у регістрі `CONTROL_0`. Залежно від обраної розрядності (14–18 біт) аналогово-цифровий перетворювач виконує інтегрування сигналу від 0.5 до 4.0 мілісекунд. Про завершення свідчить встановлення прапорця `Meas_Done` у регістрі `STATUS` або перехід виводу `INT` у високий стан. Після цього зчитуються 7 послідовних байтів починаючи з адреси `0x00`.

## Програмний драйвер мовами C та C++

У вкладках `:::tabs` наведено драйвер керування магнітометром, який реалізує ініціалізацію, подачу імпульсу розмагнічування SET/RESET, зчитування 18-бітних даних осей та конвертацію в Гауси й Тесли.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Адреса пристрою I2C */
#define MMC5983MA_I2C_ADDR      0x30

/* Регістри */
#define REG_XOUT_LOW            0x00
#define REG_STATUS              0x07
#define REG_CTRL_0              0x08
#define REG_CTRL_1              0x09
#define REG_CTRL_2              0x0A
#define REG_PRODUCT_ID          0x2F

/* Маски регістра CONTROL_0 */
#define CTRL0_TM_M              (1 << 0)
#define CTRL0_SET               (1 << 3)
#define CTRL0_RESET             (1 << 4)
#define CTRL0_AUTO_SR_EN        (1 << 5)
#define CTRL0_SW_RST            (1 << 7)

/* Маски регістра STATUS */
#define STATUS_MEAS_DONE        (1 << 0)

/* Коди помилок драйвера */
typedef enum {
    MAG_OK = 0,
    MAG_ERR_I2C,
    MAG_ERR_DEV_NOT_FOUND,
    MAG_ERR_TIMEOUT
} mag_error_t;

/* Структура результатів вимірювання (в Гаусах) */
typedef struct {
    float x_gauss;
    float y_gauss;
    float z_gauss;
} mag_data_t;

/* Прототипи низькорівневих шинних функцій (реалізуються платформою) */
extern mag_error_t i2c_read_bytes(uint8_t dev_addr, uint8_t reg_addr, uint8_t* data, size_t len);
extern mag_error_t i2c_write_byte(uint8_t dev_addr, uint8_t reg_addr, uint8_t data);
extern void delay_ms(uint32_t ms);

/* Програмне скидання та перевірка ID */
mag_error_t mag_init(void) {
    mag_error_t err;
    uint8_t id = 0;

    /* Скидання пристрою */
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_SW_RST);
    if (err != MAG_OK) return err;
    delay_ms(15);

    /* Перевірка Product ID */
    err = i2c_read_bytes(MMC5983MA_I2C_ADDR, REG_PRODUCT_ID, &id, 1);
    if (err != MAG_OK) return err;
    if (id != 0x30) return MAG_ERR_DEV_NOT_FOUND;

    /* Вмикаємо автоматичний SET/RESET та 18-бітний режим (BW = 100 Гц) */
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_1, 0x03);
    if (err != MAG_OK) return err;

    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_AUTO_SR_EN);
    return err;
}

/* Примусовий розмагнічувальний імпульс SET/RESET */
mag_error_t mag_degauss_pulse(void) {
    mag_error_t err;
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_SET);
    if (err != MAG_OK) return err;
    delay_ms(1);

    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_RESET);
    if (err != MAG_OK) return err;
    delay_ms(1);

    return i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_AUTO_SR_EN);
}

/* Одиничне вимірювання поля по трьох осях */
mag_error_t mag_read_field(mag_data_t* out_data) {
    mag_error_t err;
    uint8_t raw_buf[7];
    uint8_t status = 0;
    uint32_t timeout = 100;

    /* Запуск вимірювання */
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_TM_M | CTRL0_AUTO_SR_EN);
    if (err != MAG_OK) return err;

    /* Очікування прапорця Meas_Done */
    while (timeout > 0) {
        err = i2c_read_bytes(MMC5983MA_I2C_ADDR, REG_STATUS, &status, 1);
        if (err == MAG_OK && (status & STATUS_MEAS_DONE)) {
            break;
        }
        delay_ms(1);
        timeout--;
    }
    if (timeout == 0) return MAG_ERR_TIMEOUT;

    /* Зчитування 7 байт даних (X, Y, Z + розширення 18 біт) */
    err = i2c_read_bytes(MMC5983MA_I2C_ADDR, REG_XOUT_LOW, raw_buf, 7);
    if (err != MAG_OK) return err;

    /* Збирання 18-бітних чисел */
    uint32_t raw_x = ((uint32_t)raw_buf[0] << 10) | ((uint32_t)raw_buf[1] << 2) | ((raw_buf[6] >> 6) & 0x03);
    uint32_t raw_y = ((uint32_t)raw_buf[2] << 10) | ((uint32_t)raw_buf[3] << 2) | ((raw_buf[6] >> 4) & 0x03);
    uint32_t raw_z = ((uint32_t)raw_buf[4] << 10) | ((uint32_t)raw_buf[5] << 2) | ((raw_buf[6] >> 2) & 0x03);

    /* Перетворення у Гауси (нульова точка 131072, масштаб 16384 LSB/Gauss) */
    out_data->x_gauss = ((float)raw_x - 131072.0f) / 16384.0f;
    out_data->y_gauss = ((float)raw_y - 131072.0f) / 16384.0f;
    out_data->z_gauss = ((float)raw_z - 131072.0f) / 16384.0f;

    return MAG_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <expected>
#include <array>
#include <chrono>
#include <thread>

namespace hardware {

enum class MagnetometerError {
    BusError,
    DeviceNotFound,
    Timeout,
    InvalidConfiguration
};

struct MagneticVector {
    float x_gauss{0.0f};
    float y_gauss{0.0f};
    float z_gauss{0.0f};

    [[nodiscard]] constexpr float toTesla(float gauss) noexcept {
        return gauss * 1e-4f;
    }
};

// Контракт HAL-інтерфейсу I2C шини
class II2CBus {
public:
    virtual ~II2CBus() = default;
    virtual std::expected<void, MagnetometerError> writeRegister(uint8_t dev_addr, uint8_t reg_addr, uint8_t value) noexcept = 0;
    virtual std::expected<void, MagnetometerError> readRegisters(uint8_t dev_addr, uint8_t reg_addr, std::span<uint8_t> out_buffer) noexcept = 0;
};

class MMC5983MA {
public:
    static constexpr uint8_t I2C_ADDR = 0x30;
    static constexpr uint8_t EXPECTED_ID = 0x30;

    explicit MMC5983MA(II2CBus& bus) noexcept : bus_(bus) {}

    std::expected<void, MagnetometerError> init() noexcept {
        // Програмне скидання
        auto res = bus_.writeRegister(I2C_ADDR, 0x08, 0x80);
        if (!res) return res;

        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        // Перевірка ID
        std::array<uint8_t, 1> id_buf{};
        res = bus_.readRegisters(I2C_ADDR, 0x2F, id_buf);
        if (!res) return res;
        if (id_buf[0] != EXPECTED_ID) {
            return std::unexpected(MagnetometerError::DeviceNotFound);
        }

        // Конфігурація: 18 біт (BW = 100 Гц) + авто SET/RESET
        res = bus_.writeRegister(I2C_ADDR, 0x09, 0x03);
        if (!res) return res;

        return bus_.writeRegister(I2C_ADDR, 0x08, 0x20);
    }

    std::expected<void, MagnetometerError> degaussPulse() noexcept {
        auto res = bus_.writeRegister(I2C_ADDR, 0x08, 0x08); // SET
        if (!res) return res;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));

        res = bus_.writeRegister(I2C_ADDR, 0x08, 0x10); // RESET
        if (!res) return res;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));

        return bus_.writeRegister(I2C_ADDR, 0x08, 0x20); // Відновлення Auto SR
    }

    std::expected<MagneticVector, MagnetometerError> readMeasurement() noexcept {
        // Запуск вимірювання
        auto res = bus_.writeRegister(I2C_ADDR, 0x08, 0x21);
        if (!res) return std::unexpected(res.error());

        // Очікування готовності Data Ready
        bool ready = false;
        for (int i = 0; i < 50; ++i) {
            std::array<uint8_t, 1> st{};
            if (bus_.readRegisters(I2C_ADDR, 0x07, st)) {
                if (st[0] & 0x01) {
                    ready = true;
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }

        if (!ready) {
            return std::unexpected(MagnetometerError::Timeout);
        }

        std::array<uint8_t, 7> raw{};
        res = bus_.readRegisters(I2C_ADDR, 0x00, raw);
        if (!res) return std::unexpected(res.error());

        const uint32_t raw_x = (static_cast<uint32_t>(raw[0]) << 10) | (static_cast<uint32_t>(raw[1]) << 2) | ((raw[6] >> 6) & 0x03);
        const uint32_t raw_y = (static_cast<uint32_t>(raw[2]) << 10) | (static_cast<uint32_t>(raw[3]) << 2) | ((raw[6] >> 4) & 0x03);
        const uint32_t raw_z = (static_cast<uint32_t>(raw[4]) << 10) | (static_cast<uint32_t>(raw[5]) << 2) | ((raw[6] >> 2) & 0x03);

        MagneticVector vec{
            .x_gauss = (static_cast<float>(raw_x) - 131072.0f) / 16384.0f,
            .y_gauss = (static_cast<float>(raw_y) - 131072.0f) / 16384.0f,
            .z_gauss = (static_cast<float>(raw_z) - 131072.0f) / 16384.0f
        };

        return vec;
    }

private:
    II2CBus& bus_;
};

} // namespace hardware
```
:::

## Інженерні особливості калібрування та запобігання насиченню

При розробці навігаційних систем та компонентів електронних компасів із тривісними магнітометрами необхідно враховувати наступні правила:

1. **Захист від сильних зовнішніх полів (De-gaussing).**
   Якщо магнітометр потрапляє в поле від постійного неодимового магніту або високовольтного кабелю (понад 10–20 Гаусс), домени AMR-сенсора перемагнічуються та втрачають вихідну орієнтацію. Для відновлення працездатності драйвер мусить примусово виконати функцію `mag_degauss_pulse()`, яка подасть потужний струмовий імпульс SET/RESET та повністю відновить орієнтацію доменів.

2. **Калібрування твердого (Hard Iron) та м'якого (Soft Iron) заліза.**
   - Ефекти Hard Iron (постійні магніти поруч із платою): створюють постійне зсунення нуля `B_offset`. Компенсуються відніманням середнього вектора при обертанні датчика на 360 градусів у трьох площинах.
   - Ефекти Soft Iron (магнітом'які сталеві деталі корпусу): викривляють сферу вимірювань у деформований еліпсоїд. Компенсуються множенням вихідного вектора на 3x3 матрицю калібрування: `B_cal = M_soft · (B_raw - B_offset)`.

3. **Смуга пропускання та рівень шумів.**
   У 18-бітному режимі при смузі 100 Гц середньоквадратичний рівень шуму становить всього 0.4 мГаусс RMS, що дозволяє фіксувати зміни кута орієнтації пристрою з точністю до 0.1 градуса в геомагнітному полі Землі.
