int main() {
    ScuttlebuttEngine node_a("Node-A", 100);
    ScuttlebuttEngine node_b("Node-B", 100);

    // Node-A змінює свої атрибути
    node_a.mutate_local_key("STATUS", "NORMAL"); // version 1
    node_a.mutate_local_key("LOAD", "0.85");     // version 2

    // 1. Фаза SYN: A -> B (надсилання дайджесту)
    std::vector<GossipDigest> syn_msg = node_a.make_syn_digest();

    // 2. Фаза ACK: B обробляє SYN, знаходить дельти для A та формує свій дайджест для A
    std::vector<GossipDelta> ack_deltas = node_b.collect_deltas_for_peer(syn_msg);
    std::vector<GossipDigest> ack_digest = node_b.make_syn_digest();

    // 3. Фаза ACK2: A застосовує дельти від B та генерує дельти для B
    node_a.apply_deltas(ack_deltas);
    std::vector<GossipDelta> ack2_deltas = node_a.collect_deltas_for_peer(ack_digest);

    // B застосовує дельти від A
    node_b.apply_deltas(ack2_deltas);

    std::cout << "Реконсиляція C++20 завершена успішно. Стан Node-B для Node-A: v"
              << node_b.get_node_max_version("Node-A") << "\n";
    return 0;
}
