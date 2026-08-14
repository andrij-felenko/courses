# ⚙️ Налаштування, моніторинг та розбір сесій BGP

Ця прикладна вставка містить вичерпне керівництво з практичного розгортання сесії Border Gateway Protocol (BGP) між двома автономними системами на базі сучасного мережевого даймона FRRouting (FRR) у середовищі Linux. У ній детально розглянуто стани скінченного автомата BGP (FSM), конфігурацію параметрів оголошення префіксів, фільтрацію маршрутів за допомогою списків префіксів та маршрутних карт (route-maps), автентифікацію сесій за допомогою паролів TCP MD5, інструменти моніторингу та командний інтерфейс `vtysh`, а також наведено порівняльний реальний приклад низькорівневого розбору бінарних заголовків BGP на мовах C та C++.

---

## 1. Архітектура та схема стенду eBGP у FRRouting (FRR)

Для побудови тестового стенду розглядається з'єднання двох автономних систем. Маршрутизатор `R1` належить автономній системі клієнта (`AS 65001`), а маршрутизатор `R2` належить автономній системі вищого провайдера (`AS 65002`). Зв'язок між ними здійснюється через прямо з'єднаний кабельний сегмент у мережі `192.168.12.0/30`.

```
┌──────────────────────────────┐                   ┌──────────────────────────────┐
│     Router R1 (AS 65001)     │                   │     Router R2 (AS 65002)     │
│                              │    eBGP сесія     │                              │
│ Loopback: 1.1.1.1/32         │<──── TCP 179 ────>│ Loopback: 2.2.2.2/32         │
│ Eth0: 192.168.12.1/30        │                   │ Eth0: 192.168.12.2/30        │
└──────────────────────────────┘                   └──────────────────────────────┘
```

Даймон FRRouting є сучасним форком Quagga/Zebra і складається з центрального керуючого даймона `zebra` (який взаємодіє з ядром Linux та оновлює системні маршрути) та окремих даймонів під кожен протокол. Процес `bgpd` відповідає виключно за обробку сесій BGP, ведення таблиці Loc-RIB та розрахунок найкращих шляхів. Взаємодія з усіма даймонами здійснюється через єдину консоль `vtysh` або редагуванням конфігураційного файла `/etc/frr/bgpd.conf`.

### Конфігураційний файл `/etc/frr/bgpd.conf` на маршрутизаторі R1:

```text
! Основний блок конфігурації BGP-процесу для AS 65001
router bgp 65001
 bgp router-id 1.1.1.1
 no bgp ebgp-requires-policy

 ! Оголошення власного локального префікса в BGP
 network 1.1.1.1/32

 ! Налаштування параметрів eBGP-сусіда R2
 neighbor 192.168.12.2 remote-as 65002
 neighbor 192.168.12.2 description "eBGP Upstream Provider AS65002"
 neighbor 192.168.12.2 timers 30 90
 neighbor 192.168.12.2 password SuperSecretBgpPassword123

 ! Активація сімейства адрес IPv4 Unicast та збереження вхідних маршрутів
 address-family ipv4 unicast
  neighbor 192.168.12.2 activate
  neighbor 192.168.12.2 prefix-list PL_OUT out
  neighbor 192.168.12.2 soft-reconfiguration inbound
 exit-address-family

! Створення списку префіксів для дозволу оголошення лише власної мережі
ip prefix-list PL_OUT permit 1.1.1.1/32
```

### Пояснення важливих директив конфігурації:

- `bgp router-id 1.1.1.1`: задає унікальний 32-бітний ідентифікатор маршрутизатора. Зазвичай використовується адреса інтерфейсу Loopback. Якщо цей атрибут не задати явно, BGP автоматично обере найбільшу IPv4-адресу серед активних інтерфейсів роутера.
- `no bgp ebgp-requires-policy`: у нових версіях FRR за замовчуванням блокуються всі eBGP-маршрути, якщо для сусіда не задано `route-map` або `prefix-list`. Ця команда вимикає сувору вимогу для тестових стендів.
- `network 1.1.1.1/32`: командує процесу BGP помістити префікс `1.1.1.1/32` у BGP-таблицю. **Важливе правило:** BGP оголосить цей префікс сусідам **лише тоді**, коли цей префікс вже є у системній таблиці маршрутизації ядра Linux (FIB). Якщо мережа відсутня в таблиці ядра, BGP ігноруватиме команду `network`.
- `neighbor 192.168.12.2 password ...`: вмикає заголовок автентифікації TCP MD5 Signature Option (RFC 2385). Ядро Linux на рівні сокета перевіряє хеш кожного TCP-сегмента, унеможливлюючи підробку пакетів або підрив сесії зловмисниками.
- `soft-reconfiguration inbound`: змушує маршрутизатор зберігати у пам'яті точну копію всіх необроблених оголошень від сусіда (таблицю `Adj-RIB-In`). Це дозволяє змінювати вхідні фільтри та префікс-листи без розриву й переустановлення TCP-сесії.
- `prefix-list PL_OUT out`: застосовує фільтр на вихідні оголошення. Маршрутизатор відправить сусіду лише ті префікси, які чітко відповідають правилам `PL_OUT`, захищаючи мережу від випадкового витоку чужих маршрутів (Route Leak).

---

## 2. Скінченний автомат BGP (FSM) та стани сесії

Перш ніж BGP-сесія почне передавати префікси, вона проходить шість послідовних станів скінченного автомата (Finite State Machine, FSM):

1. **Idle (Бездіяльність):** початковий стан. BGP відхиляє всі вхідні з'єднання й чекає команди на старт (start event) від адміністратора або системи.
2. **Connect (З'єднання):** BGP чекає завершення встановлення TCP-з'єднання (триетапного рукостискання SYN, SYN-ACK, ACK) на порту 179. Якщо з'єднання успішне, надсилається пакет `OPEN` і сесія переходить у стан `OpenSent`. Якщо таймер з'єднання вичерпано, сесія переходить у `Active`.
3. **Active (Активний):** стається, якщо TCP-з'єднання не вдалося встановити за виділений час. BGP скидає таймер і продовжує повторні спроби ініціалізації TCP-з'єднання з піром.
4. **OpenSent (Надіслано OPEN):** TCP-з'єднання успішно встановлено, BGP відправив своє повідомлення `OPEN` і чекає на `OPEN` від протилежної сторони. На цьому етапі перевіряються номери ASN, версія протоколу та таймери Hold Time.
5. **OpenConfirm (Підтвердження OPEN):** BGP отримав коректне повідомлення `OPEN` від сусіда, надіслав `KEEPALIVE` і чекає у відповідь `KEEPALIVE`.
6. **Established (Установлено):** сесія повністю активна. Маршрутизатори починають обмінюватися повідомленнями `UPDATE` з префіксами.

> ⚠️ **Типовий баг:** Якщо сесія зависла у стані `Active` або `Connect`, це свідчить про проблему транспортного рівня: заблоковано порт TCP 179 у `iptables`/`nftables`, вказано неправильну IP-адресу сусіда, не збігається MD5-пароль або відсутній маршрут до IP-адреси BGP-піра.

---

## 3. Практичні команди моніторингу та трасування у CLI `vtysh`

Комплексна діагностика BGP-сесій виконується за допомогою вбудованої оболонки `vtysh`:

### 1. Перевірка загального статусу сесій (`show ip bgp summary`)

```text
vtysh# show ip bgp summary

IPv4 Unicast Summary:
BGP router identifier 1.1.1.1, local AS number 65001
V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
4 65002      42      45        2    0    0 00:18:32        1
```

Детальний аналіз колонок виводу:
- **V:** версія протоколу BGP (завжди `4`).
- **AS:** номер автономної системи BGP-сусіда.
- **MsgRcvd / MsgSent:** кількість усіх отриманих і надісланих BGP-пакетів (включаючи `OPEN`, `KEEPALIVE` та `UPDATE`).
- **InQ / OutQ:** кількість пакетів, що очікують обробки в черзі входу або виходу. У стабільному стані мають дорівнювати `0`.
- **Up/Down:** час, протягом якого сесія безперервно перебуває у поточному стані.
- **State/PfxRcd:** у разі успіху показує **число отриманих префіксів** (у прикладі `1`). Якщо сесія не встановилася, тут буде написано текстову назву стану FSM (`Active`, `Idle` або `Connect`).

### 2. Аналіз глобальної таблиці BGP (Loc-RIB) (`show ip bgp`)

```text
vtysh# show ip bgp

   Network          Next Hop            Metric LocPrf Weight Path
*> 2.2.2.2/32       192.168.12.2             0             0 65002 i
*> 1.1.1.1/32       0.0.0.0                  0         32768 i
```

Значення символів у першій колонці:
- `*` (Valid): маршрут синтаксично коректний, а його адреса `Next Hop` є досяжною згідно з локальною таблицею маршрутизації.
- `>` (Best): маршрут визнано найкращим серед усіх кандидатів за детермінованим алгоритмом BGP Decision Process. Рядки з символом `>` експортуються у системну таблицю маршрутизації ядра ОС Linux (FIB).
- `i` (Internal Origin): маршрут згенеровано всередині BGP через команду `network`.

### 3. Детальний інспекційний аналіз конкретного сусіда (`show ip bgp neighbors 192.168.12.2`)

Ця команда повертає повний зріз стану сесії: узгоджене значення Hold Time та Keepalive, лічильники помилок NOTIFICATION, статус підтримки 4-байтного ASN, підключені Capabilities, а також поточний стан таймерів відправки.

---

## 4. Трасування BGP-пакетів за допомогою `tcpdump` та Wireshark

Для налагодження сесій на низькому рівні мережевий інженер може захопити сирі TCP-пакети на інтерфейсі роутера за допомогою утиліти `tcpdump`:

```bash
# Захоплення лише кадри BGP (порт TCP 179) з виводом розширеної інформації
tcpdump -i eth0 -nn -v "tcp port 179"
```

Приклад виводу захопленого кадру `UPDATE`:
```text
12:34:56.789012 IP 192.168.12.2.179 > 192.168.12.1.45678: Flags [P.], seq 1:56, ack 1, win 502, length 55: BGP
    BGP Update (Length 55):
      Path attribute: Origin (1): IGP
      Path attribute: AS_Path (2): 65002
      Path attribute: Next_Hop (3): 192.168.12.2
      Updated routes:
        2.2.2.2/32
```

Трасування дає змогу миттєво побачити сирі атрибути `AS_PATH`, `NEXT_HOP` та `LOCAL_PREF`, перевірити прапорці TCP та переконатися у відсутності втрат пакетів чи скидань TCP-сесії прапорцем `RST`.

---

## 5. Програмний розбір бінарних заголовків BGP на C та C++

При створенні власних аналізаторів трафіку, утиліт діагностики або легких BGP-демонів постає задача розбору низькорівневих пакетів, отриманих із TCP-сокета. 

Утиліта повинна прочитати 19-байтний заголовок BGP, перевірити маркер синхронізації (16 байтів `0xFF`), перетворити порядок байтів довжини пакета з мережевого (Big-Endian) у хостовий та визначити тип повідомлення.

Нижче наведено порівняльний код на C (із класичними покажчиками та `memcpy`) та на ідіоматичному C++20 (із використанням `std::span`, `std::expected` та строгих типів даних).

:::tabs
```c
/* bgp_header_parser.c — Парсер заголовка BGP на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>

#define BGP_HEADER_LEN 19
#define BGP_MARKER_LEN 16

typedef struct {
    uint8_t  marker[BGP_MARKER_LEN];
    uint16_t length;
    uint8_t  type;
} __attribute__((packed)) bgp_header_t;

int parse_bgp_header(const uint8_t *buffer, size_t buf_len, bgp_header_t *out_hdr) {
    if (buf_len < BGP_HEADER_LEN) {
        return -1; /* Занадто короткий буфер */
    }

    memcpy(out_hdr, buffer, BGP_HEADER_LEN);
    out_hdr->length = ntohs(out_hdr->length);

    /* Перевірка кожної позиції маркера (усі байти мусять бути 0xFF) */
    for (int i = 0; i < BGP_MARKER_LEN; ++i) {
        if (out_hdr->marker[i] != 0xFF) {
            return -2; /* Збій синхронізації маркера */
        }
    }

    if (out_hdr->length < BGP_HEADER_LEN || out_hdr->length > 4096) {
        return -3; /* Вихід за межі нормативної довжини BGP-пакета */
    }

    return 0; /* Успішно розібрано */
}

int main(void) {
    /* Тестовий кадр BGP KEEPALIVE (19 байтів) */
    uint8_t raw_pkt[19] = {
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0x00, 0x13, /* Length: 19 байтів */
        0x04        /* Type: 4 (KEEPALIVE) */
    };

    bgp_header_t hdr;
    int res = parse_bgp_header(raw_pkt, sizeof(raw_pkt), &hdr);
    if (res == 0) {
        printf("[C] BGP Packet Valid! Length: %u, Type: %u\n", hdr.length, hdr.type);
    } else {
        printf("[C] BGP Header Invalid: error code %d\n", res);
    }
    return 0;
}
```
```cpp
// bgp_header_parser.cpp — Ідіоматичний парсер заголовка BGP на C++20
#include <iostream>
#include <array>
#include <span>
#include <expected>
#include <cstdint>
#include <algorithm>

enum class BgpMessageType : uint8_t {
    Open         = 1,
    Update       = 2,
    Notification = 3,
    Keepalive    = 4
};

enum class ParseError {
    BufferTooShort,
    InvalidMarker,
    InvalidLength
};

struct BgpHeader {
    std::array<uint8_t, 16> marker{};
    uint16_t length{0};
    BgpMessageType type{BgpMessageType::Keepalive};
};

class BgpParser {
public:
    static std::expected<BgpHeader, ParseError> parse_header(std::span<const uint8_t> bytes) noexcept {
        if (bytes.size() < 19) {
            return std::unexpected(ParseError::BufferTooShort);
        }

        BgpHeader hdr;
        std::copy_n(bytes.begin(), 16, hdr.marker.begin());

        // Перевірка маркера BGP (усі 16 байтів мають дорівнювати 0xFF)
        if (!std::all_of(hdr.marker.begin(), hdr.marker.end(), [](uint8_t b) { return b == 0xFF; })) {
            return std::unexpected(ParseError::InvalidMarker);
        }

        // Конвертація з мережевого порядку байтів (Big-Endian)
        hdr.length = static_cast<uint16_t>((bytes[16] << 8) | bytes[17]);
        hdr.type = static_cast<BgpMessageType>(bytes[18]);

        if (hdr.length < 19 || hdr.length > 4096) {
            return std::unexpected(ParseError::InvalidLength);
        }

        return hdr;
    }
};

int main() {
    const std::array<uint8_t, 19> raw_pkt = {
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0x00, 0x13, // Length: 19
        0x04        // Type: 4 (KEEPALIVE)
    };

    auto result = BgpParser::parse_header(raw_pkt);
    if (result) {
        std::cout << "[C++] BGP Packet Valid! Length: " << result->length
                  << ", Type: " << static_cast<int>(result->type) << "\n";
    } else {
        std::cout << "[C++] Header parsing failed!\n";
    }
    return 0;
}
```
:::
