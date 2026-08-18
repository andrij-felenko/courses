# 📋 Специфікація полів TCP SACK та параметрів керування LTE/5G HARQ

Протоколи вибіркового та гібридного автоматичного повтору запиту спираються на стандартизовані формати бітових полів, заголовків, опцій та апаратних дескрипторів.

Нижче наведено вичерпний довідник структур даних, бітових масок та інтерфейсів керування для чотирьох ключових сучасних втілень ARQ:
1. **TCP Selective Acknowledgment (SACK)** на транспортному рівні стека TCP/IP (специфікації RFC 2018 та RFC 2883).
2. **Wi-Fi Block ACK (IEEE 802.11n/ac/ax/be)** на канальному рівні бездротових локальних мереж.
3. **RLC Status PDU та MAC/PHY HARQ Control Information** у стільникових мережах 4G LTE та 5G NR (специфікації 3GPP TS 38.322 та TS 38.212).
4. **QUIC ACK Frames (RFC 9000)** у транспортному протоколі нового покоління.
5. **Програмний інтерфейс сокетів POSIX (Socket API / TCP_INFO)** для моніторингу черг SACK у ядрі.

---

### 1. Формат опцій TCP SACK (RFC 2018, RFC 2883)

У стандартному протоколі TCP підтвердження передаються в основному 20-байтовому заголовку через 32-бітове поле `Acknowledgment Number` (кумулятивний ACK). Для передачі вибіркових підтверджень використовується поле додаткових опцій TCP (англ. *TCP Options*), яке розташовується після основного заголовка.

#### Опція дозволу SACK (SACK-Permitted Option)
Під час встановлення з'єднання (тристороннього рукостискання SYN / SYN-ACK) обидва хости повинні узгодити можливість використання вибіркових підтверджень. Якщо хоча б один бік не надішле цю опцію, використання SACK у цій TCP-сесії заборонено.

```
+---------------+---------------+
|  Kind = 4     |  Length = 2   |
+---------------+---------------+
```
* **Kind (1 байт):** значення `0x04` (ідентифікатор опції SACK-Permitted).
* **Length (1 байт):** значення `0x02` (фіксована довжина опції у байтах).

#### Опція вибіркового підтвердження (SACK Option)
Ця опція додається до звичайних сегментів `ACK`, коли приймач виявляє розрив у прийнятому потоці байтів і зберігає розрізнені неперервні блоки у своєму буфері.

```
+---------------+---------------+
|  Kind = 5     |  Length = Var |
+---------------+---------------+-------------------------------+
|                      Left Edge of 1st Block                   |
+---------------------------------------------------------------+
|                      Right Edge of 1st Block                  |
+---------------------------------------------------------------+
|                                                               |
/            ... Додаткові блоки SACK (2-й, 3-й, 4-й) ...        /
|                                                               |
+---------------------------------------------------------------+
```

* **Kind (1 байт):** значення `0x05` (ідентифікатор опції SACK).
* **Length (1 байт):** повна довжина опції у байтах: `Length = 2 + 8 · N`, де `N` — кількість переданих блоків SACK (від 1 до 4).
  * 1 блок: `Length = 10` байтів (`2 + 8 · 1`).
  * 2 блоки: `Length = 18` байтів (`2 + 8 · 2`).
  * 3 блоки: `Length = 26` байтів (`2 + 8 · 3`).
  * 4 блоки: `Length = 34` байти (`2 + 8 · 4`).
* **Left Edge of Block (4 байти, 32 біти, Big-Endian):** номер першого байта неперервного отриманого блоку.
* **Right Edge of Block (4 байти, 32 біти, Big-Endian):** номер, на одиницю більший за останній отриманий байт блоку (напіввідкритий інтервал `[Left_Edge, Right_Edge)`).

#### Обмеження на кількість блоків у заголовку TCP
Максимальний сумарний розмір заголовка TCP разом із усіма опціями обмежений полем `Data Offset` (4 біти), яке вимірює довжину в 32-бітових словах: `15 · 4 = 60` байтів. Оскільки базовий заголовок займає `20` байтів, під опції залишається щонайбільше `40` байтів.

* **Без опції TCP Timestamps:** поміщається максимум **4 блоки SACK** (`2 + 8 · 4 = 34` байти).
* **За наявності опції TCP Timestamps (RFC 7323, 10 байтів + 2 байти NOP-вирівнювання = 12 байтів):** залишається `40 - 12 = 28` байтів, що дозволяє передати максимум **3 блоки SACK** (`2 + 8 · 3 = 26` байтів).

#### Розширення D-SACK (Duplicate SACK, RFC 2883)
Якщо перший блок SACK вказує на діапазон байтів, який менший або дорівнює поточному кумулятивному `ACK`, або повністю міститься всередині іншого блоку, це трактується як D-SACK. Це дозволяє передавачу точно дізнатися, що мережа дублює пакети або що таймаут `RTO` спрацював передчасно.

---

### 2. Структури даних ядра Linux для TCP SACK (C та C++)

У вихідному коді ядра Linux (`include/net/tcp.h`) діапазони вибіркових підтверджень зберігаються за допомогою масиву структур `tcp_sack_block`:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Структура одного блоку SACK у пам'яті (відповідає struct tcp_sack_block у Linux) */
typedef struct {
    uint32_t start_seq; /* Ліва межа блоку: перший отриманий байт */
    uint32_t end_seq;   /* Права межа блоку: перший байт ПІСЛЯ блоку */
} TcpSackBlock;

/* Стан вибіркових підтверджень сокета TCP */
#define TCP_NUM_SACKS 4

typedef struct {
    uint8_t      num_sacks;                    /* Кількість дійсних блоків (0..4) */
    TcpSackBlock selective_acks[TCP_NUM_SACKS]; /* Масив блоків SACK */
    uint32_t     cumulative_ack;               /* Кумулятивний ACK */
    bool         dsack_detected;               /* Ознака наявності D-SACK */
} TcpSackState;

/* Парсер опцій SACK із сирого буфера TCP */
bool parse_tcp_sack_option(const uint8_t *opt_ptr, uint8_t opt_len, TcpSackState *state) {
    if (opt_len < 10 || ((opt_len - 2) % 8) != 0) {
        return false; /* Некоректна довжина опції SACK */
    }

    uint8_t num_blocks = (uint8_t)((opt_len - 2) / 8);
    if (num_blocks > TCP_NUM_SACKS) num_blocks = TCP_NUM_SACKS;

    state->num_sacks = num_blocks;
    const uint8_t *p = opt_ptr + 2; /* Пропускаємо Kind та Length */

    for (uint8_t i = 0; i < num_blocks; ++i) {
        /* Зчитування 32-бітових чисел у мережевому порядку байтів (Big-Endian) */
        uint32_t left = ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
                        ((uint32_t)p[2] << 8)  | (uint32_t)p[3];
        uint32_t right = ((uint32_t)p[4] << 24) | ((uint32_t)p[5] << 16) |
                         ((uint32_t)p[6] << 8)  | (uint32_t)p[7];

        state->selective_acks[i].start_seq = left;
        state->selective_acks[i].end_seq = right;
        p += 8;
    }

    /* Перевірка на Duplicate SACK (D-SACK за RFC 2883) */
    if (num_blocks > 0) {
        uint32_t first_left = state->selective_acks[0].start_seq;
        uint32_t first_right = state->selective_acks[0].end_seq;
        if (first_left < state->cumulative_ack ||
           (num_blocks > 1 && first_left >= state->selective_acks[1].start_seq &&
            first_right <= state->selective_acks[1].end_seq)) {
            state->dsack_detected = true;
        } else {
            state->dsack_detected = false;
        }
    }
    return true;
}
```
```cpp
#include <cstdint>
#include <vector>
#include <array>
#include <optional>
#include <span>

namespace net {

struct SackBlock {
    uint32_t start_seq{0}; // Left Edge
    uint32_t end_seq{0};   // Right Edge

    [[nodiscard]] constexpr uint32_t length() const noexcept {
        return end_seq - start_seq;
    }

    [[nodiscard]] constexpr bool contains(uint32_t seq) const noexcept {
        return seq >= start_seq && seq < end_seq;
    }
};

class TcpSackParser {
public:
    static constexpr uint8_t KIND_SACK_PERMITTED = 4;
    static constexpr uint8_t KIND_SACK           = 5;
    static constexpr size_t  MAX_SACK_BLOCKS     = 4;

    struct ParseResult {
        std::vector<SackBlock> blocks;
        bool is_dsack{false};
    };

    static std::optional<ParseResult> parse(std::span<const uint8_t> opt, uint32_t cumulative_ack) {
        if (opt.size() < 10 || opt[0] != KIND_SACK || ((opt[1] - 2) % 8) != 0) {
            return std::nullopt;
        }

        const size_t len = opt[1];
        if (opt.size() < len) return std::nullopt;

        const size_t num_blocks = std::min<size_t>((len - 2) / 8, MAX_SACK_BLOCKS);
        ParseResult result;
        result.blocks.reserve(num_blocks);

        const uint8_t* p = opt.data() + 2;
        for (size_t i = 0; i < num_blocks; ++i) {
            const uint32_t left = (static_cast<uint32_t>(p[0]) << 24) |
                                  (static_cast<uint32_t>(p[1]) << 16) |
                                  (static_cast<uint32_t>(p[2]) << 8)  |
                                  static_cast<uint32_t>(p[3]);

            const uint32_t right = (static_cast<uint32_t>(p[4]) << 24) |
                                   (static_cast<uint32_t>(p[5]) << 16) |
                                   (static_cast<uint32_t>(p[6]) << 8)  |
                                   static_cast<uint32_t>(p[7]);

            result.blocks.push_back({left, right});
            p += 8;
        }

        if (!result.blocks.empty()) {
            const auto& first = result.blocks.front();
            if (first.start_seq < cumulative_ack ||
               (result.blocks.size() > 1 && 
                first.start_seq >= result.blocks[1].start_seq &&
                first.end_seq <= result.blocks[1].end_seq)) {
                result.is_dsack = true;
            }
        }
        return result;
    }
};

} // namespace net
```
:::

---

### 3. Специфікація Wi-Fi Block ACK (IEEE 802.11n/ac/ax/be)

У сучасних мережах Wi-Fi для зменшення службових накладних витрат при передачі агрегованих кадрів (A-MPDU) використовується механізм **Block ACK (BA)**. Замість відправлення окремого ACK на кожен мікрокадр приймач надсилає одну бітову карту (англ. *Block ACK Bitmap*), яка покриває до 64 (або 256 у 802.11ax/be) кадрів одночасно.

#### Формат кадру Block ACK (IEEE 802.11)
Кадр Block ACK належить до типу кадрів керування (Control Frame, Type `01`, Subtype `1001`):

```
+-------------------+-------------------+-------------------+-------------------+
| Frame Control (2) | Duration (2 B)    | RA (6 B)          | TA (6 B)          |
+-------------------+-------------------+-------------------+-------------------+
| BA Control (2 B)  | BA SSC (2 B)      | BA Bitmap (8/32B) | FCS (CRC32, 4 B)  |
+-------------------+-------------------+-------------------+-------------------+
```

* **BA Control (2 байти):**
  * `Bits 0..3` — Multi-TID / Compressed / Extended BA policy.
  * `Bit 4` — Multi-STA flag (у Wi-Fi 6 OFDMA).
  * `Bits 12..15` — TID (Traffic Identifier, пріоритет QoS від 0 до 15).
* **BA Starting Sequence Control (BA SSC, 2 байти):**
  * `Bits 0..3` — Fragment Number (завжди `0` для агрегованих кадрів).
  * `Bits 4..15` — **Starting Sequence Number (SSN, 12 бітів):** початковий номер послідовності кадру, з якого починається відлік бітової карти.
* **Block ACK Bitmap (8 байтів / 64 біти в Compressed BA; 32 байти / 256 бітів у 802.11ax/be):**
  * Кожен `i`-й біт карти відповідає кадру з номером `(SSN + i) % 4096`.
  * Значення біта `1` означає успішний прийом кадру.
  * Значення біта `0` означає втрату або помилку CRC, вимагаючи вибіркової повторної передачі саме цього кадру.

---

### 4. Специфікація 3GPP RLC Status PDU (LTE / 5G NR)

У мобільних мережах на рівні RLC (Radio Link Control, 3GPP TS 38.322) протокол ARQ працює в режимі з підтвердженням (Acknowledged Mode, AM). Приймач передає передавачу компактний двійковий пакет керування — **RLC Status PDU**.

#### Бітовий формат RLC AM Status PDU (12-бітні та 18-бітні номери послідовності)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|D/C| CPT |                   ACK_SN                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|E1 |                    NACK_SN 1                  |E1 |E2 |E3 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          SOstart (якщо E2=1)          |           SOend       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

* **D/C (Data/Control field, 1 біт):** `0` — Control PDU (керівний статус), `1` — Data PDU (пакет даних).
* **CPT (Control PDU Type, 3 біти):** `000` — STATUS PDU (інші комбінації зарезервовано для майбутніх релізів 3GPP).
* **ACK_SN (Acknowledgment Sequence Number, 12 або 18 бітів):** номер наступного очікуваного RLC SDU, який ще не був отриманий. Вказує на верхню кумулятивну межу прийому.
* **E1 (Extension bit 1, 1 біт):**
  * `0` — далі немає блоків NACK (усі дані до `ACK_SN` отримано успішно).
  * `1` — слідом іде набір полів, що описують втрачений пакет `NACK_SN`.
* **NACK_SN (Negative Acknowledgment Sequence Number, 12 або 18 бітів):** порядковий номер конкретного втраченого RLC SDU.
* **E2 (Extension bit 2, 1 біт):**
  * `0` — втрачено весь RLC SDU цілком.
  * `1` — втрачено лише частину SDU (слідом ідуть поля зсуву байтів `SOstart` та `SOend`).
* **E3 (Extension bit 3, 1 біт у 5G NR):** прапорець неперервного діапазону втрачених номерів (NACK range).
* **SOstart / SOend (Segment Offset, по 16 бітів кожне):** вказують точний діапазон байтів усередині частково пошкодженого великого пакета RLC.

---

### 5. Параметри керування фізичного рівня HARQ у DCI (LTE / 5G NR)

На фізичному рівні (PHY/MAC) базової станції (gNodeB) повторні передачі координуються за допомогою службових повідомлень **Downlink Control Information (DCI)**, які передаються крізь фізичний канал керування PDCCH (3GPP TS 38.212).

#### Ключові поля дескриптора HARQ у DCI Format 1_0 / 1_1:

| Поле DCI | Розрядність | Призначення в протоколі HARQ |
| :--- | :--- | :--- |
| **HARQ Process ID (HPN)** | 4 біти | Номер паралельного процесу HARQ (`0 .. 15` у 5G NR, `0 .. 7` у LTE FDD). Дозволяє паралельно вести до 16 незалежних сесій Stop-and-Wait. |
| **New Data Indicator (NDI)** | 1 біт | Прапорець перемикання нового пакету. Якщо NDI інвертовано відносно попередньої передачі цього процесу (`0 → 1` або `1 → 0`) — це **нові дані** (буфер очищується). Якщо NDI збігається — це **повторна передача** того самого блоку (виконується soft combining). |
| **Redundancy Version (RV)** | 2 біти | Версія надлишковості завадостійкого коду: `00` (RV0), `01` (RV2), `10` (RV3), `11` (RV1). Визначає початкову точку вичитування бітів із кільцевого буфера турбо- або LDPC-кодера. |
| **Modulation and Coding Scheme (MCS)** | 5 бітів | Індекс таблиці модуляції (QPSK, 16QAM, 64QAM, 256QAM) та кодової швидкості. |
| **HARQ-ACK Feedback Timing** | 3 біти | Часовий зсув у слотах між прийомом блоку PDSCH та передачею відповіді ACK/NACK на каналі PUCCH. |

#### Схематична послідовність версій надлишковості (RV Sequence)
У мобільних мережах 3GPP стандартна послідовність зміни версій надлишковості при послідовних невдалих спробах декодування визначена як:

```
Спроба 1: RV0 (містить усі систематичні біти + первинну надлишковість)
   ↓ (CRC помилка -> NACK)
Спроба 2: RV2 (містить додаткові біти парності для зниження кодової швидкості)
   ↓ (CRC помилка -> NACK)
Спроба 3: RV3 (зміщення фази парності)
   ↓ (CRC помилка -> NACK)
Спроба 4: RV1 (фінальні біти надлишковості)
```

Така комбінація гарантує, що декодер LDPC на приймачі при кожній новій спробі отримує принципово нові перевірочні рівняння, максимізуючи ймовірність успішного виправлення помилок без повторного пересилання вже відомих бітів.

---

### 6. Специфікація кадрів QUIC ACK (RFC 9000 §19.3)

У протоколі QUIC (транспортна основа HTTP/3) механізм підтвердження позбавлений обмеження TCP на 4 блоки SACK і повністю інтегрований у структуру зміннорозрядних пакетів.

#### Бітова структура QUIC ACK Frame

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Type (i)    |             Largest Acknowledged (i)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        ACK Delay (i)          |       ACK Range Count (i)     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     First ACK Range (i)       |         ACK Ranges (*) ...    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

* Позначення `(i)` вказує на поле змінної довжини QUIC Varint (1, 2, 4 або 8 байтів).
* **Type (1 байт):** `0x02` — звичайний ACK Frame; `0x03` — ACK Frame із додатковими полями лічильників явного сповіщення про затори (ECN).
* **Largest Acknowledged (Varint):** максимальний номер пакета, коли-небудь успішно прийнятий цим вузлом.
* **ACK Delay (Varint):** час у мікросекундах (масштабований експонентою `ack_delay_exponent`), який минув між прийомом найбільшого пакета та відправленням цього кадру ACK.
* **ACK Range Count (Varint):** кількість додаткових діапазонів дірок та отриманих пакетів.
* **First ACK Range (Varint):** кількість неперервно отриманих пакетів, що передують `Largest Acknowledged`.
* **ACK Ranges (`Gap` + `Range`):** пари чисел, що описують розмір пропущеної дірки (`Gap`) та довжину наступного отриманого острова пакетів (`Range`).

Завдяки компактному кодуванню чисел змінної довжини один кадр QUIC ACK може без зусиль передавати інформацію про сотні розрізнених діапазонів втрачених пакетів в одному сегменті UDP, усуваючи будь-яку необхідність у повторі вже збережених даних.

---

### 7. Системні параметри ядра Linux та діагностика через Socket API

У підсистемі `sysctl` ядра Linux роботу алгоритмів вибіркового повтору налаштовують через такі параметри:

* `net.ipv4.tcp_sack` (за замовчуванням `1`): увімкнення генерації та обробки опцій SACK (RFC 2018).
* `net.ipv4.tcp_dsack` (за замовчуванням `1`): увімкнення генерації Duplicate SACK (RFC 2883) для виявлення фальшивих повторів.
* `net.ipv4.tcp_fack` (за замовчуванням `0` у сучасних ядрах): Forward Acknowledgment — агресивне оцінювання втрат за крайньою правою межею блоків SACK (замінено алгоритмом RACK-TLP у RFC 8985).
* `net.ipv4.tcp_comp_sack_nr` (за замовчуванням `44`): поріг стиснення черги SACK у ядрі при високому рівні фрагментації з'єднання.

#### Моніторинг метрик SACK через опцію сокета TCP_INFO
У прикладних програмах стан черг повтору та ефективність SACK перевіряють через системний виклик `getsockopt` з опцією `TCP_INFO`:

:::tabs
```c
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <unistd.h>

/* Отримання статистики SACK та повторних передач для відкритого сокета TCP */
void print_socket_sack_stats(int sockfd) {
    struct tcp_info info;
    socklen_t len = sizeof(info);

    if (getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) == 0) {
        printf("=== Статистика TCP SACK сокета ===\n");
        printf("Кількість підтверджених через SACK пакетів: %u\n", info.tcpi_sacked);
        printf("Кількість зафіксованих втрачених пакетів:      %u\n", info.tcpi_lost);
        printf("Кількість виконаних повторних передач:        %u\n", info.tcpi_retrans);
        printf("Оцінка RTT:                                   %u мкс (RTTvar: %u мкс)\n", 
               info.tcpi_rtt, info.tcpi_rttvar);
        printf("Поточний розмір вікна перевантаження (CWND):   %u сегментів\n", info.tcpi_snd_cwnd);
    }
}
```
```cpp
#include <iostream>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <unistd.h>

namespace net {

struct SocketStats {
    uint32_t sacked_packets{0};
    uint32_t lost_packets{0};
    uint32_t retransmitted_packets{0};
    uint32_t rtt_us{0};
    uint32_t rttvar_us{0};
    uint32_t cwnd_segments{0};
};

[[nodiscard]] std::optional<SocketStats> get_tcp_sack_stats(int sockfd) noexcept {
    struct tcp_info info{};
    socklen_t len = sizeof(info);

    if (::getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &len) != 0) {
        return std::nullopt;
    }

    return SocketStats{
        .sacked_packets = info.tcpi_sacked,
        .lost_packets = info.tcpi_lost,
        .retransmitted_packets = info.tcpi_retrans,
        .rtt_us = info.tcpi_rtt,
        .rttvar_us = info.tcpi_rttvar,
        .cwnd_segments = info.tcpi_snd_cwnd
    };
}

void print_stats(int sockfd) {
    if (const auto stats = get_tcp_sack_stats(sockfd)) {
        std::cout << "=== Статистика TCP SACK (C++) ===\n"
                  << "SACKed: " << stats->sacked_packets << "\n"
                  << "Lost:   " << stats->lost_packets << "\n"
                  << "Retrans:" << stats->retransmitted_packets << "\n"
                  << "RTT:    " << stats->rtt_us << " us\n";
    }
}

} // namespace net
```
:::

---

### 8. Налаштування сокетів для низьколатентних повторів (TCP_QUICKACK, TCP_NODELAY, TCP_USER_TIMEOUT)

У високонавантажених серверах та розподілених системах реального часу стандартна поведінка ядра (наприклад, 40-мілісекундний відкладений `ACK` чи тривале очікування таймауту за замовчуванням у 2 хвилини) призводить до стрибків затримки. 

Для тонкого керування підтвердженнями та таймерами повторної передачі використовують системні опції сокета `setsockopt`:

```
+---------------------+---------------------------------------------------------------+
| Опція сокета        | Інженерний ефект на роботу ARQ                                |
+---------------------+---------------------------------------------------------------+
| TCP_NODELAY         | Вимикає алгоритм Нагла: пакети даних випромінюються негайно,  |
|                     | не очікуючи на заповнення MSS або прибуття чергового ACK.     |
| TCP_QUICKACK        | Примусово вимикає відкладений ACK (Delayed ACK): ядро негайно |
|                     | надсилає ACK на кожен прийнятий кадр без 40-мс паузи.         |
| TCP_USER_TIMEOUT    | Максимальний час у мілісекундах, протягом якого передані дані |
|                     | можуть лишатися непідтвердженими до примусового розриву.      |
| TCP_THIN_DUPACK     | Активує агресивний повтор для «тонких» потоків (менше 4 кадрів|
|                     | у вікні), де стандартне правило 3x DUPACK ніколи не спрацює.  |
+---------------------+---------------------------------------------------------------+
```

Нижче наведено код конфігурації сокета для низьколатентного протокольного обміну:

:::tabs
```c
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <netinet/in.h>

/* Налаштування сокета для мінімізації затримок ARQ у мовах C */
int configure_low_latency_socket(int sockfd) {
    int enable = 1;

    /* 1. Вимикаємо буферизацію Нагла */
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(enable)) != 0) {
        return -1;
    }

    /* 2. Вмикаємо негайну генерацію ACK (без затримки 40 мс) */
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK, &enable, sizeof(enable)) != 0) {
        return -1;
    }

    /* 3. Встановлюємо таймаут непідтверджених даних 1500 мс (замість 2 хв) */
    unsigned int user_timeout_ms = 1500;
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) != 0) {
        return -1;
    }

    return 0;
}
```
```cpp
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include <system_error>
#include <chrono>

namespace net {

/* Безпечне налаштування параметрів сокета у сучасному C++ */
void configure_low_latency(int sockfd, std::chrono::milliseconds timeout = std::chrono::milliseconds{1500}) {
    const int enable = 1;

    // 1. Негайна відправка (вимкнення алгоритму Нагла)
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(enable)) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_NODELAY");
    }

    // 2. Негайні підтвердження QuickACK
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK, &enable, sizeof(enable)) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_QUICKACK");
    }

    // 3. Граничний таймаут непідтверджених даних
    const auto timeout_ms = static_cast<unsigned int>(timeout.count());
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &timeout_ms, sizeof(timeout_ms)) != 0) {
        throw std::system_error(errno, std::generic_category(), "Не вдалося встановити TCP_USER_TIMEOUT");
    }
}

} // namespace net
```
:::

---

### 9. Приклад побайтового розбору 3GPP RLC Status PDU

Для ілюстрації практичного розкодування розгляньмо реальний 4-байтовий службовий пакет керування RLC AM Status PDU (12-бітні номери послідовності), перехоплений у радіоефірі 5G NR:

```
Шістнадцятковий дамп пакета: 0x01 0x2A 0x80 0x64

Двійкове представлення по полях:
[0] [000] [0001 0010 1010] [1] [0000 0000 0110 0100] [0] [0] [0]
 │    │           │          │              │          │   │   │
 │    │           │          │              │          │   │   └─ E3 = 0 (одиничний NACK)
 │    │           │          │              │          │   └───── E2 = 0 (втрачено весь PDU)
 │    │           │          │              │          └───────── E1 = 0 (більше немає NACK)
 │    │           │          │              └──────────────────── NACK_SN = 100 (SDU #100 втрачено!)
 │    │           │          └─────────────────────────────────── E1 = 1 (слідом іде перший NACK)
 │    │           └────────────────────────────────────────────── ACK_SN = 298 (чекаємо SDU #298)
 │    └────────────────────────────────────────────────────────── CPT = 000 (STATUS PDU)
 └─────────────────────────────────────────────────────────────── D/C = 0 (Control PDU)
```

**Інженерний висновок декодера:**
1. Приймач успішно прийняв усі пакети від початку до номера `#297` включно, **за винятком єдиного пакета `#100`**.
2. Поле `ACK_SN = 298` кумулятивно зсуває вікно передавача до номера 298.
3. Поле `NACK_SN = 100` змушує передавач негайно виконати вибірковий повтор (Selective Repeat) виключно втраченого пакета з номером `#100`.
