#include <stdint.h>
#include <stdbool.h>

#define ADDR_NONE 0xFFFF

typedef struct {
    uint16_t src;
    uint16_t dst;
    uint8_t  ttl;
} NetPacket;

/* 1. Логіка Зірки */
uint16_t route_star(uint16_t my_addr, uint16_t hub_addr, const NetPacket *pkt) {
    if (pkt->dst == my_addr) return my_addr;
    if (my_addr == hub_addr) return pkt->dst; /* Хаб шле прямо адресату */
    return hub_addr; /* Кінцевий датчик завжди шле на хаб */
}

/* 2. Логіка Дерева (Cskip Range Check) */
typedef struct {
    uint16_t parent;
    uint16_t child_router;
    uint16_t sub_min;
    uint16_t sub_max;
} TreeRouteConfig;

uint16_t route_tree(uint16_t my_addr, const TreeRouteConfig *cfg, const NetPacket *pkt) {
    if (pkt->dst == my_addr) return my_addr;
    
    /* Якщо адреса призначення лежить у піддереві */
    if (pkt->dst >= cfg->sub_min && pkt->dst <= cfg->sub_max) {
        return cfg->child_router; /* Шлемо вниз дочірньому роутеру */
    }
    
    /* Якщо поза межами піддерева — шлемо вгору батьківському вузлу */
    return cfg->parent;
}

/* 3. Логіка Чарунки (Failover to Backup Next-Hop) */
typedef struct {
    uint16_t target;
    uint16_t primary_hop;
    uint16_t backup_hop;
} MeshRouteEntry;

uint16_t route_mesh(uint16_t my_addr, const MeshRouteEntry *route, 
                    bool is_primary_alive, const NetPacket *pkt) {
    if (pkt->dst == my_addr) return my_addr;
    
    if (pkt->dst == route->target) {
        if (is_primary_alive) {
            return route->primary_hop;
        }
        /* Локальне відновлення: перемикання на альтернативний хоп */
        return route->backup_hop;
    }
    return ADDR_NONE;
}
