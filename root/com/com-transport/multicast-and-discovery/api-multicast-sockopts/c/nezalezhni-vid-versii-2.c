/* приєднання, яке не знає й не хоче знати версію протоколу */
static int join_any(int fd, const struct sockaddr_storage *group,
                    socklen_t grouplen, unsigned ifindex)
{
    struct group_req req;
    memset(&req, 0, sizeof req);
    req.gr_interface = ifindex;
    memcpy(&req.gr_group, group, grouplen);

    int level = (group->ss_family == AF_INET6) ? IPPROTO_IPV6 : IPPROTO_IP;
    return setsockopt(fd, level, MCAST_JOIN_GROUP, &req, sizeof req);
}
