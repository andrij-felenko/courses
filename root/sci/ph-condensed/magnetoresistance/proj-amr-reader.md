# ⚙️ Алгоритм зчитування та тривимірного калібрування магнітоопорного давача

У цьому проєкті розглянуто практичний алгоритм зчитування сигналів із 3-осьового анізотропного магніторезистивного давача (AMR, наприклад MMC5983MA або HMC5883L) на мікроконтролері. Програма виконує перемагнічувальний цикл Set/Reset для вилучення паразитного зсуву нуля та обчислює калібрований вектор магнітного поля з урахуванням викривлень від жорсткого та м'якого заліза (*hard-iron / soft-iron compensation*).

---

### Постановка задачі та фізичні вимоги

Для точного вимірювання слабкого геомагнітного поля (амплітуда порядку 30–60 мкТл) розробник змушений долати два джерела системних похибок. Першим джерелом є паразитний електронний зсув підсилювача та залишкове намагнічення доменів пермалою. Другим джерелом є власні магнітні завади друкованої плати: елементи конструкції (екрани, роз'єми, акумулятори, феритові індуктивності) створюють додаткові поля.

Магнітні завади поділяють на два види:
- **Жорстке залізо (Hard-Iron):** постійні магніти та намагнічені металеві деталі створюють сталий вектор поля `Offset`, який зсуває центр сфери вимірювання від початку координат `(0, 0, 0)`.
- **М'яке залізо (Soft-Iron):** феромагнітні деталі з високою магнітною проникністю перенаправляють лінії зовнішнього поля, деформуючи вимірювану сферичну поверхню в еліпсоїд. Для компенсації деформації вираховують симетричну 3x3 матрицю масштабування `S`.

Повний алгоритм обробки вимагає розв'язання рівняння:
```
B_calibrated = S · ( (V_SET - V_RESET) / 2 - Offset )
```
де `V_SET` та `V_RESET` — вектори АЦП після відповідних імпульсів перемагнічення.

---

### Архітектура рішень та послідовність керування

Програма реалізує двопрохідне диференціальне вимірювання:
1. Керувальний контролер генерує короткий імпульс **SET** (тривалість 10 мкс, струм до 2 А), який орієнтує домени пермалою в один бік. Через паузу в 100 мкс (необхідну для відновлення шини живлення) АЦП зчитує вектор `V_SET`.
2. Контролер генерує протилежний імпульс **RESET**, який розвертає домени на 180°. Після паузи АЦП зчитує вектор `V_RESET`.
3. Диференціальний вектор `V_diff = (V_SET - V_RESET) / 2.0` очищено від термо-ЕРС, зсуву нуля та низькочастотного шуму.
4. Вектор `V_diff` вираховується через матрично-векторне перетворення калібрування, після чого обчислюється плоский компасний азимут.

Для максимальної точності вимірювань розрядність аналогово-цифрового перетворювача (АЦП) вибирають не менше 16–18 біт. За такої чутливості найменший значущий розряд (LSB) відповідає магнітній індукції порядку 0.2–0.5 нанотесла. Зчитування здійснюється через стандартні шинні інтерфейси I2C чи SPI із частотою вибірок від 10 Гц до 100 Гц.

---

### Математичний алгоритм калібрування (Еліпсоїдна апроксимація)

Під час обертання давача в 3D просторі вектор неочищених свідчень `V_raw` описує у тривимірному просторі деформований еліпсоїд:

```
(V_raw - Offset)^T · (S^T · S) · (V_raw - Offset) = B_earth²
```

Для знаходження параметрів `Offset` та `S` застосовують метод найменших квадратів (*Least Squares Ellipsoid Fitting*). На першому етапі пристрій обертають у повітрі за всіма трьома осями, накопичуючи від 200 до 500 точок вимірювань. 

Алгоритм вираховує алгебраїчну квадратну форму 2-го порядку `A x² + B y² + C z² + 2D xy + 2E xz + 2F yz + 2G x + 2H y + 2I z = 1`. 

Вектор `Offset` знаходять як геометрічний центр отриманого еліпсоїда, а власні значення та власні вектори матриці квадрики дають коефіцієнти повороту та масштабування для діагональної матриці `S`.

---

### Простеження даних у системі Linux (sysfs/iio)

У лабораторних системах на базі Linux (наприклад, Raspberry Pi або BeagleBone) AMR-давачі підключаються через підсистему Industrial I/O (`IIO`). 

Слідкувати за станом давача можна безпосередньо через файлову систему `sysfs`:

```
/sys/bus/iio/devices/iio:device0/in_magn_x_raw
/sys/bus/iio/devices/iio:device0/in_magn_y_raw
/sys/bus/iio/devices/iio:device0/in_magn_z_raw
/sys/bus/iio/devices/iio:device0/in_magn_scale
```

Зчитування сирого значення `in_magn_x_raw` та множення на `in_magn_scale` повертає індукцію у Gauss чи Microtesla. Ядро виконує автокалібрування та періодичний виклик циклів Set/Reset у фоновому контексті драйвера.

---

### Термокомпенсація та моніторинг температури

Питомий опір пермалою та мостова чутливість AMR-структури мають температурний коефіцієнт близько `-0.3% / °C`. Для роботи в розширеному діапазоні температур (від -40°C до +85°C) на кристалі давача розміщують терморезистивний напівпровідниковий давач.

Формула термокомпенсації чутливості:

```
S_temp(T) = S_nominal · [ 1 + TCO · (T - T_ref) ]
```

де `T_ref = 25°C`, а `TCO` — температурний коефіцієнт чутливості (`-0.0031 / °C`). Значення індукції у мікротеслах коригується на поточну температуру перед виконанням орієнтаційних розрахунків.

---

### Обробка крайових випадків та відмов шини

При практичній експлуатації алгоритм має коректно реагувати на три типи помилок:
1. **Таймаут шини I2C (Bus NAK):** виникає при сильній електромагнітній заваді. Пристрій повертає значення `std::nullopt`, запобігаючи використанню застарілих даних у контурі керування польотом.
2. **Нульова детермінанта матриці калібрування:** якщо користувач не обертав давач за трьома осями під час збору точок калібрування, матриця квадрики стає виродженою (`det(S) ≈ 0`). Алгоритм повертає одиничну матрицю `S = I` та виставляє прапор помилки калібрування.
3. **Вихід у магнітне насичення (`|V_raw| > V_sat`):** при наближенні неодимового магніту АЦП видає граничне значення. Програма ініціює аварійний виклик розмагнічувальної послідовності із 5 послідовних імпульсів SET.

---

### Реалізація мовами C та C++

:::tabs
```c
/* C Implementation: Низькорівневий драйвер AMR-давача для вбудованих систем */
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    vector3f_t hard_iron_offset;
    float scale_matrix[3][3];
    float sensitivity_lsb_per_uT;
} amr_calibration_t;

/* Заглушки викликів I2C шини мікроконтролера */
static bool i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value) {
    (void)dev_addr; (void)reg; (void)value;
    return true; /* У реальній системі: HAL_I2C_Mem_Write(...) */
}

static bool i2c_read_bytes(uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint8_t len) {
    (void)dev_addr; (void)reg;
    for (uint8_t i = 0; i < len; i++) {
        buf[i] = (uint8_t)(100 + i * 10); /* Імітація даних АЦП */
    }
    return true;
}

/* Виконання циклу Set/Reset та зчитування сирого вектора */
bool amr_read_differential_raw(uint8_t dev_addr, vector3f_t *raw_out) {
    uint8_t buf[6];

    /* 1. Подаємо імпульс SET (регістр керування 0x09, біт 0x08) */
    if (!i2c_write_reg(dev_addr, 0x09, 0x08)) return false;
    if (!i2c_write_reg(dev_addr, 0x08, 0x01)) return false; /* Запуск вимірювання */
    if (!i2c_read_bytes(dev_addr, 0x00, buf, 6)) return false;

    int16_t set_x = (int16_t)((buf[0] << 8) | buf[1]);
    int16_t set_y = (int16_t)((buf[2] << 8) | buf[3]);
    int16_t set_z = (int16_t)((buf[4] << 8) | buf[5]);

    /* 2. Подаємо імпульс RESET (регістр керування 0x09, біт 0x10) */
    if (!i2c_write_reg(dev_addr, 0x09, 0x10)) return false;
    if (!i2c_write_reg(dev_addr, 0x08, 0x01)) return false; /* Запуск вимірювання */
    if (!i2c_read_bytes(dev_addr, 0x00, buf, 6)) return false;

    int16_t reset_x = (int16_t)((buf[0] << 8) | buf[1]);
    int16_t reset_y = (int16_t)((buf[2] << 8) | buf[3]);
    int16_t reset_z = (int16_t)((buf[4] << 8) | buf[5]);

    /* 3. Диференціальний вектор: V_diff = (V_SET - V_RESET) / 2 */
    raw_out->x = (float)(set_x - reset_x) / 2.0f;
    raw_out->y = (float)(set_y - reset_y) / 2.0f;
    raw_out->z = (float)(set_z - reset_z) / 2.0f;

    return true;
}

/* Обчислення вектору B у мкТл та компасного азимуту */
float amr_process_data(const vector3f_t *raw, const amr_calibration_t *cal, vector3f_t *b_out) {
    /* Віднімання hard-iron зсуву */
    float dx = (raw->x - cal->hard_iron_offset.x) / cal->sensitivity_lsb_per_uT;
    float dy = (raw->y - cal->hard_iron_offset.y) / cal->sensitivity_lsb_per_uT;
    float dz = (raw->z - cal->hard_iron_offset.z) / cal->sensitivity_lsb_per_uT;

    /* Множення на 3x3 матрицю soft-iron */
    b_out->x = cal->scale_matrix[0][0] * dx + cal->scale_matrix[0][1] * dy + cal->scale_matrix[0][2] * dz;
    b_out->y = cal->scale_matrix[1][0] * dx + cal->scale_matrix[1][1] * dy + cal->scale_matrix[1][2] * dz;
    b_out->z = cal->scale_matrix[2][0] * dx + cal->scale_matrix[2][1] * dy + cal->scale_matrix[2][2] * dz;

    /* Кут азимуту в градусах (0..360°) */
    float heading_rad = atan2f(b_out->y, b_out->x);
    float heading_deg = heading_rad * (180.0f / (float)M_PI);
    if (heading_deg < 0.0f) {
        heading_deg += 360.0f;
    }
    return heading_deg;
}
```
```cpp
// C++17/C++20 Implementation: RAII клас драйвера AMR-магнітометра
#include <iostream>
#include <cmath>
#include <array>
#include <optional>
#include <numbers>

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3f operator-(const Vector3f& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
};

struct CalibrationData {
    Vector3f hard_iron_offset{0.0f, 0.0f, 0.0f};
    std::array<std::array<float, 3>, 3> soft_iron_matrix{{{1,0,0}, {0,1,0}, {0,0,1}}};
    float sensitivity_lsb_per_uT{3000.0f};
};

class AmrSensorReader {
public:
    explicit AmrSensorReader(uint8_t i2c_address, CalibrationData cal)
        : i2c_addr_(i2c_address), cal_(std::move(cal)) {}

    // Зчитування диференціального вектора із Set/Reset імпульсом
    std::optional<Vector3f> read_differential_raw() const {
        auto set_val = read_single_pulse(PulseType::Set);
        if (!set_val) return std::nullopt;

        auto reset_val = read_single_pulse(PulseType::Reset);
        if (!reset_val) return std::nullopt;

        return Vector3f{
            (set_val->x - reset_val->x) / 2.0f,
            (set_val->y - reset_val->y) / 2.0f,
            (set_val->z - reset_val->z) / 2.0f
        };
    }

    // Обчислення фізичного вектору магнітного поля (мкТл) та азимуту
    std::pair<Vector3f, float> process(const Vector3f& raw) const noexcept {
        const Vector3f centered = (raw - cal_.hard_iron_offset);
        const float dx = centered.x / cal_.sensitivity_lsb_per_uT;
        const float dy = centered.y / cal_.sensitivity_lsb_per_uT;
        const float dz = centered.z / cal_.sensitivity_lsb_per_uT;

        const auto& m = cal_.soft_iron_matrix;
        Vector3f b_field{
            m[0][0] * dx + m[0][1] * dy + m[0][2] * dz,
            m[1][0] * dx + m[1][1] * dy + m[1][2] * dz,
            m[2][0] * dx + m[2][1] * dy + m[2][2] * dz
        };

        float heading_deg = std::atan2(b_field.y, b_field.x) * (180.0f / std::numbers::pi_v<float>);
        if (heading_deg < 0.0f) {
            heading_deg += 360.0f;
        }

        return {b_field, heading_deg};
    }

private:
    enum class PulseType { Set, Reset };

    std::optional<Vector3f> read_single_pulse(PulseType type) const {
        // У реальному коді тут відбувається виклик I2C шини
        uint8_t pulse_cmd = (type == PulseType::Set) ? 0x08 : 0x10;
        (void)pulse_cmd;
        // Симуляція відгуку АЦП
        return Vector3f{1024.0f, -512.0f, 2048.0f};
    }

    uint8_t i2c_addr_;
    CalibrationData cal_;
};
```
:::

---

### Типові пастки та інженерні помилки

1. **Недостатня пауза між Set/Reset імпульсом та запуском АЦП**:
   Перемагнічувальний імпульс генерує сильний сплеск струму (до 2 А). Джерело живлення кристала має встигнути стабілізуватися протягом 50–100 мкс до початку перетворення АЦП, інакше вихідне значення буде зашумлене.

2. **Ігнорування нахилу давача (Tilt Compensation)**:
   Простий `atan2(B_y, B_x)` дає точний азимут лише при строго горизонтальному положенні плати. При нахилах необхідно інтегрувати акселерометр для обчислення кутів тангажу (*pitch*) та крену (*roll*) і розвертати вектор `B` у горизонтальну площину:
   ```
   B_x_head = B_x · cos(pitch) + B_z · sin(pitch)
   B_y_head = B_x · sin(roll)·sin(pitch) + B_y · cos(roll) - B_z · sin(roll)·cos(pitch)
   ```

3. **Магнітна насиченість від сильних зовнішніх полів**:
   Якщо поруч із AMR давачем опиняється постійний неодимовий магніт із полем понад 1–2 мТл, пермалой входить у повне насичення. Сигнал стає константним, і відновити вимірювання можна лише подачею серії високовольтних імпульсів SET.
