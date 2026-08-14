# 📋 Інтерфейс конфігурації nl80211/mac80211 для 802.11ax

Ця довідкова вставка містить системний програмний інтерфейс (API), внутрішні структури даних ядра Linux (субсистеми `mac80211` та ядрового підсигналу `nl80211`), а також повнофункціональний довідник команд та атрибутів, необхідних для діагностики, налаштування та керування параметрами стандарту IEEE 802.11ax (Wi-Fi 6). Документ розкриває механізми конфігурації HE-PHY/HE-MAC можливостей, маркування BSS Color, порогових значень OBSS-PD, параметрів Target Wake Time (TWT), роботу алгоритму адаптації швидкостей `minstrel_he` та таблиць схем кодування MCS 0..11.

## 1. Архітектура бездротового стека Linux та інтерфейс nl80211 для 802.11ax

У системній архітектурі Linux взаємодія між програмами користувацького простору (User Space — такими як `hostapd`, `wpa_supplicant`, `iwd` або системна утиліта `iw`) та апаратними драйверами бездротових адаптерів реалізована через субсистему ядра `mac80211` та мережевий сокет **Netlink Generic (підсистема `nl80211`)**.

Підсистема `nl80211` працює за принципом «запит-відповідь» або «подія-сповіщення», передаючи бінарні атрибути (Netlink Attributes, NLA) у формі TLV (Type-Length-Value). Впровадження стандарту 802.11ax вимагало кардинального розширення протоколу `nl80211`, оскільки традиційні структури від керування 802.11n (HT) та 802.11ac (VHT) виявилися непридатними для опису паралельних ресурсних блоків OFDMA, динамічного контролю потужності та колірного маркування BSS Color.

При надсиланні команд додаток утиліти розгортає повідомлення `nl_msg`, додаючи заголовок сімейства `genlmsghdr` та унікальний код команди, такий як `NL80211_CMD_GET_INTERFACE`, `NL80211_CMD_SET_BSS` або `NL80211_CMD_SET_WIPHY`. Ядро перевіряє права прав підсистеми (`CAP_NET_ADMIN`), розбирає атрибути за допомогою `nla_parse()` і транслює їх у внутрішні структури `struct ieee80211_hw`.

Для підтримки High Efficiency (HE) у заголовочний файл ядра `<linux/nl80211.h>` було додано велику групу нових атрибутів та команд.

### Довідник ключових атрибутів Netlink для 802.11ax

Низькорівневий сокет `nl80211` оперує наступними атрибутами при обміні повідомленнями з ядром:

| Атрибут Netlink (`nl80211_attrs`) | Тип даних | Опис та системне призначення |
| :--- | :--- | :--- |
| `NL80211_ATTR_HE_CAPABILITY` | Вкладений NLA | Повний бінарний масив елемента HE Capabilities (MAC/PHY маски) |
| `NL80211_ATTR_BSS_COLOR` | `u8` | Поточне значення колірного маркування BSS Color (від 1 до 63) |
| `NL80211_ATTR_HE_OBSS_PD` | Вкладений NLA | Параметри порогового виявлення завад OBSS-PD та обмеження потужності |
| `NL80211_ATTR_HE_6GHZ_CAPABILITY` | Вкладений NLA | Специфічні можливості роботи у чистому діапазоні 6 ГГц (Wi-Fi 6E) |
| `NL80211_ATTR_HE_UL_MUTULTI_USER_CONFIG` | `u8` | Прапор дозволу зворотного мультикористувацького каналу UL-OFDMA та UL-MIMO |
| `NL80211_ATTR_PMKID` | Масив байт | Попарний майстер-ключ для захищеної реєстрації WPA3 (обов'язковий у Wi-Fi 6) |
| `NL80211_ATTR_TWT_RESPONDER` | Прапор | Підтримка точкою доступу функції відповідач TWT (TWT Responder) |

## 2. Структури даних ядра `mac80211` для опису можливостей HE

Фізичні та програмні можливості пристрою 802.11ax передаються через бінарні елементи інформації (Information Element, IE), які описуються специфікацією IEEE 802.11ax (Sec. 9.4.2.237).

Усередині ядра Linux драйвери бездротових адаптерів (наприклад, `ath11k` для Qualcomm або `mt7921` для MediaTek) заповнюють структури `struct ieee80211_he_cap` та декодують їх у маски для драйвера.

### Внутрішні структури MAC та PHY можливостей

Структура `nl80211_he_cap_elem` містить два основних масиви прапорів:

```c
/* Бінарний масив HE Capabilities Element */
struct nl80211_he_cap_elem {
    uint8_t mac_cap_info[6]; /* 48 біт MAC-можливостей */
    uint8_t phy_cap_info[11];/* 88 біт PHY-можливостей */
};
```

#### Деталізація байтів MAC Capabilities (`mac_cap_info`):
1. **Байт 0, біт 1 — HTC HE Support:** Підтримка розширеного управляючого заголовка HE Variant HT Control.
2. **Байт 0, біт 2 — TWT Requester Support:** Здатність пристрою виступати ініціатором сесій Target Wake Time.
3. **Байт 0, біт 3 — TWT Responder Support:** Здатність пристрою (точки доступу) підтримувати розклад TWT для клієнтів.
4. **Байт 1, біт 4 — Fragmented Backup Ack:** Підтримка фрагментаційного підтвердження кадрів.
5. **Байт 2, біти 1-3 — BSS Color Partial Bit:** Дозвіл часткового декодування BSS Color у стані сну.
6. **Байт 3, біт 0 — Broadcast TWT:** Підтримка загальномережевого широкомовного розкладу TWT.

#### Деталізація байтів PHY Capabilities (`phy_cap_info`):
1. **Байт 0, біт 1 — Dual Band Support:** Здатність працювати одночасно або перемикатися між 2.4 ГГц та 5 ГГц.
2. **Байт 0, біти 2-4 — Channel Width Set:** Бітова маска підтримуваної ширини каналу (40 МГц у 2.4 ГГц, 80 МГц, 160 МГц або 80+80 МГц у 5/6 ГГц).
3. **Байт 1, біти 0-1 — Preamble Punching Rx:** Здатність приймати кадри з вирізаними зашумленими суб-каналами (Preamble Puncturing).
4. **Байт 2, біт 0 — Device Class:** Клас пристрою (Indoor / Outdoor / Portable).
5. **Байт 3, біти 1-3 — OFDMA RA Support:** Підтримка випадкового доступу на ресурсних блоках (UORA).
6. **Байт 4, біти 0-1 — HE SU PPDU 1024-QAM:** Підтримка модуляції 1024-QAM для однокористувацьких кадрів.
7. **Байт 4, біти 2-3 — HE MU PPDU 1024-QAM:** Підтримка модуляції 1024-QAM для мультикористувацьких кадрів OFDMA.

### Алгоритм автовибору швидкостей Minstrel HE у ядрі Linux

Субсистема `mac80211` використовує модуль `minstrel_he` для динамічного вибору оптимальної модуляції MCS та розміру RU. Модуль безперервно збирає статистику про ймовірність успішної доставки кадрів (Packet Success Rate, PSR) для кожної комбінації MCS 0..11 та RU26..RU996.

Алгоритм розраховує математичне сподівання швидкості передачі $E[T]$ за формулою:

```text
E[T] = (1 - PER) * T_data / (T_data + PER * T_retry)
```

Де `PER` — коефіцієнт втрати пакетів, `T_data` — час передачі корисного кадру, `T_retry` — час повторної спроби. Модуль `minstrel_he` виділяє `10%` трафіку для пробного зняття характеристик (probing) вищих режимів MCS 10/11 (1024-QAM). Якщо рівень завад зростає і `EVM` погіршується, `minstrel_he` плавно скидає модуляцію до 256-QAM без обриву з'єднання.

### Структури маски схем модуляції HE-MCS (`struct nl80211_he_mcs_set`)

Схеми модуляції кодуються у масці `rx_mcs_map` та `tx_mcs_map`. Кожен просторовий потік (Spatial Stream) займає строго 2 біти у 16-бітному слові:

```c
struct nl80211_he_mcs_set {
    uint16_t rx_mcs_map; /* Кодування підтримуваних MCS для прийому (RX) */
    uint16_t tx_mcs_map; /* Кодування підтримуваних MCS для передачі (TX) */
};
```

Значення кожної двобітової пари у `rx_mcs_map`:
- `0b00` (0): Підтримуються MCS 0..7 (до 64-QAM).
- `0b01` (1): Підтримуються MCS 0..9 (до 256-QAM).
- `0b10` (2): Підтримуються MCS 0..11 (до 1024-QAM).
- `0b11` (3): Даний просторовий потік не підтримується апаратно.

Наприклад, якщо значення `rx_mcs_map = 0b1111111111101010` (`0xFFEA`), це означає:
- Потік 1: `0b10` -> MCS 0..11 (1024-QAM).
- Потік 2: `0b10` -> MCS 0..11 (1024-QAM).
- Потік 3: `0b10` -> MCS 0..11 (1024-QAM).
- Потоки 4..8: `0b11` -> Не підтримуються.
Таким чином, пристрій є адаптером 3×3 MIMO з повною підтримкою 1024-QAM.

## 3. Практичний довідник команд iw CLI

Системні адмінстратори та розробники бездротових систем у Linux використовують консольну утиліту `iw` для взаємодії з `nl80211`.

### Перевірка апаратних можливостей адаптера

Для діагностики підтримки Wi-Fi 6 на конкретному радіоінтерфейсі виконується команда:

```bash
iw phy phy0 info
```

У виводі команди з'являється деталізована секція `HE Capabilities`:

```text
Capabilities: 0x09 0x0d 0x00 0x02 0x40 0x00
    HE MAC Capabilities:
        + HTC HE Support
        + TWT Requester
        + TWT Responder
        + Multi-BSSID Support
    HE PHY Capabilities:
        + HE CBW 20/40/80 MHz
        + HE SU PPDU 1024-QAM
        + HE MU PPDU 1024-QAM
        + Dual Band Support (2.4 GHz / 5 GHz)
    HE RX MCS set:
        1 streams: MCS 0-11
        2 streams: MCS 0-11
    HE TX MCS set:
        1 streams: MCS 0-11
        2 streams: MCS 0-11
```

### Налаштування параметрів каналу та обмеження MCS

Для примусового обмеження швидкості або блокування високих режимів MCS (наприклад, при тестуванні лінійності підсилювача чи завадостійкості у лабораторії) використовується команда:

```bash
# Обмежити максимальний MCS до level 9 (256-QAM) у діапазоні 5 ГГц для 2 потоків
iw dev wlan0 set bitrates he-mcs-5 1:0-9 2:0-9

# Повернути автоматичний вибір швидкості (Auto Rate / Minstrel HE)
iw dev wlan0 set bitrates
```

### Опитування активних з'єднань та статистики OFDMA

Для перевірки поточного стану підключеного клієнта, значення BSS Color та використаного ресурсного блоку RU виконується команда:

```bash
iw dev wlan0 station dump
```

Приклад виводу для активного з'єднання Wi-Fi 6:

```text
Station 00:25:90:a1:b2:c3 (on wlan0)
    inactive time:  120 ms
    rx bytes:       15482092
    tx bytes:       8920140
    tx bitrate:     573.5 MBit/s HE-MCS 11 HE-BW 80 HE-GI 0.8 HE-DCM 0 RU-996 VHT-NSS 1
    rx bitrate:     286.7 MBit/s HE-MCS 9 HE-BW 80 HE-GI 1.6 RU-484 VHT-NSS 1
    bss color:      12
    signal:         -52 dBm
    tx failed:      0
    tx retries:     14
```

## 4. Програмна реалізація інтерфейсу Nl80211 у C та C++

Нижче наведено вихідний код двох варіантів програмного модуля для запиту інформації про стан 802.11ax через системні сокети Netlink.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <net/if.h>
#include <netlink/netlink.h>
#include <netlink/genl/genl.h>
#include <netlink/genl/ctrl.h>
#include <linux/nl80211.h>

/* Структура для збереження парсингу відповіді ядра */
typedef struct {
    int bss_color;
    int has_he_support;
    int max_streams;
    uint32_t frequency_mhz;
} wifi6_info_t;

/* Callback-функція обробки відповідей Netlink */
static int parse_nl80211_he_cb(struct nl_msg *msg, void *arg) {
    wifi6_info_t *info = (wifi6_info_t *)arg;
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    struct genlmsghdr *gnlh = nlmsg_data(nlh);
    struct nlattr *tb[NL80211_ATTR_MAX + 1];

    nla_parse(tb, NL80211_ATTR_MAX, genlmsg_attrdata(gnlh, 0),
              genlmsg_attrlen(gnlh, 0), NULL);

    if (tb[NL80211_ATTR_BSS_COLOR]) {
        info->bss_color = nla_get_u8(tb[NL80211_ATTR_BSS_COLOR]);
    }

    if (tb[NL80211_ATTR_HE_CAPABILITY]) {
        info->has_he_support = 1;
    }

    if (tb[NL80211_ATTR_WIPHY_FREQ]) {
        info->frequency_mhz = nla_get_u32(tb[NL80211_ATTR_WIPHY_FREQ]);
    }

    return NL_SKIP;
}

int query_wifi6_status(const char *ifname, wifi6_info_t *out_info) {
    struct nl_sock *sock = NULL;
    struct nl_msg *msg = NULL;
    int family_id, err = 0;

    memset(out_info, 0, sizeof(wifi6_info_t));
    out_info->bss_color = -1;

    sock = nl_socket_alloc();
    if (!sock) return -ENOMEM;

    if (genl_connect(sock) < 0) {
        nl_socket_free(sock);
        return -ECONNREFUSED;
    }

    family_id = genl_ctrl_resolve(sock, "nl80211");
    if (family_id < 0) {
        nl_socket_free(sock);
        return -ENOENT;
    }

    msg = nlmsg_alloc();
    if (!msg) {
        nl_socket_free(sock);
        return -ENOMEM;
    }

    genlmsg_put(msg, NL_AUTO_PID, NL_AUTO_SEQ, family_id, 0, 0,
               NL80211_CMD_GET_INTERFACE, 0);

    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        nlmsg_free(msg);
        nl_socket_free(sock);
        return -ENODEV;
    }

    nla_put_u32(msg, NL80211_ATTR_IFINDEX, ifindex);
    nl_socket_modify_cb(sock, NL_CB_VALID, NL_CB_CUSTOM, parse_nl80211_he_cb, out_info);

    err = nl_send_auto(sock, msg);
    if (err >= 0) {
        nl_recvmsgs_default(sock);
    }

    nlmsg_free(msg);
    nl_socket_free(sock);
    return err < 0 ? err : 0;
}

int main(int argc, char **argv) {
    const char *iface = (argc > 1) ? argv[1] : "wlan0";
    wifi6_info_t info;

    printf("Опитування статусу 802.11ax для інтерфейсу: %s
", iface);
    int res = query_wifi6_status(iface, &info);

    if (res < 0) {
        fprintf(stderr, "Помилка виклику Netlink nl80211: %d
", res);
        return 1;
    }

    printf("Підтримка 802.11ax (HE): %s
", info.has_he_support ? "ТАК" : "НІ");
    if (info.frequency_mhz > 0) {
        printf("Поточна частота каналу: %u МГц
", info.frequency_mhz);
    }
    if (info.bss_color >= 0) {
        printf("Поточний BSS Color: %d
", info.bss_color);
    } else {
        printf("BSS Color: не призначено або не підтримується
");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <net/if.h>

#include <netlink/netlink.h>
#include <netlink/genl/genl.h>
#include <netlink/genl/ctrl.h>
#include <linux/nl80211.h>

// RAII обгортка для Netlink сокета
class NlSocket {
public:
    NlSocket() : sock_(nl_socket_alloc(), nl_socket_free) {
        if (!sock_) {
            throw std::bad_alloc();
        }
        if (genl_connect(sock_.get()) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося з'єднатися з genl");
        }
    }

    struct nl_sock* get() const noexcept { return sock_.get(); }

private:
    std::unique_ptr<struct nl_sock, void(*)(struct nl_sock*)> sock_;
};

// RAII обгортка для повідомлення Netlink
class NlMessage {
public:
    NlMessage() : msg_(nlmsg_alloc(), nlmsg_free) {
        if (!msg_) {
            throw std::bad_alloc();
        }
    }

    struct nl_msg* get() const noexcept { return msg_.get(); }

private:
    std::unique_ptr<struct nl_msg, void(*)(struct nl_msg*)> msg_;
};

struct Wifi6Status {
    bool has_he_support{false};
    int bss_color{-1};
    uint32_t frequency_mhz{0};
};

class Wifi6NlClient {
public:
    Wifi6NlClient() : family_id_(genl_ctrl_resolve(sock_.get(), "nl80211")) {
        if (family_id_ < 0) {
            throw std::runtime_error("Модуль nl80211 не знайдено у ядрі");
        }
    }

    Wifi6Status query_interface(std::string_view ifname) {
        Wifi6Status status{};
        NlMessage msg;

        genlmsg_put(msg.get(), NL_AUTO_PID, NL_AUTO_SEQ, family_id_, 0, 0,
                   NL80211_CMD_GET_INTERFACE, 0);

        const unsigned int ifindex = if_nametoindex(ifname.data());
        if (ifindex == 0) {
            throw std::system_error(errno, std::generic_category(), "Невірний інтерфейс");
        }

        nla_put_u32(msg.get(), NL80211_ATTR_IFINDEX, ifindex);

        nl_socket_modify_cb(sock_.get(), NL_CB_VALID, NL_CB_CUSTOM,
            [](struct nl_msg* msg_ptr, void* arg) -> int {
                auto* st = static_cast<Wifi6Status*>(arg);
                struct nlmsghdr* nlh = nlmsg_hdr(msg_ptr);
                struct genlmsghdr* gnlh = static_cast<struct genlmsghdr*>(nlmsg_data(nlh));
                struct nlattr* tb[NL80211_ATTR_MAX + 1];

                nla_parse(tb, NL80211_ATTR_MAX, genlmsg_attrdata(gnlh, 0),
                          genlmsg_attrlen(gnlh, 0), nullptr);

                if (tb[NL80211_ATTR_BSS_COLOR]) {
                    st->bss_color = nla_get_u8(tb[NL80211_ATTR_BSS_COLOR]);
                }
                if (tb[NL80211_ATTR_HE_CAPABILITY]) {
                    st->has_he_support = true;
                }
                if (tb[NL80211_ATTR_WIPHY_FREQ]) {
                    st->frequency_mhz = nla_get_u32(tb[NL80211_ATTR_WIPHY_FREQ]);
                }
                return NL_SKIP;
            }, &status);

        if (nl_send_auto(sock_.get(), msg.get()) < 0) {
            throw std::runtime_error("Помилка відправки Netlink запиту");
        }

        nl_recvmsgs_default(sock_.get());
        return status;
    }

private:
    NlSocket sock_;
    int family_id_;
};

int main() {
    try {
        Wifi6NlClient client;
        auto status = client.query_interface("wlan0");

        std::cout << "--- Статус 802.11ax (mac80211) ---
";
        std::cout << "Підтримка HE: " << (status.has_he_support ? "ТАК" : "НІ") << "
";
        if (status.frequency_mhz > 0) {
            std::cout << "Частота каналу: " << status.frequency_mhz << " МГц
";
        }
        if (status.bss_color >= 0) {
            std::cout << "BSS Color: " << status.bss_color << "
";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "
";
        return 1;
    }
    return 0;
}
```
:::

## 5. Повна довідкова таблиця параметрів HE MCS (MCS 0..11)

Вказано теоретичну фізичну швидкість передачі даних для одного просторового потоку (`N_SS = 1`) при короткому захисному інтервалі (`T_GI = 0.8 мкс`):

| Індекс MCS | Модуляція | Кодова швидкість (R) | Швидкість у 20 МГц (Мбіт/с) | Швидкість у 80 МГц (Мбіт/с) | Швидкість у 160 МГц (Мбіт/с) | Поріг чутливості SNR (дБ) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MCS 0** | BPSK | 1/2 | 8.6 | 36.0 | 72.1 | 5.0 |
| **MCS 1** | QPSK | 1/2 | 17.2 | 72.1 | 144.1 | 8.0 |
| **MCS 2** | QPSK | 3/4 | 25.8 | 108.1 | 216.2 | 11.0 |
| **MCS 3** | 16-QAM | 1/2 | 34.4 | 144.1 | 288.2 | 14.0 |
| **MCS 4** | 16-QAM | 3/4 | 51.6 | 216.2 | 432.4 | 18.0 |
| **MCS 5** | 64-QAM | 2/3 | 68.8 | 288.2 | 576.5 | 21.0 |
| **MCS 6** | 64-QAM | 3/4 | 77.4 | 324.3 | 648.5 | 23.0 |
| **MCS 7** | 64-QAM | 5/6 | 86.0 | 360.3 | 720.6 | 25.0 |
| **MCS 8** | 256-QAM | 3/4 | 103.2 | 432.4 | 864.7 | 29.0 |
| **MCS 9** | 256-QAM | 5/6 | 114.7 | 480.4 | 960.8 | 31.0 |
| **MCS 10** | 1024-QAM | 3/4 | 129.0 | 540.4 | 1080.9 | 34.0 |
| **MCS 11** | 1024-QAM | 5/6 | 143.4 | 600.5 | 1201.0 | 36.0 |

При використанні конфігурації `8×8 MIMO` (8 просторових потоків) у каналі 160 МГц значення швидкості таблиці MCS 11 множиться на 8, що дає граничну швидкість **1201.0 × 8 = 9608 Мбіт/с (9.6 Гбіт/с)**.
