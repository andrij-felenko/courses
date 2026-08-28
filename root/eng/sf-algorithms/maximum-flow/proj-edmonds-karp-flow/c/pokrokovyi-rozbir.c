int main(void) {
    FlowNetworkC net;
    flow_network_init(&net, 6);

    flow_network_add_edge(&net, 0, 1, 10, 0);
    flow_network_add_edge(&net, 0, 2, 10, 0);
    flow_network_add_edge(&net, 1, 2, 2, 0);
    flow_network_add_edge(&net, 1, 3, 4, 0);
    flow_network_add_edge(&net, 1, 4, 8, 0);
    flow_network_add_edge(&net, 2, 4, 9, 0);
    flow_network_add_edge(&net, 3, 5, 10, 0);
    flow_network_add_edge(&net, 4, 5, 10, 0);

    int64_t max_val = flow_network_max_flow(&net, 0, 5);
    printf("Максимальний потік: %lld\n", (long long)max_val);

    bool in_s[6];
    flow_network_min_cut(&net, 0, in_s);

    printf("Критичні ребра мінімального розрізу (S -> T):\n");
    for (int u = 0; u < 6; ++u) {
        if (!in_s[u]) continue;
        for (int e = net.head[u]; e != -1; e = net.arcs[e].next) {
            int v = net.arcs[e].to;
            if (!in_s[v] && net.arcs[e].cap > 0) {
                printf("  Ребро %d -> %d (насичено %lld/%lld)\n",
                       u, v, (long long)net.arcs[e].flow, (long long)net.arcs[e].cap);
            }
        }
    }

    return 0;
}
