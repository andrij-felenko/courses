# ⚙️ Емулятор маршрутизації: зірка, дерево й динамічна чарунка

У розробці вбудованих систем вибір мережевої топології безпосередньо диктує структуру мережевого стека, обсяг необхідної оперативної пам'яті (RAM), споживання струму та алгоритм пересилання пакетів (*Forwarding Engine*). На відміну від серверних систем, де ресурси маршрутизації практично безмежні, мікроконтролер із 8–64 кБ RAM змушений шукати баланс між складністю алгоритму та надійністю доставки.

Цей проєкт реалізує компактний, повністю автономний емулятор мережевого рушія маршрутизації для трьох ключових архітектур бездротових та вбудованих систем:
1. **Зірка (*Star*)**: тривіальний безумовний роутинг на шлюз/концентратор без динамічного стану в оперативній пам'яті.
2. **Кластерне дерево (*Cluster-Tree / Cskip*)**: детермінована ієрархічна префіксна маршрутизація на основі числового діапазону адрес піддерева без таблиць у RAM.
3. **Динамічна чарунка (*Mesh*)**: дистанційно-векторна маршрутизація з підтримкою таблиці сусідів, метрикою якості зв'язку (*Link Cost / ETX*) та миттєвим локальним самовідновленням (*Local Repair*) у разі обриву лінку.

### Архітектура та інженерні механізми рушія

Кожен мережевий пакет у симуляторі моделюється структурою `Packet`, що містить адресу відправника (`src`), адресу кінцевого призначення (`dst`), лічильник граничної кількості стрибків (`ttl`), лічильник фактично пройдених хопів (`hop_count`) та корисне навантаження (`payload`).

#### 1. Модуль Зірки (Star Engine)
Кінцевий пристрій у топології зірка не виконує аналізу мережевого графа. Логіка вузла зводиться до перевірки:
- Якщо `pkt->dst == self_addr` — пакет досяг адресата.
- Якщо `self_addr == hub_addr` — центральний шлюз має прямі радіолінки до всіх периферійних абонентів і передає кадр безпосередньо одержувачу.
- Для будь-якого іншого вузла — пакет безумовно надсилається на адресу `hub_addr`.

Витрати пам'яті на кінцевому датчику становлять рівно `0 байтів`, що робить зірку ідеальною для ультраощадних пристроїв на базі крихітних МК.

#### 2. Модуль Кластерного Дерева (Cskip Engine)
Деревоподібний форвардинг реалізує логіку стандарту IEEE 802.15.4 / Zigbee. Кожен проміжний маршрутизатор конфігурується числовим діапазоном адрес нащадків `[subtree_min .. subtree_max]` та масивом адрес дочірніх роутерів.

Маршрутизація виконується за алгоритмом:
1. Якщо `pkt->dst` потрапляє в інтервал `[subtree_min .. subtree_max]`, вузол шукає, якому конкретно дочірньому роутеру належить ця адреса, і пересилає пакет **вниз** по гілці.
2. Якщо адреса лежить поза межами діапазону, пакет відправляється **вгору** батьківському вузлу (`parent`), доки не досягне спільного предка або кореня координатора.

Це забезпечує повну відсутність фонового трафіку для оновлення маршрутних таблиць і константну складність `O(1)` за пам'яттю.

#### 3. Модуль Чарунки (Mesh Failover & Local Repair)
У чарунковій мережі кожен вузол підтримує таблицю сусідів (`NeighborEntry`), де для кожного зв'язку відстежується розрахункова вартість лінку (`link_cost`, пропорційна метриці ETX) та динамічний стан зв'язку (`is_alive`).

Коли мережевий рівень отримує пакет для пересилання:
1. Алгоритм знаходить запис у таблиці маршрутів (`MeshRoute`) для адреси `pkt->dst`.
2. Перевіряється стан основного наступного хопу (`primary_next_hop`). Якщо лінк активний (`is_alive == true`), пакет передається йому.
3. Якщо на рівні канального доступу зафіксовано втрату зв'язку (наприклад, після трьох невдалих спроб передачі без отримання MAC ACK), спрацьовує механізм **локального відновлення (*Local Repair*)**. Вузол миттєво перенаправляє пакет на резервний наступний хоп (`backup_next_hop`) без відправлення широкомовних запитів перебудови графа.

### Реалізація на C та C++

Нижче наведено дві повноцінні, компільовані реалізації: модульний C99 із статичним розподілом пам'яті (типовий для bare-metal вбудованих систем) та ідіоматичний сучасний C++20 із поліморфною ієрархією вузлів, безпечними типами `std::optional` та контейнерами.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_HOPS 16
#define MAX_NEIGHBORS 4
#define NO_ROUTE 0xFFFF

typedef enum {
    TOPO_STAR,
    TOPO_TREE,
    TOPO_MESH
} TopologyType;

/* Заголовок мережевого пакета */
typedef struct {
    uint16_t src;
    uint16_t dst;
    uint8_t  ttl;
    uint8_t  hop_count;
    char     payload[32];
} Packet;

/* --- 1. Модуль Зірки (Star) --- */
uint16_t star_forward(uint16_t self_addr, uint16_t hub_addr, const Packet *pkt) {
    if (pkt->dst == self_addr) {
        return self_addr; /* Пакет досяг адресата */
    }
    if (self_addr == hub_addr) {
        /* Хаб знає, що всі його клієнти підключені напряму в 1 хоп */
        return pkt->dst;
    }
    /* Кінцевий пристрій завжди шле на хаб */
    return hub_addr;
}

/* --- 2. Модуль Кластерного Дерева (Cskip / Tree Routing) --- */
typedef struct {
    uint16_t parent;
    uint8_t  depth;
    uint16_t child_routers[MAX_NEIGHBORS];
    uint8_t  num_child_routers;
    uint16_t subtree_min;
    uint16_t subtree_max;
} TreeNode;

uint16_t tree_forward(const TreeNode *node, uint16_t self_addr, const Packet *pkt) {
    if (pkt->dst == self_addr) {
        return self_addr;
    }

    /* Чи належить адреса призначення нашому піддереву? */
    if (pkt->dst >= node->subtree_min && pkt->dst <= node->subtree_max) {
        /* Шукаємо, якій конкретно дитині належить цей діапазон */
        for (uint8_t i = 0; i < node->num_child_routers; ++i) {
            uint16_t child = node->child_routers[i];
            if (pkt->dst == child || (pkt->dst > child && pkt->dst < child + 0x0100)) {
                return child;
            }
        }
        /* Якщо це прямий кінцевий листок цього вузла */
        return pkt->dst;
    }

    /* Адреса поза нашим піддеревом — шлемо вгору батькові */
    return node->parent;
}

/* --- 3. Модуль Чарунки (Mesh Routing & Failover) --- */
typedef struct {
    uint16_t neighbor_addr;
    uint16_t link_cost;     /* Метрика якості (ETX * 10) */
    bool     is_alive;      /* Стан зв'язку за MAC ACK */
} NeighborEntry;

typedef struct {
    uint16_t target;
    uint16_t primary_next_hop;
    uint16_t backup_next_hop;
} MeshRoute;

typedef struct {
    NeighborEntry neighbors[MAX_NEIGHBORS];
    uint8_t       num_neighbors;
    MeshRoute     routes[MAX_NEIGHBORS];
    uint8_t       num_routes;
} MeshNode;

uint16_t mesh_forward(const MeshNode *node, uint16_t self_addr, const Packet *pkt) {
    if (pkt->dst == self_addr) {
        return self_addr;
    }

    for (uint8_t i = 0; i < node->num_routes; ++i) {
        if (node->routes[i].target == pkt->dst) {
            uint16_t primary = node->routes[i].primary_next_hop;
            
            /* Перевіряємо працездатність основного наступного хопу */
            for (uint8_t j = 0; j < node->num_neighbors; ++j) {
                if (node->neighbors[j].neighbor_addr == primary) {
                    if (node->neighbors[j].is_alive) {
                        return primary; /* Основний лінк працює */
                    }
                    break;
                }
            }

            /* Основний шлях зламано: застосовуємо Local Repair на резервний хоп */
            uint16_t backup = node->routes[i].backup_next_hop;
            for (uint8_t j = 0; j < node->num_neighbors; ++j) {
                if (node->neighbors[j].neighbor_addr == backup && node->neighbors[j].is_alive) {
                    return backup; /* Резервний маршрут успішно задіяно */
                }
            }
        }
    }
    return NO_ROUTE;
}

int main(void) {
    printf("=== Демонстрація рушія маршрутизації вбудованих топологій ===\n\n");

    Packet pkt = {
        .src = 0x0005,
        .dst = 0x0001,
        .ttl = 8,
        .hop_count = 0,
        .payload = "Telemetry: 24.5C"
    };

    /* 1. Тест Зірки */
    printf("[1. Зірка]\n");
    uint16_t hub = 0x0001;
    uint16_t node_star = 0x0005;
    uint16_t next_star = star_forward(node_star, hub, &pkt);
    printf("Вузол 0x%04X шле пакет до 0x%04X. Next Hop -> 0x%04X (Хаб)\n\n",
           node_star, pkt.dst, next_star);

    /* 2. Тест Дерева */
    printf("[2. Кластерне дерево (Cskip)]\n");
    TreeNode r1 = {
        .parent = 0x0000, /* Корінь */
        .depth = 1,
        .child_routers = {0x0020},
        .num_child_routers = 1,
        .subtree_min = 0x0010,
        .subtree_max = 0x00FF
    };
    Packet pkt_up = { .src = 0x0015, .dst = 0x0200 };
    uint16_t next_tree = tree_forward(&r1, 0x0010, &pkt_up);
    printf("Роутер 0x0010 отримав пакет до 0x%04X (поза піддеревом [0x0010..0x00FF]).\n"
           "Форвардинг вгору -> Батько 0x%04X\n\n", pkt_up.dst, next_tree);

    /* 3. Тест Чарунки з відмовою лінку (Failover) */
    printf("[3. Чарунка (Mesh Failover)]\n");
    MeshNode mesh_n3 = {
        .neighbors = {
            { .neighbor_addr = 0x0002, .link_cost = 12, .is_alive = false }, /* Основний лінк розірвано */
            { .neighbor_addr = 0x0004, .link_cost = 25, .is_alive = true  }  /* Резервний лінк живий */
        },
        .num_neighbors = 2,
        .routes = {
            { .target = 0x0001, .primary_next_hop = 0x0002, .backup_next_hop = 0x0004 }
        },
        .num_routes = 1
    };

    uint16_t next_mesh = mesh_forward(&mesh_n3, 0x0003, &pkt);
    printf("Вузол 0x0003: Основний шлях до 0x0001 через 0x0002 МЕРТВИЙ (is_alive=false).\n"
           "Спрацював Local Repair: пакет перенаправлено через резервний Next Hop -> 0x%04X\n",
           next_mesh);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <string_view>
#include <cstdint>
#include <format>

struct Packet {
    uint16_t src;
    uint16_t dst;
    uint8_t  ttl{8};
    uint8_t  hopCount{0};
    std::string_view payload;
};

/* Базовий інтерфейс вузла маршрутизації */
class RoutingNode {
public:
    explicit RoutingNode(uint16_t address) : address_{address} {}
    virtual ~RoutingNode() = default;

    [[nodiscard]] uint16_t address() const noexcept { return address_; }
    [[nodiscard]] virtual std::optional<uint16_t> forward(const Packet& pkt) const = 0;

protected:
    uint16_t address_;
};

/* --- 1. Реалізація Зірки (Star) --- */
class StarNode final : public RoutingNode {
public:
    StarNode(uint16_t address, uint16_t hubAddress)
        : RoutingNode(address), hubAddress_{hubAddress} {}

    [[nodiscard]] std::optional<uint16_t> forward(const Packet& pkt) const noexcept override {
        if (pkt.dst == address_) {
            return address_;
        }
        if (address_ == hubAddress_) {
            return pkt.dst; /* Шлюз має прямі радіолінки до всіх пристроїв */
        }
        return hubAddress_; /* Клієнтський вузол шле все на шлюз */
    }

private:
    uint16_t hubAddress_;
};

/* --- 2. Реалізація Кластерного Дерева (Cskip / Hierarchical Tree) --- */
class TreeNode final : public RoutingNode {
public:
    TreeNode(uint16_t address, uint16_t parentAddress, uint16_t subMin, uint16_t subMax)
        : RoutingNode(address), parent_{parentAddress}, subMin_{subMin}, subMax_{subMax} {}

    void addChildRouter(uint16_t childAddr) {
        childRouters_.push_back(childAddr);
    }

    [[nodiscard]] std::optional<uint16_t> forward(const Packet& pkt) const noexcept override {
        if (pkt.dst == address_) {
            return address_;
        }

        /* Перевіряємо попадання в префікс піддерева */
        if (pkt.dst >= subMin_ && pkt.dst <= subMax_) {
            for (uint16_t child : childRouters_) {
                if (pkt.dst == child || (pkt.dst > child && pkt.dst < child + 0x0100)) {
                    return child;
                }
            }
            return pkt.dst; /* Прямий листок */
        }

        /* Ціль поза піддеревом — маршрутизація вгору до кореня */
        return parent_;
    }

private:
    uint16_t parent_;
    uint16_t subMin_;
    uint16_t subMax_;
    std::vector<uint16_t> childRouters_;
};

/* --- 3. Реалізація Чарунки з динамічним відновленням (Mesh) --- */
struct Neighbor {
    uint16_t address;
    uint16_t linkCost; /* Оцінка якості (ETX) */
    bool     isAlive;
};

struct RouteEntry {
    uint16_t destination;
    uint16_t primaryNextHop;
    uint16_t backupNextHop;
};

class MeshNode final : public RoutingNode {
public:
    explicit MeshNode(uint16_t address) : RoutingNode(address) {}

    void addNeighbor(Neighbor n) { neighbors_.push_back(n); }
    void addRoute(RouteEntry r)  { routes_.push_back(r); }

    void setLinkStatus(uint16_t neighborAddr, bool alive) {
        for (auto& n : neighbors_) {
            if (n.address == neighborAddr) {
                n.isAlive = alive;
                break;
            }
        }
    }

    [[nodiscard]] std::optional<uint16_t> forward(const Packet& pkt) const noexcept override {
        if (pkt.dst == address_) {
            return address_;
        }

        for (const auto& route : routes_) {
            if (route.destination == pkt.dst) {
                /* Перевірка працездатності первинного шляху */
                if (isNeighborAlive(route.primaryNextHop)) {
                    return route.primaryNextHop;
                }
                /* Локальне відновлення на резервний шлях */
                if (isNeighborAlive(route.backupNextHop)) {
                    return route.backupNextHop;
                }
            }
        }
        return std::nullopt; /* Маршрут недоступний */
    }

private:
    [[nodiscard]] bool isNeighborAlive(uint16_t neighborAddr) const noexcept {
        for (const auto& n : neighbors_) {
            if (n.address == neighborAddr) {
                return n.isAlive;
            }
        }
        return false;
    }

    std::vector<Neighbor>   neighbors_;
    std::vector<RouteEntry> routes_;
};

int main() {
    std::cout << "=== C++ Routing Engine Simulation ===\n\n";

    const Packet samplePkt{
        .src = 0x0005,
        .dst = 0x0001,
        .ttl = 8,
        .hopCount = 0,
        .payload = "SensorData: 42.0"
    };

    /* 1. Star */
    const StarNode starNode(0x0005, 0x0001);
    if (auto nextHop = starNode.forward(samplePkt)) {
        std::cout << std::format("[Star] Forwarding from 0x{:04X} to Hub -> 0x{:04X}\n",
                                 starNode.address(), *nextHop);
    }

    /* 2. Tree */
    TreeNode treeNode(0x0010, 0x0000, 0x0010, 0x00FF);
    treeNode.addChildRouter(0x0020);
    const Packet outOfSubtreePkt{ .src = 0x0015, .dst = 0x0500, .payload = "Upward" };
    if (auto nextHop = treeNode.forward(outOfSubtreePkt)) {
        std::cout << std::format("[Tree] Target 0x{:04X} out of subtree. Forwarding UP -> 0x{:04X}\n",
                                 outOfSubtreePkt.dst, *nextHop);
    }

    /* 3. Mesh Failover */
    MeshNode meshNode(0x0003);
    meshNode.addNeighbor({ .address = 0x0002, .linkCost = 10, .isAlive = false });
    meshNode.addNeighbor({ .address = 0x0004, .linkCost = 22, .isAlive = true });
    meshNode.addRoute({ .destination = 0x0001, .primaryNextHop = 0x0002, .backupNextHop = 0x0004 });

    if (auto nextHop = meshNode.forward(samplePkt)) {
        std::cout << std::format("[Mesh] Primary next-hop 0x0002 dead. Local repair -> 0x{:04X}\n",
                                 *nextHop);
    }

    return 0;
}
```
:::

### Інженерні крайові випадки та пастки прошивки

Під час перенесення наведених алгоритмів у реальну прошивку мікроконтролера слід враховувати такі підводні камені:

1. **Переповнення таблиці сусідів (Neighbor Table Thrashing)**: У великих мережах вузол може чути маякові сигнали від десятків роутерів. Якщо таблиця обмежена 8 записами, часте витіснення (LRU thrashing) призводить до втрати інформації про стабільні лінки. Рішення: розділення таблиці на «кандидатів» та «фіксованих батьків» із захистом від частих перемикань (гістерезис метрики ETX).
2. **Виявлення зациклення пакетів (Routing Loops)**: У чарункових мережах під час локального відновлення виникає ризик тимчасового зациклення (A шле B, а B шле A). Протокол RPL розв'язує це через сувору монотонність рангу: вузлу заборонено надсилати пакети вгору по дереву абоненту з рівним чи вищим числовим рангом. Додатково кожен пакет несе лічильник `TTL`, який декрементується на кожному хопі й знищує зациклений кадр при досягненні нуля.
3. **Стан «сироти» у дереві (Orphan State Recovery)**: Коли батьківський роутер вимикається, деревоподібний вузол втрачає зв'язок. Щоб не посадити батарею нескінченним пошуком у радіоефірі, процедура відновлення зв'язку (*Orphan Scan*) повинна використовувати експоненційний відступ (*Exponential Backoff*): сканування каналу через 1 с, потім 2 с, 4 с, 8 с, аж до переходу в рідкісні періодичні перевірки раз на годину.

### Апаратний бюджет пам'яті та налагодження в ефірі

У реальному проекті на базі чіпів nRF52840 або ESP32-C6 кожен тип топології накладає фіксовані вимоги до Flash та SRAM мікроконтролера:
- **Зірковий стек (Star)**: займає близько 4–8 кБ Flash під драйвер радіо і менше 1 кБ RAM для буферів одного кадру. Це дозволяє використовувати найдешевші мікроконтролери без зовнішньої пам'яті.
- **Кластерне дерево (Cluster-Tree)**: вимагає 16–32 кБ Flash для стека 802.15.4 MAC та 2–4 кБ RAM для черги пакетів суперкадру.
- **Повноцінний Mesh (Thread / OpenThread)**: потребує щонайменше 128–192 кБ Flash та від 16 до 32 кБ RAM під таблиці маршрутизації, контексти безпеки криптографії AES-CCM та шари стиснення 6LoWPAN.

Для діагностики багатохопової маршрутизації в польових умовах незамінним інструментом є апаратний радіосніфер (наприклад, USB-донгл nRF52840 із прошивкою Nordic Sniffer), що захоплює сирі кадри ефіру та передає їх у Wireshark. Аналізуючи поля `Sequence Number`, `Source/Destination PAN ID` та `Frame Pending Bit`, інженер може наочно простежити кожен стрибок пакета, виявити втрати підтверджень MAC ACK та зафіксувати момент спрацьовування алгоритму перемикання на резервного батька.
