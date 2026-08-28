struct DelLinkRequest {
    nlmsghdr nlh{};
    ifinfomsg ifm{};
} del_req{};

del_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
del_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
del_req.nlh.nlmsg_type = RTM_DELLINK;
del_req.ifm.ifi_index = ::if_nametoindex("veth-host");

sockaddr_nl sa{.nl_family = AF_NETLINK};
::sendto(nl_fd, &del_req, del_req.nlh.nlmsg_len, 0, reinterpret_cast<sockaddr*>(&sa), sizeof(sa));
