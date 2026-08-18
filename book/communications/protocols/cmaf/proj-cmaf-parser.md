# ⚙️ Парсер боксів ISOBMFF та валідатор чанків CMAF

Аналіз і перевірка фрагментованого MP4 (fMP4) у низькозатримних трансляціях вимагає роботи на рівні сирих бінарних боксів. Пакувальник генерує CMAF-сегменти, які надходять чанками через HTTP Chunked Transfer Encoding, і на стороні приймача чи проміжного проксі необхідно миттєво валідувати правильність заголовків, витягувати монотонні часові мітки `baseMediaDecodeTime` із бокса `tfdt` та перевіряти наявність точок випадкового доступу (ключових кадрів) без завантаження всього масиву медіаданих `mdat`.

### Задача

Розробити надійний парсер боксів ISOBMFF/CMAF, який:
1. Виконує покроковий розбір структури двійкових боксів довільного розміру, коректно обробляючи 32-бітні та 64-бітні поля довжини (`largesize`).
2. Рекурсивно занурюється у бокси-контейнери (`moof`, `traf`) та ігнорує непрозорі блоки корисного навантаження (`mdat`), не витрачаючи пам'ять на копіювання медіасемплів.
3. Витягує параметри фрагмента: порядковий номер `sequence_number` із `mfhd`, 64-бітну часову мітку декодування `baseMediaDecodeTime` із `tfdt` та параметри вибірок (розміри, тривалості, прапорці синхронізації) із `trun`.
4. Перевіряє інваріанти CMAF: наявність бренду `cmfs` у `styp`, прапорець `default-base-is-moof` у `tfhd` та відсутність часових розривів між сусідніми чанками.

---

### Принцип роботи парсера та організація пам'яті

Файлова структура ISOBMFF організована як дерево або послідовність блоків, де кожен блок повідомляє свій повний розмір на початку. Це дозволяє парсеру працювати у потоковому режимі: прочитавши перші 8 або 16 байтів, демультиплексор знає точну довжину тіла бокса. Якщо це контейнерний бокс (як-от `moof` або `traf`), парсер переходить до аналізу його внутрішнього вмісту. Якщо це листовий бокс метаданих (`tfdt`, `tfhd`, `trun`), парсер розбирає його поля. Якщо ж це масив медіаданих `mdat`, парсер просто зміщує покажчик читання на довжину `size - header_size`, миттєво пропускаючи мегабайти відеоданих без жодного копіювання байтів у пам'яті.

Усі числові значення у заголовках боксів закодовано у порядку байтів big-endian (старший байт перший). Для коректного декодування на архітектурах x86/ARM (little-endian) кожен 32-бітний та 64-бітний фрагмент перетворюється за допомогою бітових зсувів або функцій `ntohl`/`be64toh`.

У високопродуктивних роздавальних проксі-серверах такий аналіз виконується над ковзним кільцевим буфером (*ring buffer*). Коли черговий пакет TCP або HTTP-чанк надходить із мережевого інтерфейсу, парсер перевіряє, чи достатньо байтів у буфері для закриття поточного відкритого бокса. Якщо заголовок `moof` надійшов повністю, проксі негайно витягує часовий таймкод і порядковий номер, оновлює стан медіасесії для моніторингу метрик якості (QoS) та транслює отримані байти далі у вихідні сокети клієнтів.

---

### Реалізація парсера

Нижче наведено робочу реалізацію парсера двома мовами: C (робота з пам'яттю та вказівниками) та C++20 (безпечні абстракції над зрізами пам'яті `std::span`, типізовані переліки та монодичні структури `std::expected`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <arpa/inet.h>
#endif

/* Допоміжні функції читання big-endian цілих чисел */
static inline uint32_t read_u32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  | ((uint32_t)p[3]);
}

static inline uint64_t read_u64(const uint8_t *p) {
    return ((uint64_t)read_u32(p) << 32) | (uint64_t)read_u32(p + 4);
}

static inline int32_t read_i32(const uint8_t *p) {
    return (int32_t)read_u32(p);
}

/* Структура стандартного заголовка бокса */
typedef struct {
    uint32_t type;         /* 4-байтовий FourCC (наприклад 'moof') */
    uint64_t total_size;   /* Загальний розмір бокса в байтах */
    uint32_t header_size;  /* Розмір заголовка (8 або 16 байтів) */
} BoxHeader;

/* Структура метаданих вилученого чанка CMAF */
typedef struct {
    uint32_t seq_num;
    uint32_t track_id;
    uint64_t base_decode_time;
    uint32_t sample_count;
    uint64_t total_duration;
    bool has_sync_frame;
    bool default_base_is_moof;
} CmafChunkMetadata;

/* Розбір базового заголовка бокса */
bool parse_box_header(const uint8_t *buf, size_t len, BoxHeader *out) {
    if (len < 8) return false;

    uint32_t size32 = read_u32(buf);
    out->type = read_u32(buf + 4);
    out->header_size = 8;

    if (size32 == 1) {
        /* 64-бітний розширений розмір largesize */
        if (len < 16) return false;
        out->total_size = read_u64(buf + 8);
        out->header_size = 16;
    } else if (size32 == 0) {
        /* Бокс до кінця потоку */
        out->total_size = len;
    } else {
        out->total_size = size32;
    }

    return (out->total_size >= out->header_size && out->total_size <= len);
}

/* Розбір бокса tfdt: витягування базового часу декодування */
bool parse_tfdt(const uint8_t *payload, size_t len, uint64_t *dts_out) {
    if (len < 4) return false;
    uint8_t version = payload[0];

    if (version == 1) {
        if (len < 12) return false;
        *dts_out = read_u64(payload + 4);
        return true;
    } else if (version == 0) {
        if (len < 8) return false;
        *dts_out = (uint64_t)read_u32(payload + 4);
        return true;
    }
    return false;
}

/* Розбір бокса tfhd: перевірка налаштувань треку та прапорців */
bool parse_tfhd(const uint8_t *payload, size_t len, uint32_t *track_id, bool *base_is_moof) {
    if (len < 8) return false;
    uint32_t flags = read_u32(payload) & 0x00FFFFFF;
    *track_id = read_u32(payload + 4);
    *base_is_moof = (flags & 0x020000) != 0;
    return true;
}

/* Розбір бокса trun: обчислення тривалості та перевірка ключового кадру */
bool parse_trun(const uint8_t *payload, size_t len, uint32_t *sample_count,
                uint64_t *total_duration, bool *has_sync) {
    if (len < 8) return false;

    uint8_t version = payload[0];
    uint32_t flags = read_u32(payload) & 0x00FFFFFF;
    uint32_t count = read_u32(payload + 4);
    *sample_count = count;
    *total_duration = 0;
    *has_sync = false;

    const uint8_t *p = payload + 8;
    const uint8_t *end = payload + len;

    if (flags & 0x000001) p += 4; /* data_offset */
    uint32_t first_flags = 0;
    if (flags & 0x000004) {       /* first_sample_flags */
        if (p + 4 > end) return false;
        first_flags = read_u32(p);
        p += 4;
        /* Перевірка: чи перший семпл є синхронним (ключовим) */
        if ((first_flags & 0x00010000) == 0) {
            *has_sync = true;
        }
    }

    bool has_dur = (flags & 0x000100) != 0;
    bool has_size = (flags & 0x000200) != 0;
    bool has_flags = (flags & 0x000400) != 0;
    bool has_cto = (flags & 0x000800) != 0;

    for (uint32_t i = 0; i < count; i++) {
        uint32_t dur = 1;
        if (has_dur) {
            if (p + 4 > end) return false;
            dur = read_u32(p);
            p += 4;
        }
        *total_duration += dur;

        if (has_size) {
            if (p + 4 > end) return false;
            p += 4;
        }
        if (has_flags) {
            if (p + 4 > end) return false;
            uint32_t sflags = read_u32(p);
            p += 4;
            /* Біт 16 (0x00010000): sample_is_non_sync_sample == 0 -> SAP/Sync */
            if ((sflags & 0x00010000) == 0) {
                *has_sync = true;
            }
        }
        if (has_cto) {
            if (p + 4 > end) return false;
            p += 4;
        }
    }

    return true;
}

/* Розбір контейнера traf */
bool parse_traf(const uint8_t *traf_data, size_t traf_len, CmafChunkMetadata *meta) {
    size_t offset = 0;
    while (offset + 8 <= traf_len) {
        BoxHeader h;
        if (!parse_box_header(traf_data + offset, traf_len - offset, &h)) break;

        const uint8_t *body = traf_data + offset + h.header_size;
        size_t body_len = h.total_size - h.header_size;

        if (h.type == 0x74666474) { /* 'tfdt' */
            parse_tfdt(body, body_len, &meta->base_decode_time);
        } else if (h.type == 0x74666864) { /* 'tfhd' */
            parse_tfhd(body, body_len, &meta->track_id, &meta->default_base_is_moof);
        } else if (h.type == 0x7472756E) { /* 'trun' */
            parse_trun(body, body_len, &meta->sample_count, &meta->total_duration, &meta->has_sync_frame);
        }

        offset += h.total_size;
    }
    return true;
}

/* Головна функція інспекції CMAF-сегмента/чанка */
bool inspect_cmaf_chunk(const uint8_t *data, size_t len, CmafChunkMetadata *meta) {
    memset(meta, 0, sizeof(*meta));
    size_t offset = 0;

    while (offset + 8 <= len) {
        BoxHeader h;
        if (!parse_box_header(data + offset, len - offset, &h)) return false;

        const uint8_t *body = data + offset + h.header_size;
        size_t body_len = h.total_size - h.header_size;

        if (h.type == 0x6D6F6F66) { /* 'moof' */
            size_t inner_off = 0;
            while (inner_off + 8 <= body_len) {
                BoxHeader inh;
                if (!parse_box_header(body + inner_off, body_len - inner_off, &inh)) break;
                const uint8_t *in_body = body + inner_off + inh.header_size;
                size_t in_body_len = inh.total_size - inh.header_size;

                if (inh.type == 0x6D666864 && in_body_len >= 8) { /* 'mfhd' */
                    meta->seq_num = read_u32(in_body + 4);
                } else if (inh.type == 0x74726166) { /* 'traf' */
                    parse_traf(in_body, in_body_len, meta);
                }
                inner_off += inh.total_size;
            }
        }

        offset += h.total_size;
    }
    return true;
}
```
```cpp
#include <iostream>
#include <span>
#include <string_view>
#include <vector>
#include <cstdint>
#include <expected>
#include <bit>

namespace cmaf {

enum class ParseError {
    UnexpectedEof,
    InvalidBoxSize,
    InvalidVersion,
    MalformedStructure
};

struct FourCC {
    uint32_t value{0};

    [[nodiscard]] constexpr std::string_view as_string() const noexcept {
        return std::string_view(reinterpret_cast<const char*>(&value), 4);
    }
};

struct BoxHeader {
    FourCC type;
    uint64_t total_size{0};
    uint32_t header_size{8};
};

struct ChunkSummary {
    uint32_t sequence_number{0};
    uint32_t track_id{0};
    uint64_t base_decode_time{0};
    uint32_t sample_count{0};
    uint64_t duration_ticks{0};
    bool is_sync_point{false};
    bool base_is_moof{false};
};

class BoxParser {
public:
    static uint32_t read_be32(std::span<const uint8_t> bytes) noexcept {
        return (static_cast<uint32_t>(bytes[0]) << 24) |
               (static_cast<uint32_t>(bytes[1]) << 16) |
               (static_cast<uint32_t>(bytes[2]) << 8)  |
               (static_cast<uint32_t>(bytes[3]));
    }

    static uint64_t read_be64(std::span<const uint8_t> bytes) noexcept {
        return (static_cast<uint64_t>(read_be32(bytes.subspan(0, 4))) << 32) |
               (static_cast<uint64_t>(read_be32(bytes.subspan(4, 4))));
    }

    static std::expected<BoxHeader, ParseError> parse_header(std::span<const uint8_t> data) noexcept {
        if (data.size() < 8) return std::unexpected(ParseError::UnexpectedEof);

        uint32_t s32 = read_be32(data.subspan(0, 4));
        FourCC type{read_be32(data.subspan(4, 4))};
        uint64_t total = s32;
        uint32_t hsz = 8;

        if (s32 == 1) {
            if (data.size() < 16) return std::unexpected(ParseError::UnexpectedEof);
            total = read_be64(data.subspan(8, 8));
            hsz = 16;
        } else if (s32 == 0) {
            total = data.size();
        }

        if (total < hsz || total > data.size()) {
            return std::unexpected(ParseError::InvalidBoxSize);
        }

        return BoxHeader{type, total, hsz};
    }

    static std::expected<ChunkSummary, ParseError> inspect_chunk(std::span<const uint8_t> chunk) {
        ChunkSummary summary;
        size_t offset = 0;

        while (offset + 8 <= chunk.size()) {
            auto h_res = parse_header(chunk.subspan(offset));
            if (!h_res) return std::unexpected(h_res.error());

            const auto& hdr = *h_res;
            auto body = chunk.subspan(offset + hdr.header_size, hdr.total_size - hdr.header_size);

            if (hdr.type.value == 0x6D6F6F66) { // 'moof'
                size_t in_off = 0;
                while (in_off + 8 <= body.size()) {
                    auto in_h = parse_header(body.subspan(in_off));
                    if (!in_h) break;
                    auto in_body = body.subspan(in_off + in_h->header_size, in_h->total_size - in_h->header_size);

                    if (in_h->type.value == 0x6D666864 && in_body.size() >= 8) { // 'mfhd'
                        summary.sequence_number = read_be32(in_body.subspan(4, 4));
                    } else if (in_h->type.value == 0x74726166) { // 'traf'
                        parse_traf(in_body, summary);
                    }
                    in_off += in_h->total_size;
                }
            }
            offset += hdr.total_size;
        }
        return summary;
    }

private:
    static void parse_traf(std::span<const uint8_t> traf_body, ChunkSummary& summary) {
        size_t off = 0;
        while (off + 8 <= traf_body.size()) {
            auto h = parse_header(traf_body.subspan(off));
            if (!h) break;
            auto body = traf_body.subspan(off + h->header_size, h->total_size - h->header_size);

            if (h->type.value == 0x74666474 && !body.empty()) { // 'tfdt'
                uint8_t ver = body[0];
                if (ver == 1 && body.size() >= 12) {
                    summary.base_decode_time = read_be64(body.subspan(4, 8));
                } else if (ver == 0 && body.size() >= 8) {
                    summary.base_decode_time = read_be32(body.subspan(4, 4));
                }
            } else if (h->type.value == 0x74666864 && body.size() >= 8) { // 'tfhd'
                uint32_t flags = read_be32(body.subspan(0, 4)) & 0x00FFFFFF;
                summary.track_id = read_be32(body.subspan(4, 4));
                summary.base_is_moof = (flags & 0x020000) != 0;
            } else if (h->type.value == 0x7472756E && body.size() >= 8) { // 'trun'
                uint32_t flags = read_be32(body.subspan(0, 4)) & 0x00FFFFFF;
                summary.sample_count = read_be32(body.subspan(4, 4));

                size_t p = 8;
                if (flags & 0x000001) p += 4; // data_offset
                if (flags & 0x000004) {       // first_sample_flags
                    if (p + 4 <= body.size()) {
                        uint32_t fs = read_be32(body.subspan(p, 4));
                        if ((fs & 0x00010000) == 0) summary.is_sync_point = true;
                        p += 4;
                    }
                }
                bool has_dur = (flags & 0x000100) != 0;
                bool has_flags = (flags & 0x000400) != 0;

                for (uint32_t i = 0; i < summary.sample_count; ++i) {
                    if (has_dur && p + 4 <= body.size()) {
                        summary.duration_ticks += read_be32(body.subspan(p, 4));
                        p += 4;
                    }
                    if (flags & 0x000200) p += 4; // sample_size
                    if (has_flags && p + 4 <= body.size()) {
                        uint32_t sf = read_be32(body.subspan(p, 4));
                        if ((sf & 0x00010000) == 0) summary.is_sync_point = true;
                        p += 4;
                    }
                    if (flags & 0x000800) p += 4; // sample_cto
                }
            }
            off += h->total_size;
        }
    }
};

} // namespace cmaf
```
:::

---

### Розібраний приклад: покроковий розбір реального чанка

Розглянемо шістнадцятковий дамп реального заголовка чанка відео AVC/H.264 (частота 30 кадр/с, timescale 90000, 10 кадрів = 30000 тіків):

```
Зміщення  Шістнадцятковий дамп                        Інтерпретація
---------------------------------------------------------------------------------
0x0000:   00 00 00 68 6D 6F 6F 66                     moof (size=104)
0x0008:   00 00 00 10 6D 66 68 64 00 00 00 00 00 00 00 05  mfhd (v0, seq=5)
0x0018:   00 00 00 50 74 72 61 66                     traf (size=80)
0x0020:   00 00 00 10 74 66 68 64 00 02 00 00 00 00 00 01  tfhd (flags=0x020000 [base-is-moof], track_ID=1)
0x0030:   00 00 00 14 74 66 64 74 01 00 00 00 00 00 00 00  tfdt (v1, flags=0)
0x0040:   00 04 93 E0                                 baseMediaDecodeTime = 300000 (3.333s)
0x0044:   00 00 00 24 74 72 75 6E 00 00 03 05 00 00 00 0A  trun (flags=0x000305, count=10)
0x0054:   00 00 00 70                                 data_offset = 112
0x0058:   02 00 00 00                                 first_sample_flags (I-кадр, sync)
...
```

**Крок 1: Обробка заголовка `moof`.**
Парсер зчитує 4 байти розміру (`0x00000068` = 104 байти) та 4 байти FourCC (`0x6D6F6F66` = `'moof'`). Розмір валідний, парсер переходить до аналізу дочірніх боксів.

**Крок 2: Отримання номера послідовності `mfhd`.**
Всередині `moof` на зміщенні `+8` розміщено бокс `mfhd` розміром 16 байтів. Байт версії дорівнює `0`, прапорці `0x000000`. На зміщенні `+12` парсер зчитує поле `sequence_number = 0x00000005` (5-й фрагмент).

**Крок 3: Розбір налаштувань треку `tfhd`.**
Всередині `traf` розміщено `tfhd` розміром 16 байтів. Прапорці `flags = 0x020000` вказують на встановлений прапорець `default-base-is-moof`. Поле `track_ID = 1`.

**Крок 4: Вилучення 64-бітного таймкоду `tfdt`.**
Бокс `tfdt` має довжину 20 байтів (`0x00000014`), версія дорівнює `1`. 64-бітне поле `baseMediaDecodeTime` має значення `0x00000000000493E0 = 300000` тіків. При часовій шкалі 90 кГц це відповідає точно `300000 / 90000 = 3.3333` секунди від початку ефіру.

**Крок 5: Розбір семплів `trun`.**
Бокс `trun` містить 10 семплів. Прапорці `0x000305` сигналізують про наявність `data_offset` (байти зміщення до `mdat`), `first_sample_flags` (перший кадр — ключовий I-кадр), `sample_duration` (по 3000 тіків на кадр = 33.3 мс) та `sample_size`. Сумарна тривалість чанка: `10 · 3000 = 30000` тіків (333.3 мс).

---

---

### Робота з потоковими сокетами та ковзним буфером

У реальних мережевих додатках (наприклад, у проксі-серверах на базі Epoll або Kqueue) дані надходять із сокета TCP фрагментами розміром від одного MTU (1500 байтів) до кількох десятків кілобайтів. Окремий CMAF-чанк розміром 30–100 КБ ніколи не приходить одним системним викликом `read()`.

Парсер працює за моделлю скінченного автомата з лінійним або кільцевим буфером накопичення:

1. **Фаза очікування заголовка:** Парсер накопичує мінімум 8 байтів. Зчитує `size` та `type`. Якщо `size == 1`, очікує ще 8 байтів для читання `largesize`.
2. **Фаза накопичення метаданих:** Якщо FourCC бокса належить до метаданих (`styp`, `prft`, `emsg`, `moof`), парсер чекає, поки в буфер надійде весь обсяг `total_size` байтів, після чого виконує синхронний розбір внутрішніх боксів `traf`, `tfdt`, `trun`.
3. **Фаза потокового пропуску медіаданих (`mdat`):** Коли парсер виявляє бокс `mdat`, йому не потрібно тримати всі мегабайти відео в пам'яті. Знаючи розмір із заголовка, парсер перемикається в режим наскрізної передачі: усі наступні байти, що приходять із сокета, негайно ретранслюються клієнтам або передаються в апаратний декодер, а внутрішній лічильник залишкового розміру декрементується на кількість прочитаних байтів.

---

### Інтеграція парсера у конвеєр потокового клієнта

Розглянемо, як розроблений парсер вбудовується у клієнтський стек відтворення (наприклад, у нативний C/C++ медіаплеєр на базі FFmpeg або рушій WebAssembly у браузері):

```
HTTP/1.1 Socket (Chunked Transfer)
        │
        ▼ (read chunks of 16-64 KB)
┌──────────────────────────────────────────────────────────┐
│  Кільцевий буфер вхідного потоку (Network Ring Buffer)   │
└──────────────────────────────────────────────────────────┘
        │
        ▼ inspect_cmaf_chunk()
┌──────────────────────────────────────────────────────────┐
│  Парсер боксів CMAF:                                    │
│  1. Перевірка styp/moof/mdat                             │
│  2. Вилучення sequence_number з mfhd                     │
│  3. Фіксація baseMediaDecodeTime з tfdt                  │
│  4. Розрахунок тривалостей і перевірка SAP у trun        │
└──────────────────────────────────────────────────────────┘
        │
        ├──► [Валідація таймлайну]: перевірка неперервності DTS
        │
        ▼ (сирі байти moof + mdat)
┌──────────────────────────────────────────────────────────┐
│  Буфер декодера (MSE SourceBuffer / Апаратний декодер)   │
└──────────────────────────────────────────────────────────┘
```

1. **Клієнт ініціалізує сеанс:** Першим запитом завантажується `init.mp4`. Парсер зчитує `ftyp` та `moov`, витягує кодекові структури (`avcC`, `hvcC` або `esds`) і передає їх у відеопідсистему для ініціалізації апаратного декодера H.264/HEVC.
2. **Відкриття потокового запиту сегмента:** Клієнт надсилає HTTP GET на черговий `seg-*.m4s`. Оскільки сервер використовує Chunked Transfer Encoding, тіло відповіді надходить не суцільним файлом, а послідовними чанками.
3. **Почанкковий розбір та випереджальне декодування:** Щойно у буфері збирається пара `moof` + `mdat` (розміром 30–80 КБ), парсер миттєво проводить валідацію: переконується у наявності `default-base-is-moof`, перевіряє монотонність `baseMediaDecodeTime` та передає чанк у декодер.
4. **Контроль затримки та корекція швидкості:** Плеєр порівнює поточну часову мітку кадру із годинником UTC. Якщо затримка перевищує цільові 2.0 секунди, рушій динамічно збільшує швидкість виводу кадрів на 4%, плавно підтягуючи відтворення до краю прямого ефіру.
5. **Компіляція у WebAssembly для браузерних плеєрів:** Наведений C/C++ код компілюється через Emscripten або Clang у модуль WebAssembly (Wasm). Браузер передає масив байтів `Uint8Array` безпосередньо у спільну лінійну пам'ять Wasm (`WebAssembly.Memory`), уникаючи накладних витрат на маршалінг об'єктів у JavaScript-рушії V8/SpiderMonkey та забезпечуючи обробку сотень чанків на секунду з нульовою затримкою.

---

### Розбір та валідація метаданих захисту CENC (`pssh`, `tenc`, `senc`)

У захищених комерційних потоках (наприклад, OTT-сервісах із захистом Widevine, PlayReady або FairPlay) парсер виконує додатковий рівень валідації криптографічних структур перед передачею семплів у модуль дешифрування CDM:

1. **Витягування ідентифікаторів ключів із `pssh`:**
   Парсер сканує бокс `moov` або заголовки фрагментів на наявність боксів `pssh` (FourCC `0x70737368`). Зчитує 16-байтний `SystemID`. Якщо `SystemID` збігається з підтримуваною платформою DRM (наприклад, Google Widevine `edef8ba9-79d6-4ace-a3c8-27dcd51d21ed`), парсер витягує масив 16-байтних ідентифікаторів ключів `KID` та передає бінарний блоб ініціалізації у відеоплеєр (виклик `MediaKeys.createSession()` у браузерному EME API).

2. **Перевірка параметрів шифрування треку в `tenc`:**
   Всередині `stbl->sinf->schi` парсер перевіряє значення `default_IsProtected = 1`. Для потоків зі схемою `cbcs` обов'язково перевіряються поля захисного патерну: `default_crypt_byte_block == 1` та `default_skip_byte_block == 9`. Якщо значення відрізняються від конфігурації 1:9, потік вважається несумісним зі стандартом CMAF cbcs і відхиляється.

3. **Валідація підсемплового шифрування в `senc`:**
   Усередині бокса `traf` парсер зчитує бокс `senc` (Sample Encryption Box). Якщо увімкнено прапорець `flags = 0x000002` (Subsample Encryption), парсер для кожного відеокадру вичитує масив підсемплових блоків і перевіряє арифметичний інваріант:
   `∑ (BytesOfClearData[i] + BytesOfProtectedData[i]) == trun.sample_size[frame_index]`.
   Якщо сума відкритих і зашифрованих байтів у `senc` не сходиться з точним розміром кадру з `trun` хоча б на 1 байт, це свідчить про пошкодження файлу або збій пакувальника, що призведе до аварійного завершення апаратного криптопроцесора.

---

### Консольна утиліта для швидкої перевірки та інспекції чанків (Python)

Для автоматизованого тестування у CI/CD конвеєрах та швидкого аналізу медіапотоків у терміналі наведено скрипт на мові Python, що перевіряє структуру боксів і виводить параметри чанків:

```python
#!/usr/bin/env python3
"""cmaf_inspector.py — утиліта швидкої інспекції боксів та валідації чанків CMAF."""
import sys
import struct

def parse_boxes(data, offset=0, depth=0):
    indent = "  " * depth
    while offset + 8 <= len(data):
        size32, fourcc = struct.unpack_from(">I4s", data, offset)
        fourcc_str = fourcc.decode("latin1", errors="replace")
        header_len = 8

        if size32 == 1:
            if offset + 16 > len(data):
                break
            size = struct.unpack_from(">Q", data, offset + 8)[0]
            header_len = 16
        elif size32 == 0:
            size = len(data) - offset
        else:
            size = size32

        if size < header_len or offset + size > len(data):
            print(f"{indent}❌ Помилка: невалідний розмір бокса {fourcc_str}: {size} байтів")
            break

        print(f"{indent}📦 [{fourcc_str}] розмір={size} байтів (зміщення=0x{offset:04X})")

        payload = data[offset + header_len:offset + size]

        # Рекурсивний розбір боксів-контейнерів
        if fourcc_str in ("moov", "moof", "trak", "mdia", "minf", "stbl", "mvex", "traf", "sinf", "schi"):
            parse_boxes(payload, offset=0, depth=depth + 1)
        elif fourcc_str == "tfdt" and len(payload) >= 4:
            ver = payload[0]
            if ver == 1 and len(payload) >= 12:
                dts = struct.unpack_from(">Q", payload, 4)[0]
                print(f"{indent}  ⏱ tfdt v1 baseMediaDecodeTime = {dts}")
            elif ver == 0 and len(payload) >= 8:
                dts = struct.unpack_from(">I", payload, 4)[0]
                print(f"{indent}  ⏱ tfdt v0 baseMediaDecodeTime = {dts}")
        elif fourcc_str == "mfhd" and len(payload) >= 8:
            seq = struct.unpack_from(">I", payload, 4)[0]
            print(f"{indent}  🔢 mfhd sequence_number = {seq}")

        offset += size

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python cmaf_inspector.py <сегмент.m4s | init.mp4>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        content = f.read()

    print(f"Аналіз файлу: {sys.argv[1]} ({len(content)} байтів)")
    parse_boxes(content)
```

Ця утиліта не потребує сторонніх бібліотек, працює на будь-якому сервері зі стандартним Python 3 і дозволяє миттєво локалізувати помилки пакування: виявити пошкоджені заголовки, збійні номери послідовності `sequence_number` або часові зсуви у `tfdt`.

---

### Демультиплексування NAL-юнітів усередині `mdat`

Всередині бокса `mdat` стиснене відео H.264 (AVC) та H.265 (HEVC) зберігається не у форматі потоку байтів Annex B (із розділювачами `0x000001` або `0x00000001`), а у форматі **AVCC / HVCC**.

Кожна окрема вибірка (Sample), описана у боксі `trun`, складається з одного або кількох NAL-юнітів:
* Перші 4 байти (або рідше 2 чи 1 байт, згідно з полем `lengthSizeMinusOne` у `avcC`) містять точну довжину NAL-юніта в байтах у форматі big-endian.
* Наступні байти — це сам NAL-юніт (Network Abstraction Layer unit).

Перший байт NAL-юніта містить його тип (`nal_unit_type = byte & 0x1F` для H.264):
* `type == 7`: Sequence Parameter Set (SPS) — параметри роздільності та профілю;
* `type == 8`: Picture Parameter Set (PPS) — параметри кодування кадрів;
* `type == 5`: Coded slice of an IDR picture — ключовий кадр (точка відновлення декодера);
* `type == 1`: Coded slice of a non-IDR picture — звичайний різницевий кадр (P або B).

Парсер, перевіряючи прапорці `sample_flags` у боксі `trun`, може валідувати відповідність: якщо прапорець стверджує, що кадр є ключовим (`sample_is_non_sync_sample == 0`), то перший NAL-юніт усередині відповідної ділянки `mdat` зобов'язаний мати тип 5 (IDR) або супроводжуватися SPS/PPS.

---

### Стратегії відновлення після збоїв та обробка розривів таймлайну

Під час прийому живої трансляції через нестабільний інтернет можливі кілька типів аномалій:

1. **Втрата чанка або пропуск `sequence_number`.** Якщо після чанка з `seq_num = 42` надходить чанк з `seq_num = 44`, парсер фіксує втрату чанка №43. Якщо чанк №44 не є ключовим (не містить точки випадкового доступу SAP), декодер не зможе відобразити його кадри через відсутність опорних поверхонь. У цьому разі парсер повинен відкинути всі P/B-кадри до надходження наступного чанка з IDR-кадром.
2. **Немонотонний час `tfdt`.** Якщо `baseMediaDecodeTime` нового чанка менший за час попереднього (регресія часу), це свідчить про зміну джерела трансляції або вставку реклами без створення нового періоду DASH. Парсер зобов'язаний сповістити відеоплеєр про розрив таймлайну (*discontinuity*), що змушує рушій відтворення скинути буфери Media Source Extensions та оновити внутрішнє часове зміщення `timestampOffset`.
3. **Дрейф тактового генератора.** Якщо різниця між NTP-часом із бокса `prft` та системним годинником приймача монотонно зростає або спадає, плеєр коригує темп читання сокета, уникаючи як переповнення вхідного кільцевого буфера, так і його вичерпання (*buffer underrun*).

---

### Моніторинг якості трансляції (QoS) та збір метрик

У промислових системах відеодоставки парсер CMAF-чанків виконує роль джерела метрик реального часу для систем моніторингу (Prometheus, Grafana, Datadog). Під час аналізу кожного чанка демультиплексор вираховує такі показники:

1. **Миттєва тривалість та бітрейт чанка:** Обчислюється як відношення суми розмірів семплів `sample_size` із бокса `trun` до сумарної тривалості `sample_duration`. Різкі коливання бітрейту сигналізують про неефективну роботу кодувальника або складні динамічні сцени.
2. **Інтервал між ключовими кадрами (GOP Length):** Парсер фіксує часовий інтервал між послідовними чанками із прапорцем `has_sync_frame == true`. Якщо інтервал перевищує цільове значення (наприклад, 2.0 секунди), адаптивне перемикання якості для клієнтів блокується.
3. **Кількість розривів таймлайну (Discontinuity Count):** Лічильник подій немонотонності `tfdt` або пропуску `mfhd.sequence_number`. Зростання цього лічильника понад нуль у нормальному режимі свідчить про аварійний стан каналу зв'язку між ареною та центром кодування.

Метрики експортуються у стандартному текстовому форматі Prometheus:
```
# HELP cmaf_chunk_duration_seconds Тривалість останнього чанка
# TYPE cmaf_chunk_duration_seconds gauge
cmaf_chunk_duration_seconds{track="1080p"} 0.333
# HELP cmaf_discontinuity_total Загальна кількість розривів таймлайну
# TYPE cmaf_discontinuity_total counter
cmaf_discontinuity_total{track="1080p"} 0
```
Це дозволяє черговим інженерам автоматично налаштовувати алерти при виникненні затримок або втраті синхронізації між джерелами трансляції.

---

### Підводні камені та крайові випадки

1. **Прапорець `default-base-is-moof` (`0x020000`).** У специфікаціях до CMAF зміщення семплів `data_offset` у боксі `trun` могло відлічуватися або від початку файлу, або від початку `moof`. Якщо прапорець не встановлено, парсер був змушений тримати глобальний лічильник прочитаних байтів. Для CMAF прапорець є обов'язковим: зміщення рахується локально від першого байта батьківського `moof`, що робить кожен чанк повністю автономним у потоковій передачі.
2. **Знаковий `sample_composition_time_offset` у `trun` version 1.** У потоках із B-кадрами мітка показу (PTS) може випереджати або відставати від мітки декодування (DTS). У версії 0 бокса `trun` поле було 32-бітним беззнаковим (`uint32`), що унеможливлювало від'ємні зсуви. У версії 1 поле стало 32-бітним знаковим (`int32`), і читати його необхідно із приведенням типів `(int32_t)read_u32()`.
3. **64-бітний час у `tfdt`.** При трансляції цілодобових новинних або спортивних каналів 32-бітний лічильник `baseMediaDecodeTime` при стандартній тактовій частоті 90 кГц переповнюється через `2^32 / 90000 = 47721` секунду (близько 13.2 години). CMAF суворо вимагає використання `tfdt` version 1 (64-бітне поле), що гарантує безперервну роботу без переповнення протягом понад 6.5 мільйонів років.
4. **Валідація неперервності чанків.** Під час прийому потоку LL-DASH або LL-HLS клієнт зобов'язаний перевіряти інваріант:
   `tfdt.baseMediaDecodeTime[N+1] == tfdt.baseMediaDecodeTime[N] + trun.total_duration[N]`.
   Будь-яка невідповідність свідчить про втрату пакетів або збій таймлайну на кодувальнику, що вимагає негайного перезапиту плейлиста або переініціалізації відеобуфера.
5. **Неповні буфери при потоковому прийомі (TCP Streaming Chunking).** Під час отримання даних із сокета через HTTP Chunked Transfer чанк може бути розірваний на рівні пакетів TCP. Парсер не повинен завершуватися помилкою при отриманні `len < total_size`: він повертає код очікування додаткових байтів (`UnexpectedEof`), зберігаючи стан поточного зміщення до надходження наступного мережевого пакету.
