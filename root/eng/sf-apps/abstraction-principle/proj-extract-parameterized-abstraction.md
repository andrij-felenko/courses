# ⚙️ Від дублювання до параметризованої абстракції: рефакторинг обробника потоку даних

Найчастіше абстракція народжується не з теоретичних роздумів перед білою дошкою, а під час практичного рефакторингу, коли в кодовій базі виявляються два або більше компонентів із підозріло схожою поведінкою. Проте між правильним виділенням спільного семантичного контракту та створенням заплутаного коду з десятками прапорців лежить тонка інженерна межа.

Розглянемо типове завдання бортової обробки телеметрії: отримання кадрів даних із двох фізично різних джерел — бінарного пакета навігаційного модуля GNSS та текстового повідомлення оптичного давача. Подивимося крок за кроком, як трансформувати розрізнений дубльований код у чисту параметризовану абстракцію, що не створює накладних витрат у пам'яті й часі виконання.

## Вихідний стан: дублювання автомата кадрування

Початкова кодова база містить дві окремі незалежні функції парсингу. Кожна з них реалізує власний кінцевий автомат (Finite State Machine, FSM), накопичує вхідні байти в локальний буфер, рахує контрольну суму та передає зібраний корисний вантаж у функцію зворотного виклику.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define GNSS_MAX_PAYLOAD 128
#define OPTIC_MAX_PAYLOAD 64

// Стан парсера GNSS: очікує преамбулу 0xAA 0x55, довжину, байти тіла, контрольний байт XOR
typedef struct {
    uint8_t buf[GNSS_MAX_PAYLOAD];
    size_t len;
    size_t expected_len;
    uint8_t state;
    uint8_t crc;
} gnss_parser_t;

bool gnss_feed_byte(gnss_parser_t* p, uint8_t byte, void (*on_frame)(const uint8_t*, size_t)) {
    switch (p->state) {
        case 0: // Пошук першого байта заголовка 0xAA
            if (byte == 0xAA) { p->state = 1; }
            break;
        case 1: // Пошук другого байта заголовка 0x55
            if (byte == 0x55) { p->state = 2; p->len = 0; p->crc = 0; }
            else { p->state = (byte == 0xAA) ? 1 : 0; }
            break;
        case 2: // Зчитування довжини корисного навантаження
            p->expected_len = byte;
            p->crc ^= byte;
            p->state = (byte <= GNSS_MAX_PAYLOAD) ? 3 : 0;
            break;
        case 3: // Накопичення байтів корисного навантаження
            p->buf[p->len++] = byte;
            p->crc ^= byte;
            if (p->len == p->expected_len) { p->state = 4; }
            break;
        case 4: // Звірка контрольної суми
            p->state = 0;
            if (p->crc == byte) {
                on_frame(p->buf, p->len);
                return true;
            }
            break;
    }
    return false;
}

// Стан парсера оптичного давача: очікує преамбулу '$' (0x24), довжину, дані, байт суми за модулем 256
typedef struct {
    uint8_t buf[OPTIC_MAX_PAYLOAD];
    size_t len;
    size_t expected_len;
    uint8_t state;
    uint8_t crc;
} optic_parser_t;

bool optic_feed_byte(optic_parser_t* p, uint8_t byte, void (*on_frame)(const uint8_t*, size_t)) {
    switch (p->state) {
        case 0: // Пошук заголовка '$' (0x24)
            if (byte == 0x24) { p->state = 1; p->len = 0; p->crc = 0xFF; }
            break;
        case 1: // Зчитування довжини
            p->expected_len = byte;
            p->crc += byte;
            p->state = (byte <= OPTIC_MAX_PAYLOAD) ? 2 : 0;
            break;
        case 2: // Накопичення тіла кадру
            p->buf[p->len++] = byte;
            p->crc += byte;
            if (p->len == p->expected_len) { p->state = 3; }
            break;
        case 3: // Перевірка контрольної суми
            p->state = 0;
            if (p->crc == byte) {
                on_frame(p->buf, p->len);
                return true;
            }
            break;
    }
    return false;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <functional>

constexpr size_t GNSS_MAX_PAYLOAD = 128;
constexpr size_t OPTIC_MAX_PAYLOAD = 64;

// Парсер GNSS на C++ з прямим копіюванням логіки
struct GnssParser {
    uint8_t buf[GNSS_MAX_PAYLOAD];
    size_t len = 0;
    size_t expected_len = 0;
    uint8_t state = 0;
    uint8_t crc = 0;

    template <typename Callback>
    bool feed_byte(uint8_t byte, Callback&& on_frame) {
        switch (state) {
            case 0:
                if (byte == 0xAA) state = 1;
                break;
            case 1:
                if (byte == 0x55) { state = 2; len = 0; crc = 0; }
                else state = (byte == 0xAA) ? 1 : 0;
                break;
            case 2:
                expected_len = byte;
                crc ^= byte;
                state = (byte <= GNSS_MAX_PAYLOAD) ? 3 : 0;
                break;
            case 3:
                buf[len++] = byte;
                crc ^= byte;
                if (len == expected_len) state = 4;
                break;
            case 4:
                state = 0;
                if (crc == byte) {
                    on_frame(std::span<const uint8_t>(buf, len));
                    return true;
                }
                break;
        }
        return false;
    }
};

// Парсер давача на C++
struct OpticParser {
    uint8_t buf[OPTIC_MAX_PAYLOAD];
    size_t len = 0;
    size_t expected_len = 0;
    uint8_t state = 0;
    uint8_t crc = 0;

    template <typename Callback>
    bool feed_byte(uint8_t byte, Callback&& on_frame) {
        switch (state) {
            case 0:
                if (byte == 0x24) { state = 1; len = 0; crc = 0xFF; }
                break;
            case 1:
                expected_len = byte;
                crc += byte;
                state = (byte <= OPTIC_MAX_PAYLOAD) ? 2 : 0;
                break;
            case 2:
                buf[len++] = byte;
                crc += byte;
                if (len == expected_len) state = 3;
                break;
            case 3:
                state = 0;
                if (crc == byte) {
                    on_frame(std::span<const uint8_t>(buf, len));
                    return true;
                }
                break;
        }
        return false;
    }
};
```
:::

### Чому дублювання тут є небезпечним

1. **Зчеплення інваріантів з реалізацією:** обидві функції реалізують однаковий життєвий цикл кадрування: розпізнавання преамбули, валідація довжини на переповнення буфера, наповнення пам'яті, контроль цілісності. Якщо розробник знайде крайовий баг у логіці зіставлення преамбули (наприклад, хибний скид автомата при послідовності `0xAA 0xAA 0x55`), йому доведеться виправляти його двічі в різних місцях.
2. **Комбінаторне зростання коду:** поява в системі барометра, далекоміра чи лідара з власними форматами вимагатиме нових копій того самого автомата, роздуваючи розмір Flash-пам'яті мікроконтролера.
3. **Неузгодженість обробки крайових умов:** у парсері GNSS при невідповідності другого байта преамбули перевіряється умова `(byte == 0xAA) ? 1 : 0`, що рятує від пропуску зміщеного кадру, тоді як у парсері оптичного давача цей випадок пропущено. Дубльований код природно розходиться в поведінці з часом.

## Пастка хибної абстракції: антипатерн «прапорець у спільній функції»

Найгірший спосіб позбутися дублювання — механічно злити обидві функції в одну, додавши булевий прапорець для розрізнення джерела:

:::tabs
```c
// АНТИПАТЕРН: хибна абстракція через змішування деталей за прапорцем
typedef struct {
    uint8_t buf[128];
    size_t len;
    size_t expected_len;
    uint8_t state;
    uint8_t crc;
    bool is_gnss; // ← Прапорець типу джерела
} bad_framer_t;

bool bad_framer_feed(bad_framer_t* p, uint8_t byte, void (*cb)(const uint8_t*, size_t)) {
    if (p->is_gnss) {
        // Розгалуження для першого протоколу
        if (p->state == 0 && byte == 0xAA) p->state = 1;
        // ...
    } else {
        // Розгалуження для другого протоколу
        if (p->state == 0 && byte == 0x24) p->state = 1;
        // ...
    }
    return false;
}
```
```cpp
// АНТИПАТЕРН: хибна абстракція на C++
struct BadFramer {
    uint8_t buf[128];
    size_t len = 0;
    size_t expected_len = 0;
    uint8_t state = 0;
    uint8_t crc = 0;
    bool is_gnss = false; // ← Руйнує чистоту абстракції

    template <typename Callback>
    bool feed(uint8_t byte, Callback&& cb) {
        if (is_gnss) {
            // логіка GNSS...
        } else {
            // логіка давача...
        }
        return false;
    }
};
```
:::

Така псевдоабстракція не вирішує проблему, а погіршує її:
- Вона створює жорстке зчеплення між незалежними протоколами: зміна одного протоколу вимагає редагування файлу, де живуть інші.
- Вона витрачає пам'ять під максимальний розмір буфера з усіх можливих варіантів, навіть якщо для простого давача достатньо 16 байтів.
- З появою п'яти нових протоколів функція перетворюється на некерований клубок `switch (protocol_type)` з важковиявними побічними ефектами.

## Правильне виділення параметризованої абстракції

Згідно з принципом абстракції, ми відокремлюємо:
1. **Інваріантний алгоритм (Абстракцію кадрування):** переходи кінцевого автомата `Header -> Length -> Payload -> Checksum`.
2. **Варіативні параметри (Контракт протоколу):** байти преамбули, максимальна допустима довжина корисного навантаження, початкове значення контрольної суми та математична функція її оновлення.

Нижче наведено дві ідіоматичні реалізації цієї абстракції: динамічна параметризація через структури дескрипторів у мові C та статична абстракція нульової вартості через концепти й шаблони в C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// ── 1. Контракт політики кадрування ──────────────────────────────────
typedef struct {
    const uint8_t* header;
    size_t header_len;
    size_t max_payload;
    uint8_t initial_crc;
    uint8_t (*update_crc)(uint8_t current_crc, uint8_t byte);
} frame_policy_t;

// ── 2. Єдиний механізм кінцевого автомата ───────────────────────────
typedef struct {
    const frame_policy_t* policy;
    uint8_t* buffer;
    size_t buffer_capacity;
    size_t payload_len;
    size_t expected_len;
    size_t header_matched;
    uint8_t crc;
    uint8_t state;
} stream_framer_t;

void stream_framer_init(stream_framer_t* f, const frame_policy_t* policy, uint8_t* buf, size_t cap) {
    f->policy = policy;
    f->buffer = buf;
    f->buffer_capacity = cap;
    f->state = 0;
    f->header_matched = 0;
    f->payload_len = 0;
    f->crc = policy->initial_crc;
}

bool stream_framer_feed(stream_framer_t* f, uint8_t byte, void (*on_frame)(const uint8_t*, size_t)) {
    switch (f->state) {
        case 0: // Зіставлення байтів преамбули довільної довжини
            if (byte == f->policy->header[f->header_matched]) {
                f->header_matched++;
                if (f->header_matched == f->policy->header_len) {
                    f->state = 1;
                    f->header_matched = 0;
                    f->payload_len = 0;
                    f->crc = f->policy->initial_crc;
                }
            } else {
                // Безпечний відкат FSM при частковому збігу преамбули
                f->header_matched = (byte == f->policy->header[0]) ? 1 : 0;
            }
            break;

        case 1: // Читання довжини та перевірка інваріанта переповнення
            f->expected_len = byte;
            f->crc = f->policy->update_crc(f->crc, byte);
            if (byte <= f->buffer_capacity && byte <= f->policy->max_payload) {
                f->state = 2;
            } else {
                f->state = 0; // Відхилення аномально довгого кадру
            }
            break;

        case 2: // Накопичення корисного вантажу в буфер
            f->buffer[f->payload_len++] = byte;
            f->crc = f->policy->update_crc(f->crc, byte);
            if (f->payload_len == f->expected_len) {
                f->state = 3;
            }
            break;

        case 3: // Перевірка контрольної суми
            f->state = 0;
            if (f->crc == byte) {
                on_frame(f->buffer, f->payload_len);
                return true;
            }
            break;
    }
    return false;
}

// ── 3. Декларативні конфігурації конкретних протоколів ───────────────

static uint8_t crc_xor(uint8_t c, uint8_t b) { return c ^ b; }
static uint8_t crc_add(uint8_t c, uint8_t b) { return c + b; }

static const uint8_t GNSS_HDR[] = { 0xAA, 0x55 };
static const frame_policy_t GNSS_POLICY = {
    .header = GNSS_HDR, .header_len = 2,
    .max_payload = 128, .initial_crc = 0x00, .update_crc = crc_xor
};

static const uint8_t OPTIC_HDR[] = { 0x24 };
static const frame_policy_t OPTIC_POLICY = {
    .header = OPTIC_HDR, .header_len = 1,
    .max_payload = 64, .initial_crc = 0xFF, .update_crc = crc_add
};
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>

// ── 1. Контракт через C++20 Concept (перевірка під час компіляції) ──
template <typename P>
concept FramePolicy = requires(uint8_t crc, uint8_t byte) {
    { P::header } -> std::convertible_to<std::span<const uint8_t>>;
    { P::max_payload } -> std::convertible_to<size_t>;
    { P::initial_crc } -> std::convertible_to<uint8_t>;
    { P::update_crc(crc, byte) } -> std::same_as<uint8_t>;
};

// ── 2. Параметризований FSM з нульовими накладними витратами ────────
template <FramePolicy Policy>
class StreamFramer {
public:
    template <typename Callback>
    bool feed_byte(uint8_t byte, Callback&& on_frame) {
        switch (state_) {
            case State::Header:
                if (byte == Policy::header[header_matched_]) {
                    if (++header_matched_ == Policy::header.size()) {
                        state_ = State::Length;
                        header_matched_ = 0;
                        payload_len_ = 0;
                        crc_ = Policy::initial_crc;
                    }
                } else {
                    header_matched_ = (byte == Policy::header[0]) ? 1 : 0;
                }
                break;

            case State::Length:
                expected_len_ = byte;
                crc_ = Policy::update_crc(crc_, byte);
                if (byte <= buffer_.size() && byte <= Policy::max_payload) {
                    state_ = State::Payload;
                } else {
                    state_ = State::Header;
                }
                break;

            case State::Payload:
                buffer_[payload_len_++] = byte;
                crc_ = Policy::update_crc(crc_, byte);
                if (payload_len_ == expected_len_) {
                    state_ = State::Crc;
                }
                break;

            case State::Crc:
                state_ = State::Header;
                if (crc_ == byte) {
                    on_frame(std::span<const uint8_t>(buffer_.data(), payload_len_));
                    return true;
                }
                break;
        }
        return false;
    }

private:
    enum class State : uint8_t { Header, Length, Payload, Crc };

    std::array<uint8_t, Policy::max_payload> buffer_{};
    size_t payload_len_{0};
    size_t expected_len_{0};
    size_t header_matched_{0};
    uint8_t crc_{Policy::initial_crc};
    State state_{State::Header};
};

// ── 3. Статичні описи протоколів (дані застигають під час збірки) ────

struct GnssPolicy {
    static constexpr uint8_t hdr_bytes[] = { 0xAA, 0x55 };
    static constexpr std::span<const uint8_t> header{hdr_bytes};
    static constexpr size_t max_payload = 128;
    static constexpr uint8_t initial_crc = 0x00;

    static constexpr uint8_t update_crc(uint8_t crc, uint8_t byte) noexcept {
        return crc ^ byte;
    }
};

struct OpticPolicy {
    static constexpr uint8_t hdr_bytes[] = { 0x24 };
    static constexpr std::span<const uint8_t> header{hdr_bytes};
    static constexpr size_t max_payload = 64;
    static constexpr uint8_t initial_crc = 0xFF;

    static constexpr uint8_t update_crc(uint8_t crc, uint8_t byte) noexcept {
        return static_cast<uint8_t>(crc + byte);
    }
};

// Конкретні типи парсерів створюються інстанціюванням єдиного шаблону:
using GnssFramer = StreamFramer<GnssPolicy>;
using OpticFramer = StreamFramer<OpticPolicy>;
```
:::

## Покроковий розбір структури та керування пам'яттю

Зверніть увагу на те, як вирішено питання виділення оперативної пам'яті в обох мовах:

1. **Ізоляція розміщення пам'яті в C:**
   Структура `stream_framer_t` не містить фіксованого внутрішнього буфера `uint8_t buf[...]`. Натомість вона приймає зовнішній вказівник `uint8_t* buffer` та розмір `buffer_capacity` під час виклику `stream_framer_init()`. Це дозволяє викликачеві самостійно вирішувати, де розміщувати буфер: у статичній пам'яті, на стеку чи в окремому пулі DMA-буферів.
2. **Типобезпечний буфер фіксованого розміру в C++:**
   Клас `StreamFramer` використовує `std::array<uint8_t, Policy::max_payload>`. Завдяки тому, що максимальний розмір є константою часу компіляції (`constexpr`), кожен спеціалізований парсер виділяє рівно стільки байтів, скільки потрібно його протоколу (128 байтів для GNSS і 64 байти для давача), без динамічної алокації в купі.

## Аналіз асемблерного лістингу та продуктивності

Порівняння згенерованого асемблерного коду (під архітектуру ARM Cortex-M4 з оптимізацією `-O2`) демонструє ключову різницю двох підходів:

- **У версії на C:** виклик `f->policy->update_crc(f->crc, byte)` генерує непряме завантаження адреси функції `ldr r3, [r0, #16]` та виклик `blx r3`. Це коштує додаткових 3–4 тактів на кожен прийнятий байт, але весь код автомата кадрування існує в пам'яті програм Flash в одному екземплярі (близько 160 байтів коду).
- **У версії на C++:** компілятор виконує повну мономорфізацію шаблону `StreamFramer<GnssPolicy>`. Тіло `update_crc` підставляється безпосередньо в тіло автомата у вигляді єдиної інструкції `eor r2, r2, r1` (виключне АБО). Усі перевірки преамбули скомпульовані в прямі порівняння з константами `0xAA` та `0x55`. В асемблерному коді немає жодного непрямого переходу чи розіменування покажчиків: швидкість обробки байта становить 2–3 такти процесора.

## Архітектурний підсумок

1. **Єдине джерело правди для кадрування:** весь складний механізм автомата кадрування, захист інваріантів пам'яті та керування станом зосереджені в одному місці. Якщо ми додамо тайм-аут скиду зв'язку чи покращимо логіку відновлення синхронізації, це виправлення миттєво запрацює для всіх давачів системи.
2. **Декларативність нових протоколів:** підключення нового пристрою (наприклад, далекоміра `LidarPolicy`) вимагає лише оголошення кількох статичних констант заголовка та формули цілісності. Інженеру більше не потрібно писати вразливі кінцеві автомати вручну.
3. **Гнучкість вибору стратегії оптимізації:** інженер може обрати C-варіант для екстремальної економії Flash-пам'яті (один спільний FSM у коді) або C++-варіант для досягнення абсолютної швидкодії без накладних витрат у рантаймі.
