struct rtmsg_req {
    struct nlmsghdr nlh;
    struct rtmsg rtm;
    char buf[256];
};

void add_default_gateway(int nl_fd, const char *gw_ip, int if_index) {
    struct rtmsg_req req;
    memset(&req, 0, sizeof(req));
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct rtmsg));
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.nlh.nlmsg_type = RTM_NEWROUTE;

    req.rtm.rtm_family = AF_INET;
    req.rtm.rtm_table = RT_TABLE_MAIN;
    req.rtm.rtm_protocol = RTPROT_STATIC;
    req.rtm.rtm_scope = RT_SCOPE_UNIVERSE;
    req.rtm.rtm_type = RTN_UNICAST;
    req.rtm.rtm_dst_len = 0;   /* 0.0.0.0/0 — маршрут за замовчуванням */

    /* Куди слати (RTA_GATEWAY) і через який пристрій (RTA_OIF) */
    struct rtattr *gw = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    gw->rta_type = RTA_GATEWAY;
    gw->rta_len = RTA_LENGTH(sizeof(struct in_addr));
    inet_pton(AF_INET, gw_ip, RTA_DATA(gw));
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(gw->rta_len);

    struct rtattr *oif = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    oif->rta_type = RTA_OIF;
    oif->rta_len = RTA_LENGTH(sizeof(int));
    *(int *)RTA_DATA(oif) = if_index;
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(oif->rta_len);

    send(nl_fd, &req, req.nlh.nlmsg_len, 0);
}
