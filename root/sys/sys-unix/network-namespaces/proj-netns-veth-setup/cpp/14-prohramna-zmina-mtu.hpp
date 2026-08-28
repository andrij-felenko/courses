struct MtuRequest {
    nlmsghdr nlh{};
    ifinfomsg ifm{};
    std::array<char, 64> buf{};
};

MtuRequest mtu_req{};
mtu_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
mtu_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
mtu_req.nlh.nlmsg_type = RTM_NEWLINK;
mtu_req.ifm.ifi_index = ::if_nametoindex("veth-host");

auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(&mtu_req) + mtu_req.nlh.nlmsg_len);
rta->rta_type = IFLA_MTU;
rta->rta_len = RTA_LENGTH(sizeof(uint32_t));
*reinterpret_cast<uint32_t*>(RTA_DATA(rta)) = 1450;
mtu_req.nlh.nlmsg_len = NLMSG_ALIGN(mtu_req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
