struct {
    struct nlmsghdr nlh;
    struct ifinfomsg ifm;
} del_req;

memset(&del_req, 0, sizeof(del_req));
del_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
del_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
del_req.nlh.nlmsg_type = RTM_DELLINK;
del_req.ifm.ifi_index = if_nametoindex("veth-host");

sendto(nl_fd, &del_req, del_req.nlh.nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa));
