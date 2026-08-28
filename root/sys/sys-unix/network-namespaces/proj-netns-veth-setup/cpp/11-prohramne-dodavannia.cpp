struct RtMsgRequest {
    nlmsghdr nlh{};
    rtmsg rtm{};
    std::array<char, 256> buf{};
};

void add_default_gateway(int nl_fd, const std::string& gw_ip, int if_index) {
    RtMsgRequest req{};
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(rtmsg));
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.nlh.nlmsg_type = RTM_NEWROUTE;

    req.rtm.rtm_family = AF_INET;
    req.rtm.rtm_table = RT_TABLE_MAIN;
    req.rtm.rtm_protocol = RTPROT_STATIC;
    req.rtm.rtm_scope = RT_SCOPE_UNIVERSE;
    req.rtm.rtm_type = RTN_UNICAST;
    req.rtm.rtm_dst_len = 0;   // 0.0.0.0/0

    auto put = [&](unsigned short type, const void* src, std::size_t len) {
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(&req) + req.nlh.nlmsg_len);
        rta->rta_type = type;
        rta->rta_len = RTA_LENGTH(len);
        std::memcpy(RTA_DATA(rta), src, len);
        req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
    };

    in_addr gw{};
    if (::inet_pton(AF_INET, gw_ip.c_str(), &gw) != 1) {
        throw std::invalid_argument{"некоректна адреса шлюзу: " + gw_ip};
    }
    put(RTA_GATEWAY, &gw, sizeof(gw));
    put(RTA_OIF, &if_index, sizeof(if_index));

    if (::send(nl_fd, &req, req.nlh.nlmsg_len, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "RTM_NEWROUTE");
    }
}
