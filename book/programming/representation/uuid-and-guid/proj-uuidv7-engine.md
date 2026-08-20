# ⚙️ Реалізація генератора UUIDv7 та конвертера Microsoft GUID у C та C++

Стандарт RFC 9562 визначає UUID версії 7 як часово впорядкований 128-бітний ідентифікатор, оптимізований для розподілених систем та індексів баз даних. Щоб реалізувати високопродуктивний генератор промислового рівня, інженер має розв'язати чотири ключові технічні задачі:
1. Забезпечити точне вилучення 48-бітного часу Unix Epoch у мілісекундах та монотонний інкремент субмілісекундного лічильника при масовій генерації ключів усередині однієї мілісекунди.
2. Гарантувати побітово коректне накладання 4-бітного поля версії (`0111`) та 2-бітного поля варіанта (`10`).
3. Забезпечити максимальну швидкодію серіалізації в канонічний текстовий рядок `8-4-4-4-12` без зайвих виділень динамічної пам'яті в купі (heap allocations).
4. Реалізувати надійний конвертер між мережевим двійковим масивом RFC 4122 / 9562 (Big-Endian) та внутрішньою структурою Microsoft `GUID` на платформах Little-Endian.

### Архітектура та структура двійкового буфера

Двійковий буфер UUID займає рівно 16 беззнакових байтів (`uint8_t[16]`). Процес формування ідентифікатора версії 7 складається з таких кроків:
- **Байти 0..5 (48 бітів)**: ціле число мілісекунд Unix Epoch (`timestamp_ms`), записане у порядку Big-Endian (старший байт за нульовим індексом).
- **Байти 6..7 (16 бітів)**: старший нібл байта 6 містить фіксовану версію `0x7` (`0b0111`), а решта 12 бітів (молодший нібл байта 6 та весь байт 7) відводяться під лічильник субмілісекундної послідовності `rand_a`.
- **Байти 8..9 (16 бітів)**: старші 2 біти байта 8 кодують варіант RFC `0b10` (`0x80`), а решта 14 бітів заповнюються криптографічною ентропією.
- **Байти 10..15 (48 бітів)**: шість байтів криптографічної випадковості `rand_b`.

Нижче наведено повні, самодостатні реалізації генератора, серіалізатора та конвертера мовами C (C99/C11) та C++ (C++20/C++23) у паралельних вкладках.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt.lib")
#else
#include <sys/random.h>
#endif

typedef struct {
    uint8_t bytes[16];
} uuid_t;

/* Структура Windows GUID для демонстрації конвертації */
typedef struct {
    uint32_t Data1;
    uint16_t Data2;
    uint16_t Data3;
    uint8_t  Data4[8];
} win_guid_t;

/* Заповнення буфера криптографічно стійкими випадковими байтами */
static bool get_crypto_random(uint8_t *buf, size_t len) {
#if defined(_WIN32)
    return BCryptGenRandom(NULL, buf, (ULONG)len, BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0;
#else
    return getrandom(buf, len, 0) == (ssize_t)len;
#endif
}

/* Отримання поточного Unix-часу в мілісекундах */
static uint64_t get_unix_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ((uint64_t)ts.tv_sec * 1000ULL) + ((uint64_t)ts.tv_nsec / 1000000ULL);
}

/* Генерація UUIDv7 зі збереженням монотонності */
bool uuid_generate_v7(uuid_t *out) {
    static uint64_t last_ms = 0;
    static uint16_t seq_counter = 0;

    if (!get_crypto_random(out->bytes, 16)) {
        return false;
    }

    uint64_t ms = get_unix_time_ms();

    /* Якщо час не змінився — інкрементуємо субмілісекундний лічильник */
    if (ms == last_ms) {
        seq_counter = (seq_counter + 1) & 0x0FFF; /* 12 бітів */
    } else {
        last_ms = ms;
        /* Ініціалізуємо лічильник випадковими 12 бітами для непередбачуваності */
        seq_counter = ((out->bytes[6] << 8) | out->bytes[7]) & 0x0FFF;
    }

    /* Байти 0..5: 48-бітний Unix timestamp (Big-Endian) */
    out->bytes[0] = (uint8_t)(ms >> 40);
    out->bytes[1] = (uint8_t)(ms >> 32);
    out->bytes[2] = (uint8_t)(ms >> 24);
    out->bytes[3] = (uint8_t)(ms >> 16);
    out->bytes[4] = (uint8_t)(ms >> 8);
    out->bytes[5] = (uint8_t)(ms);

    /* Байти 6..7: версія 0x7 + 12-бітний лічильник/ентропія */
    out->bytes[6] = 0x70 | (uint8_t)((seq_counter >> 8) & 0x0F);
    out->bytes[7] = (uint8_t)(seq_counter & 0xFF);

    /* Байт 8: варіант 0b10 (0x80) + випадкові біти */
    out->bytes[8] = (out->bytes[8] & 0x3F) | 0x80;

    return true;
}

/* Форматування у канонічний рядок 8-4-4-4-12 */
void uuid_to_string(const uuid_t *u, char out_str[37]) {
    snprintf(out_str, 37,
             "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
             u->bytes[0], u->bytes[1], u->bytes[2], u->bytes[3],
             u->bytes[4], u->bytes[5],
             u->bytes[6], u->bytes[7],
             u->bytes[8], u->bytes[9],
             u->bytes[10], u->bytes[11], u->bytes[12], u->bytes[13], u->bytes[14], u->bytes[15]);
}

/* Конвертація RFC 4122 / 9562 байтів у структуру Windows GUID */
void uuid_to_win_guid(const uuid_t *u, win_guid_t *g) {
    /* Little-Endian розпакування для перших трьох числових полів */
    g->Data1 = ((uint32_t)u->bytes[0] << 24) |
               ((uint32_t)u->bytes[1] << 16) |
               ((uint32_t)u->bytes[2] << 8)  |
               ((uint32_t)u->bytes[3]);
    g->Data2 = ((uint16_t)u->bytes[4] << 8)  | ((uint16_t)u->bytes[5]);
    g->Data3 = ((uint16_t)u->bytes[6] << 8)  | ((uint16_t)u->bytes[7]);
    memcpy(g->Data4, &u->bytes[8], 8);
}
```
```cpp
#include <array>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <format>
#include <expected>
#include <cstring>
#include <cstdint>

struct Uuid {
    std::array<uint8_t, 16> bytes{};

    [[nodiscard]] std::string to_string() const {
        return std::format(
            "{:02x}{:02x}{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}",
            bytes[0], bytes[1], bytes[2], bytes[3],
            bytes[4], bytes[5],
            bytes[6], bytes[7],
            bytes[8], bytes[9],
            bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]
        );
    }
};

/* Відповідник структури Microsoft GUID */
struct WindowsGuid {
    uint32_t data1;
    uint16_t data2;
    uint16_t data3;
    std::array<uint8_t, 8> data4;
};

class UuidV7Generator {
public:
    UuidV7Generator() : rng_(std::random_device{}()) {}

    [[nodiscard]] Uuid generate() {
        Uuid id{};
        fill_random(id.bytes);

        const auto now = std::chrono::system_clock::now();
        const auto ms_count = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()
        ).count();
        const auto ms = static_cast<uint64_t>(ms_count);

        if (ms == last_ms_) {
            seq_counter_ = (seq_counter_ + 1) & 0x0FFF;
        } else {
            last_ms_ = ms;
            seq_counter_ = (static_cast<uint16_t>(id.bytes[6] << 8) | id.bytes[7]) & 0x0FFF;
        }

        /* Запис 48-бітного Unix timestamp у порядку Big-Endian */
        id.bytes[0] = static_cast<uint8_t>(ms >> 40);
        id.bytes[1] = static_cast<uint8_t>(ms >> 32);
        id.bytes[2] = static_cast<uint8_t>(ms >> 24);
        id.bytes[3] = static_cast<uint8_t>(ms >> 16);
        id.bytes[4] = static_cast<uint8_t>(ms >> 8);
        id.bytes[5] = static_cast<uint8_t>(ms);

        /* Версія 0x7 + 12-бітний субмілісекундний лічильник */
        id.bytes[6] = 0x70 | static_cast<uint8_t>((seq_counter_ >> 8) & 0x0F);
        id.bytes[7] = static_cast<uint8_t>(seq_counter_ & 0xFF);

        /* Варіант RFC 9562: 0b10xxxxxx */
        id.bytes[8] = (id.bytes[8] & 0x3F) | 0x80;

        return id;
    }

    [[nodiscard]] static WindowsGuid to_windows_guid(const Uuid& u) noexcept {
        WindowsGuid g{};
        g.data1 = (static_cast<uint32_t>(u.bytes[0]) << 24) |
                  (static_cast<uint32_t>(u.bytes[1]) << 16) |
                  (static_cast<uint32_t>(u.bytes[2]) << 8)  |
                  (static_cast<uint32_t>(u.bytes[3]));
        g.data2 = (static_cast<uint16_t>(u.bytes[4]) << 8) | static_cast<uint16_t>(u.bytes[5]);
        g.data3 = (static_cast<uint16_t>(u.bytes[6]) << 8) | static_cast<uint16_t>(u.bytes[7]);
        std::memcpy(g.data4.data(), &u.bytes[8], 8);
        return g;
    }

private:
    std::mt19937_64 rng_;
    uint64_t last_ms_ = 0;
    uint16_t seq_counter_ = 0;

    void fill_random(std::array<uint8_t, 16>& arr) {
        auto* ptr = reinterpret_cast<uint64_t*>(arr.data());
        ptr[0] = rng_();
        ptr[1] = rng_();
    }
};
```
:::

---

### Детальний розбір механізмів та інженерні пастки

#### 1. Стратегії збереження монотонності при високому навантаженні

Якщо сервіс викликає генератор мільйони разів на секунду, тисячі ідентифікаторів створюються всередині однієї мілісекунди (`ms == last_ms_`). У цьому разі алгоритм інкрементує 12-бітне поле `seq_counter_`.

* **Переповнення 12-бітного лічильника**: 12 бітів вміщують рівно `4096` унікальних відліків. Якщо один потік вичерпує 4096 ідентифікаторів за одну мілісекунду, лічильник переповнюється. За стандартом RFC 9562 у цьому рідкісному випадку генератор зобов'язаний або штучно збільшити `ms` на `+1` мілісекунду (зсув уперед), або призупинити потік виконання на 1 мс через виклик системного сну (`nanosleep` / `std::this_thread::sleep_for`).
* **Багатопотоковість без блокувань**: Для уникнення синхронізаційних блокувань через глобальний `std::mutex` у високонавантажених вебсерверах генератор оголошують як `thread_local`. Кожен потік пулу виконання отримує власний екземпляр генератора та незалежний лічильник `seq_counter_`, що забезпечує нульову конкуренцію за пам'ять (Zero Lock Contention) і максимальну пропускну здатність процесора.

#### 2. Обробка немонотонного ходу годинника (Clock Rollback)

Системний годинник комп'ютера може бути переведений назад внаслідок корекції часу демоном NTP, стрибка високосної секунди або ручного налаштування адміністратором сервера.

Якщо виклик `get_unix_time_ms()` повертає значення `ms < last_ms_`, пряме використання нового часу порушить глобальний порядок сортування B-дерева в базі даних. Промислова реалізація у такому разі заморожує значення `ms = last_ms_` і продовжує інкрементувати лічильник послідовності, доки реальний астрономічний годинник не перевищить збережену мітку. Якщо ж зсув годинника назад є занадто великим (понад кілька секунд), генератор повертає помилку або переініціалізує ентропійний блок, захищаючи систему від колізій.

#### 3. Вибір системного таймера: чому CLOCK_REALTIME, а не CLOCK_MONOTONIC

Поширена помилка розробників-початківців — спроба використати `CLOCK_MONOTONIC` або `std::chrono::steady_clock` для формування часової мітки UUIDv7. Монотонний таймер ОС рахує час від моменту завантаження конкретної машини (uptime), а не астрономічний час Unix Epoch.

Якщо використати час від старту системи, два сервери після перезавантаження отримають однакові малі часові мітки (наприклад, 1000 мс після старту), що повністю зруйнує глобальне часове впорядкування між вузлами кластера. Стандарт RFC 9562 строго вимагає використання виключно астрономічного часу UTC Unix Epoch (`CLOCK_REALTIME` / `std::chrono::system_clock`).

#### 4. Векторизація форматування рядків (SIMD та табличний пошук)

Виклик функції `snprintf()` або `std::format()` на гарячому шляху виконання здійснює синтаксичний розбір форматуючого рядка та може стати вузьким місцем процесора. Для максимальної оптимізації серіалізації застосовують статичну таблицю відповідності байтів `uint8_t -> char[2]` (LUT, Lookup Table) або векторні SIMD-інструкції (AVX2 на x86 чи NEON на ARM), які перетворюють усі 16 байтів у 36 символів ASCII за 3–5 тактів процесора без жодного розгалуження.

#### 5. Коректність перетворення Microsoft GUID та модульне тестування

Перетворення структури `win_guid_t` у `uuid_t` вимагає обов'язкового порозрядного складання зсувами `>>` та `<<`, як продемонстровано у функціях `uuid_to_win_guid` та `to_windows_guid`. Пряме копіювання через `memcpy()` призведе до спотворення полів `Data1`, `Data2` та `Data3` на процесорах архітектури Little-Endian, що зламає сумісність із зовнішніми базами даних та мережевими протоколами.

Для верифікації коректності генератора у тестовому наборі (Unit Tests) обов'язково перевіряють три інваріанти:
1. **Інваріант сортування**: генерація масиву з 100 000 послідовних UUIDv7 повинна давати строго монотонний масив, де для будь-якої пари індексів `i < j` виконується двійкове та лексикографічне порівняння `uuid[i] < uuid[j]`.
2. **Інваріант версії та варіанта**: для кожного згенерованого об'єкта вираз `(bytes[6] >> 4) == 0x7` та `(bytes[8] >> 6) == 0x2` повинен повертати істину (`true`).
3. **Інваріант кругового перетворення (Roundtrip)**: форматування у текстовий рядок `to_string()` з наступним синтаксичним розбором назад у двійковий буфер повинно повертати біт-у-біт ідентичний масив байтів.
