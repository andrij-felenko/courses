struct {
    struct nlmsghdr nlh;
    struct ifinfomsg ifm;
    char buf[64];
} mtu_req;

memset(&mtu_req, 0, sizeof(mtu_req));
mtu_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
mtu_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
mtu_req.nlh.nlmsg_type = RTM_NEWLINK;
mtu_req.ifm.ifi_index = if_nametoindex("veth-host");

struct rtattr *rta = (struct rtattr *)(((char *)&mtu_req) + mtu_req.nlh.nlmsg_len);
rta->rta_type = IFLA_MTU;
rta->rta_len = RTA_LENGTH(sizeof(uint32_t));
*(uint32_t *)RTA_DATA(rta) = 1450;
mtu_req.nlh.nlmsg_len = NLMSG_ALIGN(mtu_req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
