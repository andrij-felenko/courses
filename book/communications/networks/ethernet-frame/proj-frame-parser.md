# ⚙️ Розбір та валідація Ethernet-кадру на C та C++

Практичний аналіз сирого двійкового буфера, отриманого з сокета `AF_PACKET`, драйвера мережевої карти або файлу дампу pcap, вимагає суворого послідовного розбору. Парсер повинен коректно розрізняти формати Ethernet II та IEEE 802.3, розгортати довільну кількість вкладених тегів VLAN (IEEE 802.1Q та 802.1ad QinQ), безпечно виділяти корисне навантаження без виходу за межі пам'яті та верифікувати апаратну контрольну суму FCS за алгоритмом CRC-32.

Нижче наведено проектування та реалізацію надійного парсера двома мовами програмування: процедурною C з прямим контролем вказівників і пам'яті та сучасною ідіоматичною C++20 з використанням безпечних представлень пам'яті `std::span`, типізованих результатів `std::expected` та компіляторного розрахунку констант `consteval`.

### Архітектура та етапи розбору кадру

Процес розбору сирого байтового масиву складається з п'яти обов'язкових послідовних кроків:

```
[Сирий буфер] ──> 1. Перевірка мінімального розміру (>= 14 Б)
              ──> 2. Зчитування Dst MAC, Src MAC
              ──> 3. Цикл розгортання тегів 802.1Q / 802.1ad (0x8100 / 0x88A8)
              ──> 4. Аналіз EtherType (Ethernet II) або Length + LLC/SNAP (802.3)
              ──> 5. Виділення Payload та перевірка FCS CRC-32
```

1. **Перевірка базових меж буфера:** Перед зверненням до будь-яких полів парсер зобов'язаний перевірити, що отриманий буфер має розмір щонайменше 14 байтів (розмір мінімального заголовка Ethernet). Якщо довжина менша, кадр вважається обрізаним або пошкодженим (Truncated Frame) і негайно відкидається.
2. **Зчитування апаратних адрес:** Перші 12 байтів копіюються або проектуються на структуру `mac_address`. Парсер перевіряє біт `dst_mac[0] & 0x01`, щоб встановити, чи є кадр Unicast, Multicast чи Broadcast.
3. **Ітеративне зняття тегів VLAN:** Поле на зміщенні `0x0C` перевіряється на наявність сигнатур `0x8100` (802.1Q C-Tag) або `0x88A8` (802.1ad S-Tag). Якщо тег присутній, парсер фіксує пріоритет PCP, прапор DEI та номер VLAN ID, після чого зсуває вказівник на 4 байти вперед і повторює перевірку. Це дозволяє прозоро обробляти нетеговані кадри, кадри з одним тегом та кадри з подвійним тегуванням QinQ.
4. **Розпізнавання протоколу та відтинання паддінгу:** Якщо після зняття всіх тегів поле протоколу `>= 0x0600`, кадр розпізнано як Ethernet II, і значення є кодом `EtherType`. Якщо значення `<= 1500`, парсер інтерпретує його як довжину за стандартом IEEE 802.3 і перевіряє наявність 8-байтового заголовка LLC/SNAP. Якщо розмір даних менший за 46 байтів, надлишкові нульові байти заповнення (Padding) відтинаються на основі довжини, вказаної у внутрішньому IP-заголовку.
5. **Обчислення та верифікація CRC-32 (FCS):** Якщо сирий кадр містить 4 кінцеві байти FCS (приймання з відключеним апаратним stripping), парсер обчислює циклічну контрольну суму за стандартом IEEE 802.3 (поліном `0xEDB88320` у віддзеркаленому представленні) від початку кадру до кінця корисних даних.

### Математика та алгоритм перевірки CRC-32

Контрольна сума FCS у стандарті Ethernet обчислюється над поліномом 32-го степеня:
`P(x) = x³² + x²⁶ + x²³ + x²² + x¹⁶ + x¹² + x¹¹ + x¹⁰ + x⁸ + x⁷ + x⁵ + x⁴ + x² + x + 1`

У прямому двійковому вигляді цей поліном представляється числом `0x04C11DB7`. Оскільки біти в кожному байті Ethernet передаються по дроту молодшим бітом уперед (LSB-first), апаратура Ethernet та оптимізовані програмні таблиці використовують віддзеркалений (Reflected/Reversed) поліном `0xEDB88320`.

Алгоритм використовує попередньо згенеровану таблицю на 256 елементів по 32 біти (1 КБ пам'яті), що дозволяє обробляти рівно один вхідний байт за кілька простих операцій: зсув, побітове виключне АБО (`XOR`) та одне звернення до масиву в кеші L1.

Існує два еквівалентних способи перевірки цілісності кадру:
1. Обчислити CRC-32 над усіма байтами кадру від `dst_mac` до кінця `payload` (без 4 байтів FCS), інвертувати результат і порівняти його з 32-бітним числом, записаним у полі FCS.
2. Пропустити через функцію оновлення CRC **весь кадр цілком**, включаючи самі 4 байти FCS. Якщо кадр не містить помилок, підсумковий регістр CRC набуває строго фіксованої константи, відомої як **магічний залишок** (*Magic Residue* / *CRC-32 Remainder*): `0x2144DF1C` (або `0xDEBB20E3` залежно від фінальної інверсії). Ця властивість дозволяє апаратурі перевіряти цілісність без окремого збереження та порівняння контрольної суми.

Важливо не плутати алгоритм CRC-32 стандарту IEEE 802.3 Ethernet (поліном `0xEDB88320`) з модифікацією CRC-32C (поліном Кастаньолі `0x82F63B78`). Поліном Кастаньолі має спеціальну апаратну інструкцію в наборі x86 SSE4.2 (`_mm_crc32_u64`), але обчислює зовсім інші контрольні суми. Для Ethernet CRC-32 на процесорах x86 без спеціалізованих інструкцій PCLMULQDQ найшвидшим методом залишається табличний підхід або техніка Slicing-by-8.

### Оптимізація обчислення: техніка Slicing-by-8 та векторні інструкції SIMD

Класичний табличний алгоритм CRC обробляє рівно один байт за ітерацію. На гігабітних та 10-гігабітних швидкостях це створює помітне навантаження на процесор. Для прискорення обчислень у програмних маршрутизаторах застосовують метод **Slicing-by-8** (розроблений інженерами Intel).

Ідея методу полягає в тому, що замість 1 байта алгоритм зчитує 64-бітне машинне слово (8 байтів) за один такт процесора. Для цього генеруються 8 паралельних таблиць по 256 елементів (сумарно 8 КБ, що ідеально поміщається в кеш L1D процесора). Кожна таблиця відповідає внеску відповідного байта у фінальний залишок полінома:
```
CRC = Table7[Byte0] ^ Table6[Byte1] ^ Table5[Byte2] ^ Table4[Byte3] ^
      Table3[Byte4] ^ Table2[Byte5] ^ Table1[Byte6] ^ Table0[Byte7]
```
Метод Slicing-by-8 забезпечує швидкість обробки на рівні 3.5 – 4.2 ГБ/с на одне процесорне ядро, що повністю закриває потреби 10-гігабітного каналу.

На сучасних процесорах з підтримкою векторного множення без переносів (інструкція `PCLMULQDQ` в архітектурі x86 або `PMULL` в архітектурі ARMv8 NEON) обчислення CRC-32 виконується над 128-бітними або 256-бітними регістрами паралельно. Потік даних розбивається на блоки, які множаться на попередньо обчислені константи поліноміального зсуву в полі Галуа GF(2), досягаючи пропускної здатності понад 15–20 ГБ/с.

### Покрокове трасування розбору реального дампа

Розглянемо реальний байтовий дамп 64-байтового тегованого Ethernet-кадру, отриманого з транкового порту комутатора. Дамп містить один тег VLAN 802.1Q (VID = 100, PCP = 5) та ARP-запит:

```
0000: 00 1a 2b 3c 4d 5e 00 50 56 c0 00 08 81 00 a0 64
0010: 08 06 00 01 08 00 06 04 00 01 00 50 56 c0 00 08
0020: c0 a8 01 01 00 00 00 00 00 00 c0 a8 01 64 00 00
0030: 00 00 00 00 00 00 00 00 00 00 00 00 7a 4b 1c 9e
```

Побайтовий аналіз дампа парсером:
1. **Зміщення `0x00..0x05` (`00 1a 2b 3c 4d 5e`):** Адреса призначення. Перший байт `0x00` має молодший біт `0`, отже це Unicast-кадр.
2. **Зміщення `0x06..0x0B` (`00 50 56 c0 00 08`):** Адреса джерела (віртуальна машина VMware, OUI `00:50:56`).
3. **Зміщення `0x0C..0x0D` (`81 00`):** Поле містить сигнатуру `0x8100` (IEEE 802.1Q). Парсер фіксує наявність тега VLAN і переходить до аналізу наступних двох байтів TCI.
4. **Зміщення `0x0E..0x0F` (`a0 64`):** 16-бітне слово TCI = `0xA064` (`1010 0000 0110 0100` у двійковому вигляді):
   - Старші 3 біти (`101` у двійковому вигляді = 5 десяткове): клас пріоритету **PCP = 5** (Voice / Голосовий трафік).
   - 4-й біт (`0`): прапор **DEI = 0** (кадр не підлягає першочерговому скиданню).
   - Молодші 12 бітів (`0x064` = 100 десяткове): номер віртуальної мережі **VID = 100**.
5. **Зміщення `0x10..0x11` (`08 06`):** Справжнє поле EtherType після зняття тега = `0x0806` (протокол **ARP**).
6. **Зміщення `0x12..0x2D` (28 байтів):** Тіло ARP-пакета (апаратний тип Ethernet `0x0001`, протокол IPv4 `0x0800`, розмір адрес 6 і 4 байти, код операції Request `0x0001`, IP джерела `192.168.1.1`, шукана IP `192.168.1.100`).
7. **Зміщення `0x2E..0x3B` (14 байтів):** Нульове заповнення (**Padding**). Оскільки заголовок (18 байтів із тегом) + ARP (28 байтів) = 46 байтів, а мінімальний кадр без FCS дорівнює 60 байтам, мережевий чип дописав 14 нульових байтів.
8. **Зміщення `0x3C..0x3F` (`7a 4b 1c 9e`):** Контрольна сума **FCS CRC-32**. Обчислення CRC-32 від перших 60 байтів дає рівно `0x9E1C4B7A`, що в порядку молодшим байтом уперед записується як `7a 4b 1c 9e`. Цілісність кадру підтверджено.

### Реалізація на мовах C та C++

У реалізації на C використовується класичний підхід із перевіркою кодів повернення та вказівників. Реалізація на C++20 використовує `std::span<const uint8_t>` для захисту від переповнення буфера без копіювання пам'яті, тип `std::expected` для безпечної обробки помилок та шаблонну генерацію таблиці CRC під час компіляції (`consteval`).

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ETH_ALEN           6
#define ETH_MIN_LEN        60
#define ETH_MAX_LEN        1514
#define ETHERTYPE_VLAN     0x8100
#define ETHERTYPE_QINQ     0x88A8

/* Структура результату розбору кадру */
typedef struct {
    uint8_t  dst_mac[ETH_ALEN];
    uint8_t  src_mac[ETH_ALEN];
    uint16_t vlan_ids[2];       /* Підтримка до 2 вкладених тегів (QinQ) */
    uint8_t  vlan_pcp[2];
    uint8_t  vlan_count;
    uint16_t ethertype;         /* Підсумковий EtherType після зняття тегів */
    const uint8_t *payload;     /* Вказівник на початок корисних даних */
    size_t   payload_len;       /* Довжина корисних даних */
    bool     fcs_valid;         /* Результат перевірки CRC-32 */
} parsed_frame_t;

/* Таблиця для швидкого розрахунку CRC-32 IEEE 802.3 */
static uint32_t crc32_table[256];
static bool crc32_table_ready = false;

static void init_crc32_table(void) {
    const uint32_t polynomial = 0xEDB88320u;
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t crc = i;
        for (int j = 0; j < 8; ++j) {
            if (crc & 1)
                crc = (crc >> 1) ^ polynomial;
            else
                crc >>= 1;
        }
        crc32_table[i] = crc;
    }
    crc32_table_ready = true;
}

uint32_t ethernet_crc32(const uint8_t *data, size_t len) {
    if (!crc32_table_ready)
        init_crc32_table();

    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        uint8_t table_idx = (uint8_t)((crc ^ data[i]) & 0xFF);
        crc = (crc >> 8) ^ crc32_table[table_idx];
    }
    return crc ^ 0xFFFFFFFFu;
}

/* Безпечний парсер Ethernet-кадру */
int parse_ethernet_frame(const uint8_t *raw_buf, size_t buf_len,
                         bool has_fcs, parsed_frame_t *out) {
    if (!raw_buf || !out || buf_len < 14)
        return -1; /* Помилка: буфер замалий для мінімального заголовка */

    memset(out, 0, sizeof(*out));
    memcpy(out->dst_mac, raw_buf, ETH_ALEN);
    memcpy(out->src_mac, raw_buf + ETH_ALEN, ETH_ALEN);

    size_t offset = 12;
    out->vlan_count = 0;

    /* Зчитуємо та знімаємо теги VLAN (до 2 рівнів) */
    while (offset + 4 <= buf_len && out->vlan_count < 2) {
        uint16_t tag_type = (uint16_t)((raw_buf[offset] << 8) | raw_buf[offset + 1]);
        if (tag_type != ETHERTYPE_VLAN && tag_type != ETHERTYPE_QINQ)
            break;

        uint16_t tci = (uint16_t)((raw_buf[offset + 2] << 8) | raw_buf[offset + 3]);
        out->vlan_pcp[out->vlan_count] = (uint8_t)((tci >> 13) & 0x07);
        out->vlan_ids[out->vlan_count] = (uint16_t)(tci & 0x0FFF);
        out->vlan_count++;
        offset += 4;
    }

    if (offset + 2 > buf_len)
        return -2; /* Обрізаний заголовок після тегів VLAN */

    out->ethertype = (uint16_t)((raw_buf[offset] << 8) | raw_buf[offset + 1]);
    offset += 2;

    /* Перевірка формату IEEE 802.3 LLC/SNAP */
    if (out->ethertype <= 1500) {
        if (offset + 8 <= buf_len &&
            raw_buf[offset] == 0xAA && raw_buf[offset + 1] == 0xAA && raw_buf[offset + 2] == 0x03) {
            /* SNAP Header знайдено */
            out->ethertype = (uint16_t)((raw_buf[offset + 6] << 8) | raw_buf[offset + 7]);
            offset += 8;
        }
    }

    size_t data_end = buf_len;
    if (has_fcs) {
        if (buf_len < offset + 4)
            return -3; /* Буфер не містить 4 байтів FCS */
        data_end -= 4;

        uint32_t expected_crc = ethernet_crc32(raw_buf, data_end);
        uint32_t actual_crc = (uint32_t)raw_buf[data_end] |
                             ((uint32_t)raw_buf[data_end + 1] << 8) |
                             ((uint32_t)raw_buf[data_end + 2] << 16) |
                             ((uint32_t)raw_buf[data_end + 3] << 24);
        out->fcs_valid = (expected_crc == actual_crc);
    } else {
        out->fcs_valid = true; /* Апаратне розвантаження підтвердило цілісність */
    }

    out->payload = raw_buf + offset;
    out->payload_len = data_end - offset;
    return 0;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <string>
#include <vector>
#include <expected>
#include <format>
#include <bit>

namespace net {

inline constexpr std::size_t mac_len = 6;
inline constexpr uint16_t ethertype_vlan = 0x8100;
inline constexpr uint16_t ethertype_qinq = 0x88A8;

using mac_address = std::array<uint8_t, mac_len>;

enum class parse_error {
    buffer_too_small,
    truncated_vlan_header,
    missing_fcs,
    checksum_mismatch
};

struct vlan_info {
    uint16_t vid{0};
    uint8_t  pcp{0};
    bool     dei{false};
};

struct ethernet_frame {
    mac_address dst_mac{};
    mac_address src_mac{};
    std::vector<vlan_info> vlans{};
    uint16_t ethertype{0};
    std::span<const uint8_t> payload{};
    bool fcs_verified{false};

    [[nodiscard]] std::string format_dst_mac() const {
        return std::format("{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}",
            dst_mac[0], dst_mac[1], dst_mac[2], dst_mac[3], dst_mac[4], dst_mac[5]);
    }
};

/* Генерація таблиці CRC-32 під час компіляції (C++20 consteval) */
consteval auto generate_crc32_table() {
    std::array<uint32_t, 256> table{};
    constexpr uint32_t polynomial = 0xEDB88320u;
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t crc = i;
        for (int j = 0; j < 8; ++j) {
            if (crc & 1)
                crc = (crc >> 1) ^ polynomial;
            else
                crc >>= 1;
        }
        table[i] = crc;
    }
    return table;
}

inline constexpr auto crc32_table = generate_crc32_table();

[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFu;
    for (uint8_t byte : data) {
        uint8_t table_idx = static_cast<uint8_t>((crc ^ byte) & 0xFF);
        crc = (crc >> 8) ^ crc32_table[table_idx];
    }
    return crc ^ 0xFFFFFFFFu;
}

[[nodiscard]] std::expected<ethernet_frame, parse_error>
parse_frame(std::span<const uint8_t> buffer, bool has_fcs = false) noexcept {
    if (buffer.size() < 14)
        return std::unexpected(parse_error::buffer_too_small);

    ethernet_frame frame;
    std::copy_n(buffer.data(), mac_len, frame.dst_mac.begin());
    std::copy_n(buffer.data() + mac_len, mac_len, frame.src_mac.begin());

    std::size_t offset = 12;

    /* Ітеративне зняття тегів 802.1Q / 802.1ad */
    while (offset + 4 <= buffer.size()) {
        uint16_t tag_type = static_cast<uint16_t>((buffer[offset] << 8) | buffer[offset + 1]);
        if (tag_type != ethertype_vlan && tag_type != ethertype_qinq)
            break;

        uint16_t tci = static_cast<uint16_t>((buffer[offset + 2] << 8) | buffer[offset + 3]);
        frame.vlans.push_back(vlan_info{
            .vid = static_cast<uint16_t>(tci & 0x0FFF),
            .pcp = static_cast<uint8_t>((tci >> 13) & 0x07),
            .dei = ((tci >> 12) & 0x01) != 0
        });
        offset += 4;
    }

    if (offset + 2 > buffer.size())
        return std::unexpected(parse_error::truncated_vlan_header);

    frame.ethertype = static_cast<uint16_t>((buffer[offset] << 8) | buffer[offset + 1]);
    offset += 2;

    /* Обробка IEEE 802.3 LLC/SNAP */
    if (frame.ethertype <= 1500) {
        if (offset + 8 <= buffer.size() &&
            buffer[offset] == 0xAA && buffer[offset + 1] == 0xAA && buffer[offset + 2] == 0x03) {
            frame.ethertype = static_cast<uint16_t>((buffer[offset + 6] << 8) | buffer[offset + 7]);
            offset += 8;
        }
    }

    std::size_t payload_end = buffer.size();
    if (has_fcs) {
        if (buffer.size() < offset + 4)
            return std::unexpected(parse_error::missing_fcs);
        payload_end -= 4;

        uint32_t expected_crc = calculate_crc32(buffer.subspan(0, payload_end));
        uint32_t actual_crc = static_cast<uint32_t>(buffer[payload_end]) |
                             (static_cast<uint32_t>(buffer[payload_end + 1]) << 8) |
                             (static_cast<uint32_t>(buffer[payload_end + 2]) << 16) |
                             (static_cast<uint32_t>(buffer[payload_end + 3]) << 24);

        if (expected_crc != actual_crc)
            return std::unexpected(parse_error::checksum_mismatch);

        frame.fcs_verified = true;
    } else {
        frame.fcs_verified = true;
    }

    frame.payload = buffer.subspan(offset, payload_end - offset);
    return frame;
}

} // namespace net
```
:::

### Формування та інкапсуляція кадру (Frame Crafting)

Зворотна задача полягає у формуванні дійсного двійкового кадру Ethernet з вихідного масиву байтів L3-пакета перед передачею його у сокет `AF_PACKET` або драйвер.

Процедура формування містить такі обов'язкові кроки:
1. Виділення буфера достатнього розміру: `14 байтів (заголовок) + 4 байта на кожен тег VLAN + розмір payload + 4 байти FCS`.
2. Копіювання 6 байтів MAC отримувача та 6 байтів MAC відправника.
3. Дописування 4-байтових тегів 802.1Q у разі потреби транкової передачі.
4. Запис 2-байтового значення `EtherType` (наприклад, `0x0800` для IPv4) у мережевому порядку байтів `htons()`.
5. Копіювання корисного навантаження. Якщо розмір корисних даних менший за 46 байтів (без тегів) або 42 байти (з тегом), буфер доповнюється нулями (`memset`) до досягнення мінімальної довжини 60 байтів без FCS.
6. Обчислення контрольної суми CRC-32 від усього підготовленого блоку та запис отриманого 32-бітного слова у хвіст буфера у порядку LSB-first.

:::tabs
```c
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>

size_t craft_ethernet_frame(const uint8_t *dst_mac, const uint8_t *src_mac,
                            uint16_t vlan_id, uint16_t ethertype,
                            const uint8_t *payload, size_t payload_len,
                            uint8_t *out_buf, size_t max_buf_len) {
    size_t offset = 0;

    /* Копіюємо MAC-адреси */
    memcpy(out_buf + offset, dst_mac, 6); offset += 6;
    memcpy(out_buf + offset, src_mac, 6); offset += 6;

    /* Якщо вказано VLAN ID (1..4094), вставляємо тег 802.1Q */
    if (vlan_id >= 1 && vlan_id <= 4094) {
        out_buf[offset++] = 0x81;
        out_buf[offset++] = 0x00;
        uint16_t tci = htons(vlan_id & 0x0FFF);
        memcpy(out_buf + offset, &tci, 2); offset += 2;
    }

    /* Записуємо EtherType */
    uint16_t etype_be = htons(ethertype);
    memcpy(out_buf + offset, &etype_be, 2); offset += 2;

    /* Копіюємо дані */
    memcpy(out_buf + offset, payload, payload_len);
    offset += payload_len;

    /* Доповнюємо нулями до мінімального розміру 60 байтів (без FCS) */
    if (offset < 60) {
        memset(out_buf + offset, 0, 60 - offset);
        offset = 60;
    }

    /* Обчислюємо та дописуємо FCS CRC-32 */
    uint32_t crc = ethernet_crc32(out_buf, offset);
    out_buf[offset++] = (uint8_t)(crc & 0xFF);
    out_buf[offset++] = (uint8_t)((crc >> 8) & 0xFF);
    out_buf[offset++] = (uint8_t)((crc >> 16) & 0xFF);
    out_buf[offset++] = (uint8_t)((crc >> 24) & 0xFF);

    return offset;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <bit>
#include <cstring>

namespace net {

[[nodiscard]] std::vector<uint8_t>
craft_frame(mac_address dst, mac_address src,
            uint16_t vlan_id, ether_type type,
            std::span<const uint8_t> payload) {
    std::vector<uint8_t> buffer;
    buffer.reserve(64 + payload.size());

    buffer.insert(buffer.end(), dst.begin(), dst.end());
    buffer.insert(buffer.end(), src.begin(), src.end());

    if (vlan_id >= 1 && vlan_id <= 4094) {
        buffer.push_back(0x81);
        buffer.push_back(0x00);
        buffer.push_back(static_cast<uint8_t>((vlan_id >> 8) & 0x0F));
        buffer.push_back(static_cast<uint8_t>(vlan_id & 0xFF));
    }

    auto raw_type = static_cast<uint16_t>(type);
    buffer.push_back(static_cast<uint8_t>((raw_type >> 8) & 0xFF));
    buffer.push_back(static_cast<uint8_t>(raw_type & 0xFF));

    buffer.insert(buffer.end(), payload.begin(), payload.end());

    /* Доповнення нулями до мінімального розміру 60 байтів */
    if (buffer.size() < 60) {
        buffer.resize(60, 0x00);
    }

    /* Обчислення FCS */
    uint32_t crc = calculate_crc32(buffer);
    buffer.push_back(static_cast<uint8_t>(crc & 0xFF));
    buffer.push_back(static_cast<uint8_t>((crc >> 8) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((crc >> 16) & 0xFF));
    buffer.push_back(static_cast<uint8_t>((crc >> 24) & 0xFF));

    return buffer;
}

} // namespace net
```
:::

### Отримання сирих кадрів через `AF_PACKET` у Linux

Для підключення парсера до реального мережевого інтерфейсу в операційній системі Linux використовується системний виклик `socket()` з родиною протоколів `AF_PACKET`:

:::tabs
```c
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

int open_raw_ethernet_socket(const char *ifname) {
    /* Відкриваємо сирий сокет для всіх канальних протоколів (ETH_P_ALL) */
    int fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (fd < 0)
        return -1;

    /* Знаходимо числовий індекс мережевого інтерфейсу */
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1);
    if (ioctl(fd, SIOCGIFINDEX, &ifr) < 0) {
        close(fd);
        return -2;
    }

    /* Прив'язуємо сокет виключно до цього інтерфейсу */
    struct sockaddr_ll sll;
    memset(&sll, 0, sizeof(sll));
    sll.sll_family = AF_PACKET;
    sll.sll_ifindex = ifr.ifr_ifindex;
    sll.sll_protocol = htons(ETH_P_ALL);

    if (bind(fd, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
        close(fd);
        return -3;
    }

    return fd;
}
```
```cpp
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <string_view>
#include <expected>

namespace net {

class raw_socket {
    int fd_{-1};

public:
    raw_socket() = default;
    explicit raw_socket(int fd) noexcept : fd_(fd) {}

    ~raw_socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    raw_socket(const raw_socket&) = delete;
    raw_socket& operator=(const raw_socket&) = delete;

    raw_socket(raw_socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    raw_socket& operator=(raw_socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }

    static std::expected<raw_socket, int> open(std::string_view ifname) {
        int sock = ::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
        if (sock < 0)
            return std::unexpected(-1);

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        if (::ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
            ::close(sock);
            return std::unexpected(-2);
        }

        struct sockaddr_ll sll{};
        sll.sll_family = AF_PACKET;
        sll.sll_ifindex = ifr.ifr_ifindex;
        sll.sll_protocol = htons(ETH_P_ALL);

        if (::bind(sock, reinterpret_cast<struct sockaddr*>(&sll), sizeof(sll)) < 0) {
            ::close(sock);
            return std::unexpected(-3);
        }

        return raw_socket(sock);
    }
};

} // namespace net
```
:::

У циклі захоплення кадрів застосунок викликає функцію `recvfrom()` або `recvmsg()` у буфер розміром щонайменше 2048 байтів (для стандартних кадрів) або 10000 байтів (для Jumbo Frames). Отриманий масив передається безпосередньо у функцію `parse_ethernet_frame()` або `net::parse_frame()`.

Для запобігання переповненню сокетного буфера непотрібним трафіком (наприклад, широкомовним шумом у великих мережах) до сокета підключають фільтр BPF за допомогою виклику `setsockopt(fd, SOL_SOCKET, SO_ATTACH_FILTER, &bpf_prog)`. Програма BPF відкидає сторонні кадри безпосередньо в обробнику переривання драйвера (HardIRQ/SoftIRQ), не витрачаючи пам'ять на копіювання в чергу сокета `sk_receive_queue`. У результаті парсер простору користувача отримує виключно цільовий потік пакетів із гарантованою продуктивністю.

### Високопродуктивне захоплення кадрів без копіювання (`PACKET_MMAP`)

Стандартний виклик `recvfrom()` на швидкостях понад 1 Гбіт/с створює критичні накладні витрати: для кожного кадру ядро виконує перемикання контексту процесора, виділяє пам'ять і копіює байти з ядра в простір користувача.

Для усунення цих накладних витрат ядро Linux надає механізм **`PACKET_MMAP` (версія `TPACKET_V3`)**, що організує спільний кільцевий буфер (Ring Buffer) у пам'яті:
1. Застосунок створює сокет `AF_PACKET` і конфігурує розмір блоків пам'яті через виклик `setsockopt(fd, SOL_PACKET, PACKET_RX_RING, ...)`.
2. Пам'ять кільця мапується в адресний простір процесу через системний виклик `mmap()`.
3. Мережева карта записує кадри через DMA безпосередньо в ці спільні сторінки RAM.
4. Програма перевіряє готовність кадрів без системних викликів — просто зчитуючи бітовий статус `TP_STATUS_USER` у заголовку дескриптора `tpacket3_hdr`.
5. Після обробки кадру парсером програма скидає статус у `TP_STATUS_KERNEL`, повертаючи слот буфера ядру для запису наступних пакетів.

Цей підхід дозволяє одному процесорному ядру розбирати понад 2–3 мільйони Ethernet-кадрів на секунду без жодних втрат і без додаткових алокацій динамічної пам'яті.

### Тестування та верифікація на контрольних векторах

Для перевірки коректності роботи парсера та алгоритму FCS CRC-32 розробляється набір модульних тестів, що покривають усі типи заголовків та граничні стани.

Тестовий набір перевіряє шість обов'язкових сценаріїв:
1. **Звичайний нетегований кадр (Ethernet II):** стандартний IPv4-пакет. Перевіряється коректність зчитування MAC-адрес та значення `EtherType = 0x0800`.
2. **Одинарний тег IEEE 802.1Q:** кадр із тегом VLAN. Перевіряється точність розпакування пріоритету PCP (3 біти) та ідентифікатора VID (12 бітів), а також правильність зсуву на наступний EtherType.
3. **Подвійний тег IEEE 802.1ad (QinQ):** кадр із двома вкладеними тегами (`0x88A8` та `0x8100`). Перевіряється глибина стека тегів та збереження порядку провайдерського і клієнтського VID.
4. **Короткий кадр із заповненням (Padding):** ARP-запит розміром 28 байтів у 60-байтовому L2-кадрі. Перевіряється, що парсер не падає на нульових байтах і правильно накриває їх контрольною сумою CRC-32.
5. **Пошкоджений кадр (CRC Mismatch):** кадр із навмисно інвертованим одним бітом у полі даних. Парсер зобов'язаний повернути статус помилки `checksum_mismatch` або `fcs_valid == false`.
6. **Обрізаний заголовок (Truncated Frame):** пошкоджений буфер розміром 10 байтів (менше за `ETH_HLEN`). Перевіряється миттєве повернення коду помилки без спроб читання неіснуючих полів пам'яті.

:::tabs
```c
void run_unit_tests(void) {
    /* Тестовий вектор: ARP-запит із тегом VLAN 100 */
    const uint8_t test_frame[] = {
        0x00, 0x1a, 0x2b, 0x3c, 0x4d, 0x5e,
        0x00, 0x50, 0x56, 0xc0, 0x00, 0x08,
        0x81, 0x00, 0xa0, 0x64, /* VLAN 100, PCP 5 */
        0x08, 0x06,             /* ARP */
        0x00, 0x01, 0x08, 0x00, 0x06, 0x04, 0x00, 0x01,
        0x00, 0x50, 0x56, 0xc0, 0x00, 0x08, 0xc0, 0xa8, 0x01, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xa8, 0x01, 0x64,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x7a, 0x4b, 0x1c, 0x9e  /* Валідний CRC-32 */
    };

    parsed_frame_t result;
    int status = parse_ethernet_frame(test_frame, sizeof(test_frame), true, &result);

    if (status == 0 && result.fcs_valid && result.vlan_count == 1 &&
        result.vlan_ids[0] == 100 && result.vlan_pcp[0] == 5 &&
        result.ethertype == 0x0806) {
        printf("Тест 1 (VLAN Tagged ARP + CRC32): УСПІХ\n");
    } else {
        printf("Тест 1: ПОМИЛКА (код %d)\n", status);
    }
}
```
```cpp
void run_unit_tests() {
    const std::array<uint8_t, 64> test_frame = {
        0x00, 0x1a, 0x2b, 0x3c, 0x4d, 0x5e,
        0x00, 0x50, 0x56, 0xc0, 0x00, 0x08,
        0x81, 0x00, 0xa0, 0x64,
        0x08, 0x06,
        0x00, 0x01, 0x08, 0x00, 0x06, 0x04, 0x00, 0x01,
        0x00, 0x50, 0x56, 0xc0, 0x00, 0x08, 0xc0, 0xa8, 0x01, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xa8, 0x01, 0x64,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x7a, 0x4b, 0x1c, 0x9e
    };

    auto res = net::parse_frame(test_frame, true);
    if (res.has_value() && res->fcs_verified && res->vlans.size() == 1 &&
        res->vlans[0].vid == 100 && res->vlans[0].pcp == 5 &&
        res->ethertype == 0x0806) {
        printf("Тест C++20 (VLAN Tagged ARP + CRC32): УСПІХ\n");
    }
}
```
:::

### Діагностика помилок кадру в утиліті `ethtool`

Коли мережева карта чи драйвер виявляють невалідний кадр під час апаратного розбору, лічильники помилок оновлюються в статистиці ядра. Системний адміністратор або розробник може перевірити статус розбору кадру за допомогою команди `ethtool -S <interface>`:
* `rx_crc_errors` — кількість кадрів, відкинутих через незбіг контрольної суми FCS CRC-32 (свідчить про проблеми з якістю витої пари, електромагнітні наведення або поганий контакт роз'єму RJ-45).
* `rx_length_errors` / `rx_undersize_errors` — кількість відкинутих Runt-кадрів (менших за 64 байти).
* `rx_oversize_errors` — кількість кадрів, що перевищили налаштований розмір MTU (свідчить про надходження Jumbo Frames у сегмент, де комутатор або хост налаштовані на стандартний MTU 1500).
* `rx_vlan_errors` — помилки розбору або заборонені теги VLAN на неавторизованих access-портах.

### Типові пастки та крайові випадки

Під час практичної експлуатації канального парсера виникають чотири характерні проблеми, які призводять до прихованих помилок або вразливостей:

1. **Пастка паддінгу при розрахунку розміру IP:** Якщо відправник передає маленький TCP SYN-пакет розміром 40 байтів, Ethernet-контролер дописує 6 нульових байтів паддінгу до мінімальних 46 байтів. Якщо парсер просто поверне `payload` розміром 46 байтів, вищий рівень може інтерпретувати кінцеві нулі як сміття або помилку довжини. Правильний підхід — зчитати поле `Total Length` з заголовка IPv4 і підрізати `payload` до справжнього розміру пакета.
2. **Апаратне видалення тегів VLAN (VLAN Offload):** Якщо мережева карта підтримує `rx-vlan-offload` (увімкнено за замовчуванням у Linux), драйвер передає сокету кадри, де 4 байти тега вже вирізані з потоку пам'яті. Якщо сокет очікує сирий тег у буфері, він його не знайде. У такому разі інформацію про VLAN необхідно зчитувати з допоміжних повідомлень сокета (`recvmsg` зі структурою `tpacket_auxdata`).
3. **Помилка порядку байтів при перевірці FCS:** Поле FCS записується в кінці кадру у порядку молодшим байтом уперед (Little-Endian відносно слова CRC). Спроба розіменувати його через функцію `ntohl()` замість прямого збирання байтів призведе до хибного виявлення помилок контрольної суми на Little-Endian архітектурах (x86/ARM).
4. **Некоректна робота з великими Jumbo-кадрами:** Якщо розмір вхідного статичного буфера зафіксовано на 1518 байтах, надходження Jumbo-кадру призведе до його обрізання або переповнення буфера пам'яті. Парсери виробничого рівня повинні динамічно виділяти пам'ять на основі налаштованого розміру MTU інтерфейсу або використовувати кільцеві буфери пам'яті ядра `PACKET_MMAP`.
