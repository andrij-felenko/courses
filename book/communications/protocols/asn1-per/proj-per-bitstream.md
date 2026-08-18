# ⚙️ Реалізація невирівняного бітового потоку UPER на C та C++

Упаковані правила кодування PER (ITU-T X.691) у невирівняному режимі UPER відрізняються від звичайних двійкових протоколів тим, що вони повністю відмовляються від прив'язки до меж октетів. Якщо класичний двійковий формат записує кожне поле як ціле число байтів (1, 2, 4 або 8), то в UPER кожне значення займає рівно стільки бітів, скільки необхідно згідно з його математичним діапазоном: 1 біт для логічного прапорця, 3 біти для перелічуваного типу з восьми станів, 5 бітів для кількості супутників або 31 біт для географічної координати.

Наступне поле починається безпосередньо з наступного вільного біта, перетинаючи байтові межі без жодних проміжків і вирівнювань. Звичайні апаратні інструкції процесора оперують словами фіксованої розрядності (байтами, 32- або 64-бітовими регістрами), тому прямий доступ за покажчиком до таких полів неможливий. Робота з UPER вимагає реалізації спеціалізованого рівня абстракції: бітового записувача (`BitWriter`) та бітового читача (`BitReader`).

### Анатомія та інваріанти бітового потоку

Стандарт ITU-T X.691 встановлює суворі правила орієнтації та нумерації бітів:
1. **Порядок октетів (Network Byte Order):** Байти в потоці передаються зліва направо (від нульового індексу буфера до кінцевого).
2. **Порядок бітів усередині октету (MSB-first):** Біти всередині кожного 8-бітового байта нумеруються від 7 (найстарший біт, вага `2⁷ = 128`) до 0 (наймолодший біт, вага `2⁰ = 1`).
3. **Напрямок запису:** Перший біт повідомлення записується у 7-й біт нульового байта буфера. Наступний — у 6-й біт і так далі. Коли 0-й біт поточного байта заповнено, запис автоматично переходить до 7-го біта наступного байта.
4. **Орієнтація багатобітових значень:** Якщо значення кодується числом із кількох бітів, його старші значущі біти завжди записуються першими.
5. **Фінальне доповнення кадру:** Якщо загальна кількість корисних бітів у повідомленні не є кратною 8, останні вільні біти фінального октету заповнюються нульовими бітами (`0`).

Розглянемо механіку розщеплення поля при переході через межу байта. Нехай у поточному байті залишилося 3 вільних біти (біти 2, 1, 0), а наступне значення вимагає запису 7 бітів `1011011₂`. Значення розбивається на дві частини:
* Старші 3 біти `101₂` записуються у біти 2..0 поточного байта.
* Молодші 4 біти `1011₂` зсуваються вгору і записуються у біти 7..4 наступного байта.

Створимо завершену, високоефективну бібліотеку бітового пакування на мовах C та C++, розберемо роботу крайових випадків (константні діапазони, поля понад 32 біти, захист від переповнення буфера), а потім реалізуємо повний цикл кодування та декодування структури `RRCConnectionRequest` зі стандарту стільникового зв'язку 3GPP LTE.

### Реалізація бітового записувача та читача

Нижче наведено модулі бітового потоку. У версії на C++ ми використовуємо сучасні стандарти: безпечні зрізи пам'яті `std::span`, вичерпну типізацію помилок через `std::expected` без накладних витрат на винятки та строгу концепцію володіння ресурсами.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура для побітового запису даних */
typedef struct {
    uint8_t *buffer;
    size_t capacity_bytes;
    size_t bit_pos;       /* Поточна позиція в бітах від початку буфера */
} BitWriter;

/* Ініціалізація записувача */
void bit_writer_init(BitWriter *bw, uint8_t *buf, size_t cap) {
    bw->buffer = buf;
    bw->capacity_bytes = cap;
    bw->bit_pos = 0;
    if (cap > 0) {
        memset(buf, 0, cap);
    }
}

/* Запис до 32 бітів у потік (MSB-first) */
bool bit_writer_put_bits(BitWriter *bw, uint32_t value, uint8_t num_bits) {
    if (num_bits == 0) return true;
    if (num_bits > 32) return false;
    if ((bw->bit_pos + num_bits) > (bw->capacity_bytes * 8)) return false;

    /* Маскуємо зайві старші біти */
    if (num_bits < 32) {
        value &= (1U << num_bits) - 1U;
    }

    int remaining = num_bits;
    while (remaining > 0) {
        size_t byte_idx = bw->bit_pos / 8;
        uint8_t bit_in_byte = bw->bit_pos % 8;
        uint8_t bits_free_in_byte = 8 - bit_in_byte;

        uint8_t bits_to_write = (remaining < bits_free_in_byte) ? (uint8_t)remaining : bits_free_in_byte;
        uint8_t shift = remaining - bits_to_write;
        uint8_t chunk = (uint8_t)((value >> shift) & ((1U << bits_to_write) - 1U));

        /* Зсуваємо фрагмент на потрібну позицію в поточному байті */
        bw->buffer[byte_idx] |= (uint8_t)(chunk << (bits_free_in_byte - bits_to_write));

        bw->bit_pos += bits_to_write;
        remaining -= bits_to_write;
    }
    return true;
}

/* Запис 1 біта */
bool bit_writer_put_bit(BitWriter *bw, bool bit) {
    return bit_writer_put_bits(bw, bit ? 1U : 0U, 1);
}

/* Запис обмеженого цілого числа [lb .. ub] */
bool bit_writer_put_constrained_int(BitWriter *bw, int64_t val, int64_t lb, int64_t ub) {
    if (val < lb || val > ub) return false;
    uint64_t range = (uint64_t)(ub - lb + 1);
    if (range == 1) return true; /* Константа: 0 бітів */

    /* Обчислюємо ceil(log2(range)) */
    uint8_t bits = 0;
    uint64_t temp = range - 1;
    while (temp > 0) {
        bits++;
        temp >>= 1;
    }

    uint64_t offset = (uint64_t)(val - lb);
    if (bits <= 32) {
        return bit_writer_put_bits(bw, (uint32_t)offset, bits);
    } else {
        /* Якщо діапазон більше 32 бітів, пишемо двома частинами */
        uint8_t high_bits = bits - 32;
        if (!bit_writer_put_bits(bw, (uint32_t)(offset >> 32), high_bits)) return false;
        return bit_writer_put_bits(bw, (uint32_t)(offset & 0xFFFFFFFFU), 32);
    }
}

/* Вирівнювання на найближчу межу октету (для APER та Open Type) */
void bit_writer_align_to_byte(BitWriter *bw) {
    size_t rem = bw->bit_pos % 8;
    if (rem != 0) {
        bw->bit_pos += (8 - rem);
    }
}

/* Отримання кількості повних байтів після завершення */
size_t bit_writer_get_length_bytes(const BitWriter *bw) {
    return (bw->bit_pos + 7) / 8;
}

/* Структура для побітового читання */
typedef struct {
    const uint8_t *buffer;
    size_t total_bits;
    size_t bit_pos;
} BitReader;

/* Ініціалізація читача */
void bit_reader_init(BitReader *br, const uint8_t *buf, size_t total_bytes) {
    br->buffer = buf;
    br->total_bits = total_bytes * 8;
    br->bit_pos = 0;
}

/* Читання до 32 бітів */
bool bit_reader_get_bits(BitReader *br, uint8_t num_bits, uint32_t *out_val) {
    if (num_bits == 0) { *out_val = 0; return true; }
    if (num_bits > 32) return false;
    if (br->bit_pos + num_bits > br->total_bits) return false;

    uint32_t result = 0;
    int remaining = num_bits;
    while (remaining > 0) {
        size_t byte_idx = br->bit_pos / 8;
        uint8_t bit_in_byte = br->bit_pos % 8;
        uint8_t bits_avail_in_byte = 8 - bit_in_byte;

        uint8_t bits_to_read = (remaining < bits_avail_in_byte) ? (uint8_t)remaining : bits_avail_in_byte;
        uint8_t shift = bits_avail_in_byte - bits_to_read;
        uint8_t mask = (1U << bits_to_read) - 1U;
        uint8_t chunk = (br->buffer[byte_idx] >> shift) & mask;

        result = (result << bits_to_read) | chunk;
        br->bit_pos += bits_to_read;
        remaining -= bits_to_read;
    }
    *out_val = result;
    return true;
}

/* Читання 1 біта */
bool bit_reader_get_bit(BitReader *br, bool *out_bit) {
    uint32_t val = 0;
    if (!bit_reader_get_bits(br, 1, &val)) return false;
    *out_bit = (val != 0);
    return true;
}

/* Читання обмеженого цілого числа [lb .. ub] */
bool bit_reader_get_constrained_int(BitReader *br, int64_t lb, int64_t ub, int64_t *out_val) {
    uint64_t range = (uint64_t)(ub - lb + 1);
    if (range == 1) {
        *out_val = lb;
        return true;
    }

    uint8_t bits = 0;
    uint64_t temp = range - 1;
    while (temp > 0) {
        bits++;
        temp >>= 1;
    }

    if (bits <= 32) {
        uint32_t raw = 0;
        if (!bit_reader_get_bits(br, bits, &raw)) return false;
        *out_val = lb + (int64_t)raw;
        return (*out_val <= ub);
    } else {
        uint8_t high_bits = bits - 32;
        uint32_t raw_high = 0, raw_low = 0;
        if (!bit_reader_get_bits(br, high_bits, &raw_high)) return false;
        if (!bit_reader_get_bits(br, 32, &raw_low)) return false;
        uint64_t raw = (((uint64_t)raw_high) << 32) | raw_low;
        *out_val = lb + (int64_t)raw;
        return (*out_val <= ub);
    }
}

/* Пропуск вирівнювання на межу октету */
void bit_reader_align_to_byte(BitReader *br) {
    size_t rem = br->bit_pos % 8;
    if (rem != 0) {
        br->bit_pos += (8 - rem);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <expected>
#include <format>
#include <string_view>
#include <algorithm>

enum class BitError {
    BufferOverflow,
    UnexpectedEndOfStream,
    InvalidRange,
    ValueOutOfRange
};

class BitWriter {
public:
    explicit BitWriter(std::span<uint8_t> buffer) : buffer_(buffer), bit_pos_(0) {
        std::fill(buffer_.begin(), buffer_.end(), uint8_t{0});
    }

    [[nodiscard]] std::expected<void, BitError> put_bits(uint32_t value, uint8_t num_bits) {
        if (num_bits == 0) return {};
        if (num_bits > 32) return std::unexpected(BitError::InvalidRange);
        if ((bit_pos_ + num_bits) > (buffer_.size() * 8)) {
            return std::unexpected(BitError::BufferOverflow);
        }

        if (num_bits < 32) {
            value &= (1U << num_bits) - 1U;
        }

        int remaining = num_bits;
        while (remaining > 0) {
            size_t byte_idx = bit_pos_ / 8;
            uint8_t bit_in_byte = bit_pos_ % 8;
            uint8_t bits_free_in_byte = 8 - bit_in_byte;

            uint8_t bits_to_write = std::min<uint8_t>(remaining, bits_free_in_byte);
            uint8_t shift = remaining - bits_to_write;
            uint8_t chunk = static_cast<uint8_t>((value >> shift) & ((1U << bits_to_write) - 1U));

            buffer_[byte_idx] |= static_cast<uint8_t>(chunk << (bits_free_in_byte - bits_to_write));
            bit_pos_ += bits_to_write;
            remaining -= bits_to_write;
        }
        return {};
    }

    [[nodiscard]] std::expected<void, BitError> put_bit(bool bit) {
        return put_bits(bit ? 1U : 0U, 1);
    }

    [[nodiscard]] std::expected<void, BitError> put_constrained_int(int64_t val, int64_t lb, int64_t ub) {
        if (val < lb || val > ub) return std::unexpected(BitError::ValueOutOfRange);
        uint64_t range = static_cast<uint64_t>(ub - lb + 1);
        if (range == 1) return {};

        uint8_t bits = 0;
        uint64_t temp = range - 1;
        while (temp > 0) {
            bits++;
            temp >>= 1;
        }

        uint64_t offset = static_cast<uint64_t>(val - lb);
        if (bits <= 32) {
            return put_bits(static_cast<uint32_t>(offset), bits);
        } else {
            uint8_t high_bits = bits - 32;
            auto res = put_bits(static_cast<uint32_t>(offset >> 32), high_bits);
            if (!res) return res;
            return put_bits(static_cast<uint32_t>(offset & 0xFFFFFFFFU), 32);
        }
    }

    void align_to_byte() noexcept {
        size_t rem = bit_pos_ % 8;
        if (rem != 0) {
            bit_pos_ += (8 - rem);
        }
    }

    [[nodiscard]] size_t bit_position() const noexcept { return bit_pos_; }
    [[nodiscard]] size_t byte_length() const noexcept { return (bit_pos_ + 7) / 8; }

private:
    std::span<uint8_t> buffer_;
    size_t bit_pos_;
};

class BitReader {
public:
    explicit BitReader(std::span<const uint8_t> buffer)
        : buffer_(buffer), total_bits_(buffer.size() * 8), bit_pos_(0) {}

    [[nodiscard]] std::expected<uint32_t, BitError> get_bits(uint8_t num_bits) {
        if (num_bits == 0) return 0;
        if (num_bits > 32) return std::unexpected(BitError::InvalidRange);
        if (bit_pos_ + num_bits > total_bits_) {
            return std::unexpected(BitError::UnexpectedEndOfStream);
        }

        uint32_t result = 0;
        int remaining = num_bits;
        while (remaining > 0) {
            size_t byte_idx = bit_pos_ / 8;
            uint8_t bit_in_byte = bit_pos_ % 8;
            uint8_t bits_avail = 8 - bit_in_byte;

            uint8_t bits_to_read = std::min<uint8_t>(remaining, bits_avail);
            uint8_t shift = bits_avail - bits_to_read;
            uint8_t mask = (1U << bits_to_read) - 1U;
            uint8_t chunk = (buffer_[byte_idx] >> shift) & mask;

            result = (result << bits_to_read) | chunk;
            bit_pos_ += bits_to_read;
            remaining -= bits_to_read;
        }
        return result;
    }

    [[nodiscard]] std::expected<bool, BitError> get_bit() {
        auto res = get_bits(1);
        if (!res) return std::unexpected(res.error());
        return (*res != 0);
    }

    [[nodiscard]] std::expected<int64_t, BitError> get_constrained_int(int64_t lb, int64_t ub) {
        uint64_t range = static_cast<uint64_t>(ub - lb + 1);
        if (range == 1) return lb;

        uint8_t bits = 0;
        uint64_t temp = range - 1;
        while (temp > 0) {
            bits++;
            temp >>= 1;
        }

        if (bits <= 32) {
            auto raw = get_bits(bits);
            if (!raw) return std::unexpected(raw.error());
            int64_val = lb + static_cast<int64_t>(*raw);
            if (int64_val > ub) return std::unexpected(BitError::ValueOutOfRange);
            return int64_val;
        } else {
            uint8_t high_bits = bits - 32;
            auto raw_high = get_bits(high_bits);
            if (!raw_high) return std::unexpected(raw_high.error());
            auto raw_low = get_bits(32);
            if (!raw_low) return std::unexpected(raw_low.error());
            uint64_t raw = (static_cast<uint64_t>(*raw_high) << 32) | *raw_low;
            int64_t val = lb + static_cast<int64_t>(raw);
            if (val > ub) return std::unexpected(BitError::ValueOutOfRange);
            return val;
        }
    }

    void align_to_byte() noexcept {
        size_t rem = bit_pos_ % 8;
        if (rem != 0) {
            bit_pos_ += (8 - rem);
        }
    }

    [[nodiscard]] size_t bit_position() const noexcept { return bit_pos_; }

private:
    std::span<const uint8_t> buffer_;
    size_t total_bits_;
    size_t bit_pos_;
};
```
:::

### Кодування та декодування PDU: RRCConnectionRequest

Розглянемо практичний випадок: термінал користувача (смартфон LTE/5G) надсилає на базову станцію eNodeB запит на встановлення радіоз'єднання `RRCConnectionRequest` (3GPP TS 36.331).

Схема повідомлення в ASN.1 містить вибір типу ідентифікатора, причину дзвінка та службовий біт:

```asn1
RRCConnectionRequest ::= SEQUENCE {
    criticalExtensions CHOICE {
        rrcConnectionRequest-r8 SEQUENCE {
            ue-Identity         CHOICE {
                s-TMSI          SEQUENCE {
                    mmec        INTEGER (0..255),       -- 8 бітів
                    m-TMSI      INTEGER (0..4294967295) -- 32 біти
                },
                randomValue     BIT STRING (SIZE (40))
            },
            establishmentCause  ENUMERATED {
                emergency, highPriorityAccess, mt-Access,
                mo-Signalling, mo-Data, delayTolerant-v1020,
                mo-VoiceCall-v1280, spare1              -- 8 значень -> 3 біти
            },
            spare               BIT STRING (SIZE (1))   -- 1 біт
        },
        criticalExtensionsFuture CHOICE { ... }
    }
}
```

Нижче реалізовано повний серіалізатор і десеріалізатор для цього протокольного блоку даних (PDU):

:::tabs
```c
/* Структура повідомлення */
typedef struct {
    uint8_t mmec;             /* 0..255 */
    uint32_t m_tmsi;          /* 32 біти */
    uint8_t establishment_cause; /* 0..7 */
    bool spare_bit;
} RRCConnectionRequest_r8;

/* Кодування повідомлення у буфер */
bool encode_rrc_connection_request(const RRCConnectionRequest_r8 *msg, uint8_t *out_buf, size_t cap, size_t *out_len) {
    BitWriter bw;
    bit_writer_init(&bw, out_buf, cap);

    /* 1. criticalExtensions: CHOICE index 0 (rrcConnectionRequest-r8 з 2 варіантів) -> 1 біт */
    if (!bit_writer_put_bits(&bw, 0, 1)) return false;

    /* 2. ue-Identity: CHOICE index 0 (s-TMSI з 2 варіантів: s-TMSI=0, randomValue=1) -> 1 біт */
    if (!bit_writer_put_bits(&bw, 0, 1)) return false;

    /* 3. s-TMSI.mmec: INTEGER (0..255) -> 8 бітів */
    if (!bit_writer_put_constrained_int(&bw, msg->mmec, 0, 255)) return false;

    /* 4. s-TMSI.m-TMSI: INTEGER (0..4294967295) -> 32 біти */
    if (!bit_writer_put_constrained_int(&bw, msg->m_tmsi, 0, 4294967295LL)) return false;

    /* 5. establishmentCause: ENUMERATED (8 значень -> 0..7) -> 3 біти */
    if (!bit_writer_put_constrained_int(&bw, msg->establishment_cause, 0, 7)) return false;

    /* 6. spare: BIT STRING SIZE(1) -> 1 біт */
    if (!bit_writer_put_bit(&bw, msg->spare_bit)) return false;

    /* Разом записано: 1 + 1 + 8 + 32 + 3 + 1 = 46 бітів */
    *out_len = bit_writer_get_length_bytes(&bw);
    return true;
}

/* Декодування повідомлення з буфера */
bool decode_rrc_connection_request(const uint8_t *in_buf, size_t len, RRCConnectionRequest_r8 *out_msg) {
    BitReader br;
    bit_reader_init(&br, in_buf, len);

    uint32_t crit_choice = 0;
    if (!bit_reader_get_bits(&br, 1, &crit_choice)) return false;
    if (crit_choice != 0) return false; /* Підтримуємо тільки r8 */

    uint32_t ue_id_choice = 0;
    if (!bit_reader_get_bits(&br, 1, &ue_id_choice)) return false;
    if (ue_id_choice != 0) return false; /* s-TMSI */

    int64_t mmec_val = 0;
    if (!bit_reader_get_constrained_int(&br, 0, 255, &mmec_val)) return false;
    out_msg->mmec = (uint8_t)mmec_val;

    int64_t m_tmsi_val = 0;
    if (!bit_reader_get_constrained_int(&br, 0, 4294967295LL, &m_tmsi_val)) return false;
    out_msg->m_tmsi = (uint32_t)m_tmsi_val;

    int64_t cause_val = 0;
    if (!bit_reader_get_constrained_int(&br, 0, 7, &cause_val)) return false;
    out_msg->establishment_cause = (uint8_t)cause_val;

    if (!bit_reader_get_bit(&br, &out_msg->spare_bit)) return false;

    return true;
}

int main(void) {
    uint8_t packet[16];
    size_t packet_len = 0;

    RRCConnectionRequest_r8 tx_msg = {
        .mmec = 0xE8,               /* Код MME = 232 */
        .m_tmsi = 0x3C4D5E6F,        /* M-TMSI абонента */
        .establishment_cause = 4,    /* mo-Data */
        .spare_bit = false
    };

    if (encode_rrc_connection_request(&tx_msg, packet, sizeof(packet), &packet_len)) {
        printf("Закодовано успішно! Довжина: %zu байтів (46 корисних бітів)\nHex дамп: ", packet_len);
        for (size_t i = 0; i < packet_len; i++) {
            printf("%02X ", packet[i]);
        }
        printf("\n");
    }

    RRCConnectionRequest_r8 rx_msg;
    if (decode_rrc_connection_request(packet, packet_len, &rx_msg)) {
        printf("Декодовано: MMEC=0x%02X, M-TMSI=0x%08X, Cause=%u, Spare=%d\n",
               rx_msg.mmec, rx_msg.m_tmsi, rx_msg.establishment_cause, rx_msg.spare_bit);
    }
    return 0;
}
```
```cpp
struct RRCConnectionRequest_r8 {
    uint8_t mmec;
    uint32_t m_tmsi;
    uint8_t establishment_cause;
    bool spare_bit;
};

[[nodiscard]] std::expected<size_t, BitError> encode_rrc(const RRCConnectionRequest_r8& msg, std::span<uint8_t> out_buf) {
    BitWriter bw(out_buf);

    if (auto r = bw.put_bits(0, 1); !r) return std::unexpected(r.error());
    if (auto r = bw.put_bits(0, 1); !r) return std::unexpected(r.error());
    if (auto r = bw.put_constrained_int(msg.mmec, 0, 255); !r) return std::unexpected(r.error());
    if (auto r = bw.put_constrained_int(msg.m_tmsi, 0, 4294967295LL); !r) return std::unexpected(r.error());
    if (auto r = bw.put_constrained_int(msg.establishment_cause, 0, 7); !r) return std::unexpected(r.error());
    if (auto r = bw.put_bit(msg.spare_bit); !r) return std::unexpected(r.error());

    return bw.byte_length();
}

[[nodiscard]] std::expected<RRCConnectionRequest_r8, BitError> decode_rrc(std::span<const uint8_t> in_buf) {
    BitReader br(in_buf);
    RRCConnectionRequest_r8 msg{};

    auto crit_choice = br.get_bits(1);
    if (!crit_choice || *crit_choice != 0) return std::unexpected(BitError::InvalidRange);

    auto ue_id_choice = br.get_bits(1);
    if (!ue_id_choice || *ue_id_choice != 0) return std::unexpected(BitError::InvalidRange);

    auto mmec = br.get_constrained_int(0, 255);
    if (!mmec) return std::unexpected(mmec.error());
    msg.mmec = static_cast<uint8_t>(*mmec);

    auto m_tmsi = br.get_constrained_int(0, 4294967295LL);
    if (!m_tmsi) return std::unexpected(m_tmsi.error());
    msg.m_tmsi = static_cast<uint32_t>(*m_tmsi);

    auto cause = br.get_constrained_int(0, 7);
    if (!cause) return std::unexpected(cause.error());
    msg.establishment_cause = static_cast<uint8_t>(*cause);

    auto spare = br.get_bit();
    if (!spare) return std::unexpected(spare.error());
    msg.spare_bit = *spare;

    return msg;
}

int main() {
    std::vector<uint8_t> buffer(16, 0);
    RRCConnectionRequest_r8 tx_msg{
        .mmec = 0xE8,
        .m_tmsi = 0x3C4D5E6F,
        .establishment_cause = 4,
        .spare_bit = false
    };

    auto enc_res = encode_rrc(tx_msg, buffer);
    if (enc_res) {
        size_t len = *enc_res;
        std::cout << std::format("Закодовано успішно! Довжина: {} байтів\nHex дамп: ", len);
        for (size_t i = 0; i < len; ++i) {
            std::cout << std::format("{:02X} ", buffer[i]);
        }
        std::cout << "\n";

        auto dec_res = decode_rrc(std::span(buffer.data(), len));
        if (dec_res) {
            const auto& rx = *dec_res;
            std::cout << std::format("Декодовано: MMEC=0x{:02X}, M-TMSI=0x{:08X}, Cause={}, Spare={}\n",
                                     rx.mmec, rx.m_tmsi, rx.establishment_cause, rx.spare_bit);
        }
    }
    return 0;
}
```
:::

### Покроковий бітовий аналіз результату

Подивимося, як сформувався закодований масив байтів:
* `criticalExtensions` = `0` (1 біт: `0`)
* `ue-Identity` = `0` (1 біт: `0`)
* `mmec = 0xE8 = 11101000₂` (8 бітів)
* `m-TMSI = 0x3C4D5E6F = 00111100 01001101 01011110 01101111₂` (32 біти)
* `establishmentCause = 4 = 100₂` (3 біти)
* `spare = 0` (1 біт)

Зберемо весь бітовий ланцюжок:
```
0 0 11101000 00111100 01001101 01011110 01101111 100 0
```

Розбиваємо цей 46-бітовий потік по 8 бітів на байти:
```
Байт 0: 0 0 111010  (0x3A)
Байт 1: 00 001111   (0x0F)
Байт 2: 00 010011   (0x13)
Байт 3: 01 010111   (0x57)
Байт 4: 10 011011   (0x9B)
Байт 5: 11 100 0 00 (0xE0) -- останні 2 нулі є паддінгом PDU до межі октету
```

Усе повідомлення, що містить повний 40-бітовий ідентифікатор мобільного термінала, причину виклику та службові прапорці, зайняло рівно **6 байтів**. Для порівняння, аналогічна структура у JSON зайняла б понад 110 байтів, а в Protobuf — 18 байтів.

### Робота з преамбулами опціональних полів (OPTIONAL mask)

У складних структурах `SEQUENCE` поля можуть позначатися модифікатором `OPTIONAL` або `DEFAULT`. Для таких структур стандарт ITU-T X.691 вимагає генерувати на самому початку структури компактну бітову маску наявності (англ. *presence bitmask*).

Якщо структура має `N` опціональних полів у базовому корені, маска займає рівно `N` бітів. Кожен біт відповідає одному опціональному полю у порядку його появи в тексті схеми ASN.1:
* Біт `1` означає, що поле присутнє в повідомленні, і його закодовані біти слідуватимуть у відповідній позиції потоку.
* Біт `0` означає, що поле пропущено, і в бітовому потоці для нього не виділяється жодного біта.

Наприклад, якщо структура містить 4 опціональних поля `[a, b, c, d]`, і присутні лише поля `a` та `c`, преамбула записується як 4 біти `1010₂`. Декодер спочатку читає 4 біти маски, а потім послідовно зчитує значення поля `a`, пропускає декодування `b`, зчитує `c` і пропускає `d`.

### Кодування масивів однотипних елементів (SEQUENCE OF)

Конструкція `SEQUENCE OF Type` представляє динамічний або статичний вектор елементів одного типу.

Правила кодування масиву у бітовому потоці UPER:
1. **Префікс кількості елементів:** Якщо розмір масиву обмежено діапазоном `SIZE(min..max)`, кількість елементів `count` кодується як ціле число `count - min` довжиною `ceil(log2(max - min + 1))` бітів. Якщо `min == max`, префікс довжини відсутній взагалі (`0` бітів).
2. **Послідовний запис елементів:** Кожен елемент масиву серіалізується безпосередньо за попереднім, утворюючи суцільний бітовий масив без проміжків і роздільників.

Якщо масив містить 4 елементи типу `INTEGER (0..15)` (кожен по 4 біти), і розмір масиву фіксований `SIZE(4)`, усе поле масиву займе рівно `4 · 4 = 16` бітів (2 байти), не витративши жодного біта на лічильники довжини та індекси.

### Реалізація рядків з обмеженим алфавітом (Permitted Alphabet)

Коли схема ASN.1 обмежує допустимі символи текстового поля конструкцією `FROM (...)`, пряме кодування кожного символу 8-бітовим кодом ASCII є неприпустимим марнотратством. Натомість реалізується таблиця перекодування:

1. **Етап ініціалізації:** Будується впорядкована таблиця дозволених символів `char_table`. Наприклад, для шістнадцяткового рядка `FROM ("0".."9" | "A".."F")` таблиця містить 16 елементів: від `0` до `F`.
2. **Пряме відображення (Символ → Індекс):** Для кожного символу вихідного рядка виконується швидкий пошук його індексу в таблиці (через прямий масив адресації `uint8_t ascii_to_index[256]`). Отриманий індекс `0..15` записується у бітовий потік рівно 4 бітами за допомогою `bit_writer_put_bits(bw, index, 4)`.
3. **Зворотне відображення (Індекс → Символ):** Декодер вичитує 4 біти з потоку та відновлює оригінальний ASCII-символ простим доступом до масиву `char_table[index]`.

Такий алгоритм повністю виключає повільні рядкові маніпуляції та скорочує обсяг текстових полів рівно вдвічі без жодних сторонніх бібліотек компресії.

### Реалізація розширень і відкритих типів (Open Type)

Коли в схемі присутній маркер розширення `...`, правила UPER зобов'язують підтримувати механізм відкритого типу (англ. *Open Type*). Відкритий тип є двійковим конвертом, який дозволяє старому програмному коду безпечно перестрибувати через поля невідомого формату.

Алгоритм кодування відкритого типу:
1. Значення розширення спочатку серіалізується в окремий тимчасовий бітовий буфер.
2. Якщо довжина закодованого фрагмента не кратна 8, вона доповнюється нулями до повної кількості октетних байтів `L`.
3. В основний потік записується детермінант довжини `L` (у байтах), після якого копіюються всі `L` байтів закодованого відкритого типу.

Коли старий декодер зустрічає біт розширення `1` і невідомий індекс поля, він зчитує детермінант довжини `L` і просто пропускає `L` байтів за допомогою операції зсуву покажчика. Це гарантує, що наступні повідомлення або вкладені контейнери будуть декодовані без жодного зсуву бітової синхронізації.

### Оптимізація продуктивності: регістровий акумулятор бітів та інструкції BMI2

У наведеній вище базовій реалізації запис і читання виконуються побайтово в циклі `while`. Для вбудованих модемів і базових станцій 5G, які обробляють мільйони сигнальних пакетів на секунду, цей алгоритм можна радикально прискорити за допомогою 64-бітового регістрового акумулятора (англ. *64-bit Barrel Shifter Accumulator*).

Замість того щоб оновлювати оперативну пам'ять на кожному бітовому полі, енкодер накопичує біти у 64-бітовому беззнаковому регістрі `uint64_t accumulator`:
* При виклику `put_bits(val, n)` нове значення додається до акумулятора простим зсувом: `accumulator = (accumulator << n) | val`, а лічильник бітів збільшується: `acc_bits += n`.
* Щойно `acc_bits >= 32`, старші 32 біти скидаються в основний буфер пам'яті однією апаратною інструкцією запису 32-бітового слова (`STORE` з перетворенням порядку байтів через інструкцію `bswap` або `__builtin_bswap32`), а лічильник зменшується на 32.

На сучасних процесорах архітектури x86_64 із підтримкою розширення інструкцій BMI2 (Bit Manipulation Instruction Set 2) операції вилучення та розміщення нерівномірних бітових масок можуть виконуватися за один такт апаратними інструкціями `PDEP` (Parallel Bits Deposit) та `PEXT` (Parallel Bits Extract). Це дозволяє процесорам виконувати бітову десеріалізацію на швидкості пам'яті L1-кешу без жодного умовного переходу.

### Генератори коду проти ручної реалізації

У масштабних телекомунікаційних проєктах (наприклад, реалізації повного стека 3GPP LTE або 5G NR, що налічує понад 400 окремих повідомлень RRC та NGAP) писати бітові пакувальники вручну недоцільно через колосальний обсяг роботи та ризик людської помилки в розрахунку бітових зсувів.

У промисловій розробці застосовують спеціалізовані компілятори ASN.1:
1. **Відкритий компілятор `asn1c` (Лев Валкін):** Приймає на вхід файл схеми `.asn` і транслює його у набір C-файлів і заголовків (`.c` / `.h`), що містять готові структури та дескриптори типів `asn_TYPE_descriptor_t`. Декодування повідомлення виконується єдиним універсальним викликом `uper_decode_complete(&asn_DEF_RRCConnectionRequest, ...)` або `aper_decode(...)`.
2. **Комерційні компілятори (OSS Nokalva, Marben):** Генерують надшвидкий прямий C++ код без використання важких рекурсивних таблиць дескрипторів, що дає прискорення серіалізації у 3–5 разів порівняно з `asn1c`.

Ручна реалізація бітового читача й записувача, наведена в цій статті, застосовується там, де тягнути важкий кодогенератор недоцільно: у мікроконтролерах із суворим лімітом Flash-пам'яті (до 64 КБ), у високочастотних модулях SDR (Software Defined Radio) або в ізольованих інструментах інжекції тестових сигнальних пакетів.

### Фазинг та безпека бітових парсерів

Оскільки бітовий декодер працює безпосередньо з вхідними пакетами, отриманими з відкритого радіоефіру, він є першою лінією оборони від кібератак. Історично саме декодери ASN.1 (через високу складність вкладених структур) ставали джерелом критичних вразливостей переповнення буфера (Buffer Overflow) та відмови в обслуговуванні (DoS).

Головні правила безпечної реалізації декодерів:
1. **Сувора перевірка виходу за межі:** Кожна функція читання (`get_bits`, `get_constrained_int`) зобов'язана перед зчитуванням перевіряти інваріант `bit_pos + num_bits <= total_bits`. У нашому C++ класі `BitReader` це реалізовано поверненням `std::unexpected(BitError::UnexpectedEndOfStream)`.
2. **Перевірка розкодованого значення на діапазон:** Якщо зловмисник передає спотворене бітове поле, значення якого перевищує верхню межу `ub`, декодер повинен негайно перервати розбір і повернути `ValueOutOfRange`.
3. **Автоматизований фазинг:** Усі бітові розбирачі перед випуском у реліз проходять безперервне тестування за допомогою фазерів `LLVM libFuzzer` та `AFL++`. Фазер генерує мільйони спотворених бітових послідовностей на секунду, перевіряючи, що парсер ніколи не здійснює несанкціонованого звернення до пам'яті (Out-of-Bounds Read/Write) та не зациклюється на фрагментованих довжинах.

### Простеження трафіку у сокетах Linux та відкритих стеках

При тестуванні сигнальних протоколів на практиці розробники взаємодіють з відкритими стеками стільникового зв'язку, такими як OpenAirInterface (OAI) або srsRAN. У цих системах взаємодія між базовою станцією gNodeB та ядром мережі 5G Core відбувається через протокол SCTP (Stream Control Transmission Protocol) поверх звичайних мережевих інтерфейсів Linux.

Для перехоплення сигнальних пакетів використовують стандартну утиліту `tcpdump`:
* Захоплення трафіку NGAP (порт SCTP 38412): `tcpdump -i any -w ngap_trace.pcap "sctp port 38412"`.
* Захоплення трафіку S1AP LTE (порт SCTP 36412): `tcpdump -i any -w s1ap_trace.pcap "sctp port 36412"`.

Отриманий файл `.pcap` відкривають у Wireshark, який автоматично зіставляє бітові зсуви з офіційними ASN.1 специфікаціями 3GPP, дозволяючи бачити стан кожного бітового прапорця та ідентифікатора абонента в реальному часі. Для індивідуального розбору сирих шістнадцяткових дампів (наприклад, витягнутих із діагностичного порту модема Qualcomm через протокол QXDM) застосовують утиліту `text2pcap` із зазначенням типу інкапсуляції канального рівня, що дозволяє миттєво візуалізувати структуру UPER у графічному інтерфейсі.

### Типові пастки реалізації та налагодження

Під час написання бітових енкодерів розробники найчастіше стикаються з чотирма критичними проблемами:

1. **Зсув на 32 біти в C/C++:**
   Операція `1U << 32` в стандартах C та C++ є **невизначеною поведінкою** (Undefined Behavior) на процесорах архітектури x86/ARM, якщо тип операнда є 32-бітовим. На рівні асемблера інструкція зсуву використовує лише молодші 5 бітів лічильника (`shift & 0x1F`), тому зсув на 32 перетворюється на зсув на 0, призводячи до запису `0` замість повної маски `0xFFFFFFFF`. У функції `put_bits` ми явно ізолюємо випадок `num_bits == 32`, уникаючи помилкового зсуву.

2. **Накопичення зміщення (Off-by-One Bit Error):**
   Якщо хоча б одне поле схеми декодовано з помилкою на 1 біт (наприклад, помилково прочитано 4 біти замість 3), усі наступні поля повідомлення виявляються зсунутими на 1 біт. Декодер не впаде одразу, а прочитає абсолютно валідні на вигляд, але хибні за змістом значення (спотворені координати або неіснуючі причини відключення). Для налагодження таких проблем у тестових стендах формують детальний лог зі значенням `bit_pos` перед кожним полем.

3. **Коректність очищення паддінг-бітів:**
   Стандарт ITU-T X.691 вимагає, щоб усі кінцеві невикористані біти в останньому байті PDU були заповнені нулями (`0`). Якщо буфер не був попередньо занулений функцією `memset` або конструктором `BitWriter`, там залишається випадкове «сміття» з оперативної пам'яті. Суворі перевірки безпеки на базовій станції відкидають такі пакети через порушення канонічності кодування.

4. **Розбіжність між Little-Endian та Network Byte Order:**
   Більшість процесорів загального призначення (x86_64, ARM64) працюють у режимі Little-Endian (молодший байт за молодшою адресою). При зчитуванні багатобайтових чисел (наприклад, 32-бітового `m-TMSI`) наївний каст `*(uint32_t*)(buf)` прочитає байти у зворотному порядку, перетворивши `0x3C4D5E6F` на `0x6F5E4D3C`. Побітовий зсув `result = (result << 8) | byte` у `BitReader` гарантує абсолютну переносність коду незалежно від апаратної архітектури платформи.
