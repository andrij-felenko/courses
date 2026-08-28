# 📋 Формати кадрів та інформаційних елементів (IE) 802.11k/v/r

Для узгодження параметрів роумінгу стандарти IEEE 802.11k, 802.11v та 802.11r визначають набір інформаційних елементів (англ. *Information Elements*, IE) та спеціальних кадрів дій керування (англ. *Action Frames*). Ці структури передаються у тілі beacon-кадрів, зондувальних відповідей `Probe Response`, кадрів автентифікації та реасоціації. Нижче наведено повну двійкову розкладку полів, ідентифікатори типів (Element ID), вкладені субелементи, коди статусів та програмні структури для низькорівневого розбору й формування пакетів у бездротових мережевих стеках.

### 1. Загальна інкапсуляція кадрів дій керування (Action Frames)

Усі протокольні повідомлення 802.11k та 802.11v передаються всередині стандартних кадрів керування типу `Management` із підтипом `Action` (бітове поле Type/Subtype у заголовку Frame Control дорівнює `0x00D0`):

```
Поле:           | Frame Control | Duration | DA (Одержувач) | SA (Відправник) | BSSID  | Seq Control | Category | Action | Action Payload | FCS  |
Розмір (байт):  |       2       |    2     |       6        |        6        |   6    |      2      |    1     |   1    |       N        |  4   |
```

Поле `Category` визначає функціональну групу протоколу:
* `Category 0x05 (Radio Measurement)` — використовується стандартом 802.11k для запитів та відповідей `Neighbor Report` (Action Code `0x04` для запиту, `0x05` для відповіді);
* `Category 0x0A (Wireless Network Management, WNM)` — використовується стандартом 802.11v для керування переходами BTM (Action Code `0x07` для BTM Request, `0x08` для BTM Response, `0x06` для BTM Query);
* `Category 0x06 (Fast BSS Transition)` — використовується стандартом 802.11r у режимі Over-the-DS для тунелювання запитів FT через дротову мережу (Action Code `0x01` для FT Request, `0x02` для FT Response).

### 2. Елемент 802.11k: Neighbor Report (Element ID: 52 / 0x34)

Елемент `Neighbor Report` передається точкою доступу у відповідь на запит станції або включається як вкладений список у кадри 802.11v BTM Request. Він надає вичерпну інформацію про кожну сусідню точку доступу тієї самої мережі.

```
Поле:           | Element ID | Length | BSSID  | BSSID Info | Reg Class | Channel | PHY Type | Sub-elements |
Розмір (байт):  |     1      |   1    |   6    |     4      |     1     |    1    |    1     |      N       |
Значення/Опис:  |    0x34    | 13 + N | MAC AP | Бітові фл. | Рег. клас | Номер к.| Тип PHY  | Опційні поля |
```

#### Детальна розкладка бітового поля BSSID Information (4 байти, Little Endian)

Бітове поле `BSSID Information` дозволяє клієнтській станції за один аналіз визначити придатність кандидата без виконання радіозондування:

```
Біти 0..1:   AP Reachability (Досяжність точки доступу)
             0 = Невідомо (Unknown)
             1 = Досяжна безпосередньо через радіоефір (Reachable over the air)
             2 = Недосяжна (Not reachable)
             3 = Досяжна через дротову розподільчу систему DS (Reachable via DS)
Біт 2:       Security (Політика безпеки)
             0 = Політика безпеки відрізняється від поточної AP
             1 = Політика безпеки ідентична (однаковий пароль, метод WPA, шифр CCMP/GCMP)
Біт 3:       Key Scope (Область дії майстер-ключа)
             0 = Потрібна повна повторна автентифікація
             1 = Спільний майстер-ключ PMK (дозволяє швидкий роумінг)
Біт 4:       Capabilities: Spectrum Management (підтримка 802.11h TPC/DFS)
Біт 5:       Capabilities: QoS (підтримка 802.11e WMM / EDCA)
Біт 6:       Capabilities: APSD (підтримка енергозбереження Automatic Power Save Delivery)
Біт 7:       Capabilities: Radio Measurement (підтримка 802.11k)
Біт 8:       Capabilities: Delayed Block Ack
Біт 9:       Capabilities: Immediate Block Ack
Біт 10:      Mobility Domain (1 = Точка доступу належить тому ж домену 802.11r FT)
Біт 11:      High Throughput (1 = Підтримка 802.11n HT)
Біт 12:      Very High Throughput (1 = Підтримка 802.11ac VHT)
Біт 13:      High Efficiency (1 = Підтримка 802.11ax HE / Wi-Fi 6)
Біт 14:      Extremely High Throughput (1 = Підтримка 802.11be EHT / Wi-Fi 7)
Біти 15..31: Зарезервовано стандартом
```

#### Опційні субелементи Neighbor Report (Sub-elements)

У полі змінної довжини `Sub-elements` точка доступу передає додаткові характеристики каналу:
* **Sub-element 1: TSF Information Offset (розмір 4 байти):** часова різниця лічильника TSF (англ. *Timing Synchronization Function*) між поточною та сусідньою точкою, що дозволяє клієнту прокинутися точно в момент передачі наступного маякового кадру (Target Beacon Transmission Time, TBTT) сусідньої AP.
* **Sub-element 2: Country / Regulatory Class (розмір 3 байти):** інформація про дозволені рівні потужності передавача в даній країні.
* **Sub-element 3: BSS Load (розмір 5 байтів):** стан завантаженості точки доступу:
  - `Station Count` (2 байти) — кількість підключених клієнтів;
  - `Channel Utilization` (1 байт) — відсоток часу, коли радіоканал зайнятий передачею інших пристроїв (значення `0..255`, де 255 = 100%);
  - `Available Admission Capacity` (2 байти) — залишковий ліміт пропускної здатності для нових QoS-потоків.
* **Sub-element 4: Wide Bandwidth Channel Switch (розмір 3 байти):** інформація про використання розширених смуг 80/160/320 МГц та розташування центральної частоти сегмента.
* **Sub-element 5: Beacon Transmission Interval (розмір 2 байти):** точний інтервал випромінювання маякових кадрів (Beacon Interval) сусідньої точки доступу в одиницях TU (1 TU = 1024 мкс).

### 3. Елементи 802.11r: Mobility Domain (IE 54) та Fast Transition (IE 55)

#### Mobility Domain Element (MDE, Element ID: 54 / 0x36)

Елемент MDE транслюється в кожному beacon-кадрі та зондувальній відповіді точок доступу, які підтримують швидкий перехід. Станція аналізує цей елемент перед виконанням роумінгу, щоб переконатися, що цільова точка належить до того самого домену ключів.

```
Поле:           | Element ID | Length | Mobility Domain ID (MDID) | FT Capability & Policy |
Розмір (байт):  |     1      |   1    |             2             |           1            |
Значення/Опис:  |    0x36    |   3    | 16-бітний ідентифікатор   | Бітові прапорці        |
```

* **Mobility Domain ID (MDID):** 16-бітне число, однакове для всіх точок доступу в межах однієї групи роумінгу. Якщо цільова AP транслює інший MDID, перехід за протоколом 802.11r неможливий і клієнт перемикається на повну автентифікацію.
* **FT Capability & Policy (1 байт):**
  - `Біт 0: Fast BSS Transition over DS` — встановлюється в 1, якщо точка підтримує тунелювання кадру FT через дротову мережу Ethernet;
  - `Біт 1: Resource Request Protocol Capability` — підтримка попереднього резервування смуги пропускання QoS перед переходом;
  - `Біти 2..7:` зарезервовано.

#### Fast BSS Transition Element (FTE, Element ID: 55 / 0x37)

Елемент FTE є ядром протоколу 802.11r і передається в кадрах FT Authentication та FT Reassociation. Він переносить одноразові псевдовипадкові числа (Nonces) для генерації сесійного ключа PTK та мітку цілісності повідомлення MIC (англ. *Message Integrity Code*).

```
Поле:           | ID   | Len  | MIC Control | MIC  | ANonce | SNonce | Sub-elements |
Розмір (байт):  | 1    | 1    |      2      |  16  |   32   |   32   |      N       |
Значення:       | 0x37 | 82+N | Алгоритм MIC| Хеш  | Від AP | Від STA| Вкладені поля|
```

* **MIC Control (2 байти):** вказує криптографічний алгоритм захисту мітки цілісності (0 = AES-128-CMAC, 1 = BIP / AES-128-CMAC) та кількість охоплених елементів.
* **MIC (16 байтів):** обчислюється над усім кадром запиту/відповіді за допомогою ключа `KCK` (англ. *Key Confirmation Key*), отриманого з `PMK-R1`.
* **ANonce (32 байти):** випадкове число, згенероване точкою доступу (Authenticator Nonce).
* **SNonce (32 байти):** випадкове число, згенероване клієнтською станцією (Supplicant Nonce).
* **Sub-elements FTE:**
  - `Sub-element 1: R0KH-ID` (довжина від 1 до 48 байтів) — ім'я контролера першого рівня (NAS-Identifier або доменне ім'я);
  - `Sub-element 2: R1KH-ID` (довжина 6 байтів) — MAC-адреса цільової точки доступу другого рівня;
  - `Sub-element 3: GTK (Group Transient Key)` — зашифрований груповий ключ радіолінку. Передається точкою у відповіді реасоціації всередині стандартної криптографічної обгортки AES Key Wrap (згідно з RFC 3394);
  - `Sub-element 4: IGTK (Integrity Group Transient Key)` — ключ для захисту широкомовних кадрів керування за стандартом 802.11w (BIP).

### 4. Кадри керування 802.11v BSS Transition Management (BTM)

Протокол 802.11v використовує розширені кадри дій категорії `0x0A` (Wireless Network Management, WNM).

```
Поле:           | Category | WNM Action | Dialog Token | Request Mode | Disassoc Timer | Validity Int | BSS Trans Candidates |
Розмір (байт):  |    1     |     1      |      1       |      1       |       2        |      1       |          N           |
Значення:       |   0x0A   | 0x07 (Req) |  0x01..0xFF  | Бітові прапор| Інтервали TBTT | Час життя    | Список кандидатів    |
```

#### Бітові прапорці поля Request Mode в BTM Request (1 байт)

```
Біт 0: Preferred Candidate List Included (Список містить рекомендовані контролером BSSID)
Біт 1: Abridged (Точка доступу не включає до списку кандидатів із незадовільною якістю)
Біт 2: Disassociation Imminent (Точка примусово розірве з'єднання після закінчення таймера)
Біт 3: BSS Termination Included (Точка доступу вимикає радіоінтерфейс на техобслуговування)
Біт 4: ESS Disassociation Imminent (Вся бездротова мережа стає недоступною в цій зоні)
Біти 5..7: Зарезервовано
```

#### Коди статусу у відповіді BTM Response (Action Code: 0x08)

У відповідь на запит BTM клієнт передає кадр `BTM Response`, де байт `BTM Status Code` повідомляє про результат обробки:
- `0x00`: **Accept (Прийнято)** — клієнт підтверджує перехід на одного із запропонованих кандидатів (вказує обраний Target BSSID);
- `0x01`: **Reject: Unspecified (Відхилено)** — загальна відмова без деталізації;
- `0x02`: **Reject: Insufficient Beacon/Probe (Відхилено)** — станція не змогла виявити сигнал рекомендованих AP під час швидкого сканування;
- `0x03`: **Reject: Insufficient Capabilities (Відхилено)** — кандидати не підтримують необхідні розширення (наприклад, QoS, WPA3 або смугу 160 МГц);
- `0x04`: **Reject: BSS Termination Undesired (Відхилено)** — клієнт відмовляється від переходу в разі зупинки поточної AP;
- `0x05`: **Reject: Candidate List Provided (Відхилено з контрпропозицією)** — станція надсилає власний список кандидатів, де рівень сигналу вищий.

### 5. Реалізація розбору та побудови кадрів на C та C++20

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define IEEE80211_ELEMID_NEIGHBOR_REPORT  0x34
#define IEEE80211_ELEMID_MOBILITY_DOMAIN  0x36
#define IEEE80211_ELEMID_FAST_TRANSITION  0x37

#define WNM_CATEGORY_CODE                 0x0A
#define WNM_ACTION_BTM_REQ                0x07
#define WNM_ACTION_BTM_RESP               0x08

#pragma pack(push, 1)

typedef struct {
    uint8_t  element_id;
    uint8_t  length;
    uint8_t  bssid[6];
    uint32_t bssid_info;
    uint8_t  reg_class;
    uint8_t  channel_number;
    uint8_t  phy_type;
} neighbor_report_fixed_t;

typedef struct {
    uint8_t  element_id;
    uint8_t  length;
    uint16_t mdid;
    uint8_t  ft_capability;
} mobility_domain_ie_t;

typedef struct {
    uint8_t  element_id;
    uint8_t  length;
    uint16_t mic_control;
    uint8_t  mic[16];
    uint8_t  anonce[32];
    uint8_t  snonce[32];
} fast_transition_ie_t;

typedef struct {
    uint8_t  category;        /* 0x0A - WNM */
    uint8_t  action;          /* 0x07 - BTM Request */
    uint8_t  dialog_token;
    uint8_t  request_mode;
    uint16_t disassoc_timer;  /* в одиницях TBTT */
    uint8_t  validity_interval;
} btm_request_fixed_t;

#pragma pack(pop)

bool parse_mobility_domain(const uint8_t *payload, uint16_t len, uint16_t *out_mdid, bool *out_over_ds) {
    if (!payload || len < sizeof(mobility_domain_ie_t) || !out_mdid || !out_over_ds) {
        return false;
    }
    const mobility_domain_ie_t *mde = (const mobility_domain_ie_t *)payload;
    if (mde->element_id != IEEE80211_ELEMID_MOBILITY_DOMAIN || mde->length < 3) {
        return false;
    }
    *out_mdid = mde->mdid;
    *out_over_ds = (mde->ft_capability & 0x01) != 0;
    return true;
}

bool is_neighbor_ft_capable(const uint8_t *payload, uint16_t len, uint8_t *out_channel) {
    if (!payload || len < sizeof(neighbor_report_fixed_t) || !out_channel) {
        return false;
    }
    const neighbor_report_fixed_t *rep = (const neighbor_report_fixed_t *)payload;
    if (rep->element_id != IEEE80211_ELEMID_NEIGHBOR_REPORT || rep->length < 13) {
        return false;
    }
    *out_channel = rep->channel_number;
    /* Біт 10 у BSSID Information вказує на підтримку 802.11r FT */
    return (rep->bssid_info & (1U << 10)) != 0;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <array>
#include <vector>

namespace wifi::kvr {

inline constexpr uint8_t ELEMID_NEIGHBOR_REPORT = 0x34;
inline constexpr uint8_t ELEMID_MOBILITY_DOMAIN = 0x36;
inline constexpr uint8_t ELEMID_FAST_TRANSITION = 0x37;

inline constexpr uint8_t WNM_CATEGORY_CODE   = 0x0A;
inline constexpr uint8_t WNM_ACTION_BTM_REQ  = 0x07;
inline constexpr uint8_t WNM_ACTION_BTM_RESP = 0x08;

struct MobilityDomainInfo {
    uint16_t mdid{0};
    bool ft_over_ds{false};
    bool resource_request_cap{false};
};

struct NeighborEntry {
    std::array<uint8_t, 6> bssid{};
    uint32_t bssid_info{0};
    uint8_t reg_class{0};
    uint8_t channel{0};
    uint8_t phy_type{0};

    [[nodiscard]] constexpr bool is_same_security() const noexcept {
        return (bssid_info & (1U << 2)) != 0;
    }

    [[nodiscard]] constexpr bool is_ft_supported() const noexcept {
        return (bssid_info & (1U << 10)) != 0;
    }

    [[nodiscard]] constexpr bool is_he_wifi6() const noexcept {
        return (bssid_info & (1U << 13)) != 0;
    }
};

struct BtmRequestInfo {
    uint8_t dialog_token{0};
    bool preferred_candidate_list{false};
    bool disassociation_imminent{false};
    uint16_t disassoc_timer_tbtt{0};
    uint8_t validity_interval{0};
};

class FrameParser {
public:
    static std::optional<MobilityDomainInfo> parse_mdie(std::span<const uint8_t> payload) noexcept {
        if (payload.size() < 5 || payload[0] != ELEMID_MOBILITY_DOMAIN) {
            return std::nullopt;
        }
        const uint8_t len = payload[1];
        if (len < 3 || payload.size() < static_cast<size_t>(2 + len)) {
            return std::nullopt;
        }

        const uint16_t mdid = static_cast<uint16_t>(payload[2]) | 
                             (static_cast<uint16_t>(payload[3]) << 8);
        const uint8_t cap = payload[4];

        return MobilityDomainInfo{
            .mdid = mdid,
            .ft_over_ds = (cap & 0x01) != 0,
            .resource_request_cap = (cap & 0x02) != 0
        };
    }

    static std::optional<NeighborEntry> parse_neighbor_report_elem(std::span<const uint8_t> payload) noexcept {
        if (payload.size() < 15 || payload[0] != ELEMID_NEIGHBOR_REPORT) {
            return std::nullopt;
        }
        const uint8_t len = payload[1];
        if (len < 13 || payload.size() < static_cast<size_t>(2 + len)) {
            return std::nullopt;
        }

        NeighborEntry entry{};
        for (size_t i = 0; i < 6; ++i) {
            entry.bssid[i] = payload[2 + i];
        }

        entry.bssid_info = static_cast<uint32_t>(payload[8]) |
                          (static_cast<uint32_t>(payload[9]) << 8) |
                          (static_cast<uint32_t>(payload[10]) << 16) |
                          (static_cast<uint32_t>(payload[11]) << 24);

        entry.reg_class = payload[12];
        entry.channel = payload[13];
        entry.phy_type = payload[14];

        return entry;
    }

    static std::optional<BtmRequestInfo> parse_btm_request(std::span<const uint8_t> payload) noexcept {
        if (payload.size() < 7 || payload[0] != WNM_CATEGORY_CODE || payload[1] != WNM_ACTION_BTM_REQ) {
            return std::nullopt;
        }

        const uint8_t mode = payload[3];
        const uint16_t timer = static_cast<uint16_t>(payload[4]) | 
                              (static_cast<uint16_t>(payload[5]) << 8);

        return BtmRequestInfo{
            .dialog_token = payload[2],
            .preferred_candidate_list = (mode & (1U << 0)) != 0,
            .disassociation_imminent = (mode & (1U << 2)) != 0,
            .disassoc_timer_tbtt = timer,
            .validity_interval = payload[6]
        };
    }
};

} // namespace wifi::kvr
```
:::
