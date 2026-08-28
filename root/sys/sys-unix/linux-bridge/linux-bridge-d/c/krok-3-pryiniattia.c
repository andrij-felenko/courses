/* Спрощена схема вибору маршруту в br_handle_frame_finish */
if (is_multicast_ether_addr(dest)) {
    if (is_broadcast_ether_addr(dest)) {
        br_flood(br, skb, BR_PKT_BROADCAST, false);
    } else {
        /* Обробка через IGMP snooping / MDB або загальний multicast flood */
        br_multicast_forward(br, skb, false);
    }
} else if ((dst = br_fdb_find_rcu(br, dest, vid)) != NULL) {
    if (dst->is_local)
        return br_pass_frame_up(skb);
    br_forward(dst->dst, skb, false, true);
} else {
    /* Невідомий Unicast: розсилка на всі порти */
    br_flood(br, skb, BR_PKT_UNICAST, false);
}
