// Конфігурація мережевого ruleset у C++
landlock_ruleset_attr net_attr{};
net_attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP |
                              LANDLOCK_ACCESS_NET_CONNECT_TCP;

UniqueFd net_ruleset(landlock_create_ruleset(&net_attr, sizeof(net_attr), 0));

landlock_net_port_attr port_attr{};
port_attr.allowed_access = LANDLOCK_ACCESS_NET_CONNECT_TCP;
port_attr.port = 443; // Дозволити вихідні з'єднання лише на HTTPS

landlock_add_rule(net_ruleset.get(), LANDLOCK_RULE_NET_PORT, &port_attr, 0);
