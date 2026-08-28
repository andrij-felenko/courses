struct net_bridge_port {
    struct net_bridge       *br;                /* Вказівник на батьківський міст */
    struct net_device       *dev;               /* Підпорядкований інтерфейс (eth0, veth0) */
    struct list_head        list;               /* Елемент списку br->port_list */
    
    u8                      state;              /* Стан порту STP (BR_STATE_*) */
    u8                      priority;           /* Пріоритет порту STP */
    u32                     path_cost;          /* Вартість шляху STP */
    u16                     port_no;            /* Внутрішній індекс порту в мості */
    u32                     flags;              /* Прапорці (BR_LEARNING, BR_FLOOD, BR_ISOLATED) */
    
    struct net_bridge_vlan_group __rcu *vlgrp;  /* VLAN-конфігурація порту */
    struct rcu_head         rcu;
};
