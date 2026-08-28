/* Конфігурація мережевого ruleset у C */
struct landlock_ruleset_attr net_attr = {
    .handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP |
                          LANDLOCK_ACCESS_NET_CONNECT_TCP,
};
int net_ruleset = landlock_create_ruleset(&net_attr, sizeof(net_attr), 0);

struct landlock_net_port_attr port_attr = {
    .allowed_access = LANDLOCK_ACCESS_NET_CONNECT_TCP,
    .port = 443, /* Дозволити вихідні з'єднання лише на HTTPS */
};
landlock_add_rule(net_ruleset, LANDLOCK_RULE_NET_PORT, &port_attr, 0);
