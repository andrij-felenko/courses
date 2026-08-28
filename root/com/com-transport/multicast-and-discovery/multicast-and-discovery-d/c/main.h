int sock = socket(AF_INET, SOCK_DGRAM, 0);
int yes = 1;
setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));  // порт ділять кілька процесів

struct sockaddr_in addr = { .sin_family = AF_INET,
                            .sin_port   = htons(5000),
                            .sin_addr   = { .s_addr = htonl(INADDR_ANY) } };
bind(sock, (struct sockaddr *)&addr, sizeof(addr));

struct ip_mreqn mreq = { 0 };
inet_pton(AF_INET, "239.1.2.3", &mreq.imr_multiaddr);   // яку групу слухати
mreq.imr_ifindex = if_nametoindex("eth0");              // НА ЯКОМУ інтерфейсі слухати
setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq));
