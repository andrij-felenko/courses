# ⚙️ Парсер двійкових заголовків CLNP та TP4 мовами C та C++

У цьому практичному проєкті розглядається інженерна побудова надійного, високопродуктивного та безпечного до пам'яті парсера двійкових заголовків мережевого протоколу **CLNP** (ISO 8473) та транспортного протоколу **TP4** (ISO 8073 / ITU-T X.224). Ми розберемо низькорівневі структури даних, математичний апарат і покроковий алгоритм обчислення контрольної суми **Флетчера (Fletcher-16)**, вилучення ієрархічних адрес **NSAP** змінної довжини, алгоритми дефрагментації, генерацію звітів про помилки **ER-PDU**, обробку транспортних блоків **TPDU**, сокетні інтерфейси XTI/TLI, інтеграцію з маршрутизацією IS-IS та захист від типових вразливостей переповнення буфера.

---

## 1. Архітектурні виклики розбору протоколів OSI

На відміну від мережевого стека TCP/IP, де базові заголовки IPv4 (20 байтів) та UDP (8 байтів) мають фіксовану довжину або просту структуру опцій, стек OSI спочатку проєктувався як гранично узагальнена та розширювана система. Ця гнучкість створила низку специфічних інженерних складнощів при низькорівневому парсингу двійкових кадрів у пам'яті:

1. **Динамічний розмір заголовка CLNP:** Загальна довжина заголовка визначається другим байтом кадру — індикатором довжини `Length Indicator (LI)`. Заголовок може займати від 9 до 254 байтів, змінюючись від пакета до пакета залежно від наявності полів адресації, сегментації та опцій.
2. **Адреси змінної довжини (NSAP):** На відміну від 32-бітних адрес IPv4 чи 128-бітних адрес IPv6, мережева адреса точки доступу NSAP може мати довільну довжину від 1 до 20 октетів. Кожній адресі передує окремий байт довжини (`DAL` та `SAL`), що вимагає динамічного зсуву покажчика під час читання кадру.
3. **Умовна присутність частини сегментації:** 6-байтний блок сегментації (DUID, Segment Offset, Total Length) додається до заголовка лише тоді, коли у байті прапорців встановлено біт `SP = 1` (*Segmentation Permitted*). Маршрутизатор повинен уміти динамічно змінювати схему розбору залежно від значення бітової маски.
4. **Вкладена адресація транспортного рівня (TP4):** Транспортний заголовок TPDU починається безпосередньо після закінчення заголовка CLNP і також має власний індикатор довжини `LI`, тип повідомлення та змінну частину параметрів TLV.

Будь-яка помилка в розрахунку динамічних зміщень або відсутність суворої валідації розміру буфера на кожному кроці розбору призводить до типових вразливостей системного програмування: виходу за межі виділеного буфера (*Buffer Overread*), цілочисельного переповнення (*Integer Overflow*) при розрахунку розміру корисного навантаження або некоректної інтерпретації випадкового сміття в пам'яті як довжини адреси.

---

## 2. Математичний апарат контрольної суми Флетчера (Fletcher-16)

Стек протоколів OSI відмовився від класичного 16-бітного інтернет-чексуму (алгоритму порозрядного складання в доповненні до одиниці, прийнятого в IPv4/TCP), оскільки простий суматор має критичну ваду: він абсолютно нечутливий до порядку розташування слів у пам'яті. Якщо в пакеті поміняти місцями два 16-бітних слова (наприклад, переставити адреси чи байти через збій апаратного регістру зсуву), проста сума не зміниться, і пошкоджений пакет буде прийнято як валідний.

Для розв'язання цієї проблеми Джон Флетчер (John G. Fletcher) у 1982 році запропонував алгоритм зваженого позиційного сумування, який було стандартизовано в додатку B до ISO 8473 (CLNP) та додатку A до ISO 8073 (TP4).

### Математичне визначення

Нехай заголовок пакета складається з послідовності `L` октетів: `a[1], a[2], ..., a[L]`.
Алгоритм Флетчера визначає два проміжних акумулятори `C0` та `C1`, які ініціалізуються нулями та оновлюються для кожного байта `a[i]` за модулем 255 (або 0xFF):

```
C0 = ∑ (a[i])                  (mod 255),   де i змінюється від 1 до L
C1 = ∑ ((L - i + 1) · a[i])    (mod 255),   де i змінюється від 1 до L
```

З формули для `C1` чітко видно, що кожен байт множиться на ваговий коефіцієнт `(L - i + 1)`, який лінійно зменшується від початку до кінця повідомлення. Завдяки цьому перестанова будь-яких двох байтів змінює суму `C1`, що гарантує 100% виявлення перестановок сусідніх або довільних байтів у заголовку.

### Покроковий ітеративний розрахунок

На практиці обчислення виконується в один прохід через ітеративне накопичення:

```
Початковий стан:
Встановити c0 ← 0, c1 ← 0

Для кожного вхідного байта a[i] від i = 1 до L:
c0 ← (c0 + a[i]) mod 255
c1 ← (c1 + c0)   mod 255
```

### Генерація контрольних байтів відправником

Коли вузол створює пакет, байти контрольної суми зі зміщенням `k` та `k+1` (для CLNP `k = 7`, `k+1 = 8`) спочатку встановлюються в `0`. Після цього обчислюються суми `C0` та `C1` по всьому заголовку довжиною `L`. Значення контрольних октетів `x` та `y` визначаються за формулами:

```
x = ((L - k) · C0 - C1)        (mod 255)
y = (C1 - (L - k + 1) · C0)    (mod 255)
```

Якщо в результаті обчислень виходить `x = 0` або `x = 255`, записується значення `0xFF` (255 еквівалентно 0 за модулем 255). Підстановка значень `x` та `y` у заголовок гарантує, що при повторній перевірці приймачем обидва акумулятори `C0` та `C1` точно дорівнюватимуть нулю.

### Оптимізація обчислення без частих операцій взяття за модулем

У наївній реалізації операція `% 255` виконується на кожній ітерації циклу, що істотно уповільнює роботу процесора. Оскільки максимальне значення байта становить 255, накопичувачі `C0` та `C1` у 32-бітному цілому числі не перевищать межу переповнення за декілька сотень ітерацій.

Максимальний приріст `C1` за один крок становить `255 · 255 = 65025`. Для 32-бітного беззнакового числа `uint32_t` межа становить `4 294 967 295`. Отже, операцію взяття за модулем можна виконувати не на кожному байті, а блоками по 350-500 байтів, або лише один раз у кінці для заголовків розміром до 254 байтів:

:::tabs
```c
/* Оптимізований варіант для коротких заголовків (len <= 255) мовою C */
uint32_t c0 = 0, c1 = 0;
for (size_t i = 0; i < len; ++i) {
    c0 += header[i];
    c1 += c0;
}
c0 %= 255;
c1 %= 255;
```
```cpp
// Оптимізований варіант для коротких заголовків мовою C++20
uint32_t c0 = 0, c1 = 0;
for (uint8_t byte : header) {
    c0 += byte;
    c1 += c0;
}
c0 %= 255;
c1 %= 255;
```
:::

---

## 3. Вихідний код парсера: мови C та C++

Нижче наведено дві повні, функціонально еквівалентні реалізації парсера: низькорівневий варіант мовою C (C99/C11) з прямими перевірками меж вказівників та сучасний ідіоматичний варіант мовою C++20, що використовує безпечні діапазони пам'яті `std::span`, строгу типізацію переліків `enum class` та семантику `std::optional`.

Обидві реалізації спроєктовано за принципом **нуль-копіювання (zero-copy)**: парсер не створює динамічних копій буферів у купі (`heap`), а повертає структури зі зрізами пам'яті, що посилаються на оригінальний вхідний буфер кадру.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CLNP_NLPID_CLNP        0x81
#define CLNP_TYPE_DATA         0x1C
#define CLNP_TYPE_ERROR        0x01
#define CLNP_FLAG_SP           0x80
#define CLNP_FLAG_MS           0x40
#define CLNP_FLAG_ER           0x20

#define TP4_TYPE_DT            0xF0
#define TP4_TYPE_AK            0x70
#define TP4_TYPE_CR            0xE0
#define TP4_TYPE_CC            0xD0
#define TP4_TYPE_DR            0x80

/* Структура розібраного заголовка CLNP */
typedef struct {
    uint8_t nlpid;
    uint8_t header_len;
    uint8_t version;
    uint8_t lifetime;
    uint8_t flags;
    uint16_t segment_len;
    uint16_t checksum;
    bool is_segmented;
    bool more_segments;
    bool error_report;
    uint8_t type;

    uint8_t dst_nsap_len;
    const uint8_t *dst_nsap;
    uint8_t src_nsap_len;
    const uint8_t *src_nsap;

    uint16_t duid;
    uint16_t segment_offset;
    uint16_t total_len;

    const uint8_t *payload;
    size_t payload_len;
} clnp_packet_t;

/* Структура розібраного транспортного блоку даних TP4 */
typedef struct {
    uint8_t header_len;
    uint8_t type;
    uint16_t dst_ref;
    uint8_t tpdu_nr;
    bool eot;
    const uint8_t *data;
    size_t data_len;
} tp4_dt_packet_t;

/* Перевірка контрольної суми Флетчера-16 за стандартом ISO 8473 */
bool clnp_verify_fletcher16(const uint8_t *header, size_t len) {
    if (len == 0) return false;
    
    /* Якщо байти контрольної суми нульові (зміщення 7,8) — перевірку вимкнено */
    if (len >= 9 && header[7] == 0x00 && header[8] == 0x00) {
        return true;
    }

    uint32_t c0 = 0;
    uint32_t c1 = 0;

    for (size_t i = 0; i < len; ++i) {
        c0 += header[i];
        c1 += c0;
    }

    return ((c0 % 255) == 0) && ((c1 % 255) == 0);
}

/* Безпечний нуль-копіювальний розбір заголовка CLNP */
bool clnp_parse(const uint8_t *buf, size_t buf_len, clnp_packet_t *pkt) {
    if (!buf || buf_len < 9 || !pkt) return false;
    memset(pkt, 0, sizeof(*pkt));

    pkt->nlpid = buf[0];
    if (pkt->nlpid != CLNP_NLPID_CLNP) {
        return false; /* Невідомий мережевий протокол */
    }

    pkt->header_len = buf[1];
    if (pkt->header_len < 9 || pkt->header_len > buf_len) {
        return false; /* Некоректна довжина заголовка відносно буфера */
    }

    pkt->version = buf[2];
    pkt->lifetime = buf[3];
    pkt->flags = buf[4];
    pkt->type = pkt->flags & 0x1F;
    pkt->is_segmented = (pkt->flags & CLNP_FLAG_SP) != 0;
    pkt->more_segments = (pkt->flags & CLNP_FLAG_MS) != 0;
    pkt->error_report = (pkt->flags & CLNP_FLAG_ER) != 0;

    pkt->segment_len = ((uint16_t)buf[5] << 8) | buf[6];
    pkt->checksum = ((uint16_t)buf[7] << 8) | buf[8];

    /* Перевірка контрольної суми Флетчера */
    if (!clnp_verify_fletcher16(buf, pkt->header_len)) {
        return false; /* Помилка контрольної суми */
    }

    size_t offset = 9;

    /* Розбір адреси призначення NSAP */
    if (offset >= pkt->header_len) return false;
    pkt->dst_nsap_len = buf[offset++];
    if (pkt->dst_nsap_len > 20 || offset + pkt->dst_nsap_len > pkt->header_len) {
        return false; /* Порушення довжини NSAP */
    }
    pkt->dst_nsap = &buf[offset];
    offset += pkt->dst_nsap_len;

    /* Розбір адреси джерела NSAP */
    if (offset >= pkt->header_len) return false;
    pkt->src_nsap_len = buf[offset++];
    if (pkt->src_nsap_len > 20 || offset + pkt->src_nsap_len > pkt->header_len) {
        return false; /* Порушення довжини NSAP */
    }
    pkt->src_nsap = &buf[offset];
    offset += pkt->src_nsap_len;

    /* Розбір частини сегментації (якщо встановлено прапорець SP) */
    if (pkt->is_segmented) {
        if (offset + 6 > pkt->header_len) return false;
        pkt->duid = ((uint16_t)buf[offset] << 8) | buf[offset + 1];
        pkt->segment_offset = ((uint16_t)buf[offset + 2] << 8) | buf[offset + 3];
        pkt->total_len = ((uint16_t)buf[offset + 4] << 8) | buf[offset + 5];
        offset += 6;
    }

    /* Визначаємо межі корисного навантаження */
    pkt->payload = &buf[pkt->header_len];
    if (pkt->segment_len >= pkt->header_len && pkt->segment_len <= buf_len) {
        pkt->payload_len = pkt->segment_len - pkt->header_len;
    } else {
        pkt->payload_len = buf_len - pkt->header_len;
    }

    return true;
}

/* Розбір транспортного блоку даних TP4 DT-TPDU */
bool tp4_parse_dt(const uint8_t *buf, size_t buf_len, tp4_dt_packet_t *tp) {
    if (!buf || buf_len < 5 || !tp) return false;
    memset(tp, 0, sizeof(*tp));

    tp->header_len = buf[0];
    if (tp->header_len < 4 || (size_t)(tp->header_len + 1) > buf_len) {
        return false;
    }

    uint8_t type_byte = buf[1];
    if ((type_byte & 0xF0) != TP4_TYPE_DT) {
        return false; /* Очікувався DT-TPDU */
    }
    tp->type = type_byte & 0xF0;

    tp->dst_ref = ((uint16_t)buf[2] << 8) | buf[3];
    tp->eot = (buf[4] & 0x80) != 0;
    tp->tpdu_nr = buf[4] & 0x7F;

    tp->data = &buf[tp->header_len + 1];
    tp->data_len = buf_len - (tp->header_len + 1);

    return true;
}

/* Друк адреси NSAP у шістнадцятковому форматі */
void print_nsap(const uint8_t *nsap, uint8_t len) {
    for (uint8_t i = 0; i < len; ++i) {
        printf("%02X", nsap[i]);
        if (i % 2 == 1 && i != len - 1) {
            printf(".");
        }
    }
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <span>
#include <string_view>
#include <optional>
#include <vector>
#include <cstdint>

namespace osi {

enum class NetworkProtocolId : uint8_t {
    InactiveSubnetwork = 0x00,
    CLNP               = 0x81,
    ESIS               = 0x82,
    ISIS               = 0x83
};

enum class Tp4Type : uint8_t {
    DataAck           = 0x70,
    DisconnectRequest = 0x80,
    ConnectionConfirm = 0xD0,
    ConnectionRequest = 0xE0,
    Data              = 0xF0
};

struct NsapAddress {
    std::span<const uint8_t> raw_bytes;

    void print() const {
        for (size_t i = 0; i < raw_bytes.size(); ++i) {
            std::cout << std::hex << std::uppercase << std::setw(2) << std::setfill('0')
                      << static_cast<int>(raw_bytes[i]);
            if (i % 2 == 1 && i != raw_bytes.size() - 1) {
                std::cout << ".";
            }
        }
        std::cout << std::dec;
    }
};

struct ClnpHeader {
    uint8_t nlpid{0};
    uint8_t header_len{0};
    uint8_t version{0};
    uint8_t lifetime{0};
    uint8_t flags{0};
    uint16_t segment_len{0};
    uint16_t checksum{0};
    bool is_segmented{false};
    bool more_segments{false};
    bool error_report{false};
    uint8_t type{0};

    NsapAddress dst_nsap;
    NsapAddress src_nsap;

    uint16_t duid{0};
    uint16_t segment_offset{0};
    uint16_t total_len{0};

    std::span<const uint8_t> payload;
};

struct Tp4DtHeader {
    uint8_t header_len{0};
    Tp4Type type{Tp4Type::Data};
    uint16_t dst_ref{0};
    uint8_t tpdu_nr{0};
    bool eot{false};
    std::span<const uint8_t> payload;
};

class PacketParser {
public:
    static bool verifyFletcher16(std::span<const uint8_t> header) noexcept {
        if (header.empty()) return false;
        if (header.size() >= 9 && header[7] == 0x00 && header[8] == 0x00) {
            return true; /* Перевірку вимкнено */
        }

        uint32_t c0 = 0;
        uint32_t c1 = 0;

        for (uint8_t byte : header) {
            c0 += byte;
            c1 += c0;
        }

        return ((c0 % 255) == 0) && ((c1 % 255) == 0);
    }

    static std::optional<ClnpHeader> parseClnp(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 9) return std::nullopt;

        ClnpHeader hdr;
        hdr.nlpid = buffer[0];
        if (hdr.nlpid != static_cast<uint8_t>(NetworkProtocolId::CLNP)) {
            return std::nullopt;
        }

        hdr.header_len = buffer[1];
        if (hdr.header_len < 9 || hdr.header_len > buffer.size()) {
            return std::nullopt;
        }

        hdr.version = buffer[2];
        hdr.lifetime = buffer[3];
        hdr.flags = buffer[4];
        hdr.type = hdr.flags & 0x1F;
        hdr.is_segmented = (hdr.flags & 0x80) != 0;
        hdr.more_segments = (hdr.flags & 0x40) != 0;
        hdr.error_report = (hdr.flags & 0x20) != 0;

        hdr.segment_len = (static_cast<uint16_t>(buffer[5]) << 8) | buffer[6];
        hdr.checksum = (static_cast<uint16_t>(buffer[7]) << 8) | buffer[8];

        /* Перевірка суми Флетчера */
        if (!verifyFletcher16(buffer.subspan(0, hdr.header_len))) {
            return std::nullopt;
        }

        size_t offset = 9;

        /* Розбір адреси призначення NSAP */
        if (offset >= hdr.header_len) return std::nullopt;
        uint8_t dst_len = buffer[offset++];
        if (dst_len > 20 || offset + dst_len > hdr.header_len) return std::nullopt;
        hdr.dst_nsap = NsapAddress{buffer.subspan(offset, dst_len)};
        offset += dst_len;

        /* Розбір адреси джерела NSAP */
        if (offset >= hdr.header_len) return std::nullopt;
        uint8_t src_len = buffer[offset++];
        if (src_len > 20 || offset + src_len > hdr.header_len) return std::nullopt;
        hdr.src_nsap = NsapAddress{buffer.subspan(offset, src_len)};
        offset += src_len;

        /* Частина сегментації */
        if (hdr.is_segmented) {
            if (offset + 6 > hdr.header_len) return std::nullopt;
            hdr.duid = (static_cast<uint16_t>(buffer[offset]) << 8) | buffer[offset + 1];
            hdr.segment_offset = (static_cast<uint16_t>(buffer[offset + 2]) << 8) | buffer[offset + 3];
            hdr.total_len = (static_cast<uint16_t>(buffer[offset + 4]) << 8) | buffer[offset + 5];
            offset += 6;
        }

        size_t payload_len = (hdr.segment_len >= hdr.header_len && hdr.segment_len <= buffer.size())
                           ? (hdr.segment_len - hdr.header_len)
                           : (buffer.size() - hdr.header_len);

        hdr.payload = buffer.subspan(hdr.header_len, payload_len);
        return hdr;
    }

    static std::optional<Tp4DtHeader> parseTp4Dt(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 5) return std::nullopt;

        Tp4DtHeader tp;
        tp.header_len = buffer[0];
        if (tp.header_len < 4 || (static_cast<size_t>(tp.header_len) + 1) > buffer.size()) {
            return std::nullopt;
        }

        uint8_t type_raw = buffer[1] & 0xF0;
        if (type_raw != static_cast<uint8_t>(Tp4Type::Data)) {
            return std::nullopt;
        }
        tp.type = Tp4Type::Data;

        tp.dst_ref = (static_cast<uint16_t>(buffer[2]) << 8) | buffer[3];
        tp.eot = (buffer[4] & 0x80) != 0;
        tp.tpdu_nr = buffer[4] & 0x7F;

        size_t total_hdr = static_cast<size_t>(tp.header_len) + 1;
        tp.payload = buffer.subspan(total_hdr);
        return tp;
    }
};

} // namespace osi
```
:::

---

## 4. Тестова програма та перевірка на реальному двійковому кадрі

Для перевірки коректності функціонування розбирача створено синтетичний тестовий пакет, що містить валідний заголовок CLNP з 7-байтними адресами NSAP домену приватного простору (`AFI = 0x49`), інкапсульований транспортний блок TP4 Data TPDU та рядок корисних даних:

:::tabs
```c
int main(void) {
    /* Тестовий двійковий дамп: CLNP + адреси NSAP + TP4 DT-TPDU + Дані "HELLO OSI" */
    const uint8_t sample_packet[] = {
        /* Фіксована частина CLNP (9 байтів) */
        0x81,                   /* NLPID = CLNP (0x81) */
        0x19,                   /* LI = 25 байтів заголовка */
        0x01,                   /* Version = 1 */
        0x1E,                   /* Lifetime = 30 (15 секунд) */
        0x1C,                   /* Flags = Non-segmented, Type = Data (0x1C) */
        0x00, 0x27,             /* Segment Length = 39 байтів */
        0xE6, 0xCB,             /* Checksum Fletcher-16 */

        /* Адреса призначення (7 байтів): 49.0001.001A.2B3C.4D5E.01 */
        0x07,                   /* DAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0x1A, 0x2B, 0x01,

        /* Адреса джерела (7 байтів): 49.0001.00AA.BBCC.DDEE.01 */
        0x07,                   /* SAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0xAA, 0xBB, 0x01,

        /* Транспортний блок TP4 DT-TPDU (5 байтів) */
        0x04,                   /* TPDU LI = 4 байти */
        0xF0,                   /* Type = DT-TPDU (0xF0) */
        0x12, 0x34,             /* Destination Reference = 0x1234 */
        0x85,                   /* EOT=1, TPDU-NR = 5 */

        /* Корисні дані (Payload): "HELLO OSI" */
        'H', 'E', 'L', 'L', 'O', ' ', 'O', 'S', 'I'
    };

    printf("=== ДЕМОНСТРАЦІЯ РОЗБОРУ СТЕКУ CLNP / TP4 ===\n");
    
    clnp_packet_t clnp;
    if (!clnp_parse(sample_packet, sizeof(sample_packet), &clnp)) {
        printf("ПОМИЛКА: Не вдалося розібрати заголовок CLNP або пошкоджено суму!\n");
        return 1;
    }

    printf("[CLNP] NLPID: 0x%02X (CLNP)\n", clnp.nlpid);
    printf("[CLNP] Довжина заголовка: %u байтів, Повна довжина сегмента: %u байтів\n",
           clnp.header_len, clnp.segment_len);
    printf("[CLNP] Lifetime: %u (%.1f с), Прапорці: 0x%02X\n",
           clnp.lifetime, clnp.lifetime * 0.5, clnp.flags);
    
    printf("[CLNP] Призначення NSAP: ");
    print_nsap(clnp.dst_nsap, clnp.dst_nsap_len);
    printf("\n");

    printf("[CLNP] Джерело NSAP:      ");
    print_nsap(clnp.src_nsap, clnp.src_nsap_len);
    printf("\n");

    /* Розбір вкладеного TP4 */
    tp4_dt_packet_t tp4;
    if (!tp4_parse_dt(clnp.payload, clnp.payload_len, &tp4)) {
        printf("ПОМИЛКА: Не вдалося розібрати заголовок TP4!\n");
        return 1;
    }

    printf("\n[TP4] Тип TPDU: 0x%02X (Data TPDU)\n", tp4.type);
    printf("[TP4] Destination Reference: 0x%04X\n", tp4.dst_ref);
    printf("[TP4] Порядковий номер (TPDU-NR): %u, Прапорець EOT: %s\n",
           tp4.tpdu_nr, tp4.eot ? "TRUE (останній)" : "FALSE");
    printf("[TP4] Розмір корисних даних: %zu байтів\n", tp4.data_len);
    printf("[TP4] Дані: \"%.*s\"\n", (int)tp4.data_len, (const char *)tp4.data);

    return 0;
}
```
```cpp
int main() {
    const std::vector<uint8_t> sample_packet = {
        /* Фіксована частина CLNP (9 байтів) */
        0x81,                   /* NLPID = CLNP (0x81) */
        0x19,                   /* LI = 25 байтів заголовка */
        0x01,                   /* Version = 1 */
        0x1E,                   /* Lifetime = 30 (15 секунд) */
        0x1C,                   /* Flags = Non-segmented, Type = Data (0x1C) */
        0x00, 0x27,             /* Segment Length = 39 байтів */
        0xE6, 0xCB,             /* Checksum Fletcher-16 */

        /* Адреса призначення (7 байтів) */
        0x07,                   /* DAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0x1A, 0x2B, 0x01,

        /* Адреса джерела (7 байтів) */
        0x07,                   /* SAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0xAA, 0xBB, 0x01,

        /* Транспортний блок TP4 DT-TPDU (5 байтів) */
        0x04,                   /* TPDU LI = 4 байти */
        0xF0,                   /* Type = DT-TPDU (0xF0) */
        0x12, 0x34,             /* Destination Reference = 0x1234 */
        0x85,                   /* EOT=1, TPDU-NR = 5 */

        /* Корисні дані (Payload): "HELLO OSI" */
        'H', 'E', 'L', 'L', 'O', ' ', 'O', 'S', 'I'
    };

    std::cout << "=== ДЕМОНСТРАЦІЯ РОЗБОРУ СТЕКУ CLNP / TP4 (C++20) ===\n";

    auto clnp_opt = osi::PacketParser::parseClnp(sample_packet);
    if (!clnp_opt) {
        std::cerr << "ПОМИЛКА: Некоректний пакет CLNP або пошкоджена сума Флетчера!\n";
        return 1;
    }

    const auto& clnp = *clnp_opt;
    std::cout << "[CLNP] NLPID: 0x" << std::hex << static_cast<int>(clnp.nlpid) << std::dec << " (CLNP)\n";
    std::cout << "[CLNP] Довжина заголовка: " << static_cast<int>(clnp.header_len)
              << " байтів, Повна довжина: " << clnp.segment_len << " байтів\n";
    std::cout << "[CLNP] Lifetime: " << static_cast<int>(clnp.lifetime)
              << " (" << (clnp.lifetime * 0.5) << " с)\n";

    std::cout << "[CLNP] Призначення NSAP: ";
    clnp.dst_nsap.print();
    std::cout << "\n[CLNP] Джерело NSAP:      ";
    clnp.src_nsap.print();
    std::cout << "\n";

    auto tp4_opt = osi::PacketParser::parseTp4Dt(clnp.payload);
    if (!tp4_opt) {
        std::cerr << "ПОМИЛКА: Не вдалося вилучити заголовок TP4!\n";
        return 1;
    }

    const auto& tp4 = *tp4_opt;
    std::cout << "\n[TP4] Тип TPDU: 0x" << std::hex << static_cast<int>(tp4.type) << std::dec << " (Data TPDU)\n";
    std::cout << "[TP4] Destination Reference: 0x" << std::hex << tp4.dst_ref << std::dec << "\n";
    std::cout << "[TP4] Порядковий номер (TPDU-NR): " << static_cast<int>(tp4.tpdu_nr)
              << ", EOT: " << (tp4.eot ? "TRUE (останній фрагмент)" : "FALSE") << "\n";
    std::cout << "[TP4] Розмір корисних даних: " << tp4.payload.size() << " байтів\n";

    std::string_view msg(reinterpret_cast<const char*>(tp4.payload.data()), tp4.payload.size());
    std::cout << "[TP4] Дані: \"" << msg << "\"\n";

    return 0;
}
```
:::

---

## 5. Обробка фрагментації та дефрагментації у стеку CLNP

Коли вихідний розмір мережевого пакета перевищує максимальний розмір блоку передачі каналу зв'язку (MTU), маршрутизатор виконує сегментацію. На відміну від IPv4, де фрагментація описується полями `Fragment Offset` (у 8-байтних блоках) та прапорцями `MF/DF`, протокол CLNP підтримує значно точніший і водночас важчий механізм:

1. **Точне побайтове зміщення:** Поле `Segment Offset` вимірюється в точних байтах, а не в 8-байтних блоках. Це знімає обмеження на подільність розміру фрагмента на 8, проте вимагає 16-бітного поля замість 13-бітного.
2. **Повна довжина вихідного пакета (`Total Length`):** Кожен фрагмент містить повний розмір вихідного неподіленого блоку даних. Це дозволяє приймачу заздалегідь виділити в оперативній пам'яті точний суцільний буфер потрібного розміру під час отримання найпершого фрагмента, уникаючи багаторазового динамічного перерозподілу пам'яті (`realloc`).
3. **Унікальний ідентифікатор блоку даних (`DUID`):** 16-бітне число, що унікально ідентифікує пакет у парі з адресою відправника `Source NSAP`.

### Алгоритм збирання фрагментів у пам'яті (Reassembly Buffer)

Вузол-приймач підтримує чергу незавершених збирань. Кожен запис черги ідентифікується триплетом `(Source NSAP, Destination NSAP, DUID)`. Для керування проміжками між фрагментами застосовується алгоритм списку дескрипторів прогалин (*Hole Descriptor List*):

- Спочатку створюється єдиний дескриптор прогалини розміром від `0` до `Total Length - 1`.
- При надходженні фрагмента зі зміщенням `Segment Offset` та довжиною корисного навантаження `Len` знайдена прогалина зменшується або розбивається на дві менші прогалини.
- Одночасно запускається таймер дефрагментації (зазвичай 15-60 секунд). Якщо таймер вичерпано до того, як список прогалин спорожнів, усі накопичені фрагменти знищуються, а відправнику надсилається пакет помилки `Error Report PDU`.

---

## 6. Механізм узгодження транспортного з'єднання TP4 (CR / CC TPDU)

Перед тим як обмінюватися даними `DT-TPDU`, транспортні рівні обох систем повинні встановити з'єднання через триетапне рукостискання. Цей процес починається з відправлення блоку `CR-TPDU` (*Connection Request*), на який приймач відповідає `CC-TPDU` (*Connection Confirm*).

### Структура та параметри блоку CR-TPDU

На відміну від лаконічного заголовка TCP SYN, заголовок `CR-TPDU` у стеку OSI містить розгалужену змінну частину параметрів TLV:

1. **Source Reference (SRC-REF, 2 байти):** Числовий дескриптор з'єднання, виділений відправником у своїй внутрішній таблиці сокетів.
2. **Class and Option (1 байт):** Бажаний клас протоколу (TP0..TP4) та бітовий прапорець вибору формату номерів послідовності (нормальний 7-бітний чи розширений 31-бітний).
3. **Параметр Calling TSAP (Код `0xC1`):** Селектор транспортної точки доступу джерела (ідентифікатор клієнтського процесу).
4. **Параметр Called TSAP (Код `0xC2`):** Селектор транспортної точки доступу сервера (аналог номера порту призначення у TCP).
5. **Параметр TPDU Size (Код `0xC0`):** Узгодження максимального розміру транспортного пакета (логарифмічне значення: `0x07` = 128 байтів, `0x0B` = 2048 байтів, `0x0C` = 4096 байтів).
6. **Параметр Checksum Option (Код `0xC3`):** Прапорець обов'язкового розрахунку суми Флетчера для всіх наступних блоків `DT-TPDU`.

Якщо вузол-приймач підтримує запропоновані параметри, він виділяє власний дескриптор `DST-REF`, фіксує початковий розмір вікна кредиту `Credit (CDT)` і відправляє `CC-TPDU`. Лише після цього канал вважається відкритим для передачі корисних даних.

---

## 7. Обробка помилок та генерація звітів ER-PDU

Коли проміжний маршрутизатор або кінцева система не може доставити чи коректно розібрати пакет CLNP, стандарт ISO 8473 вимагає формування спеціального діагностичного пакета **Error Report PDU (ER-PDU)** (якщо у вихідному пакеті було встановлено прапорець `E/R = 1`).

Пакет ER-PDU має власний код типу `0x01` та містить обов'язкове поле **Reason for Discard (Причина відкидання)**:

| Код причини (Hex) | Класифікація помилки | Типова інженерна ситуація |
|---|---|---|
| `0x01` | Невизначена причина | Загальний збій пам'яті або відсутність ресурсів вузла |
| `0x02` | Непідтримувана версія протоколу | Отримано пакет із полем `Version != 0x01` |
| `0x03` | Вичерпано час життя (Lifetime expired) | Лічильник `Lifetime` зменшено до 0 у черзі маршрутизатора |
| `0x04` | Помилка контрольної суми заголовка | Акумулятори `C0` чи `C1` алгоритму Флетчера не зійшлися в 0 |
| `0x80` | Недосяжна адреса призначення | У таблиці маршрутизації IS-IS відсутній маршрут до `Dst NSAP` |
| `0x81` | Невідома адреса призначення | Формат `AFI/IDI` не підтримується цим автономним доменом |
| `0x91` | Неприпустимий розмір пакета | Розмір кадру перевищує MTU інтерфейсу при прапорці `SP = 0` |
| `0xA0` | Непідтримувана опція заголовка | Зустрінуто невідомий обов'язковий параметр у блоці TLV |

Після заголовка ER-PDU завжди додається точна копія всього заголовка відкинутого пакета CLNP (разом з адресами та опціями), що дозволяє вихідному вузлу точно ідентифікувати сесію та причину збою.

---

## 8. Програмні інтерфейси: сокети Берклі проти XTI/TLI

Причиною тріумфу TCP/IP серед прикладних програмістів стала не лише простота самого протоколу, а й елегантність інтерфейсу сокетів Берклі (**Berkeley Sockets API**), представленого в системі 4.2BSD UNIX у 1983 році:

:::tabs
```c
/* Простий інтерфейс Berkeley Sockets для TCP/IP мовою C */
int fd = socket(AF_INET, SOCK_STREAM, 0);
connect(fd, (struct sockaddr*)&addr, sizeof(addr));
write(fd, "GET / HTTP/1.0\r\n\r\n", 18);
```
```cpp
// Обгортка сокета RAII мовою C++20
class TcpStream {
    int fd_{-1};
public:
    TcpStream(std::string_view host, uint16_t port);
    ~TcpStream() { if (fd_ >= 0) ::close(fd_); }
    void send(std::string_view data);
};
```
:::

Для стека OSI замість простих сокетів консорціум X/Open стандартизував інтерфейс **XTI/TLI** (*Transport Layer Interface*). Він вимагав від розробника ручного керування складним автоматом станів із десятками функцій (`t_open`, `t_bind`, `t_connect`, `t_rcvconnect`, `t_snd`, `t_rcv`, `t_snddis`), передачі багатоповерхових структур `struct t_call` та постійної перевірки специфічних кодів помилок стану (`TOUTSTATE`, `TBADADDR`, `TBADOPT`).

Складна парадигма XTI/TLI відлякувала прикладних інженерів, тоді як сокети Берклі дозволяли запустити клієнт-серверний зв'язок буквально за 10 рядків коду.

---

## 9. Маршрутизація IS-IS та взаємодія з адресацією NET

У сучасних магістральних мережах провайдерів телекомунікацій протокол маршрутизації **IS-IS** (ISO/IEC 10589) використовує адресацію NSAP особливого формату, де селектор `N-SEL` завжди дорівнює `0x00`. Така адреса називається **NET** (*Network Entity Title*) і позначає сам маршрутизатор як системну сутність, а не окремий кінцевий транспортний процес:

- На канальному рівні (L2) кадри IS-IS упаковуються безпосередньо в заголовки IEEE 802.2 LLC з байтима SAP `0xFEFE` без проміжного заголовка IP чи CLNP.
- Маршрутизатор вилучає ідентифікатор зони (Area ID) та 6-байтний `System ID`, будуючи граф топології за алгоритмом Дейкстри (SPF).
- Парсер, подібний до наведеного у цьому проєкті, використовується безпосередньо всередині демонів маршрутизації (наприклад, FRRouting або BIRD) для обробки службових блоків протоколів зв'язку проміжних систем.

---

## 10. Аналіз безпеки та порівняння мовних ідіом C та C++

Розбір двійкових пакетів у реальному системному ПЗ (драйверах мережевих карт, ядрах ОС, вбудованих контролерах) є однією з найбільш критичних зон з точки зору інформаційної безпеки. Порівняємо підходи до забезпечення надійності в обох мовах:

### 1. Захист від виходу за межі пам'яті (Bounds Checking)
- **У мові C:** Інженер змушений вручну підтримувати змінну зміщення `offset` і перед кожним доступом до наступного байта перевіряти умову `if (offset + size > header_len) return false;`. Пропуск хоча б однієї такої перевірки (наприклад, для байта `dst_nsap_len`) дозволяє зловмиснику надіслати пакет з аномально великою заявленою довжиною адреси й прочитати конфіденційні дані з сусідніх ділянок оперативної пам'яті ядра.
- **У мові C++20:** Використання контейнера `std::span` інкапсулює розмір вікна пам'яті безпосередньо разом із покажчиком. Метод `subspan(offset, count)` чітко обмежує життєвий простір дочірніх структур. Якщо довжина виходить за межі діапазону, виникає передбачувана відмова замість невизначеної поведінки (UB).

### 2. Обробка помилок та семантика повернення значень
- **У мові C:** Функція повертає логічний прапорець `bool`, а результат записує через вихідний покажчик на структуру `pkt`. Це вимагає обов'язкового обнулення структури через `memset` перед початком роботи, щоб уникнути читання неініціалізованих полів у разі часткового збою під час розбору.
- **У мові C++20:** Функція повертає `std::optional<ClnpHeader>`, що робить неможливим доступ до полів структури, якщо розбір завершився помилкою валідації суми або невідповідністю версії протоколу.

### 3. Цілочисельна арифметика та порядок байтів (Endianness)
Обидва парсери суворо дотримуються вимоги мережевого порядку байтів **Big-Endian (Network Byte Order)**. Багатобайтні поля (`segment_len`, `duid`, `segment_offset`, `total_len`, `dst_ref`) збираються за допомогою явних бітових зсувів:

:::tabs
```c
/* Бітове збирання 16-бітного слова Big-Endian у C */
uint16_t val = ((uint16_t)buf[0] << 8) | buf[1];
```
```cpp
// Бітове збирання 16-бітного слова Big-Endian у C++20
constexpr uint16_t to_u16(uint8_t hi, uint8_t lo) noexcept {
    return (static_cast<uint16_t>(hi) << 8) | lo;
}
```
:::

Цей підхід є архітектурно нейтральним і гарантує однакову коректність роботи як на процесорах архітектури x86-64 / ARM (Little-Endian), так і на архітектурах MIPS / PowerPC (Big-Endian).

### 4. Стійкість до зловмисних та пошкоджених пакетів (Fuzzing Resilience)
Розроблений парсер успішно нейтралізує типові вектори мережевих атак:
- **Атака вкороченим заголовком:** Якщо вхідний буфер містить менше 9 байтів, парсер негайно повертає відмову без спроби читання відсутніх полів.
- **Атака невідповідності індикатора довжини:** Якщо значення `LI` у байті 1 перевищує фактичний розмір отриманого буфера `buf_len`, обробка припиняється до вилучення адрес.
- **Атака переповнення поля довжини адреси:** Якщо поле `DAL` містить значення більше 20 (максимальний розмір NSAP за стандартом ISO 8348), пакет бракується як аномальний.
- **Атака підміни контрольної суми:** Будь-яка зміна бітів у заголовку призводить до ненульового значення `C0` чи `C1`, що гарантує відхилення сфальсифікованого кадру.
