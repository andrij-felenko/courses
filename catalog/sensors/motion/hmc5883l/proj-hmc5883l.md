# ⚙️ Читання GY-271 у коді: один драйвер на два чипи-двійники

<preknowlist>
- [I²C](book:communications/i2c-bus) — двопровідна шина: адреса пристрою, запис у регістр, читання N байтів поспіль з автоінкрементом.
- [atan2](book:math/atan2) — арктангенс із двома аргументами; повертає кут у всіх чотирьох чвертях, з нього рахують азимут.
- [Доповняльний код](book:math/twos-complement) — як 16-бітне число зі знаком зберігається у двох байтах; треба, щоб правильно зшити MSB і LSB.
</preknowlist>

Задача звучить оманливо просто: «прочитати з GY-271 три числа й порахувати, куди дивиться пристрій». Пастка в тому, що під однією назвою й на однаковій із виду платі живуть **два різні чипи** — Honeywell **HMC5883L** і QST **QMC5883L**. Вони несумісні на всіх рівнях: різні I²C-адреси, різні карти регістрів, різний порядок байтів даних, різні послідовності запуску. Код, написаний під один, на іншому віддає або суцільні нулі, або сміття, що «крутиться не туди».

Тому мета цієї вставки — не «код для HMC5883L», а **один драйвер, що сам розпізнає чип на шині й працює з будь-яким**. Спершу зберемо його з готової бібліотеки (найшвидший шлях у бій), потім напишемо власний — на голому I²C, без зовнішніх залежностей, щоб було видно кожен байт і жодна пастка не сховалася під абстракцією. Наприкінці — окремий розбір усіх граблів, на яких застряють найчастіше.

> 🔧 **Навіщо це.** Ти замовив «GY-271 HMC5883L», а прийшла партія з QMC5883L (так буває частіше, ніж навпаки — оригінал Honeywell зняла з виробництва). Якщо код жорстко зашитий під адресу 0x1E і порядок X-Z-Y, він мовчки не працюватиме, а ти шукатимеш проблему в паянні чи підтяжках. Драйвер із автовизначенням рятує від цілого класу «чому воно віддає нулі» — і робить прошивку переносною між партіями плат.

## Ідея: розгалуження за адресою на шині

Найнадійніша ознака чипа — **адреса, на яку він відповідає**. HMC5883L сидить на **0x1E**, QMC5883L — на **0x0D**. Адреси різні й непересічні, тож алгоритм запуску такий:

```
1. Просканувати шину (або просто пінгнути обидві адреси).
2. Відповіла 0x1E?  → це HMC5883L, для певності дочитати ID-регістри ('H','4','3').
3. Відповіла 0x0D?  → це QMC5883L.
4. Не відповіла жодна → плата не під'єднана / не живиться / підтяжки мертві.
5. Далі всі читання й запис ідуть у гілку обраного чипа.
```

«Пінгнути адресу» на I²C означає почати транзакцію запису на цю адресу й подивитися, чи прийшов ACK (підтвердження). Пристрій на шині тримає лінію на потрібному такті — і `Wire.endTransmission()` повертає 0. Немає пристрою — 2 (NACK на адресі). Це той самий механізм, яким працює будь-який I²C-сканер.

Далі буде трохи більше коду, ніж у типовому «прикладі з даташита», бо ми свідомо не ховаємо різницю чипів за магією. Натомість тримаємо її в одному місці — у структурі, що описує «як влаштований цей чип», і в двох функціях запуску. Решта прошивки працює з осями `x, y, z`, не знаючи, звідки вони.

## Шлях перший: готова бібліотека

Найшвидше — узяти бібліотеку, що вже вміє обидва чипи. Такі є; логіка автовизначення в них та сама, що описана вище. Але покажемо принцип на **власному тонкому шарі поверх `Wire`**, бо це переносно між усіма бібліотеками й не залежить від того, яку саме встановили.

Спершу — найпростіший робочий скетч для Arduino, який визначає чип і читає осі:

```c
#include <Wire.h>

#define ADDR_HMC  0x1E   // HMC5883L (Honeywell)
#define ADDR_QMC  0x0D   // QMC5883L (QST)

enum ChipKind { CHIP_NONE, CHIP_HMC, CHIP_QMC };
ChipKind chip = CHIP_NONE;

// Перевірити, чи відповідає пристрій на даній адресі (ACK на шині)
static bool i2c_present(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;   // 0 = отримали ACK
}

// Записати один байт у регістр
static void reg_write(uint8_t addr, uint8_t reg, uint8_t val) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}

// Прочитати n байтів, починаючи з reg (I²C-автоінкремент)
static uint8_t reg_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0)  // repeated START, шину не відпускаємо
        return 0;
    uint8_t got = Wire.requestFrom(addr, n);
    for (uint8_t i = 0; i < got && i < n; i++)
        buf[i] = Wire.read();
    return got;
}
```

Три допоміжні функції — це весь фундамент. `i2c_present` пінгує адресу, `reg_write` кладе один байт у регістр, `reg_read` читає пачку байтів з автоінкрементом адреси регістра (ключова властивість I²C: після кожного прочитаного байта внутрішній лічильник регістра сам зростає, тож шість байтів даних читаються одним запитом).

Зверни увагу на `Wire.endTransmission(false)` у `reg_read`: аргумент `false` означає **не відпускати шину** — надіслати «повторний старт» (repeated START) замість «стоп». Так між «я хочу читати з регістра R» і власне читанням ніхто інший не влізе на шину, і чип не скине внутрішній вказівник. Це стандартний I²C-ідіом для «запис адреси регістра, потім читання».

Тепер автовизначення й запуск:

```c
void compass_begin() {
    Wire.begin();

    if (i2c_present(ADDR_HMC)) {
        chip = CHIP_HMC;
        // Config A (0x00): 8 усереднень, 15 Гц, нормальний вимір
        reg_write(ADDR_HMC, 0x00, 0x70);
        // Config B (0x01): підсилення ±1.3 Гаус (1090 LSB/Гаус)
        reg_write(ADDR_HMC, 0x01, 0x20);
        // Mode (0x02): безперервний вимір
        reg_write(ADDR_HMC, 0x02, 0x00);
    }
    else if (i2c_present(ADDR_QMC)) {
        chip = CHIP_QMC;
        // М'яке скидання — почати з чистого стану
        reg_write(ADDR_QMC, 0x0A, 0x80);
        delay(5);
        // SET/RESET Period (0x0B): рекомендоване datasheet значення 0x01.
        // БЕЗ цього кроку QMC віддає нестабільне сміття!
        reg_write(ADDR_QMC, 0x0B, 0x01);
        // Control 1 (0x09): OSR=512 | RNG=±2Гаус | ODR=200Гц | безперервний
        // 0x00 | 0x00 | 0x0C | 0x01 = 0x1D
        reg_write(ADDR_QMC, 0x09, 0x1D);
    }
    else {
        chip = CHIP_NONE;   // нічого не знайдено
    }
}
```

Тут уже видно всі три несумісності водночас. HMC налаштовується трьома регістрами (0x00/0x01/0x02) і одразу готовий. QMC потребує **іншого**: спершу м'яке скидання (біт 0x80 у регістр 0x0A), потім — обов'язковий запис **0x0B = 0x01**, і лише тоді контрольний регістр 0x09. Пропустиш запис 0x0B — і чип начебто працює, але покази «дрейфують» і шумлять; це одна з найпідступніших пасток QMC, бо в даташиті цей крок легко проґавити.

Значення **0x1D** у регістрі 0x09 — це складене з чотирьох бітових полів: старші два біти (OSR, оверсемплінг) = 512, біт діапазону = ±2 Гаус, два біти частоти = 200 Гц, молодший біт = безперервний режим. Розкладене:

```
OSR 512   = 0x00   (біти 7:6 = 00)
RNG ±2G   = 0x00   (біт 4 = 0; для ±8Гаус тут був би 0x10)
ODR 200Гц = 0x0C   (біти 3:2 = 11)
MODE cont = 0x01   (біт 0 = 1)
                   ────────
разом     = 0x00 | 0x00 | 0x0C | 0x01 = 0x1D
```

Читання — теж дві гілки, але зовні одна функція, що повертає три осі в **уніфікованому порядку X-Y-Z** незалежно від чипа:

```c
// Повертає true, якщо є нові валідні дані. x,y,z — сирі відліки зі знаком.
bool compass_read(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t b[6];

    if (chip == CHIP_HMC) {
        // HMC: дані з 0x03, порядок у чипі X(MSB,LSB) Z(MSB,LSB) Y(MSB,LSB)
        if (reg_read(ADDR_HMC, 0x03, b, 6) != 6) return false;
        *x = (int16_t)((b[0] << 8) | b[1]);
        *z = (int16_t)((b[2] << 8) | b[3]);   // Z — ДРУГИЙ, не третій!
        *y = (int16_t)((b[4] << 8) | b[5]);   // Y — третій
        // Маркер переповнення: будь-яка вісь == -4096 → поле завелике
        if (*x == -4096 || *y == -4096 || *z == -4096) return false;
    }
    else if (chip == CHIP_QMC) {
        // QMC: дані з 0x00, порядок X Y Z, кожне число LITTLE-ENDIAN (LSB першим)
        if (reg_read(ADDR_QMC, 0x00, b, 6) != 6) return false;
        *x = (int16_t)((b[1] << 8) | b[0]);   // LSB=b[0], MSB=b[1]
        *y = (int16_t)((b[3] << 8) | b[2]);
        *z = (int16_t)((b[5] << 8) | b[4]);
    }
    else {
        return false;   // чип не знайдено
    }
    return true;
}
```

Уся підступність порядку осей і порядку байтів захована саме тут — в одному місці, під єдиним інтерфейсом. Хто викликає `compass_read`, отримує чесні `x, y, z` і не мусить пам'ятати, що в HMC осі йдуть X-Z-Y і байти big-endian, а в QMC — X-Y-Z і байти little-endian. Це і є сенс драйвера: **різницю чипів локалізувати, а не розмазати по всій прошивці**.

Азимут рахуємо однаково для обох (сирі осі вже уніфіковані):

```c
#include <math.h>

// Азимут у градусах 0…360, з поправкою на магнітне схилення
float compass_heading(int16_t x, int16_t y, float declination_deg) {
    float h = atan2f((float)y, (float)x);              // радіани, −π…+π
    h += declination_deg * (float)M_PI / 180.0f;       // схилення → істинна північ
    if (h < 0)          h += 2.0f * (float)M_PI;
    if (h >= 2*M_PI)    h -= 2.0f * (float)M_PI;
    return h * 180.0f / (float)M_PI;                   // 0…360°
}

void setup() {
    Serial.begin(115200);
    compass_begin();
    if (chip == CHIP_NONE) Serial.println("Компас не знайдено на I2C!");
    else Serial.println(chip == CHIP_HMC ? "Знайдено HMC5883L" : "Знайдено QMC5883L");
}

void loop() {
    int16_t x, y, z;
    if (compass_read(&x, &y, &z)) {
        float az = compass_heading(x, y, /*схилення для твого міста*/ 8.0f);
        Serial.print("Азимут: "); Serial.print(az, 1); Serial.println("°");
    }
    delay(100);
}
```

Це вже повністю робочий компас, який заводиться на будь-якій із двох плат. Але azimut поки що **сирий** — без калібрування твердого й м'якого заліза (про це нижче) він може бути точним у чистому полі й брехати на десятки градусів поруч із будь-яким залізяччям.

## Шлях другий: власний драйвер на голому I²C

Коли не можна тягнути `Wire` (свій HAL на STM32, ESP-IDF, робота під RTOS чи bare-metal), логіка та сама, але транзакції ідуть через власні примітиви шини. Покажу на прикладі HMC5883L з абстрактними `i2c_write_reg` / `i2c_read_regs`, які ти підставиш зі свого фреймворку. Суть — той самий порядок X-Z-Y і та сама обробка −4096, тільки без Arduino-обгортки.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// ── Ці дві функції реалізуєш під свою платформу (STM32 HAL, ESP-IDF, тощо) ──
// Записати один байт val у регістр reg пристрою addr. Повернути 0 при успіху.
extern int  i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t val);
// Прочитати n байтів у buf, починаючи з reg. Повернути 0 при успіху.
extern int  i2c_read_regs(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n);

#define HMC_ADDR 0x1E

// Регістри HMC5883L
#define HMC_CONFIG_A 0x00
#define HMC_CONFIG_B 0x01
#define HMC_MODE     0x02
#define HMC_DATA     0x03   // далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
#define HMC_STATUS   0x09
#define HMC_ID_A     0x0A   // 'H' (0x48)

// Підсилення для типового ±1.3 Гаус (Config B = 0x20): 1090 LSb/Gauss
#define HMC_LSB_PER_GAUSS 1090.0f

// Повернути true, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')
bool hmc_detect(void) {
    uint8_t id[3];
    if (i2c_read_regs(HMC_ADDR, HMC_ID_A, id, 3) != 0) return false;
    return id[0] == 'H' && id[1] == '4' && id[2] == '3';   // 0x48 0x34 0x33
}

void hmc_init(void) {
    i2c_write_reg(HMC_ADDR, HMC_CONFIG_A, 0x70);   // 8 усереднень, 15 Гц
    i2c_write_reg(HMC_ADDR, HMC_CONFIG_B, 0x20);   // ±1.3 Гаус
    i2c_write_reg(HMC_ADDR, HMC_MODE,     0x00);   // безперервний вимір
}

// Прочитати три осі. Повертає false при переповненні або помилці шини.
bool hmc_read_raw(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t b[6];
    if (i2c_read_regs(HMC_ADDR, HMC_DATA, b, 6) != 0) return false;
    // Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
    *x = (int16_t)((b[0] << 8) | b[1]);
    *z = (int16_t)((b[2] << 8) | b[3]);
    *y = (int16_t)((b[4] << 8) | b[5]);
    // -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
    if (*x == -4096 || *y == -4096 || *z == -4096) return false;
    return true;
}

// Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)
float hmc_to_gauss(int16_t raw) {
    return (float)raw / HMC_LSB_PER_GAUSS;
}
```
```cpp
#include <cstdint>
#include <optional>
#include <array>

// ── Ці дві функції реалізуєш під свою платформу (STM32 HAL, ESP-IDF, тощо) ──
// Записати один байт val у регістр reg пристрою addr. Повернути 0 при успіху.
extern int i2c_write_reg(std::uint8_t addr, std::uint8_t reg, std::uint8_t val);
// Прочитати n байтів у buf, починаючи з reg. Повернути 0 при успіху.
extern int i2c_read_regs(std::uint8_t addr, std::uint8_t reg,
                         std::uint8_t* buf, std::uint8_t n);

class Hmc5883l {
public:
    static constexpr std::uint8_t ADDR      = 0x1E;
    static constexpr std::uint8_t CONFIG_A  = 0x00;
    static constexpr std::uint8_t CONFIG_B  = 0x01;
    static constexpr std::uint8_t MODE      = 0x02;
    static constexpr std::uint8_t DATA      = 0x03;  // X(H,L) Z(H,L) Y(H,L)
    static constexpr std::uint8_t ID_A      = 0x0A;  // 'H' (0x48)
    // Підсилення для типового ±1.3 Гаус (Config B = 0x20): 1090 LSb/Gauss
    static constexpr float LSB_PER_GAUSS = 1090.0f;

    struct Axes { std::int16_t x, y, z; };

    // true, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')
    static bool detect() {
        std::array<std::uint8_t, 3> id{};
        if (i2c_read_regs(ADDR, ID_A, id.data(), 3) != 0) return false;
        return id[0] == 'H' && id[1] == '4' && id[2] == '3';  // 0x48 0x34 0x33
    }

    static void init() {
        i2c_write_reg(ADDR, CONFIG_A, 0x70);   // 8 усереднень, 15 Гц
        i2c_write_reg(ADDR, CONFIG_B, 0x20);   // ±1.3 Гаус
        i2c_write_reg(ADDR, MODE,     0x00);   // безперервний вимір
    }

    // Три осі, або std::nullopt при переповненні / помилці шини.
    static std::optional<Axes> read_raw() {
        std::uint8_t b[6];
        if (i2c_read_regs(ADDR, DATA, b, 6) != 0) return std::nullopt;
        // Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
        Axes a;
        a.x = static_cast<std::int16_t>((b[0] << 8) | b[1]);
        a.z = static_cast<std::int16_t>((b[2] << 8) | b[3]);
        a.y = static_cast<std::int16_t>((b[4] << 8) | b[5]);
        // -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
        if (a.x == -4096 || a.y == -4096 || a.z == -4096) return std::nullopt;
        return a;
    }

    // Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)
    static float to_gauss(std::int16_t raw) {
        return static_cast<float>(raw) / LSB_PER_GAUSS;
    }
};
```
```python
import struct

# ── Об'єкт шини реалізуєш під свою платформу (SMBus, periphery, тощо) ──
# bus.write_reg(addr, reg, val)          -> запис одного байта
# bus.read_regs(addr, reg, n) -> bytes   -> читання n байтів з автоінкрементом

HMC_ADDR = 0x1E

# Регістри HMC5883L
HMC_CONFIG_A = 0x00
HMC_CONFIG_B = 0x01
HMC_MODE     = 0x02
HMC_DATA     = 0x03   # далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
HMC_ID_A     = 0x0A   # 'H' (0x48)

# Підсилення для типового ±1.3 Гаус (Config B = 0x20): 1090 LSb/Gauss
HMC_LSB_PER_GAUSS = 1090.0


def hmc_detect(bus) -> bool:
    """True, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')."""
    ident = bus.read_regs(HMC_ADDR, HMC_ID_A, 3)
    return ident == b'H43'   # 0x48 0x34 0x33


def hmc_init(bus) -> None:
    bus.write_reg(HMC_ADDR, HMC_CONFIG_A, 0x70)   # 8 усереднень, 15 Гц
    bus.write_reg(HMC_ADDR, HMC_CONFIG_B, 0x20)   # ±1.3 Гаус
    bus.write_reg(HMC_ADDR, HMC_MODE,     0x00)   # безперервний вимір


def hmc_read_raw(bus):
    """Кортеж (x, y, z) або None при переповненні / помилці шини."""
    b = bus.read_regs(HMC_ADDR, HMC_DATA, 6)
    if len(b) != 6:
        return None
    # Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
    x, z, y = struct.unpack('>hhh', b)
    # -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
    if -4096 in (x, y, z):
        return None
    return x, y, z


def hmc_to_gauss(raw: int) -> float:
    """Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)."""
    return raw / HMC_LSB_PER_GAUSS
```
```micropython
import struct

HMC_ADDR = 0x1E

# Регістри HMC5883L
HMC_CONFIG_A = 0x00
HMC_CONFIG_B = 0x01
HMC_MODE     = 0x02
HMC_DATA     = 0x03   # далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
HMC_ID_A     = 0x0A   # 'H' (0x48)

HMC_LSB_PER_GAUSS = 1090.0


def hmc_detect(i2c):
    # True, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')
    ident = i2c.readfrom_mem(HMC_ADDR, HMC_ID_A, 3)
    return ident == b'H43'   # 0x48 0x34 0x33


def hmc_init(i2c):
    i2c.writeto_mem(HMC_ADDR, HMC_CONFIG_A, bytes([0x70]))  # 8 усереднень, 15 Гц
    i2c.writeto_mem(HMC_ADDR, HMC_CONFIG_B, bytes([0x20]))  # ±1.3 Гаус
    i2c.writeto_mem(HMC_ADDR, HMC_MODE,     bytes([0x00]))  # безперервний вимір


def hmc_read_raw(i2c):
    # Кортеж (x, y, z) або None при переповненні / помилці шини
    b = i2c.readfrom_mem(HMC_ADDR, HMC_DATA, 6)
    # Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
    x, z, y = struct.unpack('>hhh', b)
    # -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
    if x == -4096 or y == -4096 or z == -4096:
        return None
    return x, y, z


def hmc_to_gauss(raw):
    # Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)
    return raw / HMC_LSB_PER_GAUSS
```
```go
package compass

import "encoding/binary"

// Bus реалізуєш під свою платформу (periph.io, golang.org/x/exp/io/i2c, тощо).
type Bus interface {
	WriteReg(addr, reg, val uint8) error
	ReadRegs(addr, reg uint8, n int) ([]byte, error)
}

const (
	hmcAddr     = 0x1E
	hmcConfigA  = 0x00
	hmcConfigB  = 0x01
	hmcMode     = 0x02
	hmcData     = 0x03 // далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
	hmcIDA      = 0x0A // 'H' (0x48)
	hmcLSBGauss = 1090.0
)

// HMCDetect: true, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3').
func HMCDetect(bus Bus) bool {
	id, err := bus.ReadRegs(hmcAddr, hmcIDA, 3)
	if err != nil {
		return false
	}
	return string(id) == "H43" // 0x48 0x34 0x33
}

func HMCInit(bus Bus) error {
	if err := bus.WriteReg(hmcAddr, hmcConfigA, 0x70); err != nil { // 8 усереднень, 15 Гц
		return err
	}
	if err := bus.WriteReg(hmcAddr, hmcConfigB, 0x20); err != nil { // ±1.3 Гаус
		return err
	}
	return bus.WriteReg(hmcAddr, hmcMode, 0x00) // безперервний вимір
}

// HMCReadRaw повертає три осі; ok=false при переповненні або помилці шини.
func HMCReadRaw(bus Bus) (x, y, z int16, ok bool) {
	b, err := bus.ReadRegs(hmcAddr, hmcData, 6)
	if err != nil || len(b) != 6 {
		return 0, 0, 0, false
	}
	// Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
	x = int16(binary.BigEndian.Uint16(b[0:2]))
	z = int16(binary.BigEndian.Uint16(b[2:4]))
	y = int16(binary.BigEndian.Uint16(b[4:6]))
	// -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
	if x == -4096 || y == -4096 || z == -4096 {
		return 0, 0, 0, false
	}
	return x, y, z, true
}

// HMCToGauss переводить сирий відлік у Гауси (для діагностики / нахилокомпенсації).
func HMCToGauss(raw int16) float64 {
	return float64(raw) / hmcLSBGauss
}
```
:::

Тут кожен байт на видноті. `hmc_detect` дочитує три ASCII-байти ідентифікації й порівнює з `H43` — це фінальна певність, що на 0x1E саме HMC, а не якийсь інший пристрій, що випадково зайняв цю адресу. `hmc_read_raw` явно розкладає шість байтів у порядку X-Z-Y (не X-Y-Z!) і перевіряє кожну вісь на маркер −4096.

> 🔧 **Навіщо перевіряти −4096.** Це не «магічне число з нізвідки». Коли поле по якійсь осі виходить за обраний діапазон (±1.3 Гаус за замовчуванням), АЦП не може його представити й чип виставляє рівно −4096 як прапорець «зашкалило». Якщо це значення потрапить у `atan2` як звичайний відлік, азимут різко стрибне на випадковий кут. Тому валідне читання завжди відкидає такий кадр — або перемикає підсилення на грубіше (більший діапазон Гаусів). Практично поле Землі (0.25–0.65 Гаус) ніколи не переповнює ±1.3 Гаус саме по собі; переповнення означає, що поруч сильний магніт або великий струм — і тоді азимут усе одно недостовірний.

Для QMC5883L власна гілка симетрична, лише інші регістри й little-endian:

:::tabs
```c
#define QMC_ADDR    0x0D
#define QMC_DATA    0x00   // X(L,H) Y(L,H) Z(L,H) — LSB першим
#define QMC_STATUS  0x06   // біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
#define QMC_CONFIG1 0x09
#define QMC_RESET   0x0B

// ±2 Гаус → 12000 LSb/Gauss; ±8 Гаус → 3000 LSb/Gauss (datasheet QST)
#define QMC_LSB_PER_GAUSS 12000.0f

void qmc_init(void) {
    i2c_write_reg(QMC_ADDR, 0x0A, 0x80);   // м'яке скидання
    // (у власному HAL тут коротка пауза ~5 мс)
    i2c_write_reg(QMC_ADDR, QMC_RESET, 0x01);          // SET/RESET Period — ОБОВ'ЯЗКОВО
    i2c_write_reg(QMC_ADDR, QMC_CONFIG1, 0x1D);        // 512x, ±2G, 200Гц, безперервний
}

bool qmc_read_raw(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t st;
    if (i2c_read_regs(QMC_ADDR, QMC_STATUS, &st, 1) != 0) return false;
    if (!(st & 0x01)) return false;        // DRDY=0 → нових даних ще немає
    uint8_t b[6];
    if (i2c_read_regs(QMC_ADDR, QMC_DATA, b, 6) != 0) return false;
    // little-endian: молодший байт першим
    *x = (int16_t)((b[1] << 8) | b[0]);
    *y = (int16_t)((b[3] << 8) | b[2]);
    *z = (int16_t)((b[5] << 8) | b[4]);
    if (st & 0x02) return false;           // OVL=1 → переповнення діапазону
    return true;
}
```
```cpp
class Qmc5883l {
public:
    static constexpr std::uint8_t ADDR    = 0x0D;
    static constexpr std::uint8_t DATA    = 0x00;  // X(L,H) Y(L,H) Z(L,H) — LSB першим
    static constexpr std::uint8_t STATUS  = 0x06;  // біт0=DRDY, біт1=OVL
    static constexpr std::uint8_t CONFIG1 = 0x09;
    static constexpr std::uint8_t RESET   = 0x0B;
    // ±2 Гаус → 12000 LSb/Gauss; ±8 Гаус → 3000 LSb/Gauss (datasheet QST)
    static constexpr float LSB_PER_GAUSS = 12000.0f;

    struct Axes { std::int16_t x, y, z; };

    static void init() {
        i2c_write_reg(ADDR, 0x0A, 0x80);    // м'яке скидання
        // (у власному HAL тут коротка пауза ~5 мс)
        i2c_write_reg(ADDR, RESET, 0x01);   // SET/RESET Period — ОБОВ'ЯЗКОВО
        i2c_write_reg(ADDR, CONFIG1, 0x1D); // 512x, ±2G, 200Гц, безперервний
    }

    static std::optional<Axes> read_raw() {
        std::uint8_t st;
        if (i2c_read_regs(ADDR, STATUS, &st, 1) != 0) return std::nullopt;
        if (!(st & 0x01)) return std::nullopt;  // DRDY=0 → нових даних ще немає
        std::uint8_t b[6];
        if (i2c_read_regs(ADDR, DATA, b, 6) != 0) return std::nullopt;
        // little-endian: молодший байт першим
        Axes a;
        a.x = static_cast<std::int16_t>((b[1] << 8) | b[0]);
        a.y = static_cast<std::int16_t>((b[3] << 8) | b[2]);
        a.z = static_cast<std::int16_t>((b[5] << 8) | b[4]);
        if (st & 0x02) return std::nullopt;     // OVL=1 → переповнення діапазону
        return a;
    }
};
```
```python
QMC_ADDR    = 0x0D
QMC_DATA    = 0x00   # X(L,H) Y(L,H) Z(L,H) — LSB першим
QMC_STATUS  = 0x06   # біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
QMC_CONFIG1 = 0x09
QMC_RESET   = 0x0B

# ±2 Гаус → 12000 LSb/Gauss; ±8 Гаус → 3000 LSb/Gauss (datasheet QST)
QMC_LSB_PER_GAUSS = 12000.0


def qmc_init(bus) -> None:
    bus.write_reg(QMC_ADDR, 0x0A, 0x80)         # м'яке скидання
    # (у власному HAL тут коротка пауза ~5 мс)
    bus.write_reg(QMC_ADDR, QMC_RESET, 0x01)    # SET/RESET Period — ОБОВ'ЯЗКОВО
    bus.write_reg(QMC_ADDR, QMC_CONFIG1, 0x1D)  # 512x, ±2G, 200Гц, безперервний


def qmc_read_raw(bus):
    """Кортеж (x, y, z) або None: немає даних / переповнення / помилка шини."""
    st = bus.read_regs(QMC_ADDR, QMC_STATUS, 1)[0]
    if not (st & 0x01):        # DRDY=0 → нових даних ще немає
        return None
    b = bus.read_regs(QMC_ADDR, QMC_DATA, 6)
    if len(b) != 6:
        return None
    # little-endian: молодший байт першим
    x, y, z = struct.unpack('<hhh', b)
    if st & 0x02:              # OVL=1 → переповнення діапазону
        return None
    return x, y, z
```
```micropython
QMC_ADDR    = 0x0D
QMC_DATA    = 0x00   # X(L,H) Y(L,H) Z(L,H) — LSB першим
QMC_STATUS  = 0x06   # біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
QMC_CONFIG1 = 0x09
QMC_RESET   = 0x0B

QMC_LSB_PER_GAUSS = 12000.0


def qmc_init(i2c):
    i2c.writeto_mem(QMC_ADDR, 0x0A, bytes([0x80]))         # м'яке скидання
    time.sleep_ms(5)                                       # коротка пауза
    i2c.writeto_mem(QMC_ADDR, QMC_RESET, bytes([0x01]))    # SET/RESET — ОБОВ'ЯЗКОВО
    i2c.writeto_mem(QMC_ADDR, QMC_CONFIG1, bytes([0x1D]))  # 512x, ±2G, 200Гц, безпер.


def qmc_read_raw(i2c):
    # Кортеж (x, y, z) або None: немає даних / переповнення / помилка шини
    st = i2c.readfrom_mem(QMC_ADDR, QMC_STATUS, 1)[0]
    if not (st & 0x01):        # DRDY=0 → нових даних ще немає
        return None
    b = i2c.readfrom_mem(QMC_ADDR, QMC_DATA, 6)
    # little-endian: молодший байт першим
    x, y, z = struct.unpack('<hhh', b)
    if st & 0x02:              # OVL=1 → переповнення діапазону
        return None
    return x, y, z
```
```go
const (
	qmcAddr     = 0x0D
	qmcData     = 0x00 // X(L,H) Y(L,H) Z(L,H) — LSB першим
	qmcStatus   = 0x06 // біт 0 = DRDY (дані готові), біт 1 = OVL (переповнення)
	qmcConfig1  = 0x09
	qmcReset    = 0x0B
	qmcLSBGauss = 12000.0 // ±2G; ±8G → 3000 LSb/Gauss (datasheet QST)
)

func QMCInit(bus Bus) error {
	if err := bus.WriteReg(qmcAddr, 0x0A, 0x80); err != nil { // м'яке скидання
		return err
	}
	time.Sleep(5 * time.Millisecond) // коротка пауза
	if err := bus.WriteReg(qmcAddr, qmcReset, 0x01); err != nil { // SET/RESET — ОБОВ'ЯЗКОВО
		return err
	}
	return bus.WriteReg(qmcAddr, qmcConfig1, 0x1D) // 512x, ±2G, 200Гц, безперервний
}

// QMCReadRaw: ok=false — немає даних / переповнення / помилка шини.
func QMCReadRaw(bus Bus) (x, y, z int16, ok bool) {
	stBuf, err := bus.ReadRegs(qmcAddr, qmcStatus, 1)
	if err != nil {
		return 0, 0, 0, false
	}
	st := stBuf[0]
	if st&0x01 == 0 { // DRDY=0 → нових даних ще немає
		return 0, 0, 0, false
	}
	b, err := bus.ReadRegs(qmcAddr, qmcData, 6)
	if err != nil || len(b) != 6 {
		return 0, 0, 0, false
	}
	// little-endian: молодший байт першим
	x = int16(binary.LittleEndian.Uint16(b[0:2]))
	y = int16(binary.LittleEndian.Uint16(b[2:4]))
	z = int16(binary.LittleEndian.Uint16(b[4:6]))
	if st&0x02 != 0 { // OVL=1 → переповнення діапазону
		return 0, 0, 0, false
	}
	return x, y, z, true
}
```
:::

Різниця чипів тепер розкладена по поличках так, що видно кожну відмінність поряд:

```
                    HMC5883L              QMC5883L
─────────────────────────────────────────────────────────
I²C-адреса          0x1E                  0x0D
Регістр даних       0x03                  0x00
Порядок осей        X, Z, Y               X, Y, Z
Порядок байтів      big-endian (MSB 1-й)  little-endian (LSB 1-й)
Ідентифікація       0x0A → 'H','4','3'    адреса 0x0D сама по собі
Запуск              0x00,0x01,0x02        0x0A(reset),0x0B=0x01,0x09
Прапорець зашкалу   вісь == -4096         біт OVL у регістрі статусу 0x06
LSB/Гаус (типово)   1090 (±1.3G)          12000 (±2G)
```

Ця табличка — вичавка всіх граблів у чотирьох рядках. Найковарніші — **порядок осей** (X-Z-Y проти X-Y-Z) і **порядок байтів** (big проти little): переплутаєш будь-що з цього — компас начебто працює, віддає ненульові числа, але азимут крутиться неправильно або дзеркально. Саме тому «нулі або сміття» від невдалого коду так важко діагностувати без осцилографа: числа є, вони просто складені не так.

## Складність і пастки

Тепер — окремо кожен спосіб застрягти, з механізмом. Це не абстрактні застереження: майже кожен, хто вмикає GY-271 уперше, наступає щонайменше на одну з цих грабель.

**1. Не той чип — «віддає нулі».** Найчастіша й найпідступніша. Код зашитий під HMC (адреса 0x1E), а на платі QMC (0x0D). Транзакція на 0x1E ловить NACK, `requestFrom` повертає нулі — і здається, що «магнетометр мертвий». Лікування — автовизначення за адресою (гілка на початку). Швидка перевірка вручну: запусти будь-який I²C-сканер і подивися, яка адреса відповіла. 0x1E → HMC, 0x0D → QMC. Якщо жодна — проблема фізична (живлення/паяння/підтяжки), а не в чипі.

**2. Переплутаний порядок осей X-Z-Y.** Класична пастка саме HMC5883L. У даташиті регістри даних ідуть **не** підряд X-Y-Z, а **X, Z, Y**. Хто читає шість байтів і механічно розкладає їх як X-Y-Z (бо «так логічно»), міняє місцями Z та Y. Для азимута в горизонті беруть лише X та Y — і замість Y підставляється Z (вертикальна складова). Результат: компас реагує на нахил, а не на поворот, азимут стрибає безглуздо. Симптом дуже характерний: **крутиш пристрій навколо вертикалі — покази майже не міняються; нахиляєш — стрибають**. Побачив таке — перевір порядок осей першим ділом.

**3. Плутанина порядку байтів у QMC.** Дзеркальна пастка для клона. HMC віддає кожне 16-бітне число big-endian (старший байт першим), а QMC — **little-endian** (молодший першим). Застосуєш до QMC код зшивання від HMC (`(b[0]<<8)|b[1]`) — отримаєш число з переставленими половинами байтів. Воно не нуль, тому «наче працює», але значення дике й азимут — випадковий. Тримай зшивання в гілці свого чипа: HMC — `(b[0]<<8)|b[1]`, QMC — `(b[1]<<8)|b[0]`.

**4. Переповнення −4096 як «валідне» число.** Для HMC значення −4096 (0xF000) — це не відлік поля, а прапорець «АЦП зашкалив». Якщо не відсіювати його, `atan2` отримає −4096 замість справжньої проєкції й видасть різкий хибний кут. Причина зашкалу — сильне поле поруч (магніт, силовий дріт, динамік) або замалий обраний діапазон. Реакція: відкинути кадр, а якщо переповнення стале — перемкнути Config B на грубіший діапазон (менше LSB/Гаус, більший діапазон Гаусів). У QMC роль цього прапорця грає біт OVL у регістрі статусу 0x06 — перевіряй його так само.

**5. Забутий SET/RESET у QMC.** Специфічна пастка клона. QMC5883L вимагає запису **0x0B = 0x01** (SET/RESET Period) у послідовності запуску. Пропустиш — чип відповідає, дані начебто йдуть, але вони нестабільні: покази «пливуть», шумлять, зсув гуляє від запуску до запуску. Виглядає як «поганий екземпляр» або «завод бракований», хоча насправді бракує одного рядка ініціалізації. Симптом — компас працює, але дуже шумний і нестабільний навіть у спокої.

**6. Живлення 5 В проти 3.3 В.** Логіка модуля — 3.3 В. Оригінальний HMC5883L максимум терпить близько 3.6 В на живленні; лінії I²C у оригіналі теж 3.3-вольтові. Багато плат GY-271 мають на борту стабілізатор і дільники, тож витримують 5 В на VCC — **але не всі**. Подаси 5 В на плату без стабілізатора — у кращому разі чип працює на межі й глючить, у гіршому — тихо деградує чи гине. Безпечний шлях, що працює завжди: живити й підтягувати шину до **3.3 В**. Якщо контролер 5-вольтовий (класичний Arduino Uno) — або бери плату зі стабілізатором і рівнезсувом, або став двонапрямний зсув рівнів на SDA/SCL.

**7. Мертві або відсутні підтяжки.** I²C фізично потребує **підтяжок** (pull-up) на SDA і SCL до живлення шини — типово 4.7 кОм до 3.3 В. Без них лінії «висять» і сканер не бачить жодного пристрою (симптом як у пастці №1 — «нічого не відповідає»). На більшості плат GY-271 підтяжки вже розпаяні; але якщо на шині багато пристроїв, довгі дроти або ти живиш шину нестандартно — може знадобитися додати чи підправити номінал. Швидка перевірка: тестером між SDA і живленням має бути кілька кілоом, а не обрив.

**8. Невиконане калібрування — компас стабільно бреше.** Це не помилка коду, а пропущений крок, без якого «правильний» азимут усе одно неправильний. Поле Землі — не єдине, що ловить давач: власне залізо пристрою (батарея, мотори, саморізи, доріжки зі струмом) спотворює його. **Тверде залізо** (постійні магніти поруч) додає сталий зсув — коло вимірів з'їжджає з нуля. **М'яке залізо** (феромагнетик, що сам не магніт) розтягує коло в еліпс. Без компенсації азимут може брехати на десятки градусів, причому по-різному в різні боки. Мінімальний рецепт для найчастішого випадку (тверде залізо, компас у горизонті) — знайти зсув і відняти його перед `atan2`:

:::tabs
```c
// Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
int16_t xmin=32767, xmax=-32768, ymin=32767, ymax=-32768;

void calib_update(int16_t x, int16_t y) {   // виклик у циклі під час обертання
    if (x < xmin) xmin = x;  if (x > xmax) xmax = x;
    if (y < ymin) ymin = y;  if (y > ymax) ymax = y;
}

float heading_calibrated(int16_t x, int16_t y, float declination_deg) {
    int16_t xoff = (xmax + xmin) / 2;   // центр кола по X = зсув твердого заліза
    int16_t yoff = (ymax + ymin) / 2;
    return compass_heading(x - xoff, y - yoff, declination_deg);
}
```
```cpp
// Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
class HardIronCalib {
    std::int16_t xmin = 32767, xmax = -32768;
    std::int16_t ymin = 32767, ymax = -32768;
public:
    void update(std::int16_t x, std::int16_t y) {   // виклик у циклі під час обертання
        xmin = std::min(xmin, x);  xmax = std::max(xmax, x);
        ymin = std::min(ymin, y);  ymax = std::max(ymax, y);
    }

    float heading(std::int16_t x, std::int16_t y, float declination_deg) const {
        std::int16_t xoff = (xmax + xmin) / 2;  // центр кола по X = зсув твердого заліза
        std::int16_t yoff = (ymax + ymin) / 2;
        return compass_heading(x - xoff, y - yoff, declination_deg);
    }
};
```
```python
# Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
class HardIronCalib:
    def __init__(self):
        self.xmin = self.ymin = 32767
        self.xmax = self.ymax = -32768

    def update(self, x, y):   # виклик у циклі під час обертання
        self.xmin = min(self.xmin, x);  self.xmax = max(self.xmax, x)
        self.ymin = min(self.ymin, y);  self.ymax = max(self.ymax, y)

    def heading(self, x, y, declination_deg):
        xoff = (self.xmax + self.xmin) // 2   # центр кола по X = зсув твердого заліза
        yoff = (self.ymax + self.ymin) // 2
        return compass_heading(x - xoff, y - yoff, declination_deg)
```
```micropython
# Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
class HardIronCalib:
    def __init__(self):
        self.xmin = self.ymin = 32767
        self.xmax = self.ymax = -32768

    def update(self, x, y):   # виклик у циклі під час обертання
        self.xmin = min(self.xmin, x);  self.xmax = max(self.xmax, x)
        self.ymin = min(self.ymin, y);  self.ymax = max(self.ymax, y)

    def heading(self, x, y, declination_deg):
        xoff = (self.xmax + self.xmin) // 2   # центр кола по X = зсув твердого заліза
        yoff = (self.ymax + self.ymin) // 2
        return compass_heading(x - xoff, y - yoff, declination_deg)
```
```go
// Калібрування твердого заліза: крутимо пристрій повний оберт, ловимо min/max
type HardIronCalib struct {
	xmin, xmax, ymin, ymax int16
}

func NewHardIronCalib() *HardIronCalib {
	return &HardIronCalib{xmin: 32767, xmax: -32768, ymin: 32767, ymax: -32768}
}

func (c *HardIronCalib) Update(x, y int16) { // виклик у циклі під час обертання
	if x < c.xmin {
		c.xmin = x
	}
	if x > c.xmax {
		c.xmax = x
	}
	if y < c.ymin {
		c.ymin = y
	}
	if y > c.ymax {
		c.ymax = y
	}
}

func (c *HardIronCalib) Heading(x, y int16, declinationDeg float64) float64 {
	xoff := (c.xmax + c.xmin) / 2 // центр кола по X = зсув твердого заліза
	yoff := (c.ymax + c.ymin) / 2
	return CompassHeading(x-xoff, y-yoff, declinationDeg)
}
```
:::

Калібрувати треба **на зібраному пристрої**, з усім залізом на місці, — бо саме це залізо ми й компенсуємо; калібрування «голого» модуля на столі нічого не варте, коли потім прикрутиш його до дрона. Різниця між каліброваним і сирим компасом — між похибкою в 1–2° і похибкою в 30°. Повніша компенсація (м'яке залізо, еліпс → коло, нахилокомпенсація через акселерометр) — це вже [оцінка орієнтації](guide:embedded/attitude-estimation), окрема велика тема; тут головне зрозуміти, що **без бодай зсуву твердого заліза компас не працює як компас**.

**9. Нахил ламає плоский азимут.** Формула `atan2(y, x)` вірна лише коли давач **горизонтальний**. Щойно пристрій нахилився, вектор поля частково «перетікає» на вісь Z, а проєкції на X та Y спотворюються — азимут пливе. Тому в реальних дронах і роботах магнетометр рахують не «плоско», а з нахилокомпенсацією: беруть кути крену й тангажу з акселерометра й проєктують поле назад у горизонтальну площину. Це причина, чому в коді вище ми завжди читаємо **всі три осі**, включно з Z, хоча плоский азимут використовує лише X та Y: Z знадобиться, щойно з'явиться нахил.

Підсумок практичний: більшість «чому воно не працює» зводиться до перших п'яти пунктів — не той чип, переплутані осі, переплутані байти, необроблене переповнення, забутий SET/RESET. Драйвер із автовизначенням і локалізованою різницею чипів (як вище) закриває їх усі структурно. Решта — живлення, підтяжки, калібрування, нахил — це вже про фізику навколо модуля, а не про код читання; але без них навіть бездоганний код віддасть азимут, якому не можна вірити.
