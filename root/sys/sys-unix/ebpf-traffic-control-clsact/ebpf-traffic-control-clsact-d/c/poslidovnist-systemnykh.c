static inline struct sk_buff *sch_handle_ingress(struct sk_buff *skb,
                                                 struct packet_type **pt_prev,
                                                 int *ret, struct net_device *orig_dev) {
    struct mini_Qdisc *miniq = rcu_dereference_bh(skb->dev->miniq_ingress);
    struct tcf_result res;

    if (!miniq)
        return skb;

    // Виклик класифікаторів TC (включаючи cls_bpf) у режимі RCU
    switch (tcf_classify(skb, miniq->block, miniq->filter_list, &res, false)) {
    case TC_ACT_OK:
    case TC_ACT_RECLASSIFY:
        break;
    case TC_ACT_SHOT:
        kfree_skb(skb);
        return NULL;
    case TC_ACT_REDIRECT:
        skb_do_redirect(skb);
        return NULL;
    }
    return skb;
}
