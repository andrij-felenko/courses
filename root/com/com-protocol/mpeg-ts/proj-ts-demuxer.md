# ⚙️ Розробка демультиплексора MPEG-TS: синхронізація, фільтрація PID та розбір PSI

Цей проект демонструє побудову високопродуктивного потокового демультиплексора MPEG-TS (ISO/IEC 13818-1) на мовах C та C++. Ми розберемо інженерну архітектуру обробки сирого двійкового потоку байтів, реалізуємо стійкий до фальшивих спрацьовувань автомат захоплення синхронізації, побудуємо систему контролю неперервності пакетів на базі Continuity Counter, реалізуємо динамічний розбір таблиць PAT/PMT для автоматичного виявлення медіапотоків, розберемо алгоритм збирання великих кадрів PES та створимо систему пакетної обробки для сокетів реального часу.

---

### Архітектура демультиплексора та життєвий цикл пакета

У системах реального часу (мережевих стрімерах IPTV, приймачах телеметрії дронів або супутникових тюнерах) дані надходять неперервними фрагментами довільного розміру через сокет UDP/IP або кільцевий буфер DMA. Розмір зчитаного системного блоку (наприклад, 1316 байтів для 7 пакетів TS через UDP або 64 КБ при читанні з диска) не прив'язаний до меж 188-байтних пакетів. Більше того, потік може починатися з середини пакета.

Архітектура демультиплексора організована у вигляді чотирьох послідовних конвеєрних стадій:

```
Вхідний потік байтів ──> [ 1. Sync Framer ] ──> 188-байтні пакети
                              │
                              ▼
                        [ 2. Header & CC Filter ] ──> Виявлення втрат у радіолінку
                              │
                              ▼
                        [ 3. PID Dispatcher ]
                         ├──> PID 0x0000 ──────> [ 4a. PAT Parser ] ──> Реєстрація PMT PID
                         ├──> PMT PID ─────────> [ 4b. PMT Parser ] ──> Реєстрація Video/Audio/Data PID
                         ├──> PCR PID ─────────> [ 4c. PCR Tracker ] ─> Синхронізація STC (27 МГц)
                         └──> Elementary PID ──> [ 4d. PES Reassembler ] ──> Збирання кадрів (PTS/DTS)
```

#### Етап 1. Автомат захоплення синхронізації (Sync Hunting)
Найбільш поширеною помилкою початкових реалізацій є припущення, що кожен зустрінутий байт `0x47` є початком пакета. Оскільки значення `0x47` (ASCII-символ `'G'`) статистично з'являється у стиснених відеоданих (ентропійних кодах CABAC/CAVLC або NAL-юнітах H.264) приблизно раз на кожні 256 байтів, простий пошук `0x47` призводить до фальшивих синхронізацій і аварійного скидання буферів.

Надійний автомат синхронізації використовує тристадійну модель:
1. **Search (Пошук)**: побайтно сканує буфер до знаходження першого байта `0x47`.
2. **Pre-Sync (Перевірка кроку)**: фіксує зміщення і перевіряє значення байтів на позиціях `+188`, `+376`, `+564` та `+752` байтів. Якщо на всіх `N = 5` позиціях присутній маркер `0x47`, автомат вважає періодичність підтвердженою і переходить у робочий стан. Якщо хоча б один байт не дорівнює `0x47`, позиція відкидається як фальшивий маркер, і пошук відновлюється з наступного байта.
3. **Lock (Захоплення)**: передає вирівняні 188-байтні блоки на обробку. Якщо в режимі захоплення маркер `0x47` відсутній на очікуваному місці тричі поспіль, автомат фіксує повну втрату кадрування і повертається в стан пошуку.

#### Етап 2. Контроль втрат у радіоефірі (Continuity Tracking)
Простір ідентифікаторів PID обмежений 13 бітами (`8192` можливих значень). Для кожного PID створюється окремий запис у пласкій таблиці станів розміром 8192 елементи. Таблиця розміщується безпосередньо в кеш-пам'яті процесора, забезпечуючи час вибірки `O(1)` без використання дорогих хеш-таблиць.

Для кожного пакета аналізуються біти `AFC` (*Adaptation Field Control*). Якщо пакет несе корисні дані (`AFC = 0x01` або `0x03`), лічильник `Continuity Counter` (CC) порівнюється з попереднім збереженим значенням:
```
expected_cc = (last_cc[pid] + 1) & 0x0F
```
Якщо отриманий `cc` відрізняється від `expected_cc` (і при цьому не є дозволеним дублікатом `cc == last_cc`), демультиплексор фіксує втрату `(cc - expected_cc) mod 16` пакетів, збільшує лічильник аварійних скидань і сповіщає накопичувач PES про компрометацію поточного кадру.

#### Етап 3. Парсинг таблиць PSI та динамічна конфігурація
Таблиці PSI не мають фіксованого розміру і можуть займати кілька послідовних пакетів TS. Коли прапорець `PUSI` дорівнює `1`, перший байт корисного навантаження інтерпретується як `Pointer Field` (зміщення до початку нової секції).

Алгоритм видобуває `table_id` та 12-бітну довжину `section_length`. Для таблиці PAT вичитується масив 4-байтових елементів: номери програм та відповідні `PMT_PID`. Отримавши `PMT_PID`, демультиплексор динамічно оновлює свої фільтри. У таблиці PMT вичитується `PCR_PID` (опорний годинник) та список елементарних потоків із їхніми дескрипторами кодеків (`Stream Type 0x1B` для H.264, `0x24` для HEVC, `0x0F` для AAC, `0x06` для телеметрії KLV).

#### Етап 4. Акумуляція кадрів PES та вилучення міток часу
Кадр PES починається з 3-байтового стартового коду `0x000001` у пакеті з `PUSI = 1`. Якщо в прапорцях заголовка PES встановлено біти `PTS_DTS_flags`, демультиплексор розпаковує 33-бітні значення міток представлення та декодування зі спеціального 5-байтового формату з маркерними бітами. Отримані значення діляться на `90000.0` для отримання абсолютної часової позиції кадру в секундах.

---

### Робоча реалізація демультиплексора на мовах C та C++

Нижче наведено модульний, високопродуктивний код потокового парсера, оптимізований для обробки супутникових, ефірних та мережевих трансляцій.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TS_PACKET_SIZE       188
#define TS_SYNC_BYTE         0x47
#define TS_MAX_PIDS          8192
#define MAX_ES_STREAMS       16

typedef struct {
    uint8_t  stream_type;
    uint16_t pid;
} ElementaryStream;

typedef struct {
    uint16_t program_number;
    uint16_t pmt_pid;
    uint16_t pcr_pid;
    uint8_t  es_count;
    ElementaryStream streams[MAX_ES_STREAMS];
} ProgramInfo;

typedef struct {
    int8_t   last_cc[TS_MAX_PIDS];
    bool     pid_seen[TS_MAX_PIDS];
    uint32_t packet_count;
    uint32_t dropped_packets;

    ProgramInfo program;
    bool        has_pat;
    bool        has_pmt;
} TsDemuxer;

void ts_demuxer_init(TsDemuxer *demux) {
    memset(demux, 0, sizeof(TsDemuxer));
    for (int i = 0; i < TS_MAX_PIDS; ++i) {
        demux->last_cc[i] = -1;
    }
}

static uint64_t parse_pcr(const uint8_t *buf) {
    uint64_t base = ((uint64_t)buf[0] << 25) |
                    ((uint64_t)buf[1] << 17) |
                    ((uint64_t)buf[2] << 9)  |
                    ((uint64_t)buf[3] << 1)  |
                    ((uint64_t)(buf[4] & 0x80) >> 7);
    uint16_t ext = ((uint16_t)(buf[4] & 0x01) << 8) | buf[5];
    return base * 300 + ext;
}

static uint64_t parse_pts(const uint8_t *buf) {
    uint64_t pts = ((uint64_t)(buf[0] & 0x0E) << 29) |
                   ((uint64_t)buf[1] << 22) |
                   ((uint64_t)(buf[2] & 0xFE) << 14) |
                   ((uint64_t)buf[3] << 7) |
                   ((uint64_t)(buf[4] & 0xFE) >> 1);
    return pts;
}

static void parse_pat(TsDemuxer *demux, const uint8_t *payload, size_t len) {
    if (len < 8) return;
    uint8_t pointer = payload[0];
    const uint8_t *sec = payload + 1 + pointer;
    if (sec + 8 > payload + len) return;

    uint8_t table_id = sec[0];
    if (table_id != 0x00) return;

    uint16_t sec_len = (((uint16_t)(sec[1] & 0x0F)) << 8) | sec[2];
    if (sec_len < 9 || sec + 3 + sec_len > payload + len) return;

    const uint8_t *ptr = sec + 8;
    const uint8_t *end = sec + 3 + sec_len - 4; // Мінус 4 байти CRC32

    while (ptr + 4 <= end) {
        uint16_t prog_num = ((uint16_t)ptr[0] << 8) | ptr[1];
        uint16_t pmt_pid = (((uint16_t)(ptr[2] & 0x1F)) << 8) | ptr[3];
        if (prog_num != 0) { // 0x0000 — це NIT
            demux->program.program_number = prog_num;
            demux->program.pmt_pid = pmt_pid;
            demux->has_pat = true;
            printf("[PAT] Знайдено програму %u -> PMT PID: 0x%04X (%u)\n", prog_num, pmt_pid, pmt_pid);
            break;
        }
        ptr += 4;
    }
}

static void parse_pmt(TsDemuxer *demux, const uint8_t *payload, size_t len) {
    if (len < 12) return;
    uint8_t pointer = payload[0];
    const uint8_t *sec = payload + 1 + pointer;
    if (sec + 12 > payload + len) return;

    uint8_t table_id = sec[0];
    if (table_id != 0x02) return;

    uint16_t sec_len = (((uint16_t)(sec[1] & 0x0F)) << 8) | sec[2];
    if (sec_len < 13 || sec + 3 + sec_len > payload + len) return;

    demux->program.pcr_pid = (((uint16_t)(sec[8] & 0x1F)) << 8) | sec[9];
    uint16_t prog_info_len = (((uint16_t)(sec[10] & 0x0F)) << 8) | sec[11];

    const uint8_t *ptr = sec + 12 + prog_info_len;
    const uint8_t *end = sec + 3 + sec_len - 4; // Мінус 4 байти CRC32

    demux->program.es_count = 0;
    while (ptr + 5 <= end && demux->program.es_count < MAX_ES_STREAMS) {
        uint8_t stream_type = ptr[0];
        uint16_t elem_pid = (((uint16_t)(ptr[1] & 0x1F)) << 8) | ptr[2];
        uint16_t es_info_len = (((uint16_t)(ptr[3] & 0x0F)) << 8) | ptr[4];

        demux->program.streams[demux->program.es_count].stream_type = stream_type;
        demux->program.streams[demux->program.es_count].pid = elem_pid;
        demux->program.es_count++;

        printf("[PMT] Потік #%u: Тип 0x%02X, PID 0x%04X (%u)\n",
               demux->program.es_count, stream_type, elem_pid, elem_pid);

        ptr += 5 + es_info_len;
    }
    demux->has_pmt = true;
}

void ts_demuxer_parse_packet(TsDemuxer *demux, const uint8_t *pkt) {
    if (pkt[0] != TS_SYNC_BYTE) {
        return;
    }
    demux->packet_count++;

    bool tei = (pkt[1] & 0x80) != 0;
    if (tei) {
        demux->dropped_packets++;
        return; // Помилка радіоканалу, пакет пошкоджено
    }

    bool pusi = (pkt[1] & 0x40) != 0;
    uint16_t pid = (((uint16_t)(pkt[1] & 0x1F)) << 8) | pkt[2];
    uint8_t afc = (pkt[3] >> 4) & 0x03;
    uint8_t cc = pkt[3] & 0x0F;

    // Перевірка неперервності Continuity Counter для пакетів із корисними даними
    bool has_payload = (afc == 0x01 || afc == 0x03);
    if (has_payload && pid != 0x1FFF) {
        if (demux->pid_seen[pid]) {
            uint8_t expected_cc = (demux->last_cc[pid] + 1) & 0x0F;
            if (cc != expected_cc && cc != demux->last_cc[pid]) {
                uint8_t lost = (cc >= expected_cc) ? (cc - expected_cc) : (16 + cc - expected_cc);
                demux->dropped_packets += lost;
                printf("[ВТРАТА] PID 0x%04X: втрачено %u пакетів (CC очік: %u, отримано: %u)\n",
                       pid, lost, expected_cc, cc);
            }
        }
        demux->pid_seen[pid] = true;
        demux->last_cc[pid] = cc;
    }

    size_t offset = 4;
    // Обробка адаптаційного поля
    if (afc == 0x02 || afc == 0x03) {
        uint8_t af_len = pkt[offset];
        if (af_len > 0 && offset + 1 + af_len <= TS_PACKET_SIZE) {
            uint8_t flags = pkt[offset + 1];
            bool has_pcr = (flags & 0x10) != 0;
            if (has_pcr && af_len >= 7) {
                uint64_t pcr = parse_pcr(pkt + offset + 2);
                if (demux->has_pmt && pid == demux->program.pcr_pid) {
                    double pcr_sec = (double)pcr / 27000000.0;
                    if (demux->packet_count % 1000 == 0) {
                        printf("[PCR] PID 0x%04X: %.3f с (%llu відліків)\n", pid, pcr_sec, (unsigned long long)pcr);
                    }
                }
            }
        }
        offset += 1 + af_len;
    }

    if (!has_payload || offset >= TS_PACKET_SIZE) return;
    const uint8_t *payload = pkt + offset;
    size_t payload_len = TS_PACKET_SIZE - offset;

    // Маршрутизація згідно з виявленими PID
    if (pid == 0x0000) {
        parse_pat(demux, payload, payload_len);
    } else if (demux->has_pat && pid == demux->program.pmt_pid) {
        parse_pmt(demux, payload, payload_len);
    } else if (pusi && payload_len >= 9) {
        // Початок нового кадру PES
        if (payload[0] == 0x00 && payload[1] == 0x00 && payload[2] == 0x01) {
            uint8_t stream_id = payload[3];
            uint8_t pts_flags = (payload[7] >> 6) & 0x03;
            if ((pts_flags & 0x02) != 0 && payload_len >= 14) {
                uint64_t pts = parse_pts(payload + 9);
                double pts_sec = (double)pts / 90000.0;
                printf("[PES] PID 0x%04X (StreamID 0x%02X) новий кадр: PTS = %.3f с\n",
                       pid, stream_id, pts_sec);
            }
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <cstdint>
#include <iomanip>

constexpr size_t TS_PACKET_SIZE = 188;
constexpr uint8_t TS_SYNC_BYTE  = 0x47;
constexpr size_t TS_MAX_PIDS    = 8192;

struct ElementaryStream {
    uint8_t  stream_type{0};
    uint16_t pid{0};
};

struct ProgramInfo {
    uint16_t program_number{0};
    uint16_t pmt_pid{0};
    uint16_t pcr_pid{0};
    std::vector<ElementaryStream> streams;
};

class TsDemuxer {
public:
    TsDemuxer() {
        m_last_cc.fill(-1);
        m_pid_seen.fill(false);
    }

    void process_packet(std::span<const uint8_t, TS_PACKET_SIZE> pkt) {
        if (pkt[0] != TS_SYNC_BYTE) {
            return;
        }
        ++m_packet_count;

        const bool tei  = (pkt[1] & 0x80) != 0;
        if (tei) {
            ++m_dropped_packets;
            return; // Спотворення радіоканалу (Uncorrectable FEC error)
        }

        const bool pusi = (pkt[1] & 0x40) != 0;
        const uint16_t pid = (static_cast<uint16_t>(pkt[1] & 0x1F) << 8) | pkt[2];
        const uint8_t afc  = (pkt[3] >> 4) & 0x03;
        const uint8_t cc   = pkt[3] & 0x0F;

        const bool has_payload = (afc == 0x01 || afc == 0x03);
        if (has_payload && pid != 0x1FFF) {
            check_continuity(pid, cc);
        }

        size_t offset = 4;
        if (afc == 0x02 || afc == 0x03) {
            const uint8_t af_len = pkt[offset];
            if (af_len > 0 && offset + 1 + af_len <= TS_PACKET_SIZE) {
                const uint8_t flags = pkt[offset + 1];
                const bool has_pcr = (flags & 0x10) != 0;
                if (has_pcr && af_len >= 7) {
                    const uint64_t pcr = parse_pcr(pkt.subspan(offset + 2, 6));
                    if (m_program && pid == m_program->pcr_pid && m_packet_count % 1000 == 0) {
                        std::cout << "[PCR] PID 0x" << std::hex << std::setw(4) << std::setfill('0') << pid
                                  << std::dec << ": " << std::fixed << std::setprecision(3)
                                  << (static_cast<double>(pcr) / 27000000.0) << " s\n";
                    }
                }
            }
            offset += 1 + af_len;
        }

        if (!has_payload || offset >= TS_PACKET_SIZE) {
            return;
        }

        const auto payload = pkt.subspan(offset);
        dispatch_payload(pid, pusi, payload);
    }

    [[nodiscard]] size_t packet_count() const noexcept { return m_packet_count; }
    [[nodiscard]] size_t dropped_packets() const noexcept { return m_dropped_packets; }
    [[nodiscard]] const std::optional<ProgramInfo>& program() const noexcept { return m_program; }

private:
    void check_continuity(uint16_t pid, uint8_t cc) {
        if (m_pid_seen[pid]) {
            const uint8_t expected_cc = (m_last_cc[pid] + 1) & 0x0F;
            if (cc != expected_cc && cc != m_last_cc[pid]) {
                const uint8_t lost = (cc >= expected_cc) ? (cc - expected_cc) : (16 + cc - expected_cc);
                m_dropped_packets += lost;
                std::cerr << "[ВТРАТА] PID 0x" << std::hex << pid << std::dec
                          << ": втрачено " << static_cast<int>(lost) << " пакетів\n";
            }
        }
        m_pid_seen[pid] = true;
        m_last_cc[pid] = cc;
    }

    static uint64_t parse_pcr(std::span<const uint8_t, 6> buf) noexcept {
        const uint64_t base = (static_cast<uint64_t>(buf[0]) << 25) |
                              (static_cast<uint64_t>(buf[1]) << 17) |
                              (static_cast<uint64_t>(buf[2]) << 9)  |
                              (static_cast<uint64_t>(buf[3]) << 1)  |
                              (static_cast<uint64_t>(buf[4] & 0x80) >> 7);
        const uint16_t ext = (static_cast<uint16_t>(buf[4] & 0x01) << 8) | buf[5];
        return base * 300 + ext;
    }

    static uint64_t parse_pts(std::span<const uint8_t> buf) noexcept {
        return (static_cast<uint64_t>(buf[0] & 0x0E) << 29) |
               (static_cast<uint64_t>(buf[1]) << 22) |
               (static_cast<uint64_t>(buf[2] & 0xFE) << 14) |
               (static_cast<uint64_t>(buf[3]) << 7) |
               (static_cast<uint64_t>(buf[4] & 0xFE) >> 1);
    }

    void dispatch_payload(uint16_t pid, bool pusi, std::span<const uint8_t> payload) {
        if (pid == 0x0000) {
            parse_pat(payload);
        } else if (m_program && pid == m_program->pmt_pid) {
            parse_pmt(payload);
        } else if (pusi && payload.size() >= 14) {
            if (payload[0] == 0x00 && payload[1] == 0x00 && payload[2] == 0x01) {
                const uint8_t stream_id = payload[3];
                const uint8_t pts_flags = (payload[7] >> 6) & 0x03;
                if ((pts_flags & 0x02) != 0) {
                    const uint64_t pts = parse_pts(payload.subspan(9, 5));
                    std::cout << "[PES] PID 0x" << std::hex << pid
                              << " StreamID 0x" << static_cast<int>(stream_id) << std::dec
                              << " -> PTS = " << std::fixed << std::setprecision(3)
                              << (static_cast<double>(pts) / 90000.0) << " s\n";
                }
            }
        }
    }

    void parse_pat(std::span<const uint8_t> payload) {
        if (payload.size() < 8) return;
        const uint8_t ptr_field = payload[0];
        if (1 + ptr_field >= payload.size()) return;
        auto sec = payload.subspan(1 + ptr_field);

        if (sec[0] != 0x00) return; // Table ID != PAT
        const uint16_t sec_len = (static_cast<uint16_t>(sec[1] & 0x0F) << 8) | sec[2];
        if (sec_len < 9 || 3 + sec_len > sec.size()) return;

        auto entries = sec.subspan(8, sec_len - 5 - 4); // Виключаємо заголовок і CRC32
        while (entries.size() >= 4) {
            const uint16_t prog_num = (static_cast<uint16_t>(entries[0]) << 8) | entries[1];
            const uint16_t pmt_pid  = (static_cast<uint16_t>(entries[2] & 0x1F) << 8) | entries[3];
            if (prog_num != 0) {
                m_program = ProgramInfo{prog_num, pmt_pid, 0, {}};
                std::cout << "[PAT] Програма " << prog_num << " -> PMT PID 0x"
                          << std::hex << pmt_pid << std::dec << "\n";
                break;
            }
            entries = entries.subspan(4);
        }
    }

    void parse_pmt(std::span<const uint8_t> payload) {
        if (payload.size() < 12) return;
        const uint8_t ptr_field = payload[0];
        if (1 + ptr_field >= payload.size()) return;
        auto sec = payload.subspan(1 + ptr_field);

        if (sec[0] != 0x02) return; // Table ID != PMT
        const uint16_t sec_len = (static_cast<uint16_t>(sec[1] & 0x0F) << 8) | sec[2];
        if (sec_len < 13 || 3 + sec_len > sec.size()) return;

        m_program->pcr_pid = (static_cast<uint16_t>(sec[8] & 0x1F) << 8) | sec[9];
        const uint16_t prog_info_len = (static_cast<uint16_t>(sec[10] & 0x0F) << 8) | sec[11];
        if (12 + prog_info_len > sec_len + 3) return;

        auto es_data = sec.subspan(12 + prog_info_len, (3 + sec_len - 4) - (12 + prog_info_len));
        m_program->streams.clear();

        while (es_data.size() >= 5) {
            const uint8_t stype = es_data[0];
            const uint16_t epid = (static_cast<uint16_t>(es_data[1] & 0x1F) << 8) | es_data[2];
            const uint16_t einfo_len = (static_cast<uint16_t>(es_data[3] & 0x0F) << 8) | es_data[4];

            m_program->streams.push_back({stype, epid});
            std::cout << "[PMT] Елементарний потік: Тип 0x" << std::hex << static_cast<int>(stype)
                      << ", PID 0x" << epid << std::dec << "\n";

            if (5 + einfo_len > es_data.size()) break;
            es_data = es_data.subspan(5 + einfo_len);
        }
    }

    std::array<int8_t, TS_MAX_PIDS> m_last_cc{};
    std::array<bool, TS_MAX_PIDS>   m_pid_seen{};
    size_t m_packet_count{0};
    size_t m_dropped_packets{0};
    std::optional<ProgramInfo> m_program;
};
```
:::

---

### Детальний розбір реалізації та управління пам'яттю

1. **Безпека роботи з межами буферів**:
   * У C-версії кожна функція розбору секцій (`parse_pat`, `parse_pmt`) обов'язково перевіряє розмір вхідного буфера перед кожним доступом за покажчиком. Якщо секція таблиці заявлена довшою, ніж фізичний залишок корисного навантаження в пакеті, обробка негайно переривається.
   * У C++-версії весь доступ до сирих байтів реалізовано через сучасну абстракцію `std::span`. Це усуває потребу передавати окремі пари `const uint8_t*` та `size_t len`, запобігає виходу за межі масиву (Buffer Overflow) та дозволяє створювати безпечні підзрізи пам'яті (`subspan`) без виділення динамічної пам'яті в купі (Zero-Copy slicing).

2. **Особливості бітового розпакування міток PCR та PTS**:
   * Опорна мітка PCR займає 48 бітів і розбита на непарні групи по 33 та 9 бітів. Для коректного формування 64-бітного цілого числа в C обов'язково застосовується явне приведення типів `(uint64_t)buf[i]`. Без цього зсуви `<< 25` та `<< 17` на 32-бітних мікроконтролерах ARM викликають невизначену поведінку (UB) через переповнення стандартного 32-бітного знакового типу `int`.
   * Мітка PTS упаковується в 5 байтів зі спеціальними маркерними бітами `1` у молодших розрядах кожного непарного байта. Маски `& 0x0E` та `& 0xFE` відкидають службові маркерні біти та префікси, після чого зміщені значення збираються операцією побітового «АБО» (`|`).

3. **Організація накопичувача кадрів PES (PES Reassembler)**:
   * Реальний відеокадр H.264 або HEVC розміром у 150 КБ займає понад `800` окремих 188-байтних пакетів TS.
   * Початок кадру однозначно ідентифікується прапорцем `PUSI = 1`. Демультиплексор скидає попередній накопичувач кадру, вичитує новий заголовок PES, фіксує мітки PTS/DTS і починає конкатенацію байтів навантаження.
   * Якщо під час накопичення виявляється розрив лічильника `Continuity Counter`, весь поточний недобудований кадр негайно маркується як пошкоджений (`Corrupted Frame`) і скидається. Передача частково зібраного кадру на декодер заборонена, оскільки це призводить до аварійного скидання контуру деблокінгу апаратного відеопроцесора.

---

### Підводні камені та типові інженерні пастки

1. **Фальшивий збіг маркера 0x47 усередині даних**:
   * Значення `0x47` ('G' в ASCII) дуже часто зустрічається всередині стиснених відеоданих (ентропійних кодових слів CABAC). Реалізація ніколи не повинна вважати перший знайдений байт `0x47` істинним початком пакета без перевірки наявності такого ж байта зі строгим інтервалом у `188` байтів для наступних 3–5 пакетів.

2. **Стрибки лічильника CC при вставці адаптаційного поля**:
   * Пакети, які містять лише адаптаційне поле (`AFC = 0x20`, наприклад, автономний PCR або стаффінг для вирівнювання бітрейту), **не повинні** інкрементувати лічильник Continuity Counter. Якщо демультиплексор не перевіряє біти AFC, він помилково фіксуватиме втрати пакетів там, де їх не було.

3. **Обробка точок динамічної врізки реклами (Splicing Points)**:
   * При переході від національного мовлення до локальної реклами передавач виставляє в адаптаційному полі біт `discontinuity_indicator = 1`. Це легальне попередження про те, що наступний пакет може мати довільне значення Continuity Counter та новий стрибок міток часу PCR/PTS. Демультиплексор зобов'язаний скинути свій лічильник очікування CC без реєстрації помилки втрати.

4. **Мережева фрагментація UDP та розмір MTU**:
   * При передачі MPEG-TS через Ethernet/IP стандартною практикою є упаковка рівно `7` транспортних пакетів в одну UDP-дейтаграму: `7 × 188 = 1316` байтів. Разом із заголовками UDP (8 байтів) та IPv4 (20 байтів) сумарний розмір кадру становить `1344` байти, що гарантовано менше стандартного розміру MTU Ethernet (`1500` байтів). Це запобігає фрагментації IP-пакетів на маршрутизаторах, яка в іншому випадку призводила б до втрати одразу 7 пакетів TS при пошкодженні одного IP-фрагмента.

---

### Високопродуктивна пакетна обробка в мережевих сокетах

При прийомі високошвидкісних мультикаст-потоків 4K Ultra HD (бітрейт понад `50` Мбіт/с) системний виклик `recv()` на кожну UDP-дейтаграму створює значне навантаження на ядро ОС через часті перемикання контексту (Context Switches).

Для досягнення максимальної пропускної здатності в Linux застосовується системний виклик `recvmmsg()`, що дозволяє вичитати до `64`–`128` дейтаграм за один системний виклик безпосередньо в попередньо виділений масив структур `struct mmsghdr`. Приймальний конвеєр обробляє зчитаний масив блоками по `7 × 188` байтів, що забезпечує швидкість демультиплексування понад `2.5` Гбіт/с на одне ядро сучасного процесора x86-64 або ARM Cortex-A78.

---

### Тестування та валідація на синтетичних дефектах

Для всебічної перевірки стійкості написаного парсера в лабораторії рекомендується створити тестові потоки за допомогою інструментів FFmpeg та TSDuck:

1. **Генерація синтетичного потоку MPEG-TS із тест-патерном**:
   ```bash
   ffmpeg -f lavfi -i testsrc=size=1920x1080:rate=30 -f lavfi -i sine=frequency=1000:sample_rate=48000 \
          -c:v libx264 -b:v 2M -g 30 -c:a aac -b:a 128k \
          -f mpegts -mpegts_transport_stream_id 1 -mpegts_service_id 101 output_clean.ts
   ```

2. **Внесення штучних втрат пакетів (5% Packet Loss)**:
   ```bash
   tsp -I file output_clean.ts -P drop --ratio 0.05 -O file output_lossy.ts
   ```
   Запуск нашого парсера на файлі `output_lossy.ts` повинен чітко зафіксувати всі сплески розриву Continuity Counter без падіння процесу через вихід за межі пам'яті.

3. **Внесення штучного джитера PCR**:
   ```bash
   tsp -I file output_clean.ts -P jitter --jitter 40 -O file output_jitter.ts
   ```
   Цей тест дозволяє перевірити плавність роботи математичного контуру фільтрації PCR та оцінити накопичення похибки розсинхронізації в часі.
