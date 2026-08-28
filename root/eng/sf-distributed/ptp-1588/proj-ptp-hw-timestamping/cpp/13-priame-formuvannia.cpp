int l2_sock = ::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_1588));
if (l2_sock < 0) {
    std::perror("socket AF_PACKET");
}

sockaddr_ll sll{};
sll.sll_family = AF_PACKET;
sll.sll_ifindex = if_nametoindex("eth0");
sll.sll_protocol = htons(ETH_P_1588);

if (::bind(l2_sock, reinterpret_cast<sockaddr*>(&sll), sizeof(sll)) < 0) {
    std::perror("bind AF_PACKET");
}
