# ⚙️ Моніторинг автопогодження та евристичне виявлення Duplex Mismatch

Розсинхронізація дуплексу (**Duplex Mismatch**) належить до найпідступніших апаратних несправностей у комп'ютерних мережах. Оскільки базові утиліти діагностики на зразок `ping` оперують поодинокими пакетами малого розміру з великими паузами між ними, вони не створюють зустрічного трафіку і звітують про повну доступність вузла. Проте щойно через лінк починається інтенсивна передача даних по протоколу TCP, пропускна здатність каналу колапсує через лавину пізніх колізій (**Late Collisions**), втрату пакетів підтвердження ACK та експоненційне зростання тайм-аутів повторного передавання.

Стандартні системи моніторингу на основі протоколу SNMP або системні утиліти на зразок `netstat` часто групують усі типи збоїв у єдиний узагальнений лічильник помилок інтерфейсу (`ifInErrors` або `rx_errors`), що не дозволяє адміністратору чи системному демону швидко розпізнати першопричину збою. Для точного виявлення таких аномалій розробляють низькорівневі діагностичні утиліти, які напряму опитують трансивер PHY та детальні апаратні лічильники MAC-контролера через підсистему ядра **ethtool**.

Нижче наведено повну архітектуру, математичну модель евристики, робочу реалізацію діагностичного демона на мовах C та ідіоматичному C++20/C++23, а також детальний покроковий посібник із практичного тестування, аналізу мережевих дампів, кінцевих автоматів ядра та автоматичного усунення несправностей.

---

## 1. Архітектура підсистеми керування лінком у ядрі Linux

У ядрі Linux керування фізичним рівнем Ethernet розділене між кількома рівнями абстракції:
1. **Лінійний трансивер PHY**: кремнієва мікросхема, що підключена до процесора або MAC-контролера через послідовну шину керування MDIO/MDC;
2. **Підсистема ядра `phylib` / `phylink`**: кінцевий автомат ядра (стани `PHY_DOWN`, `PHY_STARTING`, `PHY_UP`, `PHY_RUNNING`, `PHY_NOLINK`, `PHY_RESUMING`), який обробляє апаратні переривання від лінії INT мікросхеми PHY, відстежує стан пачок FLP, таймери лінка та керує режимами роботи;
3. **Драйвер мережевого адаптера (MAC)**: реалізує набір функцій зворотного виклику `struct ethtool_ops`, надаючи користувацькому простору уніфікований інтерфейс до внутрішніх регістрів та апаратних лічильників ASIC;
4. **Користувацький простір (User Space)**: взаємодіє з ядром через системний виклик `ioctl` із сокетною командою `SIOCETHTOOL` або через сучасний протокол Generic Netlink (`NETLINK_GENERIC`, родина `ethtool`).

```general
[ User Space: link_monitor ]
             │
             ├──► socket(AF_INET, SOCK_DGRAM, 0)
             │          │
             │          ▼
             │    ioctl(fd, SIOCETHTOOL, &ifr)
             │          │
─────────────┼──────────┼────────────────────────────── Ядро Linux
             │          ▼
             │    dev_ioctl() ──► dev_ethtool()
             │                          │
             │                          ▼
             │                  struct ethtool_ops
             │                  ├── .get_link_ksettings()
             │                  ├── .get_sset_count()
             │                  ├── .get_strings()
             │                  └── .get_ethtool_stats()
             │                          │
             ▼                          ▼
[ Апаратний MAC-контролер ] ◄───► [ Трансивер PHY (MDIO) ]
```

### Кінцевий автомат `phylib` у ядрі Linux

У вихідному коді ядра (`drivers/net/phy/phy.c`) роботою трансивера керує центральна функція `phy_state_machine()`, яка виконується у фоновому потоці ядра з періодом 1 секунда (або миттєво викликається за апаратним перериванням від виводу INT трансивера):

```general
[ PHY_DOWN ] ──► phy_start() ──► [ PHY_STARTING ] ──► [ PHY_UP ]
                                                            │
                                                     phy_start_aneg()
                                                            │
                                                            ▼
[ PHY_RUNNING ] ◄── Link Up (BMSR_LSTATUS) ◄── [ PHY_AN (Чекаємо FLP) ]
       │                                                    │
  Втрата лінка                                       Таймаут FLP (1с)
       │                                                    │
       ▼                                                    ▼
 [ PHY_NOLINK ] ──► break_link_timer ──────────► [ Parallel Detection ]
```

* **`PHY_AN`**: Драйвер записує анонсовані біти в регістр `ANAR` (регістр 4) та `1000CR` (регістр 9), встановлює біт перезапуску `BMCR_ANRESTART` (регістр 0) і запускає таймер очікування;
* **`PHY_RUNNING`**: Після появи прапорця `BMSR_ANEGCOMPLETE` ядро зчитує регістри `ANLPAR` та `1000SR`, викликає функцію `phy_resolve_aneg_linkmode()` для розрахунку найвищого спільного знаменника HCD і конфігурує MAC-контролер на узгоджену швидкість та дуплекс.

### Різниця між програмними та апаратними лічильниками

У мережевому стеку Linux існує два принципово різні джерела статистики:
* **Програмні лічильники `net_device_stats`** (доступні через `ip -s link` або `/proc/net/dev`): підраховуються драйвером у ядрі на рівні обробки сокетних буферів `sk_buff`. Вони фіксують лише загальні скидання пакетів через брак пам'яті (`rx_dropped`) або збої виділення буферів кільця DMA;
* **Апаратні лічильники ASIC** (доступні через `ETHTOOL_GSTATS`): зчитуються напряму з внутрішніх регістрів накопичення кремнієвого MAC-контролера. Саме вони містять апаратні події фізичного рівня: пізні колізії (`late_collisions`), колізії після 16 спроб (`excessive_collisions`), помилки контрольної суми CRC (`rx_crc_errors`), порушення вирівнювання напівбайтів 4B5B/MLT-3 (`rx_align_errors`) та помилки несучої частоти (`carrier_errors`).

Для діагностики Duplex Mismatch програмні лічильники ядра є неінформативними, тому утиліта працює виключно з низькорівневими регістрами `ETHTOOL_GSTATS`.

### Команди `SIOCETHTOOL`

Для повної діагностики утиліта виконує три послідовні запити до ядра:

1. **`ETHTOOL_GSET` / `ETHTOOL_GLINKSETTINGS`**: повертає статус автопогодження (`autoneg`), поточну узгоджену швидкість (`speed`), режим дуплексу (`duplex`) та конфігурацію кросовера `eth_tp_mdix` (MDI, MDI-X або Auto);
2. **`ETHTOOL_GSSET_INFO` та `ETHTOOL_GSTRINGS`**: запитує кількість та текстові назви всіх апаратних лічильників, які підтримує конкретна мережева карта (наприклад, `tx_late_collisions`, `rx_crc_errors`, `align_errors`);
3. **`ETHTOOL_GSTATS`**: зчитує поточні 64-розрядні значення всіх статистичних регістрів MAC-контролера.

---

## 2. Евристична модель виявлення Duplex Mismatch

Розсинхронізація дуплексу призводить до строго визначених асиметричних аномалій у лічильниках двох з'єднаних вузлів. Нехай локальний вузол виконує періодичне опитування лічильників з інтервалом `Δt = 1 с`. Позначимо приріст лічильників за інтервал як:

```general
Δ_late  = LateCollisions(t) - LateCollisions(t - Δt)
Δ_crc   = CrcErrors(t) - CrcErrors(t - Δt)
Δ_align = AlignErrors(t) - AlignErrors(t - Δt)
Δ_tx    = TxPackets(t) - TxPackets(t - Δt)
```

### Математична логіка класифікації стану лінії:

1. **Сценарій A: Локальний вузол у Half Duplex, віддалений партнер у Full Duplex**:
   * Оскільки віддалений вузол передає кадри в будь-який момент без прослуховування лінії, колізії на локальному вузлі виникають після передавання перших 64 байтів (512 бітових інтервалів);
   * Критерій: `Duplex == Half` ТА `Δ_late > 0`;
   * Якщо при активному вихідному трафіку (`Δ_tx > 50`) швидкість пізніх колізій перевищує поріг `Δ_late / Δ_tx > 0.05` (понад 5% переданих кадрів зазнають пізніх колізій) — фіксується **критичний Duplex Mismatch**;

2. **Сценарій B: Локальний вузол у Full Duplex, віддалений партнер у Half Duplex**:
   * Локальний вузол не використовує CSMA/CD, тому його власний лічильник колізій завжди дорівнює нулю;
   * Проте кадри, які відправляє локальний вузол, переривають передачу напівдуплексного партнера. Партнер видає сигнал глушіння (JAM) або раптово обриває передачу, внаслідок чого локальний приймач отримує понівечені фрагменти з невірною контрольною сумою CRC або порушеним вирівнюванням байтів (Alignment Error);
   * Критерій: `Duplex == Full` ТА `(Δ_crc > 5 АБО Δ_align > 5)` за наявності зустрічного трафіку;

3. **Сценарій C: Штатний напівдуплексний режим (Half Duplex з обох боків)**:
   * Звичайні колізії відбуваються виключно в межах перших 64 байтів;
   * Критерій: `Δ_early_collisions > 0`, але `Δ_late == 0` та `Δ_crc == 0`. Мережа працює в межах норми CSMA/CD.

---

## 3. Реалізація утиліти на C та ідіоматичному C++

Нижче наведено вихідний код діагностичної утиліти. Версія на C демонструє роботу з низькорівневими системними викликами та динамічними буферами ядра, а версія на C++20/C++23 надає безпечну об'єктну модель із використанням концепції RAII, типів `std::expected`, `std::string_view` та виключенням ручного керування пам'яттю.

:::tabs
```c
/* link_monitor.c — Моніторинг параметрів PHY та виявлення Duplex Mismatch */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

#define ETH_GSTRING_LEN 32

/* Структура для збереження лічильників помилок */
struct error_stats {
    unsigned long long late_collisions;
    unsigned long long crc_errors;
    unsigned long long align_errors;
    unsigned long long tx_packets;
};

/* Отримання назв статистичних лічильників адаптера */
static struct ethtool_gstrings* get_stat_strings(int fd, const char* ifname, int* n_stats) {
    struct {
        struct ethtool_sset_info hdr;
        unsigned int buf[1];
    } sset_info;
    memset(&sset_info, 0, sizeof(sset_info));
    sset_info.hdr.cmd = ETHTOOL_GSSET_INFO;
    sset_info.hdr.sset_mask = 1ULL << ETH_SS_STATS;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)&sset_info;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        return NULL;
    }
    if (!sset_info.hdr.sset_mask) {
        return NULL;
    }

    *n_stats = sset_info.hdr.data[0];
    if (*n_stats == 0) {
        return NULL;
    }

    size_t sz = sizeof(struct ethtool_gstrings) + (*n_stats) * ETH_GSTRING_LEN;
    struct ethtool_gstrings* strings = (struct ethtool_gstrings*)malloc(sz);
    if (!strings) {
        return NULL;
    }

    memset(strings, 0, sz);
    strings->cmd = ETHTOOL_GSTRINGS;
    strings->string_set = ETH_SS_STATS;
    strings->len = *n_stats;

    ifr.ifr_data = (char*)strings;
    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        free(strings);
        return NULL;
    }

    return strings;
}

/* Зчитування поточних значень лічильників помилок */
static int read_error_stats(int fd, const char* ifname, const struct ethtool_gstrings* strings,
                            int n_stats, struct error_stats* out_stats) {
    memset(out_stats, 0, sizeof(*out_stats));
    if (!strings || n_stats <= 0) {
        return -1;
    }

    size_t sz = sizeof(struct ethtool_stats) + n_stats * sizeof(unsigned long long);
    struct ethtool_stats* stats = (struct ethtool_stats*)malloc(sz);
    if (!stats) {
        return -1;
    }

    memset(stats, 0, sz);
    stats->cmd = ETHTOOL_GSTATS;
    stats->n_stats = n_stats;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)stats;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        free(stats);
        return -1;
    }

    for (int i = 0; i < n_stats; ++i) {
        const char* name = (const char*)&strings->data[i * ETH_GSTRING_LEN];
        unsigned long long val = stats->data[i];

        if (strstr(name, "late_collision") || strstr(name, "tx_late_collision")) {
            out_stats->late_collisions += val;
        } else if (strstr(name, "crc_error") || strstr(name, "rx_crc_errors")) {
            out_stats->crc_errors += val;
        } else if (strstr(name, "align_error") || strstr(name, "rx_align_errors")) {
            out_stats->align_errors += val;
        } else if (strstr(name, "tx_packets") || strstr(name, "tx_ok")) {
            out_stats->tx_packets += val;
        }
    }

    free(stats);
    return 0;
}

/* Опитування параметрів лінка через ETHTOOL_GSET */
static int print_link_status(int fd, const char* ifname, int* out_duplex) {
    struct ethtool_cmd ecmd;
    memset(&ecmd, 0, sizeof(ecmd));
    ecmd.cmd = ETHTOOL_GSET;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)&ecmd;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        perror("Помилка ioctl(ETHTOOL_GSET)");
        return -1;
    }

    *out_duplex = ecmd.duplex;
    unsigned int speed = ethtool_cmd_speed(&ecmd);

    printf("=== Інтерфейс %s ===\n", ifname);
    printf("Швидкість:        ");
    if (speed == (unsigned int)-1 || speed == 0) {
        printf("Невідома (Link Down)\n");
    } else {
        printf("%u Мбіт/с\n", speed);
    }

    printf("Дуплекс:          %s\n", (ecmd.duplex == DUPLEX_FULL) ? "Full Duplex" :
                                      (ecmd.duplex == DUPLEX_HALF) ? "Half Duplex" : "Невідомо");
    printf("Автопогодження:   %s\n", (ecmd.autoneg == AUTONEG_ENABLE) ? "Увімкнено (Enabled)" : "Вимкнено (Disabled)");

    printf("Режим MDI/MDI-X:  ");
    switch (ecmd.eth_tp_mdix) {
        case ETH_TP_MDI:   printf("MDI (прямий)\n"); break;
        case ETH_TP_MDI_X: printf("MDI-X (перехресний)\n"); break;
        default:           printf("Автовизначення / Не підтримується\n"); break;
    }

    return 0;
}

int main(int argc, char** argv) {
    const char* ifname = (argc > 1) ? argv[1] : "eth0";

    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        perror("Не вдалося створити діагностичний сокет");
        return 1;
    }

    int duplex_mode = DUPLEX_HALF;
    if (print_link_status(fd, ifname, &duplex_mode) < 0) {
        close(fd);
        return 1;
    }

    int n_stats = 0;
    struct ethtool_gstrings* strings = get_stat_strings(fd, ifname, &n_stats);
    if (!strings) {
        printf("Апаратна статистика ETHTOOL_GSTATS недоступна для %s\n", ifname);
        close(fd);
        return 0;
    }

    printf("\nЗапуск моніторингу помилок Duplex Mismatch (Ctrl+C для виходу)...\n");
    struct error_stats prev_stats, curr_stats;
    read_error_stats(fd, ifname, strings, n_stats, &prev_stats);

    for (int sec = 1; sec <= 10; ++sec) {
        sleep(1);
        if (read_error_stats(fd, ifname, strings, n_stats, &curr_stats) < 0) {
            break;
        }

        unsigned long long d_late = curr_stats.late_collisions - prev_stats.late_collisions;
        unsigned long long d_crc = curr_stats.crc_errors - prev_stats.crc_errors;

        if (d_late > 0 || d_crc > 0) {
            printf("[УВАГА +%ds] Пізні колізії: +%llu, Помилки CRC: +%llu -> ",
                   sec, d_late, d_crc);
            if (d_late > 5 && duplex_mode == DUPLEX_HALF) {
                printf("КРИТИЧНО: Duplex Mismatch (ми в Half Duplex, партнер у Full Duplex)!\n");
            } else if (d_crc > 5 && duplex_mode == DUPLEX_FULL) {
                printf("КРИТИЧНО: Duplex Mismatch (ми у Full Duplex, партнер у Half Duplex)!\n");
            } else {
                printf("Зафіксовано поодинокі збої лінії.\n");
            }
        } else {
            printf("[OK +%ds] Колізій та помилок CRC немає.\n", sec);
        }

        prev_stats = curr_stats;
    }

    free(strings);
    close(fd);
    return 0;
}
```
```cpp
// link_monitor.cpp — Ідіоматичний C++20 монітор фізичного рівня та Duplex Mismatch
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

namespace net {

// RAII обгортка для файлового дескриптора діагностичного сокета
class SocketHandle {
    int m_fd{-1};
public:
    SocketHandle() : m_fd{::socket(AF_INET, SOCK_DGRAM, 0)} {}
    ~SocketHandle() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : m_fd{other.m_fd} { other.m_fd = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_valid() const noexcept { return m_fd >= 0; }
    [[nodiscard]] int native_handle() const noexcept { return m_fd; }
};

struct ErrorStats {
    uint64_t late_collisions{0};
    uint64_t crc_errors{0};
    uint64_t align_errors{0};
    uint64_t tx_packets{0};
};

struct LinkInfo {
    uint32_t speed_mbps{0};
    bool is_full_duplex{false};
    bool autoneg_enabled{false};
    std::string mdix_status;
};

class LinkMonitor {
    SocketHandle m_sock;
    std::string m_ifname;
    std::vector<std::string> m_stat_names;

public:
    explicit LinkMonitor(std::string_view ifname) : m_ifname{ifname} {
        if (!m_sock.is_valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити діагностичний сокет");
        }
        load_stat_strings();
    }

    [[nodiscard]] std::expected<LinkInfo, std::error_code> get_link_info() const {
        ethtool_cmd ecmd{};
        ecmd.cmd = ETHTOOL_GSET;

        ifreq ifr{};
        std::strncpy(ifr.ifr_name, m_ifname.c_str(), IFNAMSIZ - 1);
        ifr.ifr_data = reinterpret_cast<char*>(&ecmd);

        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        LinkInfo info;
        uint32_t sp = ethtool_cmd_speed(&ecmd);
        info.speed_mbps = (sp == static_cast<uint32_t>(-1)) ? 0 : sp;
        info.is_full_duplex = (ecmd.duplex == DUPLEX_FULL);
        info.autoneg_enabled = (ecmd.autoneg == AUTONEG_ENABLE);

        switch (ecmd.eth_tp_mdix) {
            case ETH_TP_MDI:   info.mdix_status = "MDI (прямий)"; break;
            case ETH_TP_MDI_X: info.mdix_status = "MDI-X (перехресний)"; break;
            default:           info.mdix_status = "Автовизначення / Не підтримується"; break;
        }

        return info;
    }

    [[nodiscard]] std::expected<ErrorStats, std::error_code> read_error_stats() const {
        if (m_stat_names.empty()) {
            return ErrorStats{};
        }

        size_t sz = sizeof(ethtool_stats) + m_stat_names.size() * sizeof(uint64_t);
        std::vector<uint8_t> buffer(sz);
        auto* stats = reinterpret_cast<ethtool_stats*>(buffer.data());
        stats->cmd = ETHTOOL_GSTATS;
        stats->n_stats = static_cast<uint32_t>(m_stat_names.size());

        ifreq ifr{};
        std::strncpy(ifr.ifr_name, m_ifname.c_str(), IFNAMSIZ - 1);
        ifr.ifr_data = reinterpret_cast<char*>(stats);

        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ErrorStats errs;
        for (size_t i = 0; i < m_stat_names.size(); ++i) {
            const auto& name = m_stat_names[i];
            uint64_t val = stats->data[i];

            if (name.find("late_collision") != std::string::npos) {
                errs.late_collisions += val;
            } else if (name.find("crc_error") != std::string::npos || name.find("rx_crc_errors") != std::string::npos) {
                errs.crc_errors += val;
            } else if (name.find("align_error") != std::string::npos) {
                errs.align_errors += val;
            } else if (name.find("tx_packets") != std::string::npos || name.find("tx_ok") != std::string::npos) {
                errs.tx_packets += val;
            }
        }
        return errs;
    }

private:
    void load_stat_strings() {
        struct {
            ethtool_sset_info hdr;
            uint32_t buf[1];
        } sset_info{};
        sset_info.hdr.cmd = ETHTOOL_GSSET_INFO;
        sset_info.hdr.sset_mask = 1ULL << ETH_SS_STATS;

        ifreq ifr{};
        std::strncpy(ifr.ifr_name, m_ifname.c_str(), IFNAMSIZ - 1);
        ifr.ifr_data = reinterpret_cast<char*>(&sset_info);

        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) < 0 || !sset_info.hdr.sset_mask) {
            return;
        }

        uint32_t count = sset_info.hdr.data[0];
        if (count == 0) return;

        size_t sz = sizeof(ethtool_gstrings) + count * ETH_GSTRING_LEN;
        std::vector<uint8_t> str_buf(sz);
        auto* gstrings = reinterpret_cast<ethtool_gstrings*>(str_buf.data());
        gstrings->cmd = ETHTOOL_GSTRINGS;
        gstrings->string_set = ETH_SS_STATS;
        gstrings->len = count;

        ifr.ifr_data = reinterpret_cast<char*>(gstrings);
        if (::ioctl(m_sock.native_handle(), SIOCETHTOOL, &ifr) == 0) {
            m_stat_names.reserve(count);
            for (uint32_t i = 0; i < count; ++i) {
                const char* s = reinterpret_cast<const char*>(&gstrings->data[i * ETH_GSTRING_LEN]);
                m_stat_names.emplace_back(s);
            }
        }
    }
};

} // namespace net

int main(int argc, char** argv) {
    const std::string ifname = (argc > 1) ? argv[1] : "eth0";

    try {
        net::LinkMonitor monitor{ifname};
        auto link_res = monitor.get_link_info();

        if (!link_res) {
            std::cerr << "Помилка отримання статусу лінка: " << link_res.error().message() << '\n';
            return 1;
        }

        const auto& info = *link_res;
        std::cout << "=== Інтерфейс " << ifname << " ===\n"
                  << "Швидкість:      " << (info.speed_mbps == 0 ? "Link Down" : std::to_string(info.speed_mbps) + " Мбіт/с") << '\n'
                  << "Дуплекс:        " << (info.is_full_duplex ? "Full Duplex" : "Half Duplex") << '\n'
                  << "Автопогодження: " << (info.autoneg_enabled ? "Увімкнено" : "Вимкнено") << '\n'
                  << "MDI/MDI-X стан: " << info.mdix_status << "\n\n"
                  << "Моніторинг лічильників Duplex Mismatch (10 ітерацій)...\n";

        auto prev_stats = monitor.read_error_stats().value_or(net::ErrorStats{});

        for (int i = 1; i <= 10; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            auto curr_res = monitor.read_error_stats();
            if (!curr_res) break;

            const auto& curr = *curr_res;
            uint64_t d_late = curr.late_collisions - prev_stats.late_collisions;
            uint64_t d_crc = curr.crc_errors - prev_stats.crc_errors;

            if (d_late > 0 || d_crc > 0) {
                std::cout << "[УВАГА +" << i << "s] Пізні колізії: +" << d_late
                          << ", CRC помилки: +" << d_crc << " -> ";
                if (d_late > 5 && !info.is_full_duplex) {
                    std::cout << "КРИТИЧНО: Duplex Mismatch (локальний у Half Duplex, партнер у Full Duplex)!\n";
                } else if (d_crc > 5 && info.is_full_duplex) {
                    std::cout << "КРИТИЧНО: Duplex Mismatch (локальний у Full Duplex, партнер у Half Duplex)!\n";
                } else {
                    std::cout << "Поодинокі помилки кадру лінії.\n";
                }
            } else {
                std::cout << "[OK +" << i << "s] Помилок немає.\n";
            }
            prev_stats = curr;
        }

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

---

## 4. Покроковий розбір коду та технічні пастки

Під час роботи з підсистемою `ethtool` та низькорівневими сокетами у системному програмуванні виникають специфічні нюанси, які необхідно враховувати для створення надійного програмного забезпечення.

### 1. Динамічне виділення пам'яті під структури змінної довжини

Структура `struct ethtool_gstrings` у заголовку `<linux/ethtool.h>` оголошена з гнучким масивом наприкінці (`__u8 data[0]` або `data[]` у C99). Розмір цього масиву не фіксований і залежить від кількості лічильників, які драйвер конкретної мережевої карти експортує в ядро:

```general
Розмір буфера = sizeof(struct ethtool_gstrings) + (Кількість_лічильників · 32 байти)
```

Спроба виділити статичний буфер фіксованого розміру на стеку є небезпечною помилкою: на серверних адаптерах Intel (драйвер `ixgbe` або `ice`) кількість статистичних лічильників черг RSS може перевищувати 200, що призведе до переповнення буфера або помилки `EINVAL` при виклику `ioctl`.

У наведеній реалізації розмір попередньо запитується в ядра через команду `ETHTOOL_GSSET_INFO` з маскою `ETH_SS_STATS`, після чого виділяється буфер точного розміру. У C++ версії це реалізовано через безпечний контейнер `std::vector<uint8_t>`, пам'ять якого автоматично звільняється при виході з області видимості.

### 2. Неоднорідність назв лічильників між виробниками ASIC

Стандарт ядра Linux не фіксує єдиних назв для лічильників помилок фізичного та канального рівнів. Кожен виробник називає їх відповідно до внутрішньої термінології документації на свій чіп:

* **Intel (`e1000e`, `igb`, `ixgbe`)**: використовує назви `tx_late_collision_errors`, `late_collisions`, `rx_crc_errors`, `rx_align_errors`;
* **Realtek (`r8169`)**: експортує назви `late_collisions`, `tx_late_col`, `rx_crc_errors`;
* **Broadcom (`tg3`, `bnx2`)**: використовує `dot3StatsLateCollisions`, `dot3StatsFCSErrors`, `dot3StatsAlignmentErrors`;
* **Mellanox (`mlx5_core`)**: оперує назвами `rx_crc_errors_phy`, `tx_pause_ctrl_phy`;
* **Віртуальні інтерфейси (`virtio_net`, `vmxnet3`)**: у віртуалізованих середовищах фізичний рівень емулюється гіпервізором, тому лічильники колізій та регістри MDIO зазвичай повертають нуль або статус `EOPNOTSUPP`.

З цієї причини код не спирається на жорсткі індекси масиву, а виконує пошук підрядка (`strstr` у C та `std::string::find` у C++) за ключовими словами `late_collision`, `crc_error` та `align_error`.

### 3. Значення швидкості при відключеному кабелі (Link Down)

Якщо мережевий кабель фізично від'єднано, виклик `ioctl(..., ETHTOOL_GSET, ...)` повертає успішний статус `0`, але поле швидкості містить константу `SPEED_UNKNOWN` (визначається в ядрі як `(uint32_t)-1` або `65535` у 16-бітному представленні). Без перевірки цього значення утиліта виведе абсурдну швидкість `4294967295 Мбіт/с` або `65535 Мбіт/с`. У функції `get_link_info()` це значення явно перевіряється і замінюється на нуль із виведенням повідомлення `Link Down`.

### 4. Особливості безпеки та виклики без винятків у C++

У класі `LinkMonitor` застосовано сучасні ідіоми C++20/C++23:
* Тип `std::expected<T, std::error_code>` повертає або валідну структуру результату, або код системної помилки, що дозволяє уникнути накладних витрат механізму винятків у критичних за часом циклах моніторингу;
* Клас `SocketHandle` інкапсулює файловий дескриптор сокета за патерном RAII, гарантуючи закриття сокета при будь-якому поверненні з функції (включно з аварійними гілками);
* Заборона копіювання (`delete`) та реалізація семантики переміщення (`noexcept move constructor/assignment`) унеможливлюють подвійне закриття одного й того самого дескриптора.

---

## 5. Взаємодія через Netlink (сучасна альтернатива `ioctl`)

Починаючи з версії ядра Linux 5.6, підсистема `ethtool` отримала новий інтерфейс на основі протоколу **Generic Netlink** (`linux/ethtool_netlink.h`), який вирішує фундаментальні обмеження старого `ioctl(SIOCETHTOOL)`:

```general
Типи повідомлень Netlink ethtool:
• ETHTOOL_MSG_LINKINFO_GET:  Запит швидкості, дуплексу та порту (заміна ETHTOOL_GSET)
• ETHTOOL_MSG_LINKMODES_GET: Запит бітових масок анонсів довільної довжини
• ETHTOOL_MSG_LINKSTATE_GET: Запит статусу наявності сигналу несучої та сплячого режиму
• ETHTOOL_MSG_STATS_GET:     Запит структурованої статистики за категоріями IEEE 802.3
```

Головна перевага Netlink полягає у підтримці **асинхронних широкомовних сповіщень** (`ETHTOOL_MSG_LINKSTATE_NTF`). Замість постійного опитування в безкінечному циклі (`polling`), системний демон підписується на групу мультикасту Netlink і засинає в системному виклику `epoll_wait()`. Щойно кабель від'єднують або змінюється стан дуплексу, ядро миттєво пробуджує процес, передаючи готове повідомлення про подію фізичного рівня.

### Асинхронний моніторинг несучої через сокети `NETLINK_ROUTE`

Окрім опитування через `SIOCETHTOOL` та Generic Netlink, для відстеження миттєвого зникнення фізичного лінка (висмикування кабелю або вимкнення живлення комутатора) утиліти високої доступності відкривають сокет `NETLINK_ROUTE` із підпискою на групу подій `RTMGRP_LINK`:

```general
Послідовність обробки асинхронної події Link Down:
1. Системний виклик socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
2. Прив'язка до групи подій RTMGRP_LINK через bind();
3. Очікування повідомлень RTM_NEWLINK у циклі poll() / epoll();
4. Аналіз прапорців ifinfomsg.ifi_flags:
   • Прапорець IFF_RUNNING = 0  ──► Фізичний лінк втрачено (NO CARRIER)
   • Прапорець IFF_RUNNING = 1  ──► Фізичний лінк піднято (CARRIER OK)
```

Поєднання асинхронного сокета `NETLINK_ROUTE` для фіксації переходу `Link Up` та регулярного зчитування `ETHTOOL_GSTATS` під час активного трафіку дозволяє створити бездоганний діагностичний агент із нульовим навантаженням на процесор у режимі спокою та мілісекундною реакцією на виникнення колізійних аномалій.

---

## 6. Компіляція, тестування та діагностика в лабораторії

### Компіляція

Для збірки утиліти потрібен компілятор GCC або Clang із підтримкою стандарту C11 для C-версії та стандарту C++20/C++23 для C++ версії:

```bash
# Збірка версії на C
gcc -O2 -Wall -Wextra -std=c11 link_monitor.c -o link_monitor_c

# Збірка версії на C++ (вимагає g++-13 або clang++-16 для std::expected)
g++ -O2 -Wall -Wextra -std=c++23 link_monitor.cpp -o link_monitor_cpp
```

### Права доступу та Linux Capabilities

Виклики `ioctl` із командою `SIOCETHTOOL` для читання статистики зазвичай дозволені звичайним користувачам, проте на деяких дистрибутивах із посиленою безпекою (RHEL/SELinux) для доступу до структур PHY потрібні привілеї адміністратора або розширений біт безпеки `CAP_NET_ADMIN`:

```bash
# Надання привілеїв без запуску через повний root
sudo setcap cap_net_admin=ep ./link_monitor_cpp
./link_monitor_cpp eth0
```

### Створення штучного Duplex Mismatch для тестування

Для перевірки роботи евристики в лабораторних умовах можна штучно створити стан розсинхронізації дуплексу на стенді з двома комп'ютерами або керованим комутатором:

1. На комутаторі примусово вимикаємо автопогодження та виставляємо 100 Мбіт/с Full Duplex:
   ```console
   Switch(config-if)# speed 100
   Switch(config-if)# duplex full
   ```
2. На тестовому сервері залишаємо автопогодження увімкненим. Через Parallel Detection сервер перейде у 100 Мбіт/с Half Duplex:
   ```bash
   sudo ethtool eth0 | grep -E 'Speed|Duplex|Auto-negotiation'
   # Результат: Speed: 100Mb/s, Duplex: Half, Auto-negotiation: on
   ```
3. Запускаємо наш монітор:
   ```bash
   ./link_monitor_cpp eth0
   ```
4. В іншому терміналі генеруємо двонаправлений потік трафіку за допомогою утиліти `iperf3`:
   ```bash
   iperf3 -c 192.168.1.1 -d -t 10
   ```
5. Спостерігаємо вивід утиліти:
   ```console
   === Інтерфейс eth0 ===
   Швидкість:      100 Мбіт/с
   Дуплекс:        Half Duplex
   Автопогодження: Увімкнено
   MDI/MDI-X стан: MDI (прямий)

   Моніторинг лічильників Duplex Mismatch (10 ітерацій)...
   [OK +1s] Помилок немає.
   [УВАГА +2s] Пізні колізії: +142, CRC помилки: +0 -> КРИТИЧНО: Duplex Mismatch (локальний у Half Duplex, партнер у Full Duplex)!
   [УВАГА +3s] Пізні колізії: +389, CRC помилки: +0 -> КРИТИЧНО: Duplex Mismatch (локальний у Half Duplex, партнер у Full Duplex)!
   [УВАГА +4s] Пізні колізії: +512, CRC помилки: +0 -> КРИТИЧНО: Duplex Mismatch (локальний у Half Duplex, партнер у Full Duplex)!
   ```

### Тестування у віртуалізованих лабораторіях (Network Namespaces)

Якщо під рукою немає фізичного комутатора, взаємодію сокетів та алгоритми моніторингу можна перевірити у віртуалізованому оточенні Linux за допомогою ізольованих мережевих просторів імен (Network Namespaces) та віртуальних пар інтерфейсів `veth`:

```bash
# Створення двох ізольованих просторів імен
sudo ip netns add ns_server
sudo ip netns add ns_switch

# Створення зв'язаної пари veth
sudo ip link add veth_srv type veth peer name veth_sw

# Переміщення інтерфейсів у відповідні простори
sudo ip link set veth_srv netns ns_server
sudo ip link set veth_sw netns ns_switch

# Налаштування IP-адрес та активація
sudo ip netns exec ns_server ip addr add 192.168.50.1/24 dev veth_srv
sudo ip netns exec ns_server ip link set veth_srv up
sudo ip netns exec ns_switch ip addr add 192.168.50.2/24 dev veth_sw
sudo ip netns exec ns_switch ip link set veth_sw up
```

Хоча драйвер `veth` емулює ідеальне програмне середовище без фізичних колізій, такий тестовий стенд дозволяє повністю відлагодити логіку обробки сокетів, роботу з Netlink та структуру виводу діагностичного демона.

---

### Одночасний аналіз мережевих дампів через `tcpdump`

Якщо під час роботи утиліти паралельно запустити захоплення пакетів:

```bash
sudo tcpdump -i eth0 -nn -vvv 'tcp'
```

у дампі чітко видно симптоми аварії:
* Поява масових прапорців `[TCP Retransmission]` та `[TCP Fast Retransmit]`;
* Збільшення інтервалів між повторами від 200 мс до 1, 2, 4 та 8 секунд (експоненційне зростання RTO);
* Численні повідомлення `[TCP Dup ACK]` від приймача, який марно очікує пропущений уламок потоку;
* Повне падіння середнього вікна ковзання `win` до значення `MSS` (1460 байтів).

---

## 7. Дерево рішень та алгоритм автоматичного усунення несправностей

Для чергових інженерів центрів обробки даних (SRE / NOC) діагностичний процес при деградації продуктивності порту зводиться до такого покрокового алгоритму:

```general
1. Фізичний стан (Link Check):
   ├── Link Down ──► Перевірити живлення PHY, кабель, виконати TDR тест кабелю
   └── Link Up ────► Крок 2

2. Перевірка автопогодження:
   ├── Auto-neg: Off ──► Увімкнути Auto-Negotiation (ethtool -s <iface> autoneg on)
   └── Auto-neg: On  ──► Крок 3

3. Опитування лічильників помилок (ETHTOOL_GSTATS):
   ├── Δ_late > 0 && Duplex == Half ──► Duplex Mismatch (партнер у Forced Full).
   │                                    Рішення: увімкнути автопогодження на комутаторі.
   ├── Δ_crc > 0  && Duplex == Full ──► Duplex Mismatch (партнер у Half) АБО пошкодження кабелю.
   │                                    Рішення: перевірити порт комутатора та замінити патч-корд.
   └── Помилок немає ─────────────────► Проблема лежить на вищих рівнях стеку (L3/L4/MTU).
```

### Програмне відновлення зв'язку (Auto-Remediation)

Якщо системний демон `link_monitor` фіксує критичний Duplex Mismatch на керованому сервері, він може автоматично відновити працездатність інтерфейсу, надіславши команду `ETHTOOL_SSET` для перезапуску автопогодження або скидання мікросхеми PHY:

:::tabs
```c
/* Приклад програмного перезапуску автопогодження на C */
static int restart_autoneg(int fd, const char* ifname) {
    struct ethtool_cmd ecmd;
    memset(&ecmd, 0, sizeof(ecmd));
    ecmd.cmd = ETHTOOL_GSET;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)&ecmd;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        return -1;
    }

    ecmd.cmd = ETHTOOL_SSET;
    ecmd.autoneg = AUTONEG_ENABLE;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        return -1;
    }

    return 0;
}
```
```cpp
// Приклад програмного перезапуску автопогодження на C++20
[[nodiscard]] inline std::expected<void, std::error_code> restart_autoneg(
    const net::SocketHandle& sock, std::string_view ifname) noexcept {
    ethtool_cmd ecmd{};
    ecmd.cmd = ETHTOOL_GSET;

    ifreq ifr{};
    std::strncpy(ifr.ifr_name, ifname.data(), IFNAMSIZ - 1);
    ifr.ifr_data = reinterpret_cast<char*>(&ecmd);

    if (::ioctl(sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ecmd.cmd = ETHTOOL_SSET;
    ecmd.autoneg = AUTONEG_ENABLE;

    if (::ioctl(sock.native_handle(), SIOCETHTOOL, &ifr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}
```
:::

### Особливості діагностики агрегованих інтерфейсів (Bonding / LACP)

У високопродуктивних серверах мережеві порти часто об'єднуються в агреговані канали за допомогою драйвера `bonding` або протоколу **LACP (IEEE 802.3ad)**.

При цьому виникає важлива діагностична особливість:
* Логічний віртуальний інтерфейс `bond0` **не має власного PHY-трансивера** і не підтримує команди `ETHTOOL_GSTATS` для зчитування апаратних колізій (спроба виклику `ioctl` на `bond0` повертає нуль або помилку `EOPNOTSUPP`);
* Якщо один із фізичних рабських портів (англ. *slave*, наприклад `eth1`) зазнає розсинхронізації дуплексу, балансувальник LACP продовжуватиме надсилати через нього 50% трафіку, спричиняючи спорадичні втрати пакетів без видимих збоїв на `bond0`;
* **Правило аудиту**: системний монітор зобов'язаний зчитувати список рабських інтерфейсів із файлу `/sys/class/net/bond0/bonding/slaves` і виконувати побітову діагностику `ETHTOOL_GSTATS` **окремо для кожного фізичного інтерфейсу** (`eth0`, `eth1`), який входить до складу агрегації.

### Експорт метрик у системи Prometheus та Grafana

Для інтеграції діагностики в загальнокорпоративні системи моніторингу результати евристики транслюються у стандартний текстовий формат OpenMetrics:

```general
# HELP node_network_late_collisions_total Total number of late collisions detected by ASIC
# TYPE node_network_late_collisions_total counter
node_network_late_collisions_total{device="eth0"} 14820

# HELP node_network_duplex_mismatch_state Duplex mismatch detection heuristic (0=OK, 1=Mismatch)
# TYPE node_network_duplex_mismatch_state gauge
node_network_duplex_mismatch_state{device="eth0",local_duplex="half",remote_guess="full"} 1
```

Алертинг за правилом `rate(node_network_late_collisions_total[2m]) > 1` дозволяє черговій зміні автоматично отримувати інциденти у PagerDuty ще до того, як користувачі поскаржаться на повільну роботу сервісів.

---

### Інтеграція в системні сторожові таймери (Watchdog)

Для критично важливих шлюзів та edge-серверів таку функцію доцільно вбудовувати безпосередньо в системні демони надійності:
1. **Періодичний фоновий аудит**: раз на хвилину демон виконує вибірку лічильників фізичного рівня;
2. **Згладжування стрибків через експоненційне ковзне середнє (EMA)**: для відсікання випадкових одиничних сплесків завад від електродвигунів або грозових розрядів швидкість колізій фільтрується за формулою:
   
   ```general
   EMA(t) = α · Δ_late + (1 - α) · EMA(t - 1),   де α = 0.2
   ```

3. **Тригер відновлення**: якщо значення `EMA` перевищує поріг протягом трьох послідовних вибірок, демон ініціює скидання PHY або відправляє алерт через протокол syslog/Prometheus.

Такий комплексний підхід гарантує повну автоматизацію діагностики фізичного рівня та усуває людський фактор при експлуатації корпоративних та датацентрових Ethernet-мереж.
