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
