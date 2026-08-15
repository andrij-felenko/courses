# ⚙️ Апаратно-прискорене обчислення контрольних сум CRC32c

Для забезпечення суцільного захисту файлових даних та метаданих від тихого пошкодження без виникнення критичних затримок під час операцій введення-виведення файлова система Btrfs за замовчуванням використовує 32-бітну контрольну суму **CRC32c (Castagnoli)**.

На відміну від стандартного полінома IEEE 802.3 (`0x04C11DB7`), який застосовується у протоколах Ethernet та архіваторах ZIP, CRC32c базується на поліномі Гі Кастаньйолі (Guy Castagnoli) `0x1EDC6F41`. Той самий CRC32c узяли iSCSI, SCTP і ext4 для контрольних сум метаданих.

## Математична специфіка та обґрунтування вибору Castagnoli

Алгоритм циклічного надлишкового коду (Cyclic Redundancy Check) обчислює остачу від ділення вхідного бітового потоку, представленого у вигляді многочлена у скінченному полі Галуа `GF(2)`, на фіксований генераторний поліном.

Вибір полінома Castagnoli для Btrfs зумовлений його унікальними математичними властивостями на блоках даних розміром 4096 байтів (стандартний розмір сектора диска):

1. **Відстань Хеммінга (Hamming Distance):** Для повідомлень завдовжки до 5243 бітів (близько 655 байтів) поліном CRC32c тримає відстань Хеммінга `HD = 6` — гарантовано виявляє будь-яке довільне спотворення 1, 2, 3, 4 або 5 бітів. На повному секторі 4 КіБ (32768 бітів) гарантія падає до `HD = 4`: чотири розкидані по сектору спотворені біти ловляться завжди, більша кількість — з ймовірністю, дуже близькою до одиниці. Класичний поліном IEEE 802.3 утримує `HD = 6` лише до 268 бітів, тож на дискових блоках CRC32c відчутно сильніший.
2. **Виявлення сплесків помилок (Burst Errors):** Алгоритм виявляє 100% будь-яких суцільних сплесків помилок довжиною до 32 бітів включно, що виникають під час короткочасних збоїв та наведень на дискових шинах SATA/SAS.
3. **Виявлення непарних помилок:** Поліном ділиться націло на `(x + 1)`, а це гарантує виявлення будь-якої непарної кількості спотворених бітів усередині сектора.

Завдяки цим математичним властивостям ймовірність того, що випадкове декількобайтове спотворення усередині сектора даних 4096 байтів дасть таку саму контрольну суму CRC32c, становить менше ніж 1 на 4.2 мільярди (`1 / 2^32`).

## Апаратне прискорення SSE4.2 та ARMv8 CRC

Обчислення CRC32c на звичайному програмному рівні через побітові зсуви вимагає близько 15–20 тактів центрального процесора на один байт даних, що при швидкості зчитування сучасного NVMe SSD у 5 ГБ/с завантажило б усі ядра CPU на 100% лише на перевірку хешів.

Для вирішення цієї проблеми виробники процесорів інтегрували спеціалізовані апаратні інструкції:
- **x86_64 (Intel SSE4.2 / AMD Bulldozer):** Апаратна інструкція `crc32q` (у C-компіляторах `_mm_crc32_u64`). Вона обробляє 64-бітне число (8 байтів) із затримкою (latency) у 3 такти й приймає нову інструкцію щотакту. Але кожен крок CRC залежить від попереднього, тож ядро ріже буфер на три незалежні потоки й переплітає їх — інакше швидкість уперлася б саме в ці 3 такти на 8 байтів.
- **ARM64 (розширення CRC32, обов'язкове від ARMv8.1-A):** інструкція `crc32cx` (інтринсик `__crc32cd`), яка робить той самий 64-бітний крок над звичайними цілочисловими регістрами, а не в блоці NEON.

Завдяки цим інструкціям модуль ядра Linux `crc32c-intel` досягає пропускної здатності **7–10 Гігабайт на секунду на один потік CPU**, що робить накладні витрати на обчислення хешів у Btrfs практично непомітними для системи.

## Програмний фолбек: Алгоритм Slicing-by-8

Для процесорів без підтримки SSE4.2 ядро Linux використовує алгоритм **Slicing-by-8**: табличний метод запропонував Діліп Сарвате (1988), а варіант із нарізанням на вісім таблиць — Міхаліс Кунавіс і Френк Беррі з Intel (2005). Замість побайтового обходу алгоритм будує 8 попередньо обчислених таблиць розміром по 256 елементів кожна (загалом 8 КіБ табличної пам'яті).

Таблиці заздалегідь розраховують значення полінома з урахуванням зміщення бітів на 1, 2, ..., 8 байтів уперед. Це дозволяє обробляти 8 байтів даних за один крок табличного пошуку в оперативній пам'яті без використання SIMD-інструкцій, досягаючи швидкості ~1.2 ГБ/с на ядро CPU.

## Вирівнювання адрес у пам'яті та ліквідація пенальті I/O

При виконанні апаратних інструкцій `_mm_crc32_u64` критично важливо, щоб початковий покажчик буфера в пам'яті був вирівняний по 8-байтній межі (`uintptr_t & 7 == 0`). У разі невирівняного звернення процесор x86 розщеплює на два ті доступи, що перетнули межу лінії кешу, — і саме ці розщеплені звернення, а не невирівнювання само по собі, з'їдають частину пропускної здатності.

У драйвері `crc32c-intel` для досягнення максимальної швидкодії алгоритм спочатку виконує побайтове обчислення для перших декількох байтів до досягнення 8-байтного вирівнювання адреси, після чого запускає основний 64-бітний цикл.

## Інтеграція з Crypto API ядра Linux

У ядрі Linux Btrfs не обчислює CRC32c вручну в кожному місці файлової системи, а ініціалізує хешувальник через загальну підсистему Kernel Crypto API:

:::tabs
```c
// Виділення хендла хешування під час монтування Btrfs (fs/btrfs/super.c)
struct crypto_shash *tfm = crypto_alloc_shash("crc32c", 0, 0);
if (IS_ERR(tfm)) {
    pr_err("BTRFS: не вдалося завантажити модуль хешування crc32c\n");
    return PTR_ERR(tfm);
}
```
```cpp
// C++ RAII-обгортка для керування хендлом Kernel Crypto API
#include <memory>
#include <stdexcept>
#include <crypto/hash.h>

struct CryptoShashDeleter {
    void operator()(struct crypto_shash* tfm) const {
        if (tfm && !IS_ERR(tfm)) {
            crypto_free_shash(tfm);
        }
    }
};

using CryptoShashPtr = std::unique_ptr<struct crypto_shash, CryptoShashDeleter>;

CryptoShashPtr createBtrfsHasher() {
    struct crypto_shash* tfm = crypto_alloc_shash("crc32c", 0, 0);
    if (IS_ERR(tfm)) {
        throw std::runtime_error("BTRFS: не вдалося ініціалізувати crc32c crypto handle");
    }
    return CryptoShashPtr(tfm);
}
```
:::

Ядерна підсистема Crypto API автоматично проводить перевірку прапорців `cpuid` при завантаженні й підключає найшвидший доступний модуль: `crc32c-intel` (SSE4.2), `crc32-arm64` або стандартний софтверний драйвер `crc32c-generic`.

## Реалізація модуля CRC32c: C та C++

Наведена нижче програма демонструє повноцінний модуль обчислення контрольної суми Btrfs з підтримкою апаратних інструкцій SSE4.2 та автоматичним вирівнюванням адрес у пам'яті.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <nmmintrin.h> // Intel SSE4.2 intrinsics (_mm_crc32_u64)
#define HAS_SSE42 1
#else
#define HAS_SSE42 0
#endif

// Початковий стан CRC32c у Btrfs (усі біти 1)
#define BTRFS_CRC32C_INIT 0xFFFFFFFFU

// Апаратно-прискорене обчислення CRC32c через SSE4.2
uint32_t btrfs_crc32c_hardware(uint32_t crc, const void *data, size_t length)
{
    const uint8_t *p8 = (const uint8_t *)data;
    uint64_t crc64 = (uint64_t)crc;

#if HAS_SSE42
    // 1. Вирівнювання вказівника до 8-байтної межі в пам'яті
    while (length > 0 && ((uintptr_t)p8 & 7)) {
        crc64 = _mm_crc32_u8((uint32_t)crc64, *p8++);
        length--;
    }

    // 2. Основна обробка 64-бітними блоками (8 байтів за інструкцію)
    const uint64_t *p64 = (const uint64_t *)p8;
    size_t blocks = length / sizeof(uint64_t);
    for (size_t i = 0; i < blocks; i++) {
        crc64 = _mm_crc32_u64(crc64, p64[i]);
    }

    // 3. Обробка залишкових байтів
    p8 = (const uint8_t *)(p64 + blocks);
    length %= sizeof(uint64_t);
    while (length > 0) {
        crc64 = _mm_crc32_u8((uint32_t)crc64, *p8++);
        length--;
    }
#else
    // Програмний фолбек для систем без SSE4.2 (побайтовий обхід)
    for (size_t i = 0; i < length; i++) {
        crc64 ^= p8[i];
        for (int bit = 0; bit < 8; bit++) {
            if (crc64 & 1) {
                crc64 = (crc64 >> 1) ^ 0x82F63B78U; // Зазеркалений поліном Castagnoli
            } else {
                crc64 >>= 1;
            }
        }
    }
#endif

    return (uint32_t)crc64;
}

// Завершальна інверсія бітів для специфікації Btrfs
uint32_t btrfs_crc32c_final(uint32_t raw_crc)
{
    return raw_crc ^ 0xFFFFFFFFU;
}

int main(void)
{
    // Буфер сектора даних Btrfs (4096 байтів)
    uint8_t sector_buffer[4096];
    for (size_t i = 0; i < sizeof(sector_buffer); i++) {
        sector_buffer[i] = (uint8_t)(i & 0xFF);
    }

    uint32_t crc_state = BTRFS_CRC32C_INIT;
    crc_state = btrfs_crc32c_hardware(crc_state, sector_buffer, sizeof(sector_buffer));
    uint32_t checksum = btrfs_crc32c_final(crc_state);

    printf("Обчислено CRC32c для сектора 4 КіБ: 0x%08X\n", checksum);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <cstddef>
#include <iomanip>

#if defined(__x86_64__) || defined(_M_X64)
#include <nmmintrin.h>
#define HAS_SSE42_CPP 1
#else
#define HAS_SSE42_CPP 0
#endif

namespace btrfs {

class Crc32cCalculator {
public:
    static constexpr std::uint32_t InitialState = 0xFFFFFFFFU;
    static constexpr std::uint32_t XorMask = 0xFFFFFFFFU;

    // Типобезпечне обчислення хешу через std::span без виділення пам'яті
    [[nodiscard]] static std::uint32_t calculate(std::span<const std::byte> buffer, 
                                                std::uint32_t initial = InitialState) noexcept 
    {
        std::uint64_t crc = initial;
        const auto* ptr = reinterpret_cast<const std::uint8_t*>(buffer.data());
        std::size_t length = buffer.size();

#if HAS_SSE42_CPP
        // 1. Вирівнювання адреси буфера
        while (length > 0 && (reinterpret_cast<std::uintptr_t>(ptr) & 7)) {
            crc = _mm_crc32_u8(static_cast<std::uint32_t>(crc), *ptr++);
            --length;
        }

        // 2. Конвеєрне обчислення блоків по 8 байтів
        const auto* p64 = reinterpret_cast<const std::uint64_t*>(ptr);
        std::size_t blocks = length / sizeof(std::uint64_t);
        for (std::size_t i = 0; i < blocks; ++i) {
            crc = _mm_crc32_u64(crc, p64[i]);
        }

        // 3. Залишкові байти
        ptr = reinterpret_cast<const std::uint8_t*>(p64 + blocks);
        length %= sizeof(std::uint64_t);
        while (length > 0) {
            crc = _mm_crc32_u8(static_cast<std::uint32_t>(crc), *ptr++);
            --length;
        }
#else
        for (std::size_t i = 0; i < length; ++i) {
            crc ^= ptr[i];
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc & 1) ? ((crc >> 1) ^ 0x82F63B78U) : (crc >> 1);
            }
        }
#endif

        return static_cast<std::uint32_t>(crc) ^ XorMask;
    }
};

} // namespace btrfs

int main()
{
    // Створення тестового сектора 4 КіБ у RAII-контейнері
    std::vector<std::byte> sector(4096);
    for (std::size_t i = 0; i < sector.size(); ++i) {
        sector[i] = static_cast<std::byte>(i & 0xFF);
    }

    std::uint32_t checksum = btrfs::Crc32cCalculator::calculate(sector);

    std::cout << "Обчислено CRC32c (C++ RAII/std::span): 0x"
              << std::hex << std::uppercase << std::setw(8) << std::setfill('0')
              << checksum << std::endl;

    return 0;
}
```
:::

## Співвідношення швидкодії хеш-алгоритмів Btrfs

Починаючи з ядра Linux 5.5, у Btrfs було додано можливість вибору альтернативних алгоритмів хешування під час форматування файлової системи (`mkfs.btrfs --csum <algo>`).

Вибір алгоритму безпосередньо впливає на навантаження центрального процесора та обсяг оперативної пам'яті, необхідної для кешування `CSUM Tree`:

| Алгоритм | Розмір хешу (байти) | Пропускна здатність (одне ядро CPU) | Споживання диска на 1 ТБ даних | Сфера застосування |
| :--- | :--- | :--- | :--- | :--- |
| **CRC32c** | 4 байти (32 біти) | ~8.5 ГБ/с (апаратний SSE4.2) | ~1 ГБ (CSUM Tree) | Стандарт за замовчуванням для 99% систем |
| **xxHash64** | 8 байт (64 біти) | ~12.2 ГБ/с (скалярний код, без SIMD) | ~2 ГБ (CSUM Tree) | Високопродуктивні масиви з низьким ризиком колізій |
| **SHA256** | 32 байти (256 біт) | ~0.4 ГБ/с (без криптоінструкцій) | ~8 ГБ (CSUM Tree) | Корпоративні сховища з вимогами криптозахисту |
| **BLAKE2b** | 32 байти (256 біт) | ~1.1 ГБ/с (криптографічний) | ~8 ГБ (CSUM Tree) | Швидка криптографічна альтернатива SHA256 |

Обираючи SHA256 або BLAKE2b, адміністратор повинен враховувати, що обсяг `CSUM Tree` зростає у 8 разів, що суттєво зменшує ефективну ємність дискового масиву та збільшує навантаження на сторінковий кеш ядра.
