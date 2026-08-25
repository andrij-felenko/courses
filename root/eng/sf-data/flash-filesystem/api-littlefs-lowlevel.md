# 📋 Низькорівневий інтерфейс конфігурації та драйвера LittleFS

Інтеграція файлової системи LittleFS у мікроконтролерні прошивки на базі STM32 HAL, ESP-IDF, Zephyr RTOS або власного рівня апаратних абстракцій (BSP) вимагає створення низькорівневого адаптера блокового пристрою (*block device driver*). Файлова система повністю ізольована від конкретної шини передачі даних (SPI, QSPI, Octal-SPI чи паралельний інтерфейс) і делегує апаратно-залежні операції чотирьом функціям зворотного виклику.

Щоб LittleFS функціонувала надійно й не пошкоджувала структуру накопичувача при раптових збоях живлення, розробник повинен точно налаштувати параметри геометрії, виділити статичні буфери з правильним вирівнюванням пам'яті та забезпечити суворе дотримання часових інваріантів запису й стирання.

### Структура конфігурації `struct lfs_config`

Головний дескриптор конфігурації `lfs_config` передається у виклики `lfs_mount` та `lfs_format`. Він описує фізичні властивості мікросхеми Flash, розміри робочих кеш-буферів та межі ресурсів вирівнювання зносу.

| Поле структури | Тип | Призначення та типове значення для SPI NOR Flash |
| :--- | :--- | :--- |
| `read_size` | `lfs_size_t` | Мінімальна неподільна одиниця читання в байтах. Для більшості чипів SPI NOR становить `1` або `16` байтів. Для чипів NAND дорівнює розміру фізичної сторінки (`2048` або `4096` байтів). |
| `prog_size` | `lfs_size_t` | Мінімальний розмір сторінки програмування (*page program size*). Для SPI NOR становить `256` байтів; для NAND — `2048` чи `4096` байтів. Запис меншими порціями апаратно не підтримується. |
| `block_size` | `lfs_size_t` | Розмір фізичного сектора або блоку стирання (*erase block size*). Для SPI NOR Flash найчастіше `4096` байтів (4 КБ); для чипів NAND — від `131072` (128 КБ) до `2097152` (2 МБ). |
| `block_count` | `lfs_size_t` | Загальна кількість блоків у виділеному розділі флеш-пам'яті. Наприклад, `512` блоків по 4 КБ для чипа обсягом 2 МБ. |
| `block_cycles` | `int32_t` | Поріг вирівнювання зносу: кількість операцій оновлення метаданих у блоці до його примусового перенесення в нове місце. Рекомендоване значення `100–500`. Від'ємне значення вимикає механізм. |
| `cache_size` | `lfs_size_t` | Розмір внутрішнього буфера читання та запису. Мусить бути строго кратним `read_size` та `prog_size` (зазвичай `256` або `512` байтів). |
| `lookahead_size` | `lfs_size_t` | Розмір бітової маски розподільника блоків у байтах. Одне 32-бітне слово (`4` байти) відстежує 32 блоки. Розмір повинен бути кратним 4. |
| `read_buffer` | `void*` | Вказівник на статично виділений буфер читання розміром `cache_size` (або `NULL` для динамічного виділення через `malloc`). |
| `prog_buffer` | `void*` | Вказівник на статично виділений буфер запису розміром `cache_size` (або `NULL`). |
| `lookahead_buffer` | `void*` | Вказівник на статичний буфер бітової маски розміром `lookahead_size` (або `NULL`). |
| `name_max` | `lfs_size_t` | Максимальна дозволена довжина імені файлу (за замовчуванням `255` байтів). |
| `file_max` | `lfs_size_t` | Максимальний розмір одного файлу в байтах (до `2147483647` байтів). |
| `attr_max` | `lfs_size_t` | Максимальний сукупний розмір користувацьких розширених атрибутів файлу (за замовчуванням `1022` байти). |

### Вимоги до вирівнювання та керування буферами пам'яті

LittleFS проєктувалася з розрахунком на роботу без динамічної пам'яті (*heapless execution*). Надання статичних буферів через поля `read_buffer`, `prog_buffer` та `lookahead_buffer` гарантує детермінізм прошивки та захищає від фрагментації купи мікроконтролера.

Буфери повинні задовольняти три жорсткі інваріанти:
1. **Вирівнювання адреси буфера**: адреса вказівника мусить бути вирівняна за 32-бітною межею слова процесора (кратна 4 або 8 байтам). Прямий доступ через DMA контролера SPI до неініціалізованого або невирівняного буфера на ядрах ARM Cortex-M0/M3 викликає апаратне виключення `HardFault`.
2. **Кратність кешу сторінці програмування**: якщо `prog_size = 256`, значення `cache_size` має бути кратним 256 (наприклад, 256 або 512 байтів). Якщо вказати довільний розмір, файлова система не зможе коректно синхронізувати транзакції, що призведе до збою запису.
3. **Розрахунок розміру `lookahead_size`**: розподільник блоків використовує бітову маску, де один біт відповідає одному фізичному блоку. Для чипа на 1024 блоки мінімальний розмір маски становить `1024 / 8 = 128` байтів. Якщо надати менший буфер (наприклад, 16 байтів), LittleFS скануватиме накопичувач вікнами по 128 блоків, що викликає затримки під час пошуку вільного місця.

### Життєвий цикл ініціалізації: форматування та монтування

Процес підготовки накопичувача складається з двох чітко розмежованих етапів:

1. **Форматування (`lfs_format`)**: створює початкову структуру томів. LittleFS обирає блоки `0` та `1` як кореневу пару метаданих каталогу (`/`), записує в блок `0` початковий суперблок із тегом версії та конфігурації, після чого фіксує стан контрольною сумою CRC32. Блок `1` стирається й залишається резервним.
2. **Монтування (`lfs_mount`)**: файлова система зчитує обидва блоки `0` та `1`. Вона перевіряє цілісність CRC32, знаходить блок із найбільшим валідним номером ревізії та відновлює кореневий каталог. Далі ініціалізується розподільник блоків: LittleFS сканує дерево каталогів, щоб відмітити зайняті блоки у бітовій масці `lookahead_buffer`. Цей процес займає час, пропорційний кількості відкритих каталогів, а не загальному розміру носія.

### Контракт функцій драйвера блокового пристрою

Файлова система взаємодіє з апаратним рівнем через чотири обов'язкові callback-функції, сигнатури яких наведено нижче.

:::tabs
```c
/* Контракт функцій зворотного виклику LittleFS мовою C */
int bdev_read(const struct lfs_config *c, lfs_block_t block, lfs_off_t off, void *buffer, lfs_size_t size);
int bdev_prog(const struct lfs_config *c, lfs_block_t block, lfs_off_t off, const void *buffer, lfs_size_t size);
int bdev_erase(const struct lfs_config *c, lfs_block_t block);
int bdev_sync(const struct lfs_config *c);
```
```cpp
// Інтерфейсний контракт функцій блокового пристрою мовою C++
#include <cstdint>
#include <cstddef>
#include <span>

class ILfsBlockDevice {
public:
    virtual ~ILfsBlockDevice() = default;
    [[nodiscard]] virtual int read(uint32_t block, uint32_t off, std::span<uint8_t> buffer) const noexcept = 0;
    [[nodiscard]] virtual int prog(uint32_t block, uint32_t off, std::span<const uint8_t> buffer) noexcept = 0;
    [[nodiscard]] virtual int erase(uint32_t block) noexcept = 0;
    [[nodiscard]] virtual int sync() noexcept = 0;
};
```
:::

#### Семантика повертаних значень та помилок

- **`0` (`LFS_ERR_OK`)**: операція успішно виконана на апаратному рівні, дані фізично зафіксовані в комірках.
- **`-5` (`LFS_ERR_IO`)**: апаратний збій шини SPI/QSPI, відсутність відповіді від чипа або вихід за межі таймауту очікування готовності.
- **`-84` (`LFS_ERR_CORRUPT`)**: критичне пошкодження блоку (наприклад, після стирання в блоці виявлено нульові біти або виникла невідновна помилка коду корекції ECC). Отримавши такий код, LittleFS позначає блок збійним і вилучає його з подальшого використання.

#### Часові обмеження та синхронізація

Мікросхеми Flash мають суттєву асиметрію затримки виконання операцій:
- **Читання (`read`)**: виконується на повній швидкості шини SPI (20–80 МГц) за лічені мікросекунди.
- **Програмування сторінки (`prog`)**: після надсилання команди `Page Program` (код `0x02`) кристал виконує внутрішнє зарядження плаваючих затворів. Цей процес триває від 0.2 до 1.5 мілісекунди.
- **Стирання сектора (`erase`)**: операція `Sector Erase` (код `0x20`) триває від 30 до 400 мілісекунд залежно від ступеня деградації кристала.
- **Синхронізація (`sync`)**: драйвер зобов'язаний циклічно опитувати регістр статусу чипа (команда `Read Status Register` `0x05`) і чекати скидання біта `WIP` (*Write In Progress*). Повернення з функції до скидання біта `WIP` призведе до втрати наступних команд або спотворення даних.

### Багатопоточність і реентрабельність

LittleFS не містить внутрішніх м'ютексів для синхронізації доступу між потоками операційної системи реального часу (FreeRTOS, Zephyr або RT-Thread). Якщо кілька задач одночасно викликають операції читання та запису над одним томом, розробник зобов'язаний захистити всі виклики API спільним м'ютексом на рівні операційної системи.

У фреймворку Zephyr або ESP-IDF такий захист вбудовано у шар віртуальної файлової системи (VFS). У випадку власної реалізації достатньо створити рекурсивний м'ютекс і захоплювати його перед кожним викликом `lfs_file_*` чи `lfs_dir_*`.

### Повна реалізація апаратного моста: C та C++

Нижче наведено робочу реалізацію драйвера блокового пристрою для SPI NOR Flash.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define LFS_ERR_OK       0
#define LFS_ERR_IO      -5
#define LFS_ERR_CORRUPT -84

typedef uint32_t lfs_block_t;
typedef uint32_t lfs_off_t;
typedef uint32_t lfs_size_t;

struct lfs_config;

/* Зовнішній апаратний рівень передачі даних SPI */
extern bool spi_flash_hardware_read(uint32_t address, uint8_t *dest, size_t length);
extern bool spi_flash_hardware_page_prog(uint32_t address, const uint8_t *src, size_t length);
extern bool spi_flash_hardware_sector_erase(uint32_t address);
extern bool spi_flash_hardware_wait_ready(uint32_t timeout_ms);

typedef struct {
    uint32_t base_address;
    uint32_t sector_size;
    uint32_t total_blocks;
} spi_flash_context_t;

int bdev_read(const struct lfs_config *c, lfs_block_t block, lfs_off_t off, void *buffer, lfs_size_t size) {
    const spi_flash_context_t *ctx = (const spi_flash_context_t *)c->context;
    if (block >= ctx->total_blocks || off + size > ctx->sector_size) {
        return LFS_ERR_IO;
    }

    uint32_t phys_addr = ctx->base_address + (block * ctx->sector_size) + off;
    if (!spi_flash_hardware_read(phys_addr, (uint8_t *)buffer, size)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int bdev_prog(const struct lfs_config *c, lfs_block_t block, lfs_off_t off, const void *buffer, lfs_size_t size) {
    const spi_flash_context_t *ctx = (const spi_flash_context_t *)c->context;
    if (block >= ctx->total_blocks || off + size > ctx->sector_size) {
        return LFS_ERR_IO;
    }

    uint32_t phys_addr = ctx->base_address + (block * ctx->sector_size) + off;
    if (!spi_flash_hardware_page_prog(phys_addr, (const uint8_t *)buffer, size)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int bdev_erase(const struct lfs_config *c, lfs_block_t block) {
    const spi_flash_context_t *ctx = (const spi_flash_context_t *)c->context;
    if (block >= ctx->total_blocks) {
        return LFS_ERR_IO;
    }

    uint32_t phys_addr = ctx->base_address + (block * ctx->sector_size);
    if (!spi_flash_hardware_sector_erase(phys_addr)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int bdev_sync(const struct lfs_config *c) {
    (void)c;
    /* Таймаут 500 мс покриває максимальний час стирання сектора */
    if (!spi_flash_hardware_wait_ready(500)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include <expected>

enum class LfsResult : int {
    Ok      = 0,
    IoError = -5,
    Corrupt = -84
};

struct FlashGeometry {
    uint32_t base_address{0x00000000};
    uint32_t sector_size{4096};
    uint32_t page_size{256};
    uint32_t total_blocks{512};
};

class ISpiFlashDriver {
public:
    virtual ~ISpiFlashDriver() = default;
    [[nodiscard]] virtual bool readRaw(uint32_t address, std::span<uint8_t> destination) = 0;
    [[nodiscard]] virtual bool programRaw(uint32_t address, std::span<const uint8_t> source) = 0;
    [[nodiscard]] virtual bool eraseSectorRaw(uint32_t address) = 0;
    [[nodiscard]] virtual bool waitForReady(uint32_t timeoutMs) = 0;
};

class LittleFsDriverBridge final {
public:
    LittleFsDriverBridge(std::shared_ptr<ISpiFlashDriver> hardware, FlashGeometry geometry)
        : hw_(std::move(hardware)), geom_(geometry) {}

    [[nodiscard]] int read(uint32_t block, uint32_t offset, std::span<uint8_t> dest) const noexcept {
        if (block >= geom_.total_blocks || offset + dest.size() > geom_.sector_size) {
            return static_cast<int>(LfsResult::IoError);
        }
        uint32_t phys = geom_.base_address + (block * geom_.sector_size) + offset;
        if (!hw_->readRaw(phys, dest)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

    [[nodiscard]] int prog(uint32_t block, uint32_t offset, std::span<const uint8_t> src) noexcept {
        if (block >= geom_.total_blocks || offset + src.size() > geom_.sector_size) {
            return static_cast<int>(LfsResult::IoError);
        }
        uint32_t phys = geom_.base_address + (block * geom_.sector_size) + offset;
        if (!hw_->programRaw(phys, src)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

    [[nodiscard]] int erase(uint32_t block) noexcept {
        if (block >= geom_.total_blocks) {
            return static_cast<int>(LfsResult::IoError);
        }
        uint32_t phys = geom_.base_address + (block * geom_.sector_size);
        if (!hw_->eraseSectorRaw(phys)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

    [[nodiscard]] int sync() noexcept {
        if (!hw_->waitForReady(500)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

private:
    std::shared_ptr<ISpiFlashDriver> hw_;
    FlashGeometry geom_;
};
```
:::

### Типові помилки конфігурації та їх наслідки

1. **Ігнорування апаратного захисту від запису (Write Protection)**: багато мікросхем SPI Flash після подачі живлення або апаратного скидання переходять у режим блокування запису (біти `BP0–BP2` регістра статусу встановлені в одиницю). Драйвер повинен перед першою операцією стирання чи запису надіслати команду `Write Enable` (код `0x06`) або очистити біти блокування в регістрі статусу, інакше виклики `prog` та `erase` мовчки завершаться без зміни фізичного стану кристала.
2. **Невірний поріг `block_cycles`**: встановлення надто малого значення (наприклад, `block_cycles = 10`) змушує файлову систему переносити каталог у новий блок після кожних 10 оновлень файлів. Це різко збільшує коефіцієнт посилення запису (WAF) і передчасно вичерпує ресурс чипа. Встановлення надто великого значення (`block_cycles > 5000`) створює ризик локального прогорання блоку з метаданими. Оптимальний баланс лежить у межах від 100 до 500 циклів.
3. **Робота без перевірки таймауту `sync`**: якщо у функції `sync` використовувати занадто короткий таймаут (наприклад, 10 мс), стирання сектора на зношеному чипі не встигне завершитися. LittleFS отримає помилку `LFS_ERR_IO` і помилково визначить робочий блок як пошкоджений.
4. **Некоректний розмір `cache_size` під час роботи з DMA**: якщо драйвер шини SPI використовує прямий доступ до пам'яті (DMA), буфер розміром менше мінімального транзакційного блоку SPI призведе до переривання передачі або читання залишкових даних із сусідніх ділянок SRAM.
