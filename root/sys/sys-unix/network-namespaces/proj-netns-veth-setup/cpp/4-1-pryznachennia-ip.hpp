struct alignas(NLMSG_ALIGNTO) IpAddrRequest {
    nlmsghdr nlh{};
    ifaddrmsg ifa{};
    std::array<char, 256> buf{};
};

IpAddrRequest req{};
req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifaddrmsg));
req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
req.nlh.nlmsg_type = RTM_NEWADDR;

req.ifa.ifa_family = AF_INET;
req.ifa.ifa_prefixlen = 24;
req.ifa.ifa_flags = IFA_F_PERMANENT;
req.ifa.ifa_scope = RT_SCOPE_UNIVERSE;
req.ifa.ifa_index = ::if_nametoindex("veth-host");

// Сама адреса — окремим атрибутом IFA_LOCAL
auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(&req) + req.nlh.nlmsg_len);
rta->rta_type = IFA_LOCAL;
rta->rta_len = RTA_LENGTH(sizeof(in_addr));
::inet_pton(AF_INET, "10.0.0.1", RTA_DATA(rta));
req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
